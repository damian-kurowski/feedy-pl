"""Ceneo feed validator."""
from app.services.validators.base import BaseValidator, ValidationIssue

class CeneoValidator(BaseValidator):
    platform = "ceneo"
    id_field = "@id"
    name_field = "name"
    required_fields = ["@id", "@url", "@price", "@avail", "name", "cat", "desc"]
    recommended_fields = ["producer", "code", "imgs", "old_price", "shipping"]

    def validate_product(self, pv: dict, pid: str, pname: str) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for f in self.required_fields:
            issues.extend(self.check_required(pv, f, pid, pname))
        price = self.get_field(pv, "@price")
        if price:
            issues.extend(self.check_price_no_currency("@price", price, pid, pname))
        url = self.get_field(pv, "@url")
        if url:
            issues.extend(self.check_url("@url", url, pid, pname))
        avail = self.get_field(pv, "@avail")
        if avail:
            issues.extend(self.check_enum("@avail", avail, ["1", "3", "7", "14", "99"], pid, pname))
        img_url = self._get_image_url(pv)
        issues.extend(self.check_image_present("imgs", img_url, pid, pname))
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
