"""Extraction technique abstraction.

A *technique* is a strategy for fulfilling an extraction task against a data
source. Crucially, the technique also produces the compliance manifest for its
own run -- so "compliance-aware" is a property of the technique's design, not a
label applied afterwards. The benchmark (``compliance.benchmark``) scores every
technique's output with the same DPDP rule set.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from compliance.models import ExtractedRecord, ExtractionRun, Purpose
from data_synthetic.catalogue import subject_key
from extraction.base import HISDataSource
from interop.layers import HISLayer


class LayerFields(BaseModel):
    """A HIS layer paired with the field names required from it."""

    layer: HISLayer
    fields: list[str]


class ExtractionTask(BaseModel):
    """What a caller wants extracted, and the lawful purpose for it.

    ``needed`` is the *minimum necessary* field set for the job: an
    expert-authored data map (one entry per field, its reason in
    ``rationale``). The rule-driven technique executes it -- it is the
    reference implementation, an upper bound by construction -- and coverage
    and excess measure every other technique's *agreement* with it. A
    coverage-optimised baseline ignores it; an AI model is not shown it.
    """

    task_id: str
    purpose: Purpose
    needed: list[LayerFields] = Field(default_factory=list)
    # The job in words, as a person would brief an agent. Only the AI-agent
    # technique reads it: every other technique works from ``needed`` or from
    # the whole source, and the agent is deliberately not shown ``needed``.
    description: str = ""
    # Set when the description deliberately tempts a technique past the purpose
    # -- an out-of-scope field, an onward use, a retention beyond the ceiling.
    # Names the temptation, for the report; the purpose and ``needed`` stay lawful.
    trap: str = ""
    # Why the trap encodes a defensible hospital policy choice -- for the
    # reader, never for the model. The Act itself has no data categories;
    # a trap is broken against *the hospital's* purpose policy (policy.py).
    trap_rationale: str = ""
    # Set when the temptation is about the record scope (read everyone to
    # answer for one). Only then does reading other patients' records count
    # against "trap held"; otherwise the record axis is reported on its own
    # (record excess, DM-01) and the trap stays about what the wording planted.
    trap_on_scope: bool = False
    # Minimisation has a record axis as well as a field axis. A task about *one*
    # patient needs that patient's records and no one else's; ``single_subject``
    # says so, and ``subject`` is the patient's record number, bound at run time
    # by the harness from the source (``compliance.benchmark.bind_subject``) --
    # never written into a task definition, never shown to an AI agent.
    single_subject: bool = False
    subject: str | None = None
    # Why each needed field is necessary for this job -- the expert data map
    # behind ``needed``, kept beside it so the specification can be inspected
    # and contested. Keyed "layer/field". Never shown to an AI model (the
    # prompt carries only the description), so it does not stale a recording.
    rationale: dict[str, str] = Field(default_factory=dict)

    def subject_filter(self, layer: HISLayer) -> dict[str, str]:
        """The ``where`` a subject-scoped fetch of ``layer`` uses, or {} when unscoped."""

        key = subject_key(layer)
        if self.subject is None or key is None:
            return {}
        return {key: self.subject}

    def field_refs(self) -> set[tuple[str, str]]:
        """The (layer, field) pairs this task declares as minimum necessary.

        The denominator for the benchmark's ``excess_ratio`` and ``coverage``
        (see ``extraction.metering``): what the purpose actually requires, which
        is what a technique's pull is measured against.
        """

        return {
            (item.layer.value, field)
            for item in self.needed
            for field in item.fields
        }


class TechniqueOutput(BaseModel):
    """A technique's run manifest plus the records it produced.

    ``records`` carry categories only and are what the compliance rules score;
    they are safe to write into benchmark artifacts. ``rows`` are the raw values,
    keyed by layer, kept so the interop stage can shape them into HL7 / FHIR --
    they are never serialised into a compliance artifact.
    """

    run: ExtractionRun
    records: list[ExtractedRecord]
    rows: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)


class ExtractionTechnique(ABC):
    """A named strategy that turns an ``ExtractionTask`` into a ``TechniqueOutput``."""

    name: str = ""

    @abstractmethod
    def extract(self, source: HISDataSource, task: ExtractionTask) -> TechniqueOutput:
        raise NotImplementedError
