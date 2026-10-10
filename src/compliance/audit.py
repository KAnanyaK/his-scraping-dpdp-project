"""The audit log: every extraction run, written by the pipeline, not the technique.

The capability register says the deployment has an audit log of extraction runs
(``AUDIT-LOG``). This is it. It is written at the metering boundary by the
benchmark harness and by the export stage -- never by a technique -- so a
technique cannot claim to have been logged; it simply is. Each line is one
event: what run, which technique, for what purpose, which fields from which
layers, how many records, which patients, and a digest of the manifest it
declared. Values are never written: fields are named, records are counted, and
patients appear only as keyed tokens of their record number (``subject_token``)
-- enough to answer a patient who asks what was done with their data, and
nothing a reader of the log could turn back into a record number without the
audit key. Records that carried no patient key are counted as unattributed, so
the log says plainly what it cannot answer for.

# DPDP Act 2023 -- rights of the data principal (access to information about
# processing): the log names, per run, whose data was read, so a request can be
# answered from evidence rather than reconstructed.

Append-only JSON lines, one file, under ``data/`` (git-ignored) by default. A
deployment would keep it somewhere with its own access control; the point here
is that the log exists, is produced by the machinery rather than declared by
the thing being audited, and can be read back to show what ran. It is
tamper-evident: each event carries the SHA-256 of the line before it, so an
edited or deleted line breaks the chain and ``verify`` says where. It is kept
for ``LOG_RETENTION_DAYS`` (a year), apart from the exports it describes.

# DPDP Act 2023 -- accountability principle: the Data Fiduciary demonstrates
# compliance. A run that is logged by the pipeline is demonstrable; a run that
# declares itself logged is not.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from compliance.models import ExtractionRun
from compliance.pseudonymise import token_for
from data_synthetic.catalogue import subject_key
from interop.layers import HISLayer

_REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR_ENV = "DPDP_AUDIT_DIR"
DEFAULT_AUDIT_DIR = _REPO_ROOT / "data" / "audit"
AUDIT_FILE = "extraction-audit.jsonl"
# The audit key turns a record number into the token the log stores. A
# deployment sets its own and keeps it with the data-protection contact; the
# default makes the fixture's log reproducible and protects nothing.
AUDIT_KEY_ENV = "DPDP_AUDIT_KEY"
_DEV_AUDIT_KEY = "fixture-audit-key--not-a-secret"


# DPDP Rules, 2025 -- Rule 6 (reasonable security safeguards; verify against the
# Gazette): logs of processing are retained for at least a year. The audit log
# therefore has its own retention, distinct from an export's (30 days for ours):
# an export is erased when its purpose is served; the record that it existed
# is not.
LOG_RETENTION_DAYS = 365


def audit_key() -> str:
    return os.environ.get(AUDIT_KEY_ENV) or _DEV_AUDIT_KEY


def audit_key_is_set() -> bool:
    """True when the deployment has set its own audit key (not the public dev default)."""

    return bool(os.environ.get(AUDIT_KEY_ENV))


def subject_token(value: Any) -> str:
    """The token the audit log stores for one patient's record number."""

    return token_for(value, key=audit_key())


def subjects_in(rows: dict[str, list[dict[str, Any]]], scoped_to: str | None = None) -> tuple[list[str], int]:
    """Tokens of the patients whose records ``rows`` carry, and how many rows had no key.

    ``scoped_to`` is the patient every fetch of the run was filtered to, as the
    meter observed it: a keyless row of such a run is that patient's.
    """

    tokens: set[str] = {subject_token(scoped_to)} if scoped_to else set()
    unattributed = 0
    for layer_value, layer_rows in rows.items():
        key = subject_key(HISLayer(layer_value))
        for row in layer_rows:
            value = row.get(key) if key else None
            if value in (None, ""):
                unattributed += 0 if scoped_to else 1
            else:
                tokens.add(subject_token(value))
    return sorted(tokens), unattributed


def manifest_digest(run: ExtractionRun) -> str:
    """A stable digest of the manifest as declared (the timestamp excluded)."""

    payload = run.model_dump(mode="json", exclude={"created_at"})
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


class AuditEvent(BaseModel):
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event: str                                   # extraction | export | purge
    run_id: str
    technique: str = ""
    purpose: str = ""
    source: str = ""                             # how the source described itself
    fields: dict[str, list[str]] = Field(default_factory=dict)   # layer -> field names pulled
    records: int = 0
    subjects: list[str] = Field(default_factory=list)            # keyed tokens of the patients read
    unattributed: int = 0                                        # records read with no patient key
    scoped: bool = False                                         # every fetch filtered to one patient (metered)
    manifest_sha256: str = ""
    note: str = ""
    account: str = ""                                            # the portal account the run used, if any
    authorisation: str = ""                                      # the authority automated access rested on
    prev_sha256: str = ""                                        # hash of the previous line: the chain

    def one_line(self) -> str:
        n = sum(len(v) for v in self.fields.values())
        if n > 8:
            pulled = f"{n} fields across {len(self.fields)} layer(s)"
        else:
            pulled = "; ".join(f"{layer}: {', '.join(names)}" for layer, names in sorted(self.fields.items()))
        return (f"{self.at:%Y-%m-%d %H:%M:%S}Z  {self.event:<10} {self.run_id:<44} {self.purpose:<20} "
                f"{self.records:>5} records  {pulled or self.note}")


class AuditLog:
    """Append-only JSON-lines log of extraction events."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or self.default_path()

    @staticmethod
    def default_path() -> Path:
        directory = Path(os.environ.get(AUDIT_DIR_ENV) or DEFAULT_AUDIT_DIR)
        return directory / AUDIT_FILE

    def _last_line(self) -> str:
        """The last non-empty line, read from the end (the log can be long)."""

        if not self.path.exists():
            return ""
        with self.path.open("rb") as fh:
            fh.seek(0, os.SEEK_END)
            end = fh.tell()
            size = min(end, 65536)
            while True:
                fh.seek(end - size)
                lines = [l for l in fh.read(size).splitlines() if l.strip()]
                if not lines:
                    return ""
                if len(lines) > 1 or size == end:
                    return lines[-1].decode("utf-8")
                size = min(end, size * 2)

    def record(self, event: AuditEvent) -> AuditEvent:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        last = self._last_line()
        event.prev_sha256 = hashlib.sha256(last.encode("utf-8")).hexdigest() if last else ""
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(event.model_dump_json() + "\n")
        return event

    def verify(self) -> tuple[bool, int | None]:
        """Walk the chain. Returns (intact, index of the first event whose link is broken)."""

        if not self.path.exists():
            return True, None
        prev = ""
        lines = [l for l in self.path.read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, line in enumerate(lines):
            want = hashlib.sha256(prev.encode("utf-8")).hexdigest() if prev else ""
            if json.loads(line).get("prev_sha256", "") != want:
                return False, i
            prev = line
        return True, None

    @staticmethod
    def retention_note() -> str:
        return (f"audit log kept {LOG_RETENTION_DAYS} days (DPDP Rules, 2025, Rule 6), "
                f"apart from the exports it records")

    def extraction(
        self,
        run: ExtractionRun,
        *,
        technique: str,
        fields: dict[str, list[str]],
        records: int,
        source: str = "",
        rows: dict[str, list[dict[str, Any]]] | None = None,
        scoped_to: str | None = None,
        account: str = "",
        authorisation: str = "",
    ) -> AuditEvent:
        subjects, unattributed = subjects_in(rows, scoped_to) if rows is not None else ([], 0)
        return self.record(AuditEvent(
            event="extraction", run_id=run.run_id, technique=technique,
            purpose=run.purpose.value, source=source, fields=fields, records=records,
            subjects=subjects, unattributed=unattributed, scoped=bool(scoped_to),
            manifest_sha256=manifest_digest(run), account=account, authorisation=authorisation,
        ))

    def touching(self, token: str) -> list[AuditEvent]:
        """Every event whose run read the patient behind ``token``, and the events
        that followed from those runs (their exports and purges)."""

        entries = self.entries()
        runs = {e.run_id for e in entries if token in e.subjects}
        return [e for e in entries if e.run_id in runs]

    def entries(self) -> list[AuditEvent]:
        if not self.path.exists():
            return []
        out: list[AuditEvent] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(AuditEvent.model_validate_json(line))
        return out

    def for_run(self, run_id: str) -> list[AuditEvent]:
        return [e for e in self.entries() if e.run_id == run_id]

    def logged(self, run_id: str) -> bool:
        """Was an extraction event written for this run? The evidence AUDIT-LOG rests on."""

        return any(e.event == "extraction" for e in self.for_run(run_id))

    def render_tail(self, n: int = 5) -> str:
        entries = self.entries()
        lines = [f"  {self.path}  ({len(entries)} events)"]
        lines += ["  " + e.one_line() for e in entries[-n:]]
        return "\n".join(lines)


def fields_by_layer(pulled: set[tuple[str, str]]) -> dict[str, list[str]]:
    """Group the meter's (layer, field) pairs for the log."""

    out: dict[str, list[str]] = {}
    for layer, name in sorted(pulled):
        out.setdefault(layer, []).append(name)
    return out


__all__ = ["AuditEvent", "AuditLog", "manifest_digest", "fields_by_layer", "AUDIT_DIR_ENV", "DEFAULT_AUDIT_DIR",
           "AUDIT_KEY_ENV", "audit_key", "audit_key_is_set", "subject_token", "subjects_in", "LOG_RETENTION_DAYS"]
