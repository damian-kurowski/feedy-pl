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
