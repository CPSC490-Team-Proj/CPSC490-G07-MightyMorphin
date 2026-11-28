"""Automatic checks run on every draft save (sequence diagram #87, step "Check
required fields, types, units, plausible ranges").

These checks only accept or reject submitted values and report which fields
are wrong. They never approve a record. The plausible ranges below are broad,
illustrative sanity limits for catching extraction mistakes; they are not
material specification limits (the sponsor has not supplied any).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

# Plausible range per property type, in the property's standard unit.
PLAUSIBLE_RANGES: dict[str, tuple[Decimal, Decimal]] = {
    "Tensile strength": (Decimal("50"), Decimal("3000")),
    "Yield strength": (Decimal("20"), Decimal("3000")),
    "Elongation": (Decimal("0"), Decimal("100")),
}

MAX_TEXT_LENGTH = 40

# A plain decimal number in ASCII digits: "850", "18.5". No sign, exponent,
# digit separators or non-ASCII digits; none of the properties can be negative.
PLAIN_NUMBER = re.compile(r"\d{1,10}(\.\d{1,6})?", re.ASCII)


@dataclass(frozen=True)
class PropertyField:
    """One editable property value as the checks see it."""

    key: str            # e.g. "value:3", the PROPERTY_VALUE row it belongs to
    property_name: str  # PROPERTY_TYPE.name
    standard_unit: str  # PROPERTY_TYPE.standard_unit


def check_material_code(value: str | None) -> str | None:
    text = (value or "").strip()
    if not text:
        return "Material ID is required"
    if len(text) > MAX_TEXT_LENGTH:
        return f"Material ID is longer than {MAX_TEXT_LENGTH} characters"
    return None


def check_lot_number(value: str | None) -> str | None:
    # Lot is optional in the data model (not always printed on the document).
    if value is not None and len(value.strip()) > MAX_TEXT_LENGTH:
        return f"Lot number is longer than {MAX_TEXT_LENGTH} characters"
    return None


def parse_property_value(raw: str | None) -> Decimal | None:
    """Return the value as a Decimal, or None when the field is blank.

    Raises ValueError for text that is not a plain decimal number.
    """
    text = (raw or "").strip()
    if not text:
        return None
    if not PLAIN_NUMBER.fullmatch(text):
        raise ValueError("Enter a plain number, such as 850 or 18.5")
    return Decimal(text)


def check_property(field: PropertyField, raw: str | None, unit: str | None) -> str | None:
    """Return an error message for one property value, or None if it passes.

    A blank value passes the checks (it is saved as a "Missing value" flag
    that blocks approval) so a reviewer can save a partial draft.
    """
    if raw is not None and len(raw) > MAX_TEXT_LENGTH:
        return f"Value is longer than {MAX_TEXT_LENGTH} characters"
    if unit is not None and unit.strip() != field.standard_unit:
        return (
            f"Unit must be {field.standard_unit}; unit conversion is not designed yet"
        )
    try:
        number = parse_property_value(raw)
    except ValueError as exc:
        return str(exc)
    if number is None:
        return None
    low, high = PLAUSIBLE_RANGES.get(field.property_name, (None, None))
    if low is not None and not (low <= number <= high):
        return (
            f"{field.property_name} must be between {low} and {high} "
            f"{field.standard_unit} to be plausible"
        )
    return None
