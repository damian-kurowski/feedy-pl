"""Google Merchant Center feed validator."""
from app.services.validators.base import BaseValidator, ValidationIssue

class GmcValidator(BaseValidator):
    platform = "gmc"
    id_field = "g:id"
    name_field = "title"
    required_fields = ["g:id", "title", "description", "link", "g:image_link", "g:availability", "g:price", "g:condition"]
    recommended_fields = ["g:brand", "g:gtin", "g:mpn", "g:google_product_category", "g:product_type", "g:additional_image_link"]
    _VALID_AVAILABILITY = ["in_stock", "out_of_stock", "preorder", "backorder"]
    _VALID_CONDITION = ["new", "refurbished", "used"]

    def validate_product(self, pv: dict, pid: str, pname: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))
        title = self.get_field(pv, "title")
        if title:
            issues.extend(self.check_max_length("title", title, 150, pid, pname))
        desc = self.get_field(pv, "description")
        if desc:
            issues.extend(self.check_max_length("description", desc, 5000, pid, pname))
        price = self.get_field(pv, "g:price")
        if price:
            issues.extend(self.check_price_with_currency("g:price", price, pid, pname))
        link = self.get_field(pv, "link")
        if link:
            issues.extend(self.check_url("link", link, pid, pname))
        avail = self.get_field(pv, "g:availability")
        if avail:
            issues.extend(self.check_enum("g:availability", avail, self._VALID_AVAILABILITY, pid, pname))
        condition = self.get_field(pv, "g:condition")
        if condition:
            issues.extend(self.check_enum("g:condition", condition, self._VALID_CONDITION, pid, pname))
        brand = self.get_field(pv, "g:brand")
        gtin = self.get_field(pv, "g:gtin")
        if not brand and not gtin:
            issues.append(ValidationIssue(level="error", field="g:brand", message="Wymagane pole 'g:brand' lub 'g:gtin' — co najmniej jedno musi być podane", product_id=pid, product_name=pname, rule="brand_or_gtin"))
        if gtin:
            issues.extend(self.check_ean13("g:gtin", gtin, pid, pname))
        img = self.get_field(pv, "g:image_link")
        issues.extend(self.check_image_present("g:image_link", img, pid, pname))
        gpc = self.get_field(pv, "g:google_product_category")
        if not gpc:
            issues.append(ValidationIssue(level="warning", field="g:google_product_category", message="Brak 'g:google_product_category' — Google może nieprawidłowo sklasyfikować produkt", product_id=pid, product_name=pname, rule="missing_recommended"))
        return issues
