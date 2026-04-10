"""Value transformers for feed data normalisation."""

import re


def strip_currency(value: str | None) -> str | None:
    """Strip currency code (3 uppercase letters) from the end of a string."""
    if value is None:
        return None
    if value == "":
        return ""
    return re.sub(r"\s*[A-Z]{3}$", "", value)


def format_price(value: str | None) -> str | None:
    """Strip currency, then format the numeric value to 2 decimal places."""
    if value is None:
        return None
    if value == "":
        return ""
    stripped = strip_currency(value)
    return f"{float(stripped):.2f}"


def map_availability(value: str | None) -> str:
    """Map availability strings to codes (case-insensitive)."""
    if value is None:
        return "0"
    normalised = value.strip().lower().replace(" ", "_").replace("-", "_")

    # Already a numeric code (from Ceneo source)
    if normalised in ("1", "0", "99"):
        return normalised

    mapping = {
        "in_stock": "1",
        "available": "1",
        "out_of_stock": "0",
        "preorder": "99",
        "pre_order": "99",
    }
    return mapping.get(normalised, "0")


def strip_html(value: str | None) -> str | None:
    """Remove HTML tags from a string."""
    if value is None:
        return None
    if value == "":
        return ""
    return re.sub(r"<[^>]+>", "", value)
