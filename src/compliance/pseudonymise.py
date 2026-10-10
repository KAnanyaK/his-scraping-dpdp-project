"""Pseudonymisation of direct identifiers on export.

The compliance-aware technique *declares* ``identifiers_pseudonymised=True`` in
its manifest, and rule SS-01 gives it credit for that. This module is where the
declaration becomes behaviour: before an extracted row is shaped into an HL7
message or a FHIR resource, every field the catalogue classes as a direct
identifier is replaced by a keyed token.

Pseudonymisation, not anonymisation: the same value yields the same token within
one export (a keyed hash), so records about one patient stay linkable to each
other, while the identifier itself does not leave the system. The key is the
export's secret; without it the token cannot be reversed or matched to a fresh
hash of the real value.

# DPDP Act 2023 -- security safeguards principle: reasonable technical measures to
# protect personal data. Pseudonymising direct identifiers on export is one, and
# ``interop.normalise.audit`` checks that it actually happened rather than trusting
# the manifest.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from compliance.models import FieldCategory
from data_synthetic.catalogue import FIELD_CATALOGUE
from interop.layers import HISLayer

TOKEN_PREFIX = "PSN-"


def direct_identifier_fields(layer: HISLayer) -> list[str]:
    """Catalogue fields on ``layer`` that are direct identifiers."""

    return [
        name for name, category in FIELD_CATALOGUE.get(layer, {}).items()
        if category == FieldCategory.DIRECT_IDENTIFIER
    ]


def token_for(value: Any, *, key: str) -> str:
    """A stable, keyed, non-reversible stand-in for one identifier value."""

    digest = hmac.new(key.encode("utf-8"), str(value).encode("utf-8"), hashlib.sha256)
    return TOKEN_PREFIX + digest.hexdigest()[:12]


def pseudonymise_row(layer: HISLayer, row: dict[str, Any], *, key: str) -> dict[str, Any]:
    """Return a copy of ``row`` with its direct identifiers replaced by tokens."""

    out = dict(row)
    for name in direct_identifier_fields(layer):
        if name in out and out[name] not in (None, ""):
            out[name] = token_for(out[name], key=key)
    return out


def is_token(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(TOKEN_PREFIX)


# Quasi-identifiers generalised on a pseudonymised export (review F3): date of
# birth, sex and PIN code together re-identify most people. The date keeps its
# year (age stays usable clinically), the PIN its first three digits (the
# sorting district). Sex is kept: it is clinically needed and, without the
# other two at full precision, far less identifying.
QUASI_IDENTIFIERS = ("date_of_birth", "sex", "pincode")


def generalise_row(row: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``row`` with its quasi-identifiers generalised."""

    out = dict(row)
    if out.get("date_of_birth"):
        out["date_of_birth"] = str(out["date_of_birth"])[:4]
    if out.get("pincode"):
        digits = "".join(ch for ch in str(out["pincode"]) if ch.isdigit())
        out["pincode"] = digits[:3] + "XXX" if len(digits) >= 3 else digits
    return out


def k_anonymity(rows: list[dict[str, Any]]) -> int | None:
    """The smallest group of exported rows sharing one combination of the
    quasi-identifiers present -- the k in k-anonymity. None when no row carries any."""

    groups: dict[tuple, int] = {}
    for row in rows:
        key = tuple(row.get(q) for q in QUASI_IDENTIFIERS)
        if any(v not in (None, "") for v in key):
            groups[key] = groups.get(key, 0) + 1
    return min(groups.values()) if groups else None
