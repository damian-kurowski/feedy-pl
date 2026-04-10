"""Static platform information for the feed creation wizard."""

_PLATFORMS: dict[str, dict] = {
    "ceneo": {
        "platform": "ceneo",
        "name": "Ceneo",
        "description": "Ceneo.pl — najwieksza porownywarka cen w Polsce",
        "required_fields": [
            {"field": "@id", "description": "Unikalny identyfikator produktu"},
            {"field": "@url", "description": "URL strony produktu w sklepie"},
            {"field": "@price", "description": "Cena brutto, format numeryczny BEZ waluty (np. 49.99)"},
            {"field": "@avail", "description": "Dostepnosc: 1 (dostepny), 3, 7, 14, 99 (na zamowienie)"},
            {"field": "name", "description": "Pelna nazwa produktu z marka i kluczowymi cechami"},
            {"field": "cat", "description": "Kategoria produktu ze sklepu"},
            {"field": "desc", "description": "Opis produktu"},
        ],
        "recommended_fields": [
            {"field": "producer", "description": "Marka / producent"},
            {"field": "code", "description": "Kod EAN/GTIN"},
            {"field": "imgs", "description": "Zdjecie glowne produktu"},
            {"field": "old_price", "description": "Cena przed obnizka"},
            {"field": "shipping", "description": "Koszt dostawy"},
        ],
        "tips": [
            "Cena NIE moze zawierac waluty — sam numer, np. 49.99",
            "Produkty z kodem EAN sa automatycznie dopasowywane do kart produktow",
            "Dostepnosc musi byc kodem numerycznym: 1, 3, 7, 14 lub 99",
        ],
    },
    "gmc": {
        "platform": "gmc",
        "name": "Google Merchant Center",
        "description": "Google Shopping — najwieksza platforma zakupowa na swiecie",
        "required_fields": [
            {"field": "g:id", "description": "Unikalny identyfikator, max 50 znakow"},
            {"field": "title", "description": "Tytul produktu, max 150 znakow"},
            {"field": "description", "description": "Opis produktu, max 5000 znakow, bez HTML"},
            {"field": "link", "description": "URL strony produktu"},
            {"field": "g:image_link", "description": "URL glownego zdjecia, min 100x100 px"},
            {"field": "g:availability", "description": "in_stock, out_of_stock, preorder lub backorder"},
            {"field": "g:price", "description": "Cena Z waluta, format: 29.99 PLN"},
            {"field": "g:condition", "description": "Stan: new, refurbished, used"},
            {"field": "g:brand / g:gtin", "description": "Marka lub kod EAN — co najmniej jedno wymagane"},
        ],
        "recommended_fields": [
            {"field": "g:google_product_category", "description": "Kategoria z taksonomii Google"},
            {"field": "g:gtin", "description": "Kod EAN-13 — produkty z EAN maja ~40% wiecej wyswietlen"},
            {"field": "g:mpn", "description": "Kod producenta"},
            {"field": "g:product_type", "description": "Twoja kategoria produktu"},
            {"field": "g:additional_image_link", "description": "Dodatkowe zdjecia (do 10)"},
        ],
        "tips": [
            "Cena MUSI zawierac walute: 29.99 PLN",
            "Produkty z poprawnym EAN maja ~40% wiecej wyswietlen",
            "Tytul: Marka + Typ produktu + Kluczowe cechy",
            "Zdjecia min 800x800 px",
        ],
    },
    "facebook": {
        "platform": "facebook",
        "name": "Facebook / Meta Catalog",
        "description": "Meta Commerce — reklamy produktowe na Facebooku i Instagramie",
        "required_fields": [
            {"field": "id", "description": "Unikalny identyfikator, max 100 znakow"},
            {"field": "title", "description": "Tytul, max 200 znakow"},
            {"field": "description", "description": "Opis, max 9999 znakow"},
            {"field": "availability", "description": "in stock, out of stock, available for order, discontinued"},
            {"field": "condition", "description": "new, refurbished, used"},
            {"field": "price", "description": "Cena z waluta: 29.99 PLN"},
            {"field": "link", "description": "URL strony produktu"},
            {"field": "image_link", "description": "URL zdjecia, min 500x500 px"},
            {"field": "brand", "description": "Marka produktu"},
        ],
        "recommended_fields": [
            {"field": "sale_price", "description": "Cena promocyjna"},
            {"field": "additional_image_link", "description": "Dodatkowe zdjecia (do 20)"},
            {"field": "google_product_category", "description": "Meta akceptuje taksonomie Google"},
        ],
        "tips": [
            "Pierwsze 65 znakow tytulu widoczne w reklamach",
            "Zdjecia kwadratowe (1:1) dzialaja najlepiej",
            "Meta akceptuje format XML Google Merchant Center",
        ],
    },
    "allegro": {
        "platform": "allegro",
        "name": "Allegro",
        "description": "Allegro — najwiekszy marketplace w Polsce",
        "required_fields": [
            {"field": "id", "description": "Unikalny identyfikator"},
            {"field": "name", "description": "Nazwa produktu, MAX 75 znakow"},
            {"field": "description", "description": "Opis produktu"},
            {"field": "url", "description": "URL strony produktu"},
            {"field": "price", "description": "Cena produktu"},
            {"field": "category", "description": "Kategoria produktu"},
            {"field": "image", "description": "URL glownego zdjecia, min 600x400 px"},
            {"field": "availability", "description": "Dostepnosc produktu"},
        ],
        "recommended_fields": [
            {"field": "brand", "description": "Marka"},
            {"field": "ean", "description": "Kod EAN"},
            {"field": "condition", "description": "Stan: new, used, refurbished"},
        ],
        "tips": [
            "Tytul MAX 75 znakow — dluzsze sa obcinane",
            "Zdjecia min 600x400 px",
        ],
    },
    "skapiec": {
        "platform": "skapiec",
        "name": "Skapiec",
        "description": "Skapiec.pl — porownywarka cen (grupa Wirtualna Polska)",
        "required_fields": [
            {"field": "id", "description": "Unikalny identyfikator"},
            {"field": "name", "description": "Nazwa produktu"},
            {"field": "url", "description": "URL strony produktu"},
            {"field": "price", "description": "Cena brutto bez waluty"},
            {"field": "category", "description": "Kategoria produktu"},
            {"field": "image", "description": "URL glownego zdjecia"},
            {"field": "description", "description": "Opis produktu"},
            {"field": "producer", "description": "Producent / marka"},
            {"field": "availability", "description": "Dostepnosc"},
        ],
        "recommended_fields": [
            {"field": "ean", "description": "Kod EAN"},
            {"field": "old_price", "description": "Cena przed obnizka"},
            {"field": "shipping", "description": "Koszt dostawy"},
        ],
        "tips": [
            "Format bardzo podobny do Ceneo",
            "Cena bez waluty — tylko liczba",
        ],
    },
    "domodi": {
        "platform": "domodi",
        "name": "Domodi / Homebook",
        "description": "Domodi (moda) i Homebook (dom) — platformy zakupowe",
        "required_fields": [
            {"field": "id", "description": "Unikalny identyfikator"},
            {"field": "name", "description": "Nazwa z marka, typem, kolorem, materialem"},
            {"field": "url", "description": "URL strony produktu"},
            {"field": "price", "description": "Cena brutto bez waluty"},
            {"field": "image", "description": "URL zdjecia"},
            {"field": "category", "description": "Kategoria: Odziez > Sukienki > Koktajlowe"},
            {"field": "producer", "description": "Marka — kluczowa dla mody"},
            {"field": "availability", "description": "Dostepnosc"},
        ],
        "recommended_fields": [
            {"field": "color", "description": "Kolor — uzywany do filtrowania"},
            {"field": "size", "description": "Rozmiar"},
            {"field": "material", "description": "Material"},
            {"field": "gender", "description": "damskie / meskie / unisex"},
            {"field": "old_price", "description": "Cena przed obnizka"},
        ],
        "tips": [
            "Zdjecia na modelu lepiej konwertuja niz flat-lay",
            "Kolor i rozmiar sa kluczowe dla filtrow",
            "Nazwa: Marka + Typ + Kolor + Material",
        ],
    },
}


def get_platform_info(platform: str) -> dict | None:
    return _PLATFORMS.get(platform)


def get_all_platforms() -> list[dict]:
    return [
        {
            "platform": p["platform"],
            "name": p["name"],
            "description": p["description"],
            "required_count": len(p["required_fields"]),
        }
        for p in _PLATFORMS.values()
    ]
