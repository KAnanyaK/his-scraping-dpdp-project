"""What leaves in an export: quasi-identifiers generalised, k measured, leaks found however written."""

from __future__ import annotations

from compliance.models import Purpose
from compliance.pseudonymise import generalise_row, k_anonymity
from extraction.adapters.mock_his import MockHISDataSource
from extraction.technique import ExtractionTask, LayerFields
from extraction.techniques.compliant import CompliantExtractionTechnique
from extraction.techniques.unconstrained import UnconstrainedExtractionTechnique
from interop.layers import HISLayer
from interop.normalise import _appears, _norm, audit, normalise

COHORT = ExtractionTask(task_id="cohort", purpose=Purpose.CARE_COORDINATION, needed=[
    LayerFields(layer=HISLayer.PATIENT_ADMINISTRATION, fields=["mrn", "date_of_birth", "sex", "pincode"])])


def test_quasi_identifiers_are_generalised_not_dropped():
    row = generalise_row({"date_of_birth": "1988-03-14", "sex": "F", "pincode": "560034", "mrn": "X"})
    assert row == {"date_of_birth": "1988", "sex": "F", "pincode": "560XXX", "mrn": "X"}


def test_k_is_the_smallest_group_sharing_the_quasi_identifiers():
    rows = [{"date_of_birth": "1988", "sex": "F"}, {"date_of_birth": "1988", "sex": "F"},
            {"date_of_birth": "1990", "sex": "M"}]
    assert k_anonymity(rows) == 1
    assert k_anonymity(rows[:2]) == 2
    assert k_anonymity([{"mrn": "X"}]) is None


def test_a_pseudonymised_cohort_export_is_less_identifiable_than_a_raw_one():
    source = MockHISDataSource(records_per_layer=60, seed=3)
    ours = CompliantExtractionTechnique().extract(source, COHORT)
    raw = UnconstrainedExtractionTechnique().extract(source, COHORT)
    a_ours, a_raw = audit(ours, normalise(ours, key="k")), audit(raw, normalise(raw, key="k"))
    assert a_ours.generalised and not a_raw.generalised
    assert a_ours.k_rows == a_raw.k_rows == 60
    assert a_ours.k >= a_raw.k and a_raw.k == 1
    assert "k = " in a_ours.one_line() and "generalised" in a_ours.one_line()


def test_the_leak_search_sees_through_reordering_and_formatting():
    texts = [_norm("PID|1||X|Kapoor^Krisha||1988|F|||||91 98765 43210")]
    digits = ["".join(ch for ch in "PID|1||X|Kapoor^Krisha||1988|F|||||91 98765 43210" if ch.isdigit())]
    assert _appears("Krisha Kapoor", texts, digits)               # Family^Given in HL7
    assert _appears("+91-9876543210", texts, digits)               # spaces instead of a dash
    assert not _appears("Meera Goda", texts, digits)
