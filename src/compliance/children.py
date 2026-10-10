"""Children's data: a finding, not a score.

The DPDP Act 2023 treats a child's personal data differently (s.9: verifiable
consent of a parent or lawful guardian before processing on consent, and no
tracking, behavioural monitoring or targeted advertising directed at children).
The DPDP Rules, 2025 exempt a clinical establishment from the parental-consent
requirement to the extent the processing is necessary for health services
(verify against the Gazette). Routine care of a minor therefore rests on that
exemption, not on a child's own consent.

The synthetic population spans ages 0 to 95, so minors are in every dataset.
Nothing in the seven rules depends on age, and nothing should: the purposes we
model are the hospital's own health services. But a reader should be told when
a pull includes children's records, so this module counts them and the
benchmark reports the count beside the scores -- a finding, never a deduction.

# DPDP Act 2023 -- processing of personal data of children (s.9).
"""

from __future__ import annotations

from datetime import date
from typing import Any

ADULT_AGE = 18


def age_on(dob: Any, today: date) -> int | None:
    """Whole years from an ISO date of birth (or a bare year) to ``today``; None if unreadable."""

    text = str(dob or "").strip()
    try:
        if len(text) == 4 and text.isdigit():
            return today.year - int(text)           # a generalised birth year: the age this year
        born = date.fromisoformat(text[:10])
    except ValueError:
        return None
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def minors_in(rows: dict[str, list[dict[str, Any]]], today: date | None = None) -> int:
    """How many records read carry a date of birth under 18 (0 when no date of birth was pulled)."""

    today = today or date.today()
    count = 0
    for layer_rows in rows.values():
        for row in layer_rows:
            age = age_on(row.get("date_of_birth"), today)
            if age is not None and age < ADULT_AGE:
                count += 1
    return count


NOTE = ("records of patients under 18 were read. Processing a child's data on consent needs "
        "verifiable parental consent (DPDP Act 2023, s.9); care itself rests on the "
        "clinical-establishment exemption for health services. A finding, not a deduction.")

__all__ = ["ADULT_AGE", "age_on", "minors_in", "NOTE"]
