"""Synthetic HIS record generator (build step 3).

Produces plain-dict records for every field in
``data_synthetic.catalogue.FIELD_CATALOGUE``. No real patients and no real
hospital distributions -- but values a clinician or an Indian reviewer would
not laugh at (review D1):

- Indian names, addresses and companies (Faker ``en_IN``); a patient's name
  agrees with the recorded sex;
- mobile numbers that are valid Indian mobiles (+91, first digit 6-9) and PIN
  codes that are valid in form (first digit 1-8, never 0);
- diagnosis, medication and allergy drawn together from a small coherent table
  (ICD-10 code, diagnosis, a usual first-line drug, and the allergy that would
  contraindicate it -- which a patient on that drug never has);
- a lab result whose value sits in the range of the diagnosis's monitoring test
  (the catalogue has no test-name or unit field; adding one would change every
  AI model's brief and force re-recording, so the value stands alone);
- patients with several encounters: record i of a layer belongs to patient
  ``i mod k``, so the first patients have two records per layer and the last
  have none (registered, not seen) -- see ``build_dataset``.

Seeded for reproducible demos and tests.
"""

from __future__ import annotations

from typing import Any

from faker import Faker

from data_synthetic.catalogue import FIELD_CATALOGUE
from interop.layers import HISLayer

LOCALE = "en_IN"

# (ICD-10, diagnosis, usual first-line drug, contraindicating allergy, monitoring-test range)
CLINICAL_TABLE: tuple[tuple[str, str, str, str | None, tuple[float, float]], ...] = (
    ("E11.9", "Type 2 diabetes mellitus", "Metformin 500mg", None, (6.5, 10.5)),          # HbA1c, %
    ("I10", "Essential hypertension", "Amlodipine 5mg", None, (130.0, 170.0)),             # systolic BP, mmHg
    ("J20.9", "Acute bronchitis", "Amoxicillin 500mg", "Penicillin", (4.0, 14.0)),         # WBC, x10^9/L
    ("D50.9", "Iron deficiency anaemia", "Ferrous sulfate 200mg", None, (7.0, 11.5)),      # haemoglobin, g/dL
    ("J45.9", "Asthma", "Salbutamol inhaler 100mcg", None, (55.0, 90.0)),                  # peak flow, % predicted
    ("K21.9", "Gastro-oesophageal reflux disease", "Pantoprazole 40mg", None, (0.5, 1.2)), # creatinine, mg/dL
    ("N39.0", "Urinary tract infection", "Nitrofurantoin 100mg", None, (10.0, 100.0)),     # urine WBC, /hpf
    ("E03.9", "Hypothyroidism", "Levothyroxine 50mcg", None, (4.5, 12.0)),                 # TSH, mIU/L
)
_ALLERGIES = ("None known", "Penicillin", "Sulfa drugs", "Latex")
# Payers as an Indian hospital's billing desk sees them: self-pay, government
# schemes and private insurance through a TPA -- generic, no insurer named.
_PAYERS = ("Self-pay", "CGHS", "PM-JAY", "ECHS", "State health scheme", "Private insurer (via TPA)",
           "Corporate tie-up")


def _mobile(fake: Faker) -> str:
    return f"+91-{fake.random_element('6789')}{fake.numerify('#########')}"


def _pincode(fake: Faker) -> str:
    return f"{fake.random_int(1, 8)}{fake.numerify('#####')}"


def _clinical(fake: Faker) -> dict[str, Any]:
    """One coherent (diagnosis, medication, allergy, lab value) draw."""

    code, diagnosis, drug, contra, (lo, hi) = fake.random_element(CLINICAL_TABLE)
    allergies = [a for a in _ALLERGIES if a != contra]
    return {
        "primary_diagnosis": f"{diagnosis} ({code})",
        "medication": drug,
        "allergy": fake.random_element(allergies),
        "lab_result": round(fake.random.uniform(lo, hi), 1),
    }


def _value_for(field: str, fake: Faker, row: dict[str, Any]) -> Any:
    match field:
        case "mrn":
            return f"MRN{fake.random_number(digits=7, fix_len=True)}"
        case "full_name":
            sex = row.get("sex")
            return fake.name_female() if sex == "F" else fake.name_male() if sex == "M" else fake.name()
        case "attending_clinician":
            return f"Dr. {fake.name()}"
        case "phone":
            return _mobile(fake)
        case "email":
            # Agrees with the name when there is one: priya.raman42@example.in, not a stranger's address.
            parts = [w for w in str(row.get("full_name", "")).lower().split() if w.isalpha()]
            local = ".".join(parts[:1] + parts[-1:]) if parts else fake.user_name()
            return f"{local}{fake.random_int(1, 99)}@{fake.free_email_domain()}"
        case "street_address":
            return f"{fake.street_address()}, {fake.city()}".replace("\n", ", ")
        case "date_of_birth":
            return fake.date_of_birth(minimum_age=0, maximum_age=95).isoformat()
        case "sex":
            return fake.random_element(("F", "M", "O")) if fake.random_int(1, 100) == 1 \
                else fake.random_element(("F", "M"))
        case "pincode":
            return _pincode(fake)
        case "admission_ward":
            return fake.random_element(("General Ward A", "General Ward B", "ICU", "Day Care"))
        case "admission_datetime" | "encounter_datetime":
            return fake.date_time_this_year().isoformat(timespec="seconds")
        case "primary_diagnosis" | "medication" | "allergy" | "lab_result":
            if "_clinical" not in row:
                row["_clinical"] = _clinical(fake)
            return row["_clinical"][field]
        case "result_value":
            return round(fake.random.uniform(0.1, 15.0), 1)
        case "specimen_type":
            return fake.random_element(("Blood", "Urine", "Swab", "Tissue"))
        case "imaging_modality":
            return fake.random_element(("XR", "CT", "MRI", "US"))
        case "report_text":
            return fake.random_element((
                "No acute abnormality detected.", "Findings consistent with the clinical history.",
                "Mild changes; clinical correlation advised.", "Normal study.",
            ))
        case "order_id":
            return f"ORD{fake.random_number(digits=8, fix_len=True)}"
        case "invoice_id":
            return f"INV{fake.random_number(digits=8, fix_len=True)}"
        case "billed_amount":
            return round(fake.random.uniform(100.0, 90000.0), 2)
        case "insurance_policy_no":
            return fake.bothify("??########").upper()
        case "payer_name":
            return fake.random_element(_PAYERS)
        case "audit_event_id":
            return f"EVT{fake.random_number(digits=9, fix_len=True)}"
        case "event_timestamp":
            return fake.date_time_this_year().isoformat(timespec="seconds")
        case "actor_role":
            return fake.random_element(("reception", "nurse", "administrator", "clinician"))
        case "action":
            return fake.random_element(("read", "create", "update", "export"))
        case "source_system":
            return fake.random_element(("registration", "ehr", "lab", "billing", "portal"))
        case "subject_mrn":
            return f"MRN{fake.random_number(digits=7, fix_len=True)}"
        case _:  # pragma: no cover - guards against a catalogue field with no recipe
            return fake.word()


def _record(fields, fake: Faker) -> dict[str, Any]:
    row: dict[str, Any] = {}
    # sex before the name, so the name can agree with it
    order = sorted(fields, key=lambda f: 0 if f == "sex" else 1)
    for name in order:
        row[name] = _value_for(name, fake, row)
    row.pop("_clinical", None)
    return {name: row[name] for name in fields}


def generate_layer_records(
    layer: HISLayer, n: int, *, seed: int | None = None
) -> list[dict[str, Any]]:
    """Generate ``n`` records for one HIS layer, one value per catalogue field."""

    fake = Faker(LOCALE)
    if seed is not None:
        fake.seed_instance(seed)
    fields = FIELD_CATALOGUE[layer]
    return [_record(fields, fake) for _ in range(n)]


def build_dataset(
    records_per_layer: int, *, seed: int | None = None
) -> dict[HISLayer, list[dict[str, Any]]]:
    """Generate a full synthetic dataset: records for every catalogue layer.

    Each layer is seeded with a distinct offset of ``seed`` so layers do not
    share an identical value sequence.
    """

    data = {
        layer: generate_layer_records(
            layer, records_per_layer, seed=None if seed is None else seed + offset
        )
        for offset, layer in enumerate(FIELD_CATALOGUE)
    }
    # One patient population across the layers, keyed by MRN -- the join a real
    # HIS carries, and what a single-patient task scopes by. Record i of a layer
    # belongs to patient i mod k, k about 70% of the patients: the first
    # patients have two encounters, invoices, orders; the last have none yet.
    from data_synthetic.catalogue import SUBJECT_KEY
    from interop.layers import HISLayer as _L
    mrns = [row["mrn"] for row in data[_L.PATIENT_ADMINISTRATION]]
    for layer, rows in data.items():
        key = SUBJECT_KEY.get(layer)
        if layer is _L.PATIENT_ADMINISTRATION or key is None:
            continue
        k = max(1, round(len(mrns) * 0.7))
        for i, row in enumerate(rows):
            row[key] = mrns[(i % k) % len(mrns)]
    return data
