# Faza 3: Nowe generatory XML + Taksonomia Google + Mapowanie kategorii per platforma

**Data:** 2026-04-10
**Status:** Draft
**Scope:** Generatory Facebook/Skapiec/Domodi, statyczny plik taksonomii Google PL, rozszerzenie mapowania kategorii na wszystkie platformy

---

## Kontekst

Po Fazach 1-2 Feedy ma walidatory 6 platform, quality score, podgląd zdjęć, overrides per produkt, szablon opisów i wizard. Ale generatory XML obsługują tylko Ceneo, GMC, Allegro i Custom. Brakuje Facebook, Skąpiec, Domodi. Mapowanie kategorii działa tylko dla Ceneo.

## Cele

1. Nowe generatory XML: Facebook (reuse GMC), Skąpiec, Domodi
2. Taksonomia Google jako statyczny plik z wyszukiwarką
3. Mapowanie kategorii dostępne dla wszystkich platform z odpowiednimi sugestiami

---

## 1. Nowe generatory XML

### Facebook / Meta Catalog

Meta akceptuje format RSS 2.0 z namespace `g:` — identyczny jak Google Merchant Center. Nie tworzymy osobnego generatora.

`generate_facebook_xml` = alias na `generate_gmc_xml`. W `public_feed.py` typ `"facebook"` wywołuje `generate_gmc_xml()`.

### Skąpiec

Nowa funkcja `generate_skapiec_xml(products, category_mapping)` w `feed_generator.py`.

Format XML:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<offers>
  <offer>
    <id>123</id>
    <name>Nazwa produktu</name>
    <url>https://shop.pl/p/123</url>
    <price>49.99</price>
    <category>Elektronika</category>
    <image>https://shop.pl/img.jpg</image>
    <description>Opis produktu</description>
    <producer>Marka</producer>
    <availability>1</availability>
    <ean>5901234123457</ean>
  </offer>
</offers>
```

Pola mapowane przez `SKAPIEC_TEMPLATE`:
- `id` ← `g:id` / `@id` / `id`
- `name` ← `title` / `name`
- `url` ← `link` / `@url` / `url`
- `price` ← `g:price` / `@price` / `price` (transform: `format_price`)
- `category` ← `g:product_type` / `cat` / `category`
- `image` ← `g:image_link` / `image` / `img`
- `description` ← `description` / `desc` (transform: `strip_html`)
- `producer` ← `g:brand` / `brand` / `producer`
- `availability` ← `g:availability` / `@avail` (transform: `map_availability`)
- `ean` ← `g:gtin` / `ean` / `code`

### Domodi / Homebook

Nowa funkcja `generate_domodi_xml(products, category_mapping)` — identyczna struktura jak Skąpiec + dodatkowe pola fashion:

```xml
  <offer>
    ... (same as Skapiec) ...
    <color>Czerwony</color>
    <size>M</size>
    <material>Bawełna</material>
    <gender>damskie</gender>
  </offer>
```

`DOMODI_TEMPLATE` rozszerza `SKAPIEC_TEMPLATE` o:
- `color` ← `color`
- `size` ← `size`
- `material` ← `material`
- `gender` ← `gender`

### Szablony w templates.py

Nowe szablony: `SKAPIEC_TEMPLATE`, `DOMODI_TEMPLATE`.
Nowe funkcje: `get_skapiec_structure_rows(feed_out_id)`, `get_domodi_structure_rows(feed_out_id)`.

### Integracja

**`public_feed.py`** — dodanie do switch:
```python
elif feed_out.type == "facebook":
    xml_bytes = generate_gmc_xml(product_dicts)
elif feed_out.type == "skapiec":
    xml_bytes = generate_skapiec_xml(product_dicts, category_mapping=feed_out.category_mapping)
elif feed_out.type == "domodi":
    xml_bytes = generate_domodi_xml(product_dicts, category_mapping=feed_out.category_mapping)
```

**`feeds_out.py`** — auto-populate structure dla nowych szablonów:
```python
elif data.template == "skapiec":
    for row in get_skapiec_structure_rows(feed_out.id): ...
elif data.template == "domodi":
    for row in get_domodi_structure_rows(feed_out.id): ...
```

---

## 2. Taksonomia Google

### Plik statyczny

`backend/app/data/google_taxonomy_pl.txt` — pobrany z Google:
https://www.google.com/basepages/producttype/taxonomy-with-ids.pl-PL.txt

Format (każda linia):
```
1 - Zwierzęta i artykuły dla zwierząt
3237 - Zwierzęta i artykuły dla zwierząt > Artykuły dla zwierząt
...
```

~5800 linii, ~500KB. Ładowany do pamięci (lazy, raz przy pierwszym użyciu).

### Serwis `google_taxonomy.py`

```python
_categories: list[str] = []  # lazy loaded

def _load():
    global _categories
    if _categories:
        return
    path = Path(__file__).parent.parent / "data" / "google_taxonomy_pl.txt"
    lines = path.read_text("utf-8").splitlines()
    _categories = [line.split(" - ", 1)[1] for line in lines if " - " in line]

def search_google_categories(query: str, limit: int = 10) -> list[str]:
    _load()
    q = query.lower()
    # Exact prefix match first, then contains
    exact = [c for c in _categories if c.lower().startswith(q)]
    contains = [c for c in _categories if q in c.lower() and c not in exact]
    return (exact + contains)[:limit]
```

### Endpoint

`GET /api/feeds-out/google-categories?q=folie&limit=10`

Dodany do `feeds_out.py` obok istniejącego `/ceneo-categories`.

---

## 3. Mapowanie kategorii per platforma

### Backend

Brak zmian modelu — `FeedOut.category_mapping` (JSONB) już istnieje i jest używany przez generatory. Wystarczy że nowe generatory (Skąpiec, Domodi) też go obsługują.

### Frontend

**Zmiana w `FeedOutDetailView.vue`:**

1. Usunięcie `v-if="feedOut.type === 'ceneo'"` z sekcji "Mapowanie kategorii" — widoczna dla wszystkich typów
2. Logika sugestii zależy od typu feedu:
   - Typ `gmc` lub `facebook` → sugestie z `/google-categories?q=...`
   - Typ `ceneo`, `skapiec`, `domodi`, `allegro` → sugestie z `/ceneo-categories?q=...` (obecny mechanizm)
3. Zmiana etykiety sekcji: "Mapowanie kategorii" (bez "Ceneo")

### Nowy endpoint store

W `feedsOut.ts` dodanie:
```typescript
async function getGoogleCategories(q: string) {
  const { data } = await api.get('/feeds-out/google-categories', { params: { q } })
  return data.categories
}
```

---

## Wpływ na istniejący kod

### Backend — nowe pliki
- `backend/app/data/google_taxonomy_pl.txt` — statyczny plik taksonomii (~500KB)
- `backend/app/services/google_taxonomy.py` — lazy-load + search
- `backend/tests/test_google_taxonomy.py` — testy wyszukiwania
- `backend/tests/test_skapiec_generator.py` — testy generatora Skąpiec
- `backend/tests/test_domodi_generator.py` — testy generatora Domodi

### Backend — modyfikowane pliki
- `backend/app/services/feed_generator.py` — nowe funkcje: `generate_skapiec_xml`, `generate_domodi_xml`
- `backend/app/services/templates.py` — nowe szablony + structure rows
- `backend/app/routers/feeds_out.py` — nowy endpoint google-categories, auto-populate dla nowych szablonów
- `backend/app/routers/public_feed.py` — nowe typy w switch

### Frontend — modyfikowane pliki
- `frontend/src/views/FeedOutDetailView.vue` — mapowanie kategorii per platforma
- `frontend/src/stores/feedsOut.ts` — nowa metoda getGoogleCategories

### Brak migracji bazy danych
