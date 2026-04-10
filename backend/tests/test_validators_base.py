from app.services.validators.base import (
    BaseValidator,
    ValidationIssue,
    FieldCoverage,
    ValidationResult,
)


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
