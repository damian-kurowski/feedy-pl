"""Google product taxonomy search — lazy-loaded from static file."""

from pathlib import Path

_categories: list[str] = []


def _load() -> None:
    global _categories
    if _categories:
        return
    path = Path(__file__).parent.parent / "data" / "google_taxonomy_pl.txt"
    if not path.exists():
        _categories = []
        return
    lines = path.read_text("utf-8").splitlines()
    _categories = [
        line.split(" - ", 1)[1]
        for line in lines
        if " - " in line and not line.startswith("#")
    ]


def search_google_categories(query: str, limit: int = 10) -> list[str]:
    """Search Google taxonomy categories by query string."""
    _load()
    if not query:
        return _categories[:limit]
    q = query.lower()
    exact = [c for c in _categories if c.lower().startswith(q)]
    contains = [c for c in _categories if q in c.lower() and c not in exact]
    return (exact + contains)[:limit]


def get_all_google_categories() -> list[str]:
    """Return all Google taxonomy categories."""
    _load()
    return _categories
