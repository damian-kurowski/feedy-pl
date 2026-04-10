from app.services.changelog_service import generate_changelog


def _product(name: str, pv: dict) -> dict:
    return {"product_name": name, "product_value": pv}


def test_no_changes():
    old = [_product("A", {"price": "10"})]
    new = [_product("A", {"price": "10"})]
    changes = generate_changelog(old, new)
    assert changes == []


def test_added_product():
    old = [_product("A", {"price": "10"})]
    new = [_product("A", {"price": "10"}), _product("B", {"price": "20"})]
    changes = generate_changelog(old, new)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "added"
    assert changes[0]["product_name"] == "B"


def test_removed_product():
    old = [_product("A", {"price": "10"}), _product("B", {"price": "20"})]
    new = [_product("A", {"price": "10"})]
    changes = generate_changelog(old, new)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "removed"
    assert changes[0]["product_name"] == "B"


def test_price_changed():
    old = [_product("A", {"@price": "10.00"})]
    new = [_product("A", {"@price": "15.00"})]
    changes = generate_changelog(old, new)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "price_changed"
    assert changes[0]["details"]["old_price"] == "10.00"
    assert changes[0]["details"]["new_price"] == "15.00"


def test_price_changed_gmc_format():
    old = [_product("A", {"g:price": "10.00 PLN"})]
    new = [_product("A", {"g:price": "15.00 PLN"})]
    changes = generate_changelog(old, new)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "price_changed"


def test_modified_product():
    old = [_product("A", {"name": "Old Name", "price": "10"})]
    new = [_product("A", {"name": "New Name", "price": "10"})]
    changes = generate_changelog(old, new)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "modified"
    assert "name" in changes[0]["details"]["changed_fields"]


def test_multiple_changes():
    old = [_product("A", {"price": "10"}), _product("B", {"price": "20"})]
    new = [_product("A", {"price": "15"}), _product("C", {"price": "30"})]
    changes = generate_changelog(old, new)
    types = {c["change_type"] for c in changes}
    assert "price_changed" in types
    assert "added" in types
    assert "removed" in types


def test_empty_lists():
    assert generate_changelog([], []) == []


def test_all_new():
    changes = generate_changelog([], [_product("A", {}), _product("B", {})])
    assert len(changes) == 2
    assert all(c["change_type"] == "added" for c in changes)
