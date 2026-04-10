"""Allegro feed validator."""
from app.services.validators.base import BaseValidator, ValidationIssue

class AllegroValidator(BaseValidator):
    platform = "allegro"
    id_field = "id"
    name_field = "name"
    required_fields = ["id", "name", "description", "url", "price", "category", "image", "availability"]
    recommended_fields = ["brand", "ean", "condition"]

    def validate_product(self, pv: dict, pid: str, pname: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))
        name = self.get_field(pv, "name")
        if name:
            issues.extend(self.check_max_length("name", name, 75, pid, pname))
        url = self.get_field(pv, "url")
        if url:
            issues.extend(self.check_url("url", url, pid, pname))
        img = self.get_field(pv, "image")
        issues.extend(self.check_image_present("image", img, pid, pname))
        ean = self.get_field(pv, "ean")
        if ean:
            issues.extend(self.check_ean13("ean", ean, pid, pname))
        return issues
