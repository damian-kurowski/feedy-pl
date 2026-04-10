from app.services.title_optimizer import optimize_title, optimize_titles_bulk


def test_optimize_adds_brand():
    result = optimize_title("Folia okienna", brand="LiteSolar")
    assert result.startswith("LiteSolar")


def test_optimize_doesnt_duplicate_brand():
    result = optimize_title("LiteSolar Folia okienna", brand="LiteSolar")
    assert result.count("LiteSolar") == 1


def test_optimize_strips_html():
    result = optimize_title("<b>Folia</b> okienna")
    assert "<b>" not in result


def test_optimize_truncates():
    result = optimize_title("A" * 200, max_length=50)
    assert len(result) <= 50


def test_optimize_adds_color():
    result = optimize_title("Folia okienna", color="srebrna")
    assert "srebrna" in result


def test_optimize_bulk():
    products = [
        {"product_value": {"title": "Folia", "g:brand": "EU"}},
        {"product_value": {"name": "Płyn", "g:brand": "Solar"}},
    ]
    result = optimize_titles_bulk(products)
    assert len(result) == 2
    assert "EU" in (result[0]["product_value"].get("title") or "")


def test_optimize_empty_title():
    assert optimize_title("") == ""
    assert optimize_title(None) == ""
