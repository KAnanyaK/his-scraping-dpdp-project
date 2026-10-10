"""The export's FHIR and HL7 v2 are structurally sound and attributable.

A light structural check, not a validator: the elements FHIR R4 makes mandatory
(1..1) for the resources we emit are present, every resource about a patient
references the patient, and every HL7 v2 message carries a PID with the record
number (or its token). The HL7 FHIR validator is the stronger check.
"""

from __future__ import annotations

from compliance.pseudonymise import is_token
from extraction.adapters.mock_his import MockHISDataSource
from extraction.technique import ExtractionTask, LayerFields
from extraction.techniques.compliant import CompliantExtractionTechnique
from extraction.techniques.unconstrained import UnconstrainedExtractionTechnique
from compliance.models import Purpose
from interop.fhir.resources import bundle
from interop.layers import HISLayer
from interop.normalise import normalise

# resourceType -> elements R4 requires (1..1 or 1..*) for what we emit
REQUIRED = {
    "Patient": [],
    "Encounter": ["status", "class"],
    "Condition": ["subject"],
    "MedicationRequest": ["status", "intent", "subject", "medicationCodeableConcept"],
    "AllergyIntolerance": ["patient"],
    "Observation": ["status", "code"],
    "ServiceRequest": ["status", "intent", "subject"],
    "DiagnosticReport": ["status", "code"],
    "Invoice": ["status"],
    "Coverage": ["status", "beneficiary", "payor"],
    "AuditEvent": ["type", "recorded", "agent", "source"],
}
PATIENT_LINK = {"Encounter": "subject", "Condition": "subject", "MedicationRequest": "subject",
                "AllergyIntolerance": "patient", "Observation": "subject", "ServiceRequest": "subject",
                "DiagnosticReport": "subject", "Invoice": "subject", "Coverage": "beneficiary"}

EVERYTHING = ExtractionTask(task_id="all", purpose=Purpose.CARE_COORDINATION, needed=[
    LayerFields(layer=HISLayer.PATIENT_ADMINISTRATION, fields=["mrn"])])


def _export(technique):
    source = MockHISDataSource(records_per_layer=4, seed=11)
    return normalise(technique.extract(source, EVERYTHING), key="k")


def test_every_emitted_resource_has_its_required_elements_and_its_patient():
    shaped = _export(UnconstrainedExtractionTechnique())          # every field of every layer
    seen = set()
    for resources in shaped.fhir.values():
        for r in resources:
            kind = r["resourceType"]
            seen.add(kind)
            missing = [e for e in REQUIRED[kind] if e not in r and not (kind == "AuditEvent" and e == "recorded")]
            assert not missing, (kind, missing)
            if kind in PATIENT_LINK:
                ref = r[PATIENT_LINK[kind]]
                assert ref.get("identifier", {}).get("value"), (kind, ref)
            if kind == "AuditEvent":
                assert r["agent"] and all("requestor" in a for a in r["agent"])
                assert "observer" in r["source"]
    assert {"Patient", "Condition", "MedicationRequest", "AllergyIntolerance", "Coverage"} <= seen


def test_the_bundle_gives_every_entry_a_full_url_and_an_id():
    b = bundle([{"resourceType": "Patient"}, {"resourceType": "Condition", "subject": {"display": "x"}}],
               namespace="run-1")
    assert all(e["fullUrl"].startswith("urn:uuid:") and e["resource"]["id"] == e["fullUrl"][9:] for e in b["entry"])
    assert b == bundle([{"resourceType": "Patient"}, {"resourceType": "Condition", "subject": {"display": "x"}}],
                       namespace="run-1")                     # stable: the same export, the same ids


def test_every_hl7_message_carries_a_pid_and_its_structure():
    shaped = _export(UnconstrainedExtractionTechnique())
    for layer, messages in shaped.hl7.items():
        for m in messages:
            segs = m.split("\r")
            msh = segs[0].split("|")
            assert msh[8].count("^") == 2, msh[8]               # code ^ event ^ structure
            pid = [s for s in segs if s.startswith("PID|")]
            assert len(pid) == 1, (layer, segs)
            assert pid[0].split("|")[3], (layer, pid)            # PID-3: the record number


def test_a_pseudonymised_export_links_clinical_resources_by_token():
    from extraction.adapters.mock_his import MockHISDataSource
    from compliance.benchmark import bind_subject
    from scripts.run_benchmark import TASKS
    source = MockHISDataSource(records_per_layer=4, seed=11)
    [task] = bind_subject([next(t for t in TASKS if t.task_id == "patient-summary")], source)
    shaped = normalise(CompliantExtractionTechnique().extract(source, task), key="k")
    assert shaped.pseudonymised
    clinical = shaped.fhir["clinical_ehr"]
    tokens = {r[PATIENT_LINK[r["resourceType"]]]["identifier"]["value"] for r in clinical
              if r["resourceType"] in PATIENT_LINK}
    patient = [r for r in shaped.fhir["patient_administration"] if r["resourceType"] == "Patient"][0]
    assert len(tokens) == 1 and is_token(next(iter(tokens)))
    assert patient["identifier"][0]["value"] in tokens            # the token links them, the MRN is gone
