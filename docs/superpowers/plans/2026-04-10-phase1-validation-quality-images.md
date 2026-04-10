# Phase 1: Validation + Quality Score + Image Previews — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace basic feed validation with comprehensive per-platform validators, add a quality score dashboard, and add product image previews.

**Architecture:** New `validators/` module with one class per platform, all sharing a `BaseValidator`. Quality score computed from validation results (no DB changes). Image previews are frontend-only — thumbnails rendered from existing URLs in `product_value`.

**Tech Stack:** Python (dataclasses, lxml), FastAPI, Vue 3, Tailwind CSS, Pinia

---

## File Structure

### Backend — New files
- `backend/app/services/validators/__init__.py` — registry, `validate_feed()` dispatcher
- `backend/app/services/validators/base.py` — `ValidationIssue`, `FieldCoverage`, `ValidationResult`, `BaseValidator` with shared rules
- `backend/app/services/validators/ceneo.py` — `CeneoValidator`
- `backend/app/services/validators/gmc.py` — `GmcValidator`
- `backend/app/services/validators/facebook.py` — `FacebookValidator`
- `backend/app/services/validators/allegro.py` — `AllegroValidator`
- `backend/app/services/validators/skapiec.py` — `SkapiecValidator`
- `backend/app/services/validators/domodi.py` — `DomodiValidator`
- `backend/tests/test_validators_base.py` — tests for shared validation logic
- `backend/tests/test_validators_ceneo.py` — tests for CeneoValidator
- `backend/tests/test_validators_gmc.py` — tests for GmcValidator
- `backend/tests/test_validators_facebook.py` — tests for FacebookValidator
- `backend/tests/test_validators_allegro.py` — tests for AllegroValidator
- `backend/tests/test_validators_skapiec.py` — tests for SkapiecValidator
- `backend/tests/test_validators_domodi.py` — tests for DomodiValidator

### Backend — Modified files
- `backend/app/routers/feeds_out.py` — update `/validate` endpoint to use new validators
- `backend/tests/test_feed_validator.py` — update imports to new module

### Backend — Deleted files
- `backend/app/services/feed_validator.py` — replaced by `validators/` module

### Frontend — New files
- `frontend/src/utils/imageExtractor.ts` — extract image URLs from product_value
- `frontend/src/components/QualityScore.vue` — circular score indicator
- `frontend/src/components/ValidationIssues.vue` — filterable issues list
- `frontend/src/components/ImageLightbox.vue` — image modal/lightbox

### Frontend — Modified files
- `frontend/src/components/ProductPreview.vue` — add image thumbnails
- `frontend/src/components/MappingTable.vue` — image preview in "Podgląd" column
- `frontend/src/views/FeedOutDetailView.vue` — add quality score section, update validation UI
- `frontend/src/views/DashboardView.vue` — add quality score badges on feed out cards
- `frontend/src/stores/feedsOut.ts` — add `ValidationResult` type, validation cache

---

### Task 1: BaseValidator and shared validation utilities

**Files:**
- Create: `backend/app/services/validators/__init__.py`
- Create: `backend/app/services/validators/base.py`
- Test: `backend/tests/test_validators_base.py`

- [ ] **Step 1: Write tests for shared validation utilities**

```python
# backend/tests/test_validators_base.py
from app.services.validators.base import (
    BaseValidator,
    ValidationIssue,
    FieldCoverage,
    ValidationResult,
)


def _make_product(overrides: dict | None = None) -> dict:
    base = {
        "id": "123",
        "title": "Test Product",
        "link": "https://shop.pl/p/123",
        "price": "49.99 PLN",
        "image": "https://shop.pl/img/123.jpg",
    }
    if overrides:
        base.update(overrides)
    return {"product_value": base}


class TestBaseValidator:
    def test_validate_url_valid(self):
        v = BaseValidator("test")
        issues = v.check_url("link", "https://shop.pl/p/1", "1", "P")
        assert issues == []

    def test_validate_url_http_warning(self):
        v = BaseValidator("test")
        issues = v.check_url("link", "http://shop.pl/p/1", "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "warning"
        assert "HTTPS" in issues[0].message

    def test_validate_url_invalid(self):
        v = BaseValidator("test")
        issues = v.check_url("link", "not-a-url", "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "error"

    def test_validate_price_with_currency_valid(self):
        v = BaseValidator("test")
        issues = v.check_price_with_currency("price", "49.99 PLN", "1", "P")
        assert issues == []

    def test_validate_price_with_currency_missing_currency(self):
        v = BaseValidator("test")
        issues = v.check_price_with_currency("price", "49.99", "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "error"

    def test_validate_price_no_currency_valid(self):
        v = BaseValidator("test")
        issues = v.check_price_no_currency("price", "49.99", "1", "P")
        assert issues == []

    def test_validate_price_no_currency_has_currency(self):
        v = BaseValidator("test")
        issues = v.check_price_no_currency("price", "49.99 PLN", "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "warning"

    def test_validate_price_no_currency_invalid(self):
        v = BaseValidator("test")
        issues = v.check_price_no_currency("price", "abc", "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "error"

    def test_validate_ean13_valid(self):
        v = BaseValidator("test")
        # Valid EAN-13: 5901234123457
        issues = v.check_ean13("ean", "5901234123457", "1", "P")
        assert issues == []

    def test_validate_ean13_invalid_checksum(self):
        v = BaseValidator("test")
        issues = v.check_ean13("ean", "5901234123456", "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "warning"

    def test_validate_ean13_wrong_length(self):
        v = BaseValidator("test")
        issues = v.check_ean13("ean", "12345", "1", "P")
        assert len(issues) == 1

    def test_validate_required_present(self):
        v = BaseValidator("test")
        issues = v.check_required({"title": "Test"}, "title", "1", "P")
        assert issues == []

    def test_validate_required_missing(self):
        v = BaseValidator("test")
        issues = v.check_required({}, "title", "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "error"

    def test_validate_required_empty_string(self):
        v = BaseValidator("test")
        issues = v.check_required({"title": ""}, "title", "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "error"

    def test_validate_max_length_ok(self):
        v = BaseValidator("test")
        issues = v.check_max_length("title", "Short", 150, "1", "P")
        assert issues == []

    def test_validate_max_length_exceeded(self):
        v = BaseValidator("test")
        issues = v.check_max_length("title", "x" * 200, 150, "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "warning"

    def test_validate_enum_valid(self):
        v = BaseValidator("test")
        issues = v.check_enum("availability", "in_stock", ["in_stock", "out_of_stock"], "1", "P")
        assert issues == []

    def test_validate_enum_invalid(self):
        v = BaseValidator("test")
        issues = v.check_enum("availability", "maybe", ["in_stock", "out_of_stock"], "1", "P")
        assert len(issues) == 1
        assert issues[0].level == "error"

    def test_calculate_quality_score_perfect(self):
        result = BaseValidator.calculate_quality_score([], [
            FieldCoverage(field="id", required=True, filled=10, total=10, percent=100.0),
        ])
        assert result >= 90

    def test_calculate_quality_score_with_errors(self):
        issues = [
            ValidationIssue(level="error", field="price", message="Bad", product_id="1", product_name="P", rule="r"),
            ValidationIssue(level="error", field="price", message="Bad", product_id="2", product_name="P", rule="r"),
        ]
        result = BaseValidator.calculate_quality_score(issues, [])
        assert result == 90  # 100 - 2*5

    def test_calculate_quality_score_clamped_to_zero(self):
        issues = [
            ValidationIssue(level="error", field="x", message="Bad", product_id=str(i), product_name="P", rule="r")
            for i in range(30)
        ]
        result = BaseValidator.calculate_quality_score(issues, [])
        assert result == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_validators_base.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement BaseValidator**

```python
# backend/app/services/validators/__init__.py
"""Feed validators — one per platform."""

from app.services.validators.base import (
    BaseValidator,
    FieldCoverage,
    ValidationIssue,
    ValidationResult,
)

__all__ = [
    "BaseValidator",
    "FieldCoverage",
    "ValidationIssue",
    "ValidationResult",
    "validate_feed",
]


def validate_feed(platform: str, products: list[dict]) -> ValidationResult:
    """Run the validator for *platform* against *products*.

    Each product is a dict with a ``product_value`` key.
    """
    from app.services.validators.ceneo import CeneoValidator
    from app.services.validators.gmc import GmcValidator
    from app.services.validators.facebook import FacebookValidator
    from app.services.validators.allegro import AllegroValidator
    from app.services.validators.skapiec import SkapiecValidator
    from app.services.validators.domodi import DomodiValidator

    registry: dict[str, type[BaseValidator]] = {
        "ceneo": CeneoValidator,
        "gmc": GmcValidator,
        "facebook": FacebookValidator,
        "allegro": AllegroValidator,
        "skapiec": SkapiecValidator,
        "domodi": DomodiValidator,
    }
    validator_cls = registry.get(platform)
    if validator_cls is None:
        return ValidationResult(
            platform=platform,
            total_products=len(products),
            issues=[],
            field_coverage=[],
            quality_score=100,
            quality_label="Doskonały",
            quality_breakdown={
                "required_fields_score": 100,
                "recommended_fields_score": 100,
                "format_compliance_score": 100,
            },
        )
    validator = validator_cls()
    return validator.validate(products)
```

```python
# backend/app/services/validators/base.py
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
        val = product.get(field_name)
        if val is None or (isinstance(val, str) and not val.strip()):
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
        digits = value.strip()
        if not digits.isdigit() or len(digits) not in (8, 12, 13, 14):
            return [
                ValidationIssue(
                    level="warning",
                    field=field_name,
                    message=f"Nieprawidłowy kod EAN/GTIN: '{digits}' (oczekiwano 8, 12, 13 lub 14 cyfr)",
                    product_id=pid,
                    product_name=pname,
                    rule="invalid_ean_length",
                )
            ]
        if len(digits) == 13:
            # EAN-13 checksum
            odd = sum(int(digits[i]) for i in range(0, 12, 2))
            even = sum(int(digits[i]) for i in range(1, 12, 2))
            check = (10 - (odd + even * 3) % 10) % 10
            if check != int(digits[12]):
                return [
                    ValidationIssue(
                        level="warning",
                        field=field_name,
                        message=f"Nieprawidłowa suma kontrolna EAN-13: '{digits}'",
                        product_id=pid,
                        product_name=pname,
                        rule="invalid_ean_checksum",
                    )
                ]
        return []

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
        if value.strip().lower() not in [a.lower() for a in allowed]:
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

    def get_field(self, pv: dict, field_name: str) -> str | None:
        """Get a field value from product_value dict, returning str or None."""
        val = pv.get(field_name)
        if val is None:
            return None
        if isinstance(val, dict):
            # Handle nested image structures like imgs: {main: {@url: "..."}}
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_validators_base.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/validators/__init__.py backend/app/services/validators/base.py backend/tests/test_validators_base.py
git commit -m "feat: add BaseValidator with shared validation utilities"
```

---

### Task 2: CeneoValidator

**Files:**
- Create: `backend/app/services/validators/ceneo.py`
- Test: `backend/tests/test_validators_ceneo.py`

- [ ] **Step 1: Write tests**

```python
# backend/tests/test_validators_ceneo.py
from app.services.validators.ceneo import CeneoValidator


def _ceneo_product(overrides: dict | None = None) -> dict:
    base = {
        "@id": "123",
        "@url": "https://shop.pl/p/123",
        "@price": "49.99",
        "@avail": "1",
        "name": "Test Product",
        "cat": "Elektronika",
        "desc": "Opis produktu testowego",
        "imgs": {"main": {"@url": "https://shop.pl/img.jpg"}},
    }
    if overrides:
        base.update(overrides)
    return {"product_value": base}


def test_valid_ceneo_product():
    v = CeneoValidator()
    result = v.validate([_ceneo_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0
    assert result.quality_score >= 80


def test_ceneo_missing_id():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@id": None})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "@id" for i in errors)


def test_ceneo_missing_price():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@price": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "@price" for i in errors)


def test_ceneo_invalid_price_format():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@price": "abc"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.rule == "invalid_price" for i in errors)


def test_ceneo_price_with_currency_warns():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@price": "49.99 PLN"})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.rule == "price_has_currency" for i in warnings)


def test_ceneo_invalid_avail():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@avail": "maybe"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "@avail" for i in errors)


def test_ceneo_missing_image_warning():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"imgs": None})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.rule == "missing_image" for i in warnings)


def test_ceneo_missing_producer_warning():
    v = CeneoValidator()
    # No producer field at all
    result = v.validate([_ceneo_product()])
    warnings = [i for i in result.issues if i.level == "warning"]
    # producer is recommended, not required — just check coverage
    producer_coverage = [c for c in result.field_coverage if c.field == "producer"]
    assert len(producer_coverage) == 1
    assert producer_coverage[0].filled == 0


def test_ceneo_field_coverage():
    v = CeneoValidator()
    result = v.validate([_ceneo_product()])
    assert result.total_products == 1
    assert len(result.field_coverage) > 0
    id_cov = next(c for c in result.field_coverage if c.field == "@id")
    assert id_cov.filled == 1
    assert id_cov.percent == 100.0


def test_ceneo_quality_score_present():
    v = CeneoValidator()
    result = v.validate([_ceneo_product()])
    assert 0 <= result.quality_score <= 100
    assert result.quality_label in ("Doskonały", "Dobry", "Wymaga poprawy", "Słaby")
    assert "required_fields_score" in result.quality_breakdown
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_validators_ceneo.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement CeneoValidator**

```python
# backend/app/services/validators/ceneo.py
"""Ceneo feed validator."""

from app.services.validators.base import BaseValidator, ValidationIssue


class CeneoValidator(BaseValidator):
    platform = "ceneo"
    id_field = "@id"
    name_field = "name"

    required_fields = ["@id", "@url", "@price", "@avail", "name", "cat", "desc"]
    recommended_fields = ["producer", "code", "imgs", "old_price", "shipping"]

    def validate_product(
        self, pv: dict, pid: str, pname: str
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        # Required fields
        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))

        # Price format (no currency)
        price = self.get_field(pv, "@price")
        if price:
            issues.extend(self.check_price_no_currency("@price", price, pid, pname))

        # URL
        url = self.get_field(pv, "@url")
        if url:
            issues.extend(self.check_url("@url", url, pid, pname))

        # Availability must be valid code
        avail = self.get_field(pv, "@avail")
        if avail:
            issues.extend(
                self.check_enum("@avail", avail, ["1", "3", "7", "14", "99"], pid, pname)
            )

        # Image check
        img_url = self._get_image_url(pv)
        issues.extend(self.check_image_present("imgs", img_url, pid, pname))

        # EAN check if present
        ean = self.get_field(pv, "code")
        if ean:
            issues.extend(self.check_ean13("code", ean, pid, pname))

        return issues

    def _get_image_url(self, pv: dict) -> str | None:
        imgs = pv.get("imgs")
        if isinstance(imgs, dict):
            main = imgs.get("main")
            if isinstance(main, dict):
                return main.get("@url")
            if isinstance(main, str):
                return main
        img = pv.get("img")
        if isinstance(img, str):
            return img
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_validators_ceneo.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/validators/ceneo.py backend/tests/test_validators_ceneo.py
git commit -m "feat: add CeneoValidator with full field validation"
```

---

### Task 3: GmcValidator

**Files:**
- Create: `backend/app/services/validators/gmc.py`
- Test: `backend/tests/test_validators_gmc.py`

- [ ] **Step 1: Write tests**

```python
# backend/tests/test_validators_gmc.py
from app.services.validators.gmc import GmcValidator


def _gmc_product(overrides: dict | None = None) -> dict:
    base = {
        "g:id": "SKU-123",
        "title": "Test Product",
        "description": "Product description text here",
        "link": "https://shop.pl/p/123",
        "g:image_link": "https://shop.pl/img/123.jpg",
        "g:availability": "in_stock",
        "g:price": "49.99 PLN",
        "g:condition": "new",
        "g:brand": "TestBrand",
    }
    if overrides:
        base.update(overrides)
    return {"product_value": base}


def test_valid_gmc_product():
    v = GmcValidator()
    result = v.validate([_gmc_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0


def test_gmc_missing_title():
    v = GmcValidator()
    result = v.validate([_gmc_product({"title": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "title" for i in errors)


def test_gmc_title_too_long():
    v = GmcValidator()
    result = v.validate([_gmc_product({"title": "x" * 200})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "title" and i.rule == "max_length" for i in warnings)


def test_gmc_price_no_currency():
    v = GmcValidator()
    result = v.validate([_gmc_product({"g:price": "49.99"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "g:price" for i in errors)


def test_gmc_invalid_availability():
    v = GmcValidator()
    result = v.validate([_gmc_product({"g:availability": "maybe"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "g:availability" for i in errors)


def test_gmc_no_brand_no_gtin():
    v = GmcValidator()
    result = v.validate([_gmc_product({"g:brand": None, "g:gtin": None})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.rule == "brand_or_gtin" for i in errors)


def test_gmc_gtin_valid():
    v = GmcValidator()
    result = v.validate([_gmc_product({"g:brand": None, "g:gtin": "5901234123457"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert not any(i.rule == "brand_or_gtin" for i in errors)


def test_gmc_missing_google_category_warning():
    v = GmcValidator()
    result = v.validate([_gmc_product()])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "g:google_product_category" for i in warnings)


def test_gmc_description_too_long():
    v = GmcValidator()
    result = v.validate([_gmc_product({"description": "x" * 6000})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "description" and i.rule == "max_length" for i in warnings)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_validators_gmc.py -v`
Expected: FAIL

- [ ] **Step 3: Implement GmcValidator**

```python
# backend/app/services/validators/gmc.py
"""Google Merchant Center feed validator."""

from app.services.validators.base import BaseValidator, ValidationIssue


class GmcValidator(BaseValidator):
    platform = "gmc"
    id_field = "g:id"
    name_field = "title"

    required_fields = [
        "g:id", "title", "description", "link", "g:image_link",
        "g:availability", "g:price", "g:condition",
    ]
    recommended_fields = [
        "g:brand", "g:gtin", "g:mpn", "g:google_product_category",
        "g:product_type", "g:additional_image_link",
    ]

    _VALID_AVAILABILITY = ["in_stock", "out_of_stock", "preorder", "backorder"]
    _VALID_CONDITION = ["new", "refurbished", "used"]

    def validate_product(
        self, pv: dict, pid: str, pname: str
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        # Required fields
        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))

        # Title length
        title = self.get_field(pv, "title")
        if title:
            issues.extend(self.check_max_length("title", title, 150, pid, pname))

        # Description length
        desc = self.get_field(pv, "description")
        if desc:
            issues.extend(self.check_max_length("description", desc, 5000, pid, pname))

        # Price must have currency
        price = self.get_field(pv, "g:price")
        if price:
            issues.extend(self.check_price_with_currency("g:price", price, pid, pname))

        # Link URL
        link = self.get_field(pv, "link")
        if link:
            issues.extend(self.check_url("link", link, pid, pname))

        # Availability enum
        avail = self.get_field(pv, "g:availability")
        if avail:
            issues.extend(
                self.check_enum("g:availability", avail, self._VALID_AVAILABILITY, pid, pname)
            )

        # Condition enum
        condition = self.get_field(pv, "g:condition")
        if condition:
            issues.extend(
                self.check_enum("g:condition", condition, self._VALID_CONDITION, pid, pname)
            )

        # Brand or GTIN required
        brand = self.get_field(pv, "g:brand")
        gtin = self.get_field(pv, "g:gtin")
        if not brand and not gtin:
            issues.append(
                ValidationIssue(
                    level="error",
                    field="g:brand",
                    message="Wymagane pole 'g:brand' lub 'g:gtin' — co najmniej jedno musi być podane",
                    product_id=pid,
                    product_name=pname,
                    rule="brand_or_gtin",
                )
            )

        # GTIN checksum
        if gtin:
            issues.extend(self.check_ean13("g:gtin", gtin, pid, pname))

        # Image
        img = self.get_field(pv, "g:image_link")
        issues.extend(self.check_image_present("g:image_link", img, pid, pname))

        # Google product category (warning only)
        gpc = self.get_field(pv, "g:google_product_category")
        if not gpc:
            issues.append(
                ValidationIssue(
                    level="warning",
                    field="g:google_product_category",
                    message="Brak 'g:google_product_category' — Google może nieprawidłowo sklasyfikować produkt",
                    product_id=pid,
                    product_name=pname,
                    rule="missing_recommended",
                )
            )

        return issues
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_validators_gmc.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/validators/gmc.py backend/tests/test_validators_gmc.py
git commit -m "feat: add GmcValidator with Google Merchant Center rules"
```

---

### Task 4: Facebook, Allegro, Skapiec, Domodi validators

**Files:**
- Create: `backend/app/services/validators/facebook.py`
- Create: `backend/app/services/validators/allegro.py`
- Create: `backend/app/services/validators/skapiec.py`
- Create: `backend/app/services/validators/domodi.py`
- Test: `backend/tests/test_validators_facebook.py`
- Test: `backend/tests/test_validators_allegro.py`
- Test: `backend/tests/test_validators_skapiec.py`
- Test: `backend/tests/test_validators_domodi.py`

- [ ] **Step 1: Write tests for all four validators**

```python
# backend/tests/test_validators_facebook.py
from app.services.validators.facebook import FacebookValidator


def _fb_product(overrides: dict | None = None) -> dict:
    base = {
        "id": "123",
        "title": "Test Product",
        "description": "Product description",
        "availability": "in stock",
        "condition": "new",
        "price": "49.99 PLN",
        "link": "https://shop.pl/p/123",
        "image_link": "https://shop.pl/img.jpg",
        "brand": "TestBrand",
    }
    if overrides:
        base.update(overrides)
    return {"product_value": base}


def test_valid_fb_product():
    v = FacebookValidator()
    result = v.validate([_fb_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0


def test_fb_missing_brand():
    v = FacebookValidator()
    result = v.validate([_fb_product({"brand": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "brand" for i in errors)


def test_fb_title_too_long():
    v = FacebookValidator()
    result = v.validate([_fb_product({"title": "x" * 250})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "title" for i in warnings)


def test_fb_id_too_long():
    v = FacebookValidator()
    result = v.validate([_fb_product({"id": "x" * 150})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "id" for i in warnings)
```

```python
# backend/tests/test_validators_allegro.py
from app.services.validators.allegro import AllegroValidator


def _allegro_product(overrides: dict | None = None) -> dict:
    base = {
        "id": "123",
        "name": "Test Product",
        "description": "Product description",
        "url": "https://shop.pl/p/123",
        "price": "49.99",
        "category": "Elektronika",
        "image": "https://shop.pl/img.jpg",
        "availability": "available",
    }
    if overrides:
        base.update(overrides)
    return {"product_value": base}


def test_valid_allegro_product():
    v = AllegroValidator()
    result = v.validate([_allegro_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0


def test_allegro_name_too_long():
    v = AllegroValidator()
    result = v.validate([_allegro_product({"name": "x" * 100})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "name" for i in warnings)


def test_allegro_missing_required():
    v = AllegroValidator()
    result = v.validate([_allegro_product({"name": "", "price": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) >= 2
```

```python
# backend/tests/test_validators_skapiec.py
from app.services.validators.skapiec import SkapiecValidator


def _skapiec_product(overrides: dict | None = None) -> dict:
    base = {
        "id": "123",
        "name": "Test Product",
        "url": "https://shop.pl/p/123",
        "price": "49.99",
        "category": "Elektronika",
        "image": "https://shop.pl/img.jpg",
        "description": "Opis produktu",
        "producer": "TestBrand",
        "availability": "1",
    }
    if overrides:
        base.update(overrides)
    return {"product_value": base}


def test_valid_skapiec_product():
    v = SkapiecValidator()
    result = v.validate([_skapiec_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0


def test_skapiec_missing_producer():
    v = SkapiecValidator()
    result = v.validate([_skapiec_product({"producer": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "producer" for i in errors)
```

```python
# backend/tests/test_validators_domodi.py
from app.services.validators.domodi import DomodiValidator


def _domodi_product(overrides: dict | None = None) -> dict:
    base = {
        "id": "123",
        "name": "Sukienka letnia",
        "url": "https://shop.pl/p/123",
        "price": "199.99",
        "image": "https://shop.pl/img.jpg",
        "category": "Odzież > Sukienki",
        "producer": "FashionBrand",
        "availability": "1",
    }
    if overrides:
        base.update(overrides)
    return {"product_value": base}


def test_valid_domodi_product():
    v = DomodiValidator()
    result = v.validate([_domodi_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0


def test_domodi_missing_color_warning():
    v = DomodiValidator()
    result = v.validate([_domodi_product()])
    # color is recommended, should appear in coverage as 0%
    color_cov = [c for c in result.field_coverage if c.field == "color"]
    assert len(color_cov) == 1
    assert color_cov[0].filled == 0


def test_domodi_with_fashion_fields():
    v = DomodiValidator()
    product = _domodi_product({"color": "Czerwony", "size": "M", "gender": "damskie", "material": "Bawełna"})
    result = v.validate([product])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0
    assert result.quality_score >= 90
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_validators_facebook.py tests/test_validators_allegro.py tests/test_validators_skapiec.py tests/test_validators_domodi.py -v`
Expected: FAIL

- [ ] **Step 3: Implement all four validators**

```python
# backend/app/services/validators/facebook.py
"""Facebook / Meta Catalog feed validator."""

from app.services.validators.base import BaseValidator, ValidationIssue


class FacebookValidator(BaseValidator):
    platform = "facebook"
    id_field = "id"
    name_field = "title"

    required_fields = [
        "id", "title", "description", "availability", "condition",
        "price", "link", "image_link", "brand",
    ]
    recommended_fields = [
        "sale_price", "additional_image_link", "google_product_category",
        "product_type", "color", "size", "gender",
    ]

    _VALID_AVAILABILITY = ["in stock", "out of stock", "available for order", "discontinued"]
    _VALID_CONDITION = ["new", "refurbished", "used"]

    def validate_product(self, pv: dict, pid: str, pname: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))

        # Length limits
        issues.extend(self.check_max_length("id", self.get_field(pv, "id"), 100, pid, pname))
        issues.extend(self.check_max_length("title", self.get_field(pv, "title"), 200, pid, pname))
        issues.extend(self.check_max_length("description", self.get_field(pv, "description"), 9999, pid, pname))

        # Price with currency
        price = self.get_field(pv, "price")
        if price:
            issues.extend(self.check_price_with_currency("price", price, pid, pname))

        # URL
        link = self.get_field(pv, "link")
        if link:
            issues.extend(self.check_url("link", link, pid, pname))

        # Availability enum
        avail = self.get_field(pv, "availability")
        if avail:
            issues.extend(self.check_enum("availability", avail, self._VALID_AVAILABILITY, pid, pname))

        # Condition enum
        cond = self.get_field(pv, "condition")
        if cond:
            issues.extend(self.check_enum("condition", cond, self._VALID_CONDITION, pid, pname))

        # Image
        img = self.get_field(pv, "image_link")
        issues.extend(self.check_image_present("image_link", img, pid, pname))

        return issues
```

```python
# backend/app/services/validators/allegro.py
"""Allegro feed validator."""

from app.services.validators.base import BaseValidator, ValidationIssue


class AllegroValidator(BaseValidator):
    platform = "allegro"
    id_field = "id"
    name_field = "name"

    required_fields = [
        "id", "name", "description", "url", "price",
        "category", "image", "availability",
    ]
    recommended_fields = ["brand", "ean", "condition"]

    def validate_product(self, pv: dict, pid: str, pname: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))

        # Name max 75 chars (Allegro limit)
        name = self.get_field(pv, "name")
        if name:
            issues.extend(self.check_max_length("name", name, 75, pid, pname))

        # URL
        url = self.get_field(pv, "url")
        if url:
            issues.extend(self.check_url("url", url, pid, pname))

        # Image
        img = self.get_field(pv, "image")
        issues.extend(self.check_image_present("image", img, pid, pname))

        # EAN
        ean = self.get_field(pv, "ean")
        if ean:
            issues.extend(self.check_ean13("ean", ean, pid, pname))

        return issues
```

```python
# backend/app/services/validators/skapiec.py
"""Skapiec.pl feed validator."""

from app.services.validators.base import BaseValidator, ValidationIssue


class SkapiecValidator(BaseValidator):
    platform = "skapiec"
    id_field = "id"
    name_field = "name"

    required_fields = [
        "id", "name", "url", "price", "category",
        "image", "description", "producer", "availability",
    ]
    recommended_fields = ["ean", "old_price", "shipping"]

    def validate_product(self, pv: dict, pid: str, pname: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))

        # Price no currency
        price = self.get_field(pv, "price")
        if price:
            issues.extend(self.check_price_no_currency("price", price, pid, pname))

        # URL
        url = self.get_field(pv, "url")
        if url:
            issues.extend(self.check_url("url", url, pid, pname))

        # Image
        img = self.get_field(pv, "image")
        issues.extend(self.check_image_present("image", img, pid, pname))

        # EAN
        ean = self.get_field(pv, "ean")
        if ean:
            issues.extend(self.check_ean13("ean", ean, pid, pname))

        return issues
```

```python
# backend/app/services/validators/domodi.py
"""Domodi / Homebook feed validator."""

from app.services.validators.base import BaseValidator, ValidationIssue


class DomodiValidator(BaseValidator):
    platform = "domodi"
    id_field = "id"
    name_field = "name"

    required_fields = [
        "id", "name", "url", "price", "image",
        "category", "producer", "availability",
    ]
    recommended_fields = ["color", "size", "material", "gender", "old_price"]

    def validate_product(self, pv: dict, pid: str, pname: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))

        # Price no currency
        price = self.get_field(pv, "price")
        if price:
            issues.extend(self.check_price_no_currency("price", price, pid, pname))

        # URL
        url = self.get_field(pv, "url")
        if url:
            issues.extend(self.check_url("url", url, pid, pname))

        # Image
        img = self.get_field(pv, "image")
        issues.extend(self.check_image_present("image", img, pid, pname))

        return issues
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_validators_facebook.py tests/test_validators_allegro.py tests/test_validators_skapiec.py tests/test_validators_domodi.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/validators/facebook.py backend/app/services/validators/allegro.py backend/app/services/validators/skapiec.py backend/app/services/validators/domodi.py backend/tests/test_validators_facebook.py backend/tests/test_validators_allegro.py backend/tests/test_validators_skapiec.py backend/tests/test_validators_domodi.py
git commit -m "feat: add Facebook, Allegro, Skapiec, Domodi validators"
```

---

### Task 5: Wire up validate endpoint and remove old validator

**Files:**
- Modify: `backend/app/routers/feeds_out.py:152-181`
- Delete: `backend/app/services/feed_validator.py`
- Modify: `backend/tests/test_feed_validator.py`

- [ ] **Step 1: Write integration test for the new validate endpoint**

```python
# backend/tests/test_feed_validator.py
"""Tests for the validate_feed dispatcher."""
from app.services.validators import validate_feed


def _product(pv: dict) -> dict:
    return {"product_value": pv}


def test_validate_feed_ceneo():
    products = [_product({"@id": "1", "@url": "https://x.pl", "@price": "10.00", "@avail": "1", "name": "P", "cat": "C", "desc": "D"})]
    result = validate_feed("ceneo", products)
    assert result.platform == "ceneo"
    assert result.total_products == 1
    assert result.quality_score >= 0


def test_validate_feed_gmc():
    products = [_product({
        "g:id": "1", "title": "P", "description": "D", "link": "https://x.pl",
        "g:image_link": "https://x.pl/img.jpg", "g:availability": "in_stock",
        "g:price": "10.00 PLN", "g:condition": "new", "g:brand": "B",
    })]
    result = validate_feed("gmc", products)
    assert result.platform == "gmc"
    assert 0 <= result.quality_score <= 100


def test_validate_feed_unknown_platform():
    result = validate_feed("unknown", [_product({"id": "1"})])
    assert result.quality_score == 100
    assert result.issues == []


def test_validate_feed_empty_products():
    result = validate_feed("ceneo", [])
    assert result.total_products == 0
    assert result.quality_score >= 0
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_feed_validator.py -v`
Expected: All PASS

- [ ] **Step 3: Update the `/validate` endpoint in feeds_out.py**

Replace lines 152-181 in `backend/app/routers/feeds_out.py`. The new endpoint uses `validate_feed` from the validators module and returns the full `ValidationResult` as a dict.

Update imports at top of file: remove `from app.services.feed_validator import ...` and add `from app.services.validators import validate_feed`.

New endpoint code:

```python
@router.get("/{feed_out_id}/validate")
async def validate_feed_endpoint(
    feed_out_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed_out = await _get_user_feed_out(db, feed_out_id, user.id)

    # Get products
    products_result = await db.execute(
        select(ProductIn).where(ProductIn.feed_in_id == feed_out.feed_in_id)
    )
    products = [{"product_value": p.product_value} for p in products_result.scalars().all()]

    # Apply rules if any
    if feed_out.rules:
        from app.services.rules_engine import apply_rules
        products = apply_rules(products, feed_out.rules)

    result = validate_feed(feed_out.type, products)

    return {
        "platform": result.platform,
        "total_products": result.total_products,
        "quality_score": result.quality_score,
        "quality_label": result.quality_label,
        "quality_breakdown": result.quality_breakdown,
        "summary": {
            "errors": sum(1 for i in result.issues if i.level == "error"),
            "warnings": sum(1 for i in result.issues if i.level == "warning"),
            "info": sum(1 for i in result.issues if i.level == "info"),
        },
        "field_coverage": [
            {
                "field": c.field,
                "required": c.required,
                "filled": c.filled,
                "total": c.total,
                "percent": c.percent,
            }
            for c in result.field_coverage
        ],
        "issues": [
            {
                "level": i.level,
                "field": i.field,
                "message": i.message,
                "product_id": i.product_id,
                "product_name": i.product_name,
                "rule": i.rule,
            }
            for i in result.issues[:100]  # Limit to 100 issues
        ],
    }
```

- [ ] **Step 4: Delete old feed_validator.py**

```bash
rm backend/app/services/feed_validator.py
```

- [ ] **Step 5: Run all tests**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/ -v --ignore=backend/venv`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/feeds_out.py backend/tests/test_feed_validator.py
git rm backend/app/services/feed_validator.py
git commit -m "feat: wire up new validators to /validate endpoint, remove old validator"
```

---

### Task 6: Frontend — image extractor utility

**Files:**
- Create: `frontend/src/utils/imageExtractor.ts`

- [ ] **Step 1: Create the image extractor utility**

```typescript
// frontend/src/utils/imageExtractor.ts

export interface ProductImages {
  main: string | null
  additional: string[]
}

/**
 * Extract image URLs from a product_value object.
 * Handles different feed formats: Google (g:image_link), Ceneo (imgs/main/@url),
 * Facebook (image_link), Allegro/Skapiec (image), etc.
 */
export function extractImageUrls(productValue: Record<string, unknown>): ProductImages {
  const result: ProductImages = { main: null, additional: [] }
  if (!productValue) return result

  // Try known main image fields in priority order
  const mainCandidates = [
    'g:image_link',
    'image_link',
    'image',
    'img',
  ]

  for (const key of mainCandidates) {
    const val = productValue[key]
    if (typeof val === 'string' && val.trim()) {
      result.main = val.trim()
      break
    }
  }

  // Handle nested Ceneo structure: imgs: { main: { @url: "..." } }
  if (!result.main) {
    const imgs = productValue['imgs']
    if (imgs && typeof imgs === 'object') {
      const imgsObj = imgs as Record<string, unknown>
      const main = imgsObj['main']
      if (main && typeof main === 'object') {
        const mainObj = main as Record<string, unknown>
        if (typeof mainObj['@url'] === 'string') {
          result.main = mainObj['@url']
        }
      } else if (typeof main === 'string') {
        result.main = main
      }
    }
  }

  // Additional images
  const additionalCandidates = ['g:additional_image_link', 'additional_image_link']
  for (const key of additionalCandidates) {
    const val = productValue[key]
    if (typeof val === 'string' && val.trim()) {
      result.additional.push(val.trim())
    } else if (Array.isArray(val)) {
      for (const v of val) {
        if (typeof v === 'string' && v.trim()) {
          result.additional.push(v.trim())
        }
      }
    }
  }

  return result
}

/**
 * Check if a path_in field name is likely an image field.
 */
export function isImageField(pathIn: string | null): boolean {
  if (!pathIn) return false
  const lower = pathIn.toLowerCase()
  return (
    lower.includes('image') ||
    lower.includes('img') ||
    lower === 'imgs' ||
    lower.includes('photo') ||
    lower.includes('picture')
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/utils/imageExtractor.ts
git commit -m "feat: add image URL extractor utility"
```

---

### Task 7: Frontend — ProductPreview with image thumbnails

**Files:**
- Modify: `frontend/src/components/ProductPreview.vue`
- Create: `frontend/src/components/ImageLightbox.vue`

- [ ] **Step 1: Create ImageLightbox component**

```vue
<!-- frontend/src/components/ImageLightbox.vue -->
<script setup lang="ts">
defineProps<{
  images: string[]
  show: boolean
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
      @click.self="emit('close')"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-4 max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-3">
          <h3 class="text-sm font-medium text-gray-700">Zdjęcia produktu ({{ images.length }})</h3>
          <button
            class="text-gray-400 hover:text-gray-600 cursor-pointer"
            @click="emit('close')"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div v-for="(img, idx) in images" :key="idx">
            <img
              :src="img"
              :alt="`Zdjęcie ${idx + 1}`"
              class="w-full h-auto rounded border border-gray-200"
              loading="lazy"
              @error="($event.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2240%22 height=%2240%22><rect fill=%22%23f3f4f6%22 width=%2240%22 height=%2240%22/><text x=%2220%22 y=%2224%22 text-anchor=%22middle%22 fill=%22%239ca3af%22 font-size=%2212%22>Err</text></svg>'"
            />
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
```

- [ ] **Step 2: Update ProductPreview with image thumbnails**

Replace the full content of `frontend/src/components/ProductPreview.vue`:

```vue
<!-- frontend/src/components/ProductPreview.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import type { Product } from '../stores/feedsIn'
import { extractImageUrls } from '../utils/imageExtractor'
import ImageLightbox from './ImageLightbox.vue'

defineProps<{
  products: Product[]
}>()

const expanded = ref<Set<number>>(new Set())
const lightboxImages = ref<string[]>([])
const showLightbox = ref(false)

const placeholderSvg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23f3f4f6' width='48' height='48' rx='6'/%3E%3Ctext x='24' y='28' text-anchor='middle' fill='%239ca3af' font-size='10'%3EBrak%3C/text%3E%3C/svg%3E"

function toggle(id: number) {
  if (expanded.value.has(id)) {
    expanded.value.delete(id)
  } else {
    expanded.value.add(id)
  }
}

function getMainImage(product: Product): string | null {
  const images = extractImageUrls(product.product_value as Record<string, unknown>)
  return images.main
}

function getAllImages(product: Product): string[] {
  const images = extractImageUrls(product.product_value as Record<string, unknown>)
  const all: string[] = []
  if (images.main) all.push(images.main)
  all.push(...images.additional)
  return all
}

function openLightbox(product: Product) {
  lightboxImages.value = getAllImages(product)
  showLightbox.value = true
}

function getPrice(product: Product): string | null {
  const pv = product.product_value as Record<string, unknown>
  return (pv['@price'] ?? pv['g:price'] ?? pv['price'] ?? null) as string | null
}

function getCategory(product: Product): string | null {
  const pv = product.product_value as Record<string, unknown>
  return (pv['cat'] ?? pv['g:product_type'] ?? pv['category'] ?? null) as string | null
}

function handleImgError(e: Event) {
  (e.target as HTMLImageElement).src = placeholderSvg
}
</script>

<template>
  <div>
    <div v-if="products.length === 0" class="text-gray-500 text-sm py-4">
      Brak produktów do wyświetlenia.
    </div>
    <div v-for="product in products" :key="product.id" class="border border-gray-200 rounded-md mb-2">
      <button
        class="w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-gray-50 cursor-pointer"
        @click="toggle(product.id)"
      >
        <!-- Thumbnail -->
        <img
          :src="getMainImage(product) || placeholderSvg"
          :alt="product.product_name"
          class="w-12 h-12 object-cover rounded border border-gray-200 shrink-0"
          loading="lazy"
          @error="handleImgError"
        />

        <!-- Product info -->
        <div class="flex-1 min-w-0">
          <span class="font-medium text-gray-900 text-sm block truncate">{{ product.product_name }}</span>
          <span v-if="getCategory(product)" class="text-xs text-gray-400 truncate block">{{ getCategory(product) }}</span>
        </div>

        <!-- Price -->
        <span v-if="getPrice(product)" class="text-sm font-medium text-gray-700 shrink-0">
          {{ getPrice(product) }}
        </span>

        <!-- Expand arrow -->
        <svg
          class="w-4 h-4 text-gray-400 transition-transform shrink-0"
          :class="{ 'rotate-180': expanded.has(product.id) }"
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Expanded content -->
      <div v-if="expanded.has(product.id)" class="px-4 pb-3 space-y-3">
        <!-- Images row -->
        <div v-if="getAllImages(product).length > 0" class="flex gap-2 flex-wrap">
          <img
            v-for="(img, idx) in getAllImages(product).slice(0, 6)"
            :key="idx"
            :src="img"
            :alt="`Zdjęcie ${idx + 1}`"
            class="w-20 h-20 object-cover rounded border border-gray-200 cursor-pointer hover:ring-2 hover:ring-indigo-400"
            loading="lazy"
            @click.stop="openLightbox(product)"
            @error="handleImgError"
          />
        </div>

        <!-- Raw data -->
        <pre class="text-xs bg-gray-50 p-3 rounded overflow-x-auto">{{ JSON.stringify(product.product_value, null, 2) }}</pre>
      </div>
    </div>

    <ImageLightbox
      :images="lightboxImages"
      :show="showLightbox"
      @close="showLightbox = false"
    />
  </div>
</template>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ProductPreview.vue frontend/src/components/ImageLightbox.vue
git commit -m "feat: add image thumbnails to product preview"
```

---

### Task 8: Frontend — MappingTable image preview

**Files:**
- Modify: `frontend/src/components/MappingTable.vue`

- [ ] **Step 1: Update MappingTable to show image previews**

Add import at top of `<script setup>`:
```typescript
import { isImageField } from '../utils/imageExtractor'
```

Replace the `previewValue` function:
```typescript
function previewValue(pathIn: string | null): string {
  if (!pathIn || !props.sampleProduct) return ''
  const val = props.sampleProduct[pathIn]
  if (val === undefined || val === null) return ''
  if (typeof val === 'object') return '[obiekt]'
  const str = String(val)
  return str.length > 60 ? str.slice(0, 60) + '...' : str
}

function previewImageUrl(pathIn: string | null): string | null {
  if (!pathIn || !props.sampleProduct || !isImageField(pathIn)) return null
  const val = props.sampleProduct[pathIn]
  if (typeof val === 'string' && val.startsWith('http')) return val
  if (typeof val === 'object' && val) {
    const obj = val as Record<string, unknown>
    for (const v of Object.values(obj)) {
      if (typeof v === 'object' && v) {
        const inner = v as Record<string, unknown>
        if (typeof inner['@url'] === 'string') return inner['@url']
      }
      if (typeof v === 'string' && v.startsWith('http')) return v
    }
  }
  return null
}
```

In the template, replace the "Podgląd" `<td>`:

```html
          <!-- Podgląd -->
          <td class="px-4 py-3 text-gray-500 truncate max-w-[200px] text-sm">
            <div v-if="previewImageUrl(row.path_in)" class="flex items-center gap-2">
              <img
                :src="previewImageUrl(row.path_in)!"
                alt="Preview"
                class="w-8 h-8 object-cover rounded border border-gray-200"
                @error="($event.target as HTMLImageElement).style.display='none'"
              />
              <span class="truncate text-xs">{{ previewValue(row.path_in) }}</span>
            </div>
            <span v-else>{{ previewValue(row.path_in) }}</span>
          </td>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/MappingTable.vue
git commit -m "feat: add image preview in mapping table"
```

---

### Task 9: Frontend — QualityScore and ValidationIssues components

**Files:**
- Create: `frontend/src/components/QualityScore.vue`
- Create: `frontend/src/components/ValidationIssues.vue`

- [ ] **Step 1: Create QualityScore component**

```vue
<!-- frontend/src/components/QualityScore.vue -->
<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
  label: string
  breakdown: {
    required_fields_score: number
    recommended_fields_score: number
    format_compliance_score: number
  }
  summary: { errors: number; warnings: number; info: number }
}>()

const colorClass = computed(() => {
  if (props.score >= 90) return { text: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200', ring: 'ring-green-500' }
  if (props.score >= 70) return { text: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200', ring: 'ring-yellow-500' }
  if (props.score >= 50) return { text: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200', ring: 'ring-orange-500' }
  return { text: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', ring: 'ring-red-500' }
})
</script>

<template>
  <div :class="[colorClass.bg, colorClass.border]" class="border rounded-lg p-5">
    <div class="flex items-center gap-6">
      <!-- Score circle -->
      <div
        class="w-20 h-20 rounded-full flex items-center justify-center border-4 shrink-0"
        :class="[colorClass.border]"
      >
        <span class="text-2xl font-bold" :class="colorClass.text">{{ score }}%</span>
      </div>

      <div class="flex-1">
        <h3 class="text-lg font-semibold" :class="colorClass.text">{{ label }}</h3>
        <p class="text-sm text-gray-600 mt-1">
          {{ summary.errors }} błędów
          <span class="mx-1">|</span>
          {{ summary.warnings }} ostrzeżeń
          <span v-if="summary.info > 0" class="mx-1">|</span>
          <span v-if="summary.info > 0">{{ summary.info }} informacji</span>
        </p>

        <!-- Breakdown bars -->
        <div class="mt-3 space-y-1.5">
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span class="w-32">Pola wymagane</span>
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-500 rounded-full" :style="{ width: breakdown.required_fields_score + '%' }" />
            </div>
            <span class="w-8 text-right">{{ breakdown.required_fields_score }}%</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span class="w-32">Pola zalecane</span>
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-300 rounded-full" :style="{ width: breakdown.recommended_fields_score + '%' }" />
            </div>
            <span class="w-8 text-right">{{ breakdown.recommended_fields_score }}%</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span class="w-32">Zgodność formatu</span>
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-green-500 rounded-full" :style="{ width: breakdown.format_compliance_score + '%' }" />
            </div>
            <span class="w-8 text-right">{{ breakdown.format_compliance_score }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Create ValidationIssues component**

```vue
<!-- frontend/src/components/ValidationIssues.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'

export interface Issue {
  level: string
  field: string
  message: string
  product_id: string
  product_name: string
  rule: string
}

const props = defineProps<{
  issues: Issue[]
}>()

const activeFilter = ref<'all' | 'error' | 'warning'>('all')

const filtered = computed(() => {
  if (activeFilter.value === 'all') return props.issues
  return props.issues.filter(i => i.level === activeFilter.value)
})

const errorCount = computed(() => props.issues.filter(i => i.level === 'error').length)
const warningCount = computed(() => props.issues.filter(i => i.level === 'warning').length)
</script>

<template>
  <div>
    <!-- Filter tabs -->
    <div class="flex gap-2 mb-3">
      <button
        class="px-3 py-1 text-xs font-medium rounded-full cursor-pointer"
        :class="activeFilter === 'all' ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
        @click="activeFilter = 'all'"
      >
        Wszystko ({{ issues.length }})
      </button>
      <button
        class="px-3 py-1 text-xs font-medium rounded-full cursor-pointer"
        :class="activeFilter === 'error' ? 'bg-red-600 text-white' : 'bg-red-50 text-red-600 hover:bg-red-100'"
        @click="activeFilter = 'error'"
      >
        Błędy ({{ errorCount }})
      </button>
      <button
        class="px-3 py-1 text-xs font-medium rounded-full cursor-pointer"
        :class="activeFilter === 'warning' ? 'bg-yellow-600 text-white' : 'bg-yellow-50 text-yellow-600 hover:bg-yellow-100'"
        @click="activeFilter = 'warning'"
      >
        Ostrzeżenia ({{ warningCount }})
      </button>
    </div>

    <!-- Issues list -->
    <div class="space-y-1 max-h-80 overflow-y-auto">
      <div
        v-for="(issue, idx) in filtered.slice(0, 50)"
        :key="idx"
        class="flex items-start gap-2 px-3 py-2 rounded text-sm"
        :class="issue.level === 'error' ? 'bg-red-50' : 'bg-yellow-50'"
      >
        <span class="shrink-0 mt-0.5" :class="issue.level === 'error' ? 'text-red-500' : 'text-yellow-500'">
          {{ issue.level === 'error' ? '✗' : '⚠' }}
        </span>
        <div class="min-w-0">
          <p :class="issue.level === 'error' ? 'text-red-700' : 'text-yellow-700'">
            {{ issue.message }}
          </p>
          <p class="text-xs text-gray-400 mt-0.5 truncate">
            Produkt: {{ issue.product_name }} ({{ issue.product_id }}) | Pole: {{ issue.field }}
          </p>
        </div>
      </div>
      <p v-if="filtered.length === 0" class="text-sm text-gray-400 py-2">Brak problemów w tej kategorii.</p>
      <p v-if="filtered.length > 50" class="text-xs text-gray-400 py-2">Pokazano 50 z {{ filtered.length }} problemów.</p>
    </div>
  </div>
</template>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/QualityScore.vue frontend/src/components/ValidationIssues.vue
git commit -m "feat: add QualityScore and ValidationIssues components"
```

---

### Task 10: Frontend — Update FeedOutDetailView with quality section

**Files:**
- Modify: `frontend/src/views/FeedOutDetailView.vue`

- [ ] **Step 1: Add imports and validation data**

At the top of `<script setup>`, add imports:

```typescript
import QualityScore from '../components/QualityScore.vue'
import ValidationIssues from '../components/ValidationIssues.vue'
```

Replace the existing `validation` ref and `validateFeed` function (lines 48-62) with:

```typescript
const validation = ref<any>(null)
const validating = ref(false)

async function validateFeed() {
  if (!feedOut.value) return
  validating.value = true
  try {
    const { data } = await api.get(`/feeds-out/${feedOut.value.id}/validate`)
    validation.value = data
  } catch {
    validation.value = null
  } finally {
    validating.value = false
  }
}
```

- [ ] **Step 2: Replace the validation section in template**

Replace the entire "Validation section" (lines 649-670) and the old validation button/result with the new quality score section. Insert it right after the header section (after line 328, before the "Mapping section"):

```html
      <!-- Quality Score section -->
      <section class="mb-10">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-800">Jakość feedu</h2>
          <button
            type="button"
            :disabled="validating"
            class="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 disabled:opacity-50 text-white font-medium rounded-md text-sm cursor-pointer"
            @click="validateFeed"
          >
            {{ validating ? 'Sprawdzanie...' : validation ? 'Sprawdź ponownie' : 'Sprawdź jakość feedu' }}
          </button>
        </div>

        <div v-if="validation">
          <QualityScore
            :score="validation.quality_score"
            :label="validation.quality_label"
            :breakdown="validation.quality_breakdown"
            :summary="validation.summary"
          />

          <!-- Field coverage -->
          <div v-if="validation.field_coverage?.length" class="mt-4 bg-white border rounded-lg p-4">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Pokrycie pól</h3>
            <div class="space-y-1.5">
              <div
                v-for="field in validation.field_coverage"
                :key="field.field"
                class="flex items-center gap-2 text-xs"
              >
                <span class="w-40 truncate" :class="field.required ? 'text-gray-700 font-medium' : 'text-gray-500'">
                  {{ field.field }}
                  <span v-if="field.required" class="text-red-400">*</span>
                </span>
                <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full"
                    :class="field.percent === 100 ? 'bg-green-500' : field.percent > 0 ? 'bg-yellow-400' : 'bg-red-300'"
                    :style="{ width: field.percent + '%' }"
                  />
                </div>
                <span class="w-16 text-right text-gray-500">{{ field.filled }}/{{ field.total }}</span>
              </div>
            </div>
          </div>

          <!-- Issues -->
          <div v-if="validation.issues?.length" class="mt-4 bg-white border rounded-lg p-4">
            <h3 class="text-sm font-medium text-gray-700 mb-3">Problemy</h3>
            <ValidationIssues :issues="validation.issues" />
          </div>
        </div>

        <div v-else-if="!validating" class="text-sm text-gray-400 bg-gray-50 border rounded-lg p-6 text-center">
          Kliknij "Sprawdź jakość feedu" aby zobaczyć wynik walidacji.
        </div>
      </section>
```

Also remove the old "Validation section" at the bottom of the template (the `<section class="mt-6">` with the old validate button and simple result display).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/FeedOutDetailView.vue
git commit -m "feat: add quality score dashboard to feed out detail view"
```

---

### Task 11: Frontend — Dashboard quality badges

**Files:**
- Modify: `frontend/src/views/DashboardView.vue`
- Modify: `frontend/src/stores/feedsOut.ts`

- [ ] **Step 1: Add validation cache to feedsOut store**

Add to `frontend/src/stores/feedsOut.ts` inside the store function, after existing methods:

```typescript
  const validationCache = ref<Record<number, { score: number; label: string; timestamp: number }>>({})

  async function getQualityScore(id: number): Promise<{ score: number; label: string } | null> {
    const cached = validationCache.value[id]
    if (cached && Date.now() - cached.timestamp < 5 * 60 * 1000) {
      return { score: cached.score, label: cached.label }
    }
    try {
      const { data } = await api.get(`/feeds-out/${id}/validate`)
      const result = { score: data.quality_score, label: data.quality_label }
      validationCache.value[id] = { ...result, timestamp: Date.now() }
      return result
    } catch {
      return null
    }
  }
```

Add `validationCache` and `getQualityScore` to the return statement.

- [ ] **Step 2: Add quality badges to DashboardView**

In `DashboardView.vue`, add a reactive map and load scores lazily. Add to `<script setup>`:

```typescript
import { ref, onMounted, watch } from 'vue'

const qualityScores = ref<Record<number, { score: number; label: string }>>({})

// Load quality scores lazily after feeds load
watch(() => feedsOutStore.feeds, async (feeds) => {
  for (const feed of feeds) {
    if (!qualityScores.value[feed.id]) {
      const result = await feedsOutStore.getQualityScore(feed.id)
      if (result) {
        qualityScores.value[feed.id] = result
      }
    }
  }
}, { immediate: false })
```

In the template, inside the feed out card (after the active/inactive badge, around line 231), add:

```html
            <span
              v-if="qualityScores[feed.id]"
              class="inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold"
              :class="{
                'bg-green-100 text-green-700': qualityScores[feed.id].score >= 90,
                'bg-yellow-100 text-yellow-700': qualityScores[feed.id].score >= 70 && qualityScores[feed.id].score < 90,
                'bg-orange-100 text-orange-700': qualityScores[feed.id].score >= 50 && qualityScores[feed.id].score < 70,
                'bg-red-100 text-red-700': qualityScores[feed.id].score < 50,
              }"
              :title="`Jakość feedu: ${qualityScores[feed.id].score}% — ${qualityScores[feed.id].label}`"
            >
              {{ qualityScores[feed.id].score }}
            </span>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/DashboardView.vue frontend/src/stores/feedsOut.ts
git commit -m "feat: add quality score badges to dashboard"
```

---

### Task 12: Run full test suite and verify

- [ ] **Step 1: Run all backend tests**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/ -v --ignore=venv`
Expected: All PASS

- [ ] **Step 2: Verify frontend compiles**

Run: `cd frontend && npx vue-tsc --noEmit 2>&1 || true && npx vite build`
Expected: Build succeeds

- [ ] **Step 3: Manual smoke test**

1. Open http://localhost:5173/
2. Go to a feed output detail page
3. Click "Sprawdź jakość feedu" — should show quality score, breakdown, field coverage, issues
4. Go to a feed input detail page — products should show image thumbnails
5. Click a product — should show expanded images
6. Dashboard should show small quality badges on feed out cards

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: Phase 1 complete — validation, quality score, image previews"
```
