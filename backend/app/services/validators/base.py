"""Shared validation base class and data types."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    level: str  # "error" | "warning" | "info"
    field: str
    message: str
    product_id: str
    product_name: str
    rule: str


@dataclass
class FieldCoverage:
    field: str
    required: bool
    filled: int
    total: int
    percent: float


@dataclass
class ValidationResult:
    platform: str
    total_products: int
    issues: list[ValidationIssue]
    field_coverage: list[FieldCoverage]
    quality_score: int
    quality_label: str
    quality_breakdown: dict


_URL_RE = re.compile(r"^https?://\S+$")
_ISO_CURRENCY_RE = re.compile(r"^\d+(\.\d{1,2})?\s+[A-Z]{3}$")
_NUMERIC_PRICE_RE = re.compile(r"^\d+(\.\d{1,2})?$")


def validate_ean(value: str | None) -> dict:
    """Validate an EAN/GTIN code. Returns dict with status and details.

    Accepts EAN-8, EAN-12 (UPC-A), EAN-13, EAN-14 (GTIN-14).
    Returns:
      {"valid": bool, "format": "ean8"|"ean12"|"ean13"|"ean14"|None,
       "reason": str, "fixed": str|None}

    The "fixed" key, if present, contains an auto-corrected version
    (e.g. trimmed whitespace, leading-zero padding to 13 digits).
    """
    if value is None or value == "":
        return {"valid": False, "format": None, "reason": "Pusty kod EAN", "fixed": None}

    raw = str(value)
    stripped = raw.strip().replace(" ", "").replace("-", "")
    if not stripped:
        return {"valid": False, "format": None, "reason": "Pusty kod EAN", "fixed": None}

    if not stripped.isdigit():
        return {"valid": False, "format": None, "reason": "EAN zawiera znaki inne niż cyfry", "fixed": None}

    fixed: str | None = None
    if stripped != raw:
        fixed = stripped

    length = len(stripped)
    if length not in (8, 12, 13, 14):
        # Try padding with leading zeros (common for short codes)
        if length < 13:
            padded = stripped.zfill(13)
            if _checksum_valid(padded):
                return {"valid": True, "format": "ean13", "reason": "OK (auto-padded)", "fixed": padded}
        return {"valid": False, "format": None, "reason": f"Nieprawidłowa długość: {length} (oczekiwane 8/12/13/14)", "fixed": fixed}

    if not _checksum_valid(stripped):
        return {"valid": False, "format": f"ean{length}", "reason": "Nieprawidłowa suma kontrolna", "fixed": fixed}

    return {"valid": True, "format": f"ean{length}", "reason": "OK", "fixed": fixed}


def _checksum_valid(digits: str) -> bool:
    """Verify GTIN checksum (works for EAN-8, UPC-A, EAN-13, GTIN-14)."""
    if not digits.isdigit() or len(digits) < 8:
        return False
    body = digits[:-1]
    expected = int(digits[-1])
    total = 0
    # Multiply each digit by 3 or 1 alternately, starting from the right of body
    for i, d in enumerate(reversed(body)):
        weight = 3 if (i % 2 == 0) else 1
        total += int(d) * weight
    check = (10 - (total % 10)) % 10
    return check == expected


class BaseValidator:
    """Base class for platform validators."""

    platform: str = ""

    # Subclasses override these lists of (field_name, required) tuples.
    required_fields: list[str] = []
    recommended_fields: list[str] = []

    def __init__(self, platform: str = ""):
        if platform:
            self.platform = platform

    # ------------------------------------------------------------------
    # Shared check helpers — each returns a list of ValidationIssue
    # ------------------------------------------------------------------

    def check_required(
        self, product: dict, field_name: str, pid: str, pname: str
    ) -> list[ValidationIssue]:
        val = self.get_field(product, field_name)
        if val is None or not val.strip():
            return [
                ValidationIssue(
                    level="error",
                    field=field_name,
                    message=f"Brak wymaganego pola '{field_name}'",
                    product_id=pid,
                    product_name=pname,
                    rule="required_field",
                )
            ]
        return []

    def check_url(
        self, field_name: str, value: str | None, pid: str, pname: str
    ) -> list[ValidationIssue]:
        if not value:
            return []
        issues: list[ValidationIssue] = []
        if not _URL_RE.match(value):
            issues.append(
                ValidationIssue(
                    level="error",
                    field=field_name,
                    message=f"Nieprawidłowy URL: '{value[:80]}'",
                    product_id=pid,
                    product_name=pname,
                    rule="invalid_url",
                )
            )
        elif value.startswith("http://"):
            issues.append(
                ValidationIssue(
                    level="warning",
                    field=field_name,
                    message="URL powinien używać HTTPS",
                    product_id=pid,
                    product_name=pname,
                    rule="prefer_https",
                )
            )
        return issues

    def check_price_with_currency(
        self, field_name: str, value: str | None, pid: str, pname: str
    ) -> list[ValidationIssue]:
        if not value:
            return []
        if not _ISO_CURRENCY_RE.match(value.strip()):
            return [
                ValidationIssue(
                    level="error",
                    field=field_name,
                    message=f"Cena musi mieć format 'XX.XX PLN', jest: '{value}'",
                    product_id=pid,
                    product_name=pname,
                    rule="format_price_currency",
                )
            ]
        return []

    def check_price_no_currency(
        self, field_name: str, value: str | None, pid: str, pname: str
    ) -> list[ValidationIssue]:
        if not value:
            return []
        stripped = value.strip()
        if _NUMERIC_PRICE_RE.match(stripped):
            return []
        # Maybe has currency attached
        if _ISO_CURRENCY_RE.match(stripped):
            return [
                ValidationIssue(
                    level="warning",
                    field=field_name,
                    message=f"Cena nie powinna zawierać waluty, jest: '{value}'",
                    product_id=pid,
                    product_name=pname,
                    rule="price_has_currency",
                )
            ]
        return [
            ValidationIssue(
                level="error",
                field=field_name,
                message=f"Nieprawidłowy format ceny: '{value}'",
                product_id=pid,
                product_name=pname,
                rule="invalid_price",
            )
        ]

    def check_ean13(
        self, field_name: str, value: str | None, pid: str, pname: str
    ) -> list[ValidationIssue]:
        if not value:
            return []
        result = validate_ean(value)
        if result["valid"]:
            return []
        rule = "invalid_ean_length" if "długość" in result["reason"].lower() else "invalid_ean_checksum"
        return [
            ValidationIssue(
                level="warning",
                field=field_name,
                message=f"Nieprawidłowy kod EAN/GTIN: '{value}' — {result['reason']}",
                product_id=pid,
                product_name=pname,
                rule=rule,
            )
        ]

    def check_max_length(
        self,
        field_name: str,
        value: str | None,
        max_len: int,
        pid: str,
        pname: str,
    ) -> list[ValidationIssue]:
        if not value:
            return []
        if len(value) > max_len:
            return [
                ValidationIssue(
                    level="warning",
                    field=field_name,
                    message=f"Pole '{field_name}' ma {len(value)} znaków, max {max_len}",
                    product_id=pid,
                    product_name=pname,
                    rule="max_length",
                )
            ]
        return []

    def check_enum(
        self,
        field_name: str,
        value: str | None,
        allowed: list[str],
        pid: str,
        pname: str,
    ) -> list[ValidationIssue]:
        if not value:
            return []
        # Normalize: "in stock" -> "in_stock", case insensitive
        normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
        allowed_normalized = [a.lower().replace(" ", "_").replace("-", "_") for a in allowed]
        if normalized not in allowed_normalized:
            return [
                ValidationIssue(
                    level="error",
                    field=field_name,
                    message=f"Niedozwolona wartość '{value}' dla '{field_name}'. Dozwolone: {', '.join(allowed)}",
                    product_id=pid,
                    product_name=pname,
                    rule="invalid_enum",
                )
            ]
        return []

    def check_image_present(
        self, field_name: str, value: str | None, pid: str, pname: str
    ) -> list[ValidationIssue]:
        if not value or not value.strip():
            return [
                ValidationIssue(
                    level="warning",
                    field=field_name,
                    message="Brak zdjęcia produktu",
                    product_id=pid,
                    product_name=pname,
                    rule="missing_image",
                )
            ]
        return self.check_url(field_name, value, pid, pname)

    # ------------------------------------------------------------------
    # Field resolution helper
    # ------------------------------------------------------------------

    # Alternative field names across different feed formats (Shoper, GMC, Ceneo, Skapiec)
    _FIELD_ALTERNATIVES: dict[str, list[str]] = {
        "g:id": ["@id", "id", "compid"],
        "title": ["name", "g:title"],
        "description": ["desc", "g:description", "desclong"],
        "link": ["@url", "url"],
        "g:image_link": ["image", "img", "photo"],
        "g:availability": ["@avail", "avail", "availability"],
        "g:price": ["@price", "price"],
        "g:condition": ["condition"],
        "g:brand": ["brand", "vendor", "producent", "producer"],
        "g:gtin": ["ean", "gtin", "code"],
        "g:mpn": ["mpn", "partnr"],
        "g:product_type": ["cat", "category", "catpath", "catname"],
        # Reverse mappings for platform-specific validators
        "@id": ["g:id", "id", "compid"],
        "@url": ["link", "url", "g:link"],
        "@price": ["g:price", "price"],
        "@avail": ["g:availability", "availability", "avail"],
        "name": ["title", "g:title"],
        "cat": ["g:product_type", "category", "catpath", "catname"],
        "desc": ["description", "g:description", "desclong"],
        "id": ["g:id", "@id", "compid"],
        "url": ["link", "@url"],
        "price": ["g:price", "@price"],
        "category": ["g:product_type", "cat", "catpath", "catname"],
        "image": ["g:image_link", "img", "photo"],
        "producer": ["g:brand", "brand", "vendor"],
        "availability": ["g:availability", "@avail", "avail"],
        "ean": ["g:gtin", "gtin", "code"],
    }

    def get_field(self, pv: dict, field_name: str) -> str | None:
        """Get a field value from product_value dict, trying alternatives."""
        # Direct match
        val = pv.get(field_name)
        if val is not None:
            return self._resolve_value(val)

        # Try alternatives
        for alt in self._FIELD_ALTERNATIVES.get(field_name, []):
            val = pv.get(alt)
            if val is not None:
                return self._resolve_value(val)

        return None

    def _resolve_value(self, val) -> str | None:
        """Convert a value to string, handling nested dicts (images)."""
        if isinstance(val, dict):
            for k, v in val.items():
                if isinstance(v, dict) and "@url" in v:
                    return v["@url"]
                if isinstance(v, str):
                    return v
            return None
        return str(val).strip() if val else None

    # ------------------------------------------------------------------
    # Main validate method — subclasses override validate_product
    # ------------------------------------------------------------------

    def validate(self, products: list[dict]) -> ValidationResult:
        all_issues: list[ValidationIssue] = []
        field_counts: dict[str, int] = {}
        all_fields = self.required_fields + self.recommended_fields

        for product in products:
            pv = product.get("product_value", {})
            pid = str(self.get_field(pv, self.id_field) or "?")
            pname = str(self.get_field(pv, self.name_field) or "?")[:80]

            issues = self.validate_product(pv, pid, pname)
            all_issues.extend(issues)

            # Track field coverage
            for f in all_fields:
                val = self.get_field(pv, f)
                if f not in field_counts:
                    field_counts[f] = 0
                if val:
                    field_counts[f] += 1

        total = len(products)
        coverage = []
        for f in all_fields:
            filled = field_counts.get(f, 0)
            coverage.append(
                FieldCoverage(
                    field=f,
                    required=f in self.required_fields,
                    filled=filled,
                    total=total,
                    percent=round(filled / total * 100, 1) if total > 0 else 0.0,
                )
            )

        score = self.calculate_quality_score(all_issues, coverage)
        label = self._score_label(score)

        # Breakdown
        req_coverage = [c for c in coverage if c.required]
        rec_coverage = [c for c in coverage if not c.required]
        req_score = int(sum(c.percent for c in req_coverage) / len(req_coverage)) if req_coverage else 100
        rec_score = int(sum(c.percent for c in rec_coverage) / len(rec_coverage)) if rec_coverage else 100
        error_count = sum(1 for i in all_issues if i.level == "error")
        format_score = max(0, 100 - error_count * 2)

        return ValidationResult(
            platform=self.platform,
            total_products=total,
            issues=all_issues,
            field_coverage=coverage,
            quality_score=score,
            quality_label=label,
            quality_breakdown={
                "required_fields_score": req_score,
                "recommended_fields_score": rec_score,
                "format_compliance_score": min(format_score, 100),
            },
        )

    def validate_product(
        self, pv: dict, pid: str, pname: str
    ) -> list[ValidationIssue]:
        """Override in subclass. Validate one product's fields."""
        return []

    # Subclasses set these
    id_field: str = "id"
    name_field: str = "title"

    # ------------------------------------------------------------------
    # Quality score
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_quality_score(
        issues: list[ValidationIssue], coverage: list[FieldCoverage]
    ) -> int:
        score = 100.0
        error_count = sum(1 for i in issues if i.level == "error")
        warning_count = sum(1 for i in issues if i.level == "warning")
        score -= error_count * 5
        score -= warning_count * 1

        recommended = [c for c in coverage if not c.required]
        if recommended:
            avg = sum(c.percent for c in recommended) / len(recommended)
            score += (avg / 100) * 10

        return max(0, min(100, int(score)))

    @staticmethod
    def _score_label(score: int) -> str:
        if score >= 90:
            return "Doskonały"
        if score >= 70:
            return "Dobry"
        if score >= 50:
            return "Wymaga poprawy"
        return "Słaby"
