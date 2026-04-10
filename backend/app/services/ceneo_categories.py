"""Ceneo category dictionary and suggestion matching for category mapping."""

from __future__ import annotations

CENEO_CATEGORIES = [
    "Telefony i akcesoria > Smartfony i telefony",
    "Telefony i akcesoria > Etui i pokrowce",
    "Komputery > Laptopy",
    "Komputery > Tablety",
    "Komputery > Monitory",
    "Komputery > Drukarki",
    "Komputery > Podzespoły komputerowe",
    "RTV i AGD > Telewizory",
    "RTV i AGD > Lodówki",
    "RTV i AGD > Pralki",
    "RTV i AGD > Odkurzacze",
    "RTV i AGD > Ekspresy do kawy",
    "Zdrowie i uroda > Perfumy",
    "Zdrowie i uroda > Kosmetyki",
    "Zdrowie i uroda > Suplementy diety",
    "Dom i ogród > Meble",
    "Dom i ogród > Oświetlenie",
    "Dom i ogród > Narzędzia",
    "Dom i ogród > Ogród",
    "Dom i ogród > Dekoracje",
    "Motoryzacja > Opony",
    "Motoryzacja > Oleje silnikowe",
    "Motoryzacja > Części samochodowe",
    "Moda > Buty damskie",
    "Moda > Buty męskie",
    "Moda > Odzież damska",
    "Moda > Odzież męska",
    "Moda > Torebki",
    "Sport i turystyka > Rowery",
    "Sport i turystyka > Bieżnie",
    "Sport i turystyka > Suplementy sportowe",
    "Dziecko > Wózki dziecięce",
    "Dziecko > Foteliki samochodowe",
    "Dziecko > Zabawki",
    "Supermarket > Kawa",
    "Supermarket > Herbata",
    "Supermarket > Karma dla zwierząt",
    "Kultura i rozrywka > Książki",
    "Kultura i rozrywka > Gry",
    "Kultura i rozrywka > Filmy",
    "Elektronika > Słuchawki",
    "Elektronika > Głośniki",
    "Elektronika > Smartwatche",
    "Elektronika > Aparaty fotograficzne",
    "Elektronika > Konsole",
    "Budownictwo > Folie budowlane",
    "Budownictwo > Farby",
    "Budownictwo > Kleje",
    "Budownictwo > Okna",
    "Budownictwo > Drzwi",
]


def suggest_ceneo_category(product_category: str, limit: int = 5) -> list[str]:
    """Suggest matching Ceneo categories based on text similarity.

    Uses simple keyword matching -- no ML needed for MVP.
    """
    if not product_category:
        return CENEO_CATEGORIES[:limit]

    query = product_category.lower().strip()
    words = query.split()

    scored: list[tuple[int, str]] = []
    for cat in CENEO_CATEGORIES:
        cat_lower = cat.lower()
        score = 0
        for word in words:
            if len(word) < 3:
                continue
            if word in cat_lower:
                score += 10
            # Partial match
            for cat_word in cat_lower.split():
                if word[:4] in cat_word or cat_word[:4] in word:
                    score += 3
        if score > 0:
            scored.append((score, cat))

    scored.sort(key=lambda x: -x[0])
    return [cat for _, cat in scored[:limit]]


def get_all_categories() -> list[str]:
    """Return the full list of Ceneo categories."""
    return CENEO_CATEGORIES
