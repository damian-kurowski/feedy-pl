"""Skapiec.pl feed validator."""
from app.services.validators.base import BaseValidator, ValidationIssue

class SkapiecValidator(BaseValidator):
    platform = "skapiec"
    id_field = "id"
    name_field = "name"
    required_fields = ["id", "name", "url", "price", "category", "image", "description", "producer", "availability"]
    recommended_fields = ["ean", "old_price", "shipping"]

    def validate_product(self, pv: dict, pid: str, pname: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))
        price = self.get_field(pv, "price")
        if price:
            issues.extend(self.check_price_no_currency("price", price, pid, pname))
        url = self.get_field(pv, "url")
        if url:
            issues.extend(self.check_url("url", url, pid, pname))
        img = self.get_field(pv, "image")
        issues.extend(self.check_image_present("image", img, pid, pname))
        ean = self.get_field(pv, "ean")
        if ean:
            issues.extend(self.check_ean13("ean", ean, pid, pname))
        return issues
