"""Normalise an extraction into interoperability artefacts, and audit the export.

This is the pipeline's export stage. It takes a technique's output -- the manifest
and the raw rows it pulled -- and shapes each row into the standards its layer
carries (``interop.mapping.LAYER_STANDARDS``): HL7 v2 messages and FHIR resources.
DICOM and ISO/IEEE 11073 are still stubs and are skipped.

Two things make this compliance work rather than plumbing:

1. **The manifest's claim becomes behaviour.** If the run declared
   ``security.identifiers_pseudonymised``, direct identifiers are replaced by keyed
   tokens *before* shaping. The compliant technique declares it; the baseline does
   not; the exports differ accordingly.

2. **The export is audited, not trusted.** ``audit()`` searches every emitted
   artefact for the raw direct-identifier values that were extracted, and counts
   the leaks. A compliant export leaks none; the baseline's leaks every one. This
   turns SS-01's pseudonymisation check from a declaration the rule takes on faith
   into a property verified against the actual output.

# DPDP Act 2023 -- security safeguards (pseudonymisation on export) and data
# minimisation (shaping adds nothing that was not extracted).
"""

from __future__ import annotations

import json
import re
import secrets
from pathlib import Path
from typing import Any

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:  # pragma: no cover
    from compliance.audit import AuditLog

from compliance.pseudonymise import (
    QUASI_IDENTIFIERS,
    direct_identifier_fields,
    generalise_row,
    k_anonymity,
    pseudonymise_row,
)
from extraction.technique import TechniqueOutput
from interop.fhir.resources import bundle as fhir_bundle, shape_fhir
from interop.hl7.messages import shape_hl7
from interop.layers import HISLayer
from interop.mapping import InteropStandard, standards_for

_REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = _REPO_ROOT / "docs" / "benchmark_results"
# Who holds an export's pseudonymisation key (see NormalisedOutput.to_files).
KEY_HOLDER = "the data-protection officer (DPO)"


class ExportAudit(BaseModel):
    """Did any raw direct identifier reach the exported artefacts -- and how
    identifiable are the rows that left?

    A sanity check, not a discriminator: a technique that never pseudonymises
    leaks every identifier by construction. The match is normalised (case,
    punctuation, a name's tokens in any order, a phone's digits), so a name
    re-ordered for HL7 (``Family^Given``) or a re-formatted phone is still found.
    ``k`` is the k-anonymity of the exported registration rows over the
    quasi-identifiers (date of birth, sex, PIN code) as exported.
    """

    pseudonymisation_declared: bool
    identifier_values: int             # distinct raw direct-identifier values extracted
    leaked: int                        # of those, how many appear in an artefact (normalised match)
    artefacts_checked: int
    k: int | None = None               # smallest group sharing the exported quasi-identifiers
    k_rows: int = 0                    # registration rows k is computed over
    generalised: bool = False          # quasi-identifiers generalised on export

    @property
    def clean(self) -> bool:
        return self.leaked == 0

    def one_line(self) -> str:
        state = "declared" if self.pseudonymisation_declared else "not declared"
        verdict = "no raw direct identifier in the export" if self.clean else (
            f"{self.leaked} of {self.identifier_values} raw direct identifiers appear in the export"
        )
        quasi = ""
        if self.k is not None:
            quasi = (f"; quasi-identifiers {'generalised (birth year, 3-digit PIN)' if self.generalised else 'raw'}, "
                     f"k = {self.k} over {self.k_rows} row(s)")
        return f"pseudonymisation {state}; {verdict}{quasi} ({self.artefacts_checked} artefacts checked)"


class NormalisedOutput(BaseModel):
    run_id: str
    pseudonymised: bool
    # Carried from the manifest so the export can be scheduled for erasure.
    purpose: str = ""
    retention_days: int | None = None
    deletion_mechanism: str = ""
    schedule_note: str = ""                       # set by to_files(): when the export is due to go
    hl7: dict[str, list[str]] = Field(default_factory=dict)              # layer -> encoded messages
    fhir: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)  # layer -> resources
    skipped_standards: list[str] = Field(default_factory=list)
    subjects: list[str] = Field(default_factory=list)    # audit tokens of the patients exported
    unattributed: int = 0
    # The registration rows' quasi-identifiers as exported, for the k-anonymity figure.
    quasi_rows: list[dict[str, Any]] = Field(default_factory=list, exclude=True, repr=False)
    # The export's pseudonymisation key. Never serialised with the export: it is
    # written to a separate key file the data-protection officer holds, so the
    # hospital -- and only the key holder -- can re-link a token to a patient.
    key: str = Field(default="", exclude=True, repr=False)

    def counts(self) -> dict[str, int]:
        return {
            "hl7_messages": sum(len(v) for v in self.hl7.values()),
            "fhir_resources": sum(len(v) for v in self.fhir.values()),
        }

    def sample(self, layer: HISLayer) -> str:
        """One HL7 message and one FHIR resource for ``layer``, for a reader."""

        lines: list[str] = []
        msgs = self.hl7.get(layer.value) or []
        if msgs:
            lines.append("  HL7 v2:")
            lines += ["    " + seg for seg in msgs[0].split("\r")]
        res = self.fhir.get(layer.value) or []
        if res:
            lines.append("  FHIR:")
            lines += ["    " + l for l in json.dumps(res[0], indent=2).split("\n")]
        return "\n".join(lines) if lines else "  (nothing shaped for this layer)"

    def to_files(self, directory: Path | None = None, *, audit: "AuditLog | None" = None,
                 key_dir: Path | None = None) -> list[Path]:
        """Write the export: one ``.hl7`` file of messages and one FHIR Bundle.

        Segments are newline-separated in the ``.hl7`` file so a reader can open
        it; an interface engine would expect ``\\r``. The FHIR side is a
        ``collection`` Bundle -- the resources exactly as shaped, wrapped in the
        standard container.

        Write only exports whose identifiers are pseudonymised when the source
        may be real: the caller decides, and the audit says which is which.

        Beside the files goes a retention sidecar (``compliance.retention``):
        the run, the retention the manifest declared, and the date after which
        ``purge_expired`` erases them. The export is logged as an event.

        A pseudonymised export's key is written apart from it -- to
        ``key_dir``, by default a sibling ``<directory>.keys`` folder -- with
        its holder (the data-protection officer); the sidecar records where,
        and the purge erases it with the export.
        """

        from compliance.audit import AuditEvent, AuditLog
        from compliance.models import ExtractionRun, Purpose
        from compliance.retention import schedule

        directory = directory or ARTIFACT_DIR
        directory.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []

        messages = [m for msgs in self.hl7.values() for m in msgs]
        if messages:
            hl7_path = directory / f"{self.run_id}.hl7"
            hl7_path.write_text(
                "\n\n".join(m.replace("\r", "\n") for m in messages) + "\n",
                encoding="utf-8",
            )
            written.append(hl7_path)

        resources = [r for rs in self.fhir.values() for r in rs]
        if resources:
            bundle = fhir_bundle(resources, namespace=self.run_id)
            fhir_path = directory / f"{self.run_id}.fhir.json"
            fhir_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
            written.append(fhir_path)

        key_file: Path | None = None
        if written and self.pseudonymised and self.key:
            key_dir = key_dir or directory.with_name(directory.name + ".keys")
            key_dir.mkdir(parents=True, exist_ok=True)
            key_file = key_dir / f"{self.run_id}.key.json"
            key_file.write_text(json.dumps({
                "run_id": self.run_id, "holder": KEY_HOLDER, "key": self.key,
                "use": "re-link the export's tokens to patients; erased with the export",
            }, indent=2), encoding="utf-8")

        if written and self.purpose:
            stub = ExtractionRun(run_id=self.run_id, purpose=Purpose(self.purpose),
                                 retention_days=self.retention_days,
                                 deletion_mechanism=self.deletion_mechanism or None)
            sched = schedule(stub, written, key_file=key_file, key_holder=KEY_HOLDER if key_file else "")
            if sched is not None:
                self.schedule_note = sched.one_line()
                written.append(directory / sched.path_name)
            (audit or AuditLog()).record(AuditEvent(
                event="export", run_id=self.run_id, purpose=self.purpose,
                records=self.counts()["hl7_messages"] + self.counts()["fhir_resources"],
                subjects=self.subjects, unattributed=self.unattributed,
                note=f"{'pseudonymised' if self.pseudonymised else 'RAW'} export, "
                     f"{len(written)} file(s); " + (self.schedule_note or "no retention declared")
                     + (f"; key held by {KEY_HOLDER}, apart from the export" if key_file else ""),
            ))
        return written

    def render_summary(self) -> str:
        c = self.counts()
        lines = [
            f"normalised '{self.run_id}': {c['hl7_messages']} HL7 v2 messages, "
            f"{c['fhir_resources']} FHIR resources"
            + ("; direct identifiers pseudonymised" if self.pseudonymised else "; identifiers raw"),
        ]
        for layer_value in sorted(set(self.hl7) | set(self.fhir)):
            h = len(self.hl7.get(layer_value, []))
            f = len(self.fhir.get(layer_value, []))
            lines.append(f"  {layer_value:<26} {h:>5} HL7   {f:>5} FHIR")
        if self.skipped_standards:
            lines.append("  skipped (stubs this phase): " + ", ".join(sorted(set(self.skipped_standards))))
        return "\n".join(lines)


def normalise(output: TechniqueOutput, *, key: str | None = None) -> NormalisedOutput:
    """Shape a technique's rows into HL7 v2 and FHIR, per the layer's standards.

    Pseudonymisation is applied exactly when the run's manifest declares it; the
    ``key`` is the export's secret and defaults to a fresh random one.
    """

    pseudonymise = output.run.security.identifiers_pseudonymised
    key = key or secrets.token_hex(16)
    result = NormalisedOutput(key=key if pseudonymise else "",
        run_id=output.run.run_id, pseudonymised=pseudonymise,
        purpose=output.run.purpose.value, retention_days=output.run.retention_days,
        deletion_mechanism=output.run.deletion_mechanism or "",
    )
    from compliance.audit import subjects_in           # lazy: compliance.audit imports interop
    result.subjects, result.unattributed = subjects_in(output.rows)

    for layer_value, rows in output.rows.items():
        layer = HISLayer(layer_value)
        standards = standards_for(layer)
        for n, raw in enumerate(rows, start=1):
            row = generalise_row(pseudonymise_row(layer, raw, key=key)) if pseudonymise else raw
            if layer is HISLayer.PATIENT_ADMINISTRATION:
                result.quasi_rows.append({q: row.get(q) for q in QUASI_IDENTIFIERS if q in row})
            if InteropStandard.HL7_V2 in standards:
                msg = shape_hl7(layer, row, control_id=f"{output.run.run_id}-{layer_value}-{n}")
                if msg is not None:
                    result.hl7.setdefault(layer_value, []).append(msg.encode())
            if InteropStandard.FHIR in standards:
                shaped = shape_fhir(layer, row)
                if shaped:
                    result.fhir.setdefault(layer_value, []).extend(shaped)
        for std in standards:
            if std not in (InteropStandard.HL7_V2, InteropStandard.FHIR):
                result.skipped_standards.append(std.value)

    return result


def audit(output: TechniqueOutput, normalised: NormalisedOutput) -> ExportAudit:
    """Search the export for the raw direct-identifier values that were extracted.

    Normalised before matching: case and punctuation are ignored, a name is
    found when all its words appear in one artefact in any order (HL7 writes
    ``Family^Given``), and a phone number by its digits within one field, however
    that field formats them. Digits are never joined across fields: a message's
    timestamp, control id and tokens together can spell any short number by chance.
    """

    corpus: list[str] = []
    for msgs in normalised.hl7.values():
        corpus.extend(msgs)
    for resources in normalised.fhir.values():
        corpus.extend(json.dumps(r) for r in resources)
    texts = [_norm(c) for c in corpus]
    digits = [_digit_fields(c) for c in corpus]

    values: set[str] = set()
    for layer_value, rows in output.rows.items():
        fields = direct_identifier_fields(HISLayer(layer_value))
        for row in rows:
            for name in fields:
                v = row.get(name)
                if v not in (None, ""):
                    values.add(str(v))

    leaked = sum(1 for v in values if _appears(v, texts, digits))
    return ExportAudit(
        pseudonymisation_declared=output.run.security.identifiers_pseudonymised,
        identifier_values=len(values),
        leaked=leaked,
        artefacts_checked=len(corpus),
        k=k_anonymity(normalised.quasi_rows),
        k_rows=len(normalised.quasi_rows),
        generalised=normalised.pseudonymised,
    )


def _norm(text: str) -> str:
    return " " + re.sub(r"[^a-z0-9]+", " ", text.casefold()) + " "


# What separates one field from the next: HL7's delimiters (| ^ ~ & \ and the segment break)
# and JSON's structure. A phone written "+91 98765-43210" stays one field.
_FIELD_BREAK = re.compile(r'[|^~&\\\r\n"{}\[\],:]')


def _digit_fields(text: str) -> list[str]:
    """The digits of each field of one artefact, field by field."""

    return [d for d in (re.sub(r"\D", "", f) for f in _FIELD_BREAK.split(text)) if d]


def _appears(value: str, texts: list[str], digits: list[list[str]]) -> bool:
    """A raw value is in the export if it, its words, or its digits (within one field) are."""

    words = _norm(value).split()
    only_digits = re.sub(r"\D", "", value)
    if len(only_digits) >= 7 and len(only_digits) >= len(value.replace(" ", "")) - 4:
        # a phone-like value: match by digits, however it is formatted
        if any(only_digits in d for fields in digits for d in fields):
            return True
    if not words:
        return False
    return any(all(f" {w} " in t for w in words) for t in texts)


__all__ = ["normalise", "audit", "NormalisedOutput", "ExportAudit"]
