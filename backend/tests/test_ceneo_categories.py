from app.services.ceneo_categories import suggest_ceneo_category, get_all_categories


def test_get_all_categories():
    cats = get_all_categories()
    assert len(cats) > 20


def test_suggest_folie():
    suggestions = suggest_ceneo_category("folie")
    assert any("Foli" in s for s in suggestions)


def test_suggest_telefon():
    suggestions = suggest_ceneo_category("telefon")
    assert any("Telefon" in s for s in suggestions)


def test_suggest_empty():
    suggestions = suggest_ceneo_category("")
    assert len(suggestions) > 0


def test_suggest_limit():
    suggestions = suggest_ceneo_category("folie", limit=3)
    assert len(suggestions) <= 3
