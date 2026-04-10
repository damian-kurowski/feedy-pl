"""Domodi / Homebook feed validator."""
from app.services.validators.base import BaseValidator, ValidationIssue

class DomodiValidator(BaseValidator):
    platform = "domodi"
    id_field = "id"
    name_field = "name"
    required_fields = ["id", "name", "url", "price", "image", "category", "producer", "availability"]
    recommended_fields = ["color", "size", "material", "gender", "old_price"]

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
        return issues
