from app.services.google_taxonomy import search_google_categories, get_all_google_categories


def test_search_returns_results():
    results = search_google_categories("Elektronika")
    assert len(results) > 0
    assert any("Elektronika" in r for r in results)


def test_search_case_insensitive():
    results = search_google_categories("elektronika")
    assert len(results) > 0


def test_search_limit():
    results = search_google_categories("", limit=5)
    assert len(results) <= 5


def test_search_no_results():
    results = search_google_categories("xyznonexistent12345")
    assert results == []


def test_get_all_categories():
    cats = get_all_google_categories()
    assert len(cats) > 0
    assert all(isinstance(c, str) for c in cats)


def test_search_prefix_first():
    results = search_google_categories("Odzież", limit=20)
    # Prefix matches should come before contains matches
    if len(results) >= 2:
        assert results[0].startswith("Odzież")
