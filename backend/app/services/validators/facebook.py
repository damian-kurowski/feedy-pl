"""Facebook / Meta Catalog feed validator."""
from app.services.validators.base import BaseValidator, ValidationIssue

class FacebookValidator(BaseValidator):
    platform = "facebook"
    id_field = "id"
    name_field = "title"
    required_fields = ["id", "title", "description", "availability", "condition", "price", "link", "image_link", "brand"]
    recommended_fields = ["sale_price", "additional_image_link", "google_product_category", "product_type", "color", "size", "gender"]
    _VALID_AVAILABILITY = ["in stock", "out of stock", "available for order", "discontinued"]
    _VALID_CONDITION = ["new", "refurbished", "used"]

    def validate_product(self, pv: dict, pid: str, pname: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))
        issues.extend(self.check_max_length("id", self.get_field(pv, "id"), 100, pid, pname))
        issues.extend(self.check_max_length("title", self.get_field(pv, "title"), 200, pid, pname))
        issues.extend(self.check_max_length("description", self.get_field(pv, "description"), 9999, pid, pname))
        price = self.get_field(pv, "price")
        if price:
            issues.extend(self.check_price_with_currency("price", price, pid, pname))
        link = self.get_field(pv, "link")
        if link:
            issues.extend(self.check_url("link", link, pid, pname))
        avail = self.get_field(pv, "availability")
        if avail:
            issues.extend(self.check_enum("availability", avail, self._VALID_AVAILABILITY, pid, pname))
        cond = self.get_field(pv, "condition")
        if cond:
            issues.extend(self.check_enum("condition", cond, self._VALID_CONDITION, pid, pname))
        img = self.get_field(pv, "image_link")
        issues.extend(self.check_image_present("image_link", img, pid, pname))
        return issues
