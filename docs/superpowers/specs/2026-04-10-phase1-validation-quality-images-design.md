# Faza 1: Walidacja per platforma + Feed Quality Score + Podgląd zdjęć

**Data:** 2026-04-10
**Status:** Draft
**Scope:** Backend validators, quality scoring, image previews in UI

---

## Kontekst

Feedy to narzędzie do zarządzania feedami produktowymi e-commerce. Obecna walidacja jest podstawowa (Ceneo: id/url/price, GMC: title/link/price). Użytkownicy nie widzą co brakuje w ich feedach, nie mają podglądu zdjęć produktów, i nie mają wskaźnika jakości feedu.

Faza 1 to fundament — bez niej użytkownik nie wie czy jego feed jest poprawny dla danej platformy.

## Cele

1. Pełna walidacja feedów wyjściowych zgodnie z wymaganiami 6 platform
2. Feed Quality Score — jeden wskaźnik jakości feedu (0-100%)
3. Podgląd zdjęć produktów w listach i mappingu

---

## 1. Walidacja per platforma

### Architektura

Nowy moduł `backend/app/services/validators/` zastępujący obecny `feed_validator.py`:

```
validators/
  __init__.py          # eksportuje validate_feed(), registry walidatorów
  base.py              # BaseValidator, ValidationIssue dataclass, wspólne reguły
  ceneo.py             # CeneoValidator
  gmc.py               # GmcValidator
  facebook.py          # FacebookValidator
  allegro.py           # AllegroValidator
  skapiec.py           # SkapiecValidator
  domodi.py            # DomodiValidator
```

### Wspólny interfejs

```python
@dataclass
class ValidationIssue:
    level: str          # "error" | "warning" | "info"
    field: str          # np. "g:price", "image_link"
    message: str        # czytelny opis problemu
    product_id: str     # identyfikator produktu w feedzie
    product_name: str   # nazwa produktu dla czytelności
    rule: str           # identyfikator reguły, np. "required_field", "format_price"

@dataclass
class FieldCoverage:
    field: str
    required: bool
    filled: int
    total: int
    percent: float

@dataclass
class ValidationResult:
    platform: str
    total_products: int
    issues: list[ValidationIssue]
    field_coverage: list[FieldCoverage]
    quality_score: int          # 0-100
    quality_label: str          # "Doskonały" / "Dobry" / "Wymaga poprawy" / "Słaby"
    quality_breakdown: dict     # required_fields_score, recommended_fields_score, format_compliance_score
```

### Dane wejściowe walidatora

Walidator operuje na liście produktów (`list[dict]`) — `product_value` z modelu `ProductIn` po zastosowaniu template'u i rules. Dane pobierane z bazy przez `feed_in_id` powiązany z feedem wyjściowym. Walidacja następuje na danych transformowanych (po template + rules), nie na surowym XML ani na raw product_value.

### BaseValidator (wspólne reguły)

- `validate_url(value)` — sprawdza format URL, preferuje HTTPS
- `validate_price_with_currency(value)` — format `XX.XX PLN` (Google, Facebook)
- `validate_price_no_currency(value)` — format `XX.XX` bez waluty (Ceneo, Skąpiec)
- `validate_ean13(value)` — checksum EAN-13 (algorytm modulo 10)
- `validate_max_length(value, max_len)` — sprawdza limit znaków
- `validate_required(product, field_name)` — sprawdza czy pole istnieje i nie jest puste
- `validate_image_url(value)` — sprawdza format URL, ostrzeżenie jeśli HTTP

### Reguły per platforma

#### Google Merchant Center (GmcValidator)

**Errors (wymagane):**
- `g:id` — wymagane, max 50 znaków
- `g:title` — wymagane, max 150 znaków
- `g:description` — wymagane, max 5000 znaków
- `g:link` — wymagane, poprawny URL
- `g:image_link` — wymagane, poprawny URL
- `g:availability` — wymagane, wartość: `in_stock` | `out_of_stock` | `preorder` | `backorder`
- `g:price` ��� wymagane, format `XX.XX CCC` (waluta ISO 4217)
- `g:condition` — wymagane, wartość: `new` | `refurbished` | `used`
- `g:brand` lub `g:gtin` — co najmniej jedno wymagane

**Warunkowo wymagane (odzież — wykrywane po google_product_category):**
- `g:color`
- `g:size`
- `g:gender` — `male` | `female` | `unisex`
- `g:age_group` — `newborn` | `infant` | `toddler` | `kids` | `adult`

**Warnings (zalecane):**
- `g:google_product_category` — brak = gorsza klasyfikacja
- `g:mpn` — brak gdy brak GTIN
- `g:additional_image_link` — brak dodatkowych zdjęć
- `g:gtin` checksum niepoprawny
- Zdjęcie główne < 800x800 px (info, nie sprawdzane w runtime — uwaga w docs)
- Tekst promocyjny w tytule (regex: "free shipping", "kup teraz", "promocja", "najlepszy")
- ALL CAPS w tytule

#### Ceneo (CeneoValidator)

**Errors:**
- `id` (atrybut `@id`) — wymagane
- `url` (atrybut `@url`) — wymagane, poprawny URL
- `price` (atrybut `@price`) — wymagane, format numeryczny BEZ waluty
- `name` — wymagane
- `cat` — wymagane
- `desc` — wymagane
- `avail` (atrybut `@avail`) — wymagane, wartość: `1` | `3` | `7` | `14` | `99`

**Warnings:**
- `producer` — brak producenta
- `code` (EAN) — brak EAN
- `img` / `imgs/main/@url` — brak zdjęcia
- `old_price` — brak (nie pokaże przekreślonej ceny)
- `shipping` — brak kosztu dostawy
- Rozbieżność ceny z `old_price` (old_price <= price)

#### Facebook / Meta Catalog (FacebookValidator)

**Errors:**
- `id` — wymagane, max 100 znaków
- `title` — wymagane, max 200 znaków
- `description` — wymagane, max 9999 znaków
- `availability` — wymagane: `in stock` | `out of stock` | `available for order` | `discontinued`
- `condition` — wymagane: `new` | `refurbished` | `used`
- `price` — wymagane, format `XX.XX CCC`
- `link` — wymagane, poprawny URL
- `image_link` — wymagane
- `brand` — wymagane

**Warnings:**
- `sale_price` — brak
- `additional_image_link` — brak (do 20 dozwolone)
- `google_product_category` lub `fb_product_category` — brak
- Zdjęcie < 600x600 px

#### Allegro (AllegroValidator)

**Errors:**
- `id` — wymagane
- `name` — wymagane, max 75 znaków
- `description` — wymagane
- `url` — wymagane
- `price` — wymagane
- `category` — wymagane
- `image` — wymagane
- `availability` — wymagane

**Warnings:**
- `brand` — brak
- `ean` — brak
- `condition` — brak
- Tytuł > 75 znaków (Allegro obcina)

#### Skąpiec (SkapiecValidator)

**Errors:**
- `id` — wymagane
- `name` — wymagane
- `url` — wymagane, poprawny URL
- `price` — wymagane, format numeryczny bez waluty
- `category` — wymagane
- `image` — wymagane
- `description` — wymagane
- `producer` — wymagane
- `availability` — wymagane

**Warnings:**
- `ean` — brak
- `old_price` — brak
- `shipping` — brak

#### Domodi / Homebook (DomodiValidator)

**Errors:**
- `id` — wymagane
- `name` — wymagane
- `url` — wymagane
- `price` — wymagane
- `image` — wymagane
- `category` — wymagane
- `producer` — wymagane
- `availability` — wymagane

**Warnings (fashion-specific):**
- `color` — brak
- `size` — brak
- `material` — brak
- `gender` — brak
- `old_price` — brak
- Dodatkowe zdjęcia — brak (lifestyle shots preferowane)

### Endpoint

Rozbudowa istniejącego `GET /api/feeds-out/{id}/validate`.

**Response:**

```json
{
  "platform": "gmc",
  "total_products": 45,
  "quality_score": 78,
  "quality_label": "Dobry",
  "quality_breakdown": {
    "required_fields_score": 85,
    "recommended_fields_score": 60,
    "format_compliance_score": 90
  },
  "summary": {
    "errors": 3,
    "warnings": 12,
    "info": 5
  },
  "field_coverage": [
    {"field": "g:id", "required": true, "filled": 45, "total": 45, "percent": 100.0},
    {"field": "g:gtin", "required": false, "filled": 12, "total": 45, "percent": 26.7}
  ],
  "issues": [
    {
      "level": "error",
      "field": "g:price",
      "message": "Brak kodu waluty w cenie. Wymagany format: '29.99 PLN'",
      "product_id": "69",
      "product_name": "Folia przeciwsłoneczna R20 Silver",
      "rule": "format_price_currency"
    }
  ]
}
```

### Migracja

Obecny `feed_validator.py` z funkcjami `validate_ceneo_xml()` i `validate_gmc_xml()` zostaje zastąpiony nową strukturą. Stary plik usunięty. Istniejący endpoint `/validate` zachowuje ten sam URL, zmienia się tylko wewnętrzna implementacja i format odpowiedzi.

---

## 2. Feed Quality Score

### Obliczanie

Quality Score obliczany w runtime przy walidacji (nie przechowywany w bazie). Formuła:

```python
def calculate_quality_score(issues: list[ValidationIssue], field_coverage: list[FieldCoverage]) -> int:
    score = 100.0

    # Kary za issues
    error_count = sum(1 for i in issues if i.level == "error")
    warning_count = sum(1 for i in issues if i.level == "warning")
    
    score -= error_count * 5   # -5 za każdy error
    score -= warning_count * 1  # -1 za każdy warning

    # Bonus za pokrycie pól zalecanych (0-10 punktów)
    recommended = [f for f in field_coverage if not f.required]
    if recommended:
        avg_coverage = sum(f.percent for f in recommended) / len(recommended)
        score += (avg_coverage / 100) * 10

    return max(0, min(100, int(score)))
```

### Breakdown

- `required_fields_score` — procent produktów z kompletnymi polami wymaganymi
- `recommended_fields_score` — średnie pokrycie pól zalecanych
- `format_compliance_score` — procent produktów bez błędów formatowania

### Kategorie

| Zakres | Label | Kolor (Tailwind) |
|--------|-------|-------------------|
| 90-100 | Doskonały | `text-green-600`, `bg-green-50` |
| 70-89 | Dobry | `text-yellow-600`, `bg-yellow-50` |
| 50-69 | Wymaga poprawy | `text-orange-600`, `bg-orange-50` |
| 0-49 | Słaby | `text-red-600`, `bg-red-50` |

### Frontend — sekcja "Jakość feedu" w FeedOutDetailView

Nowa sekcja na górze strony feedu wyjściowego (przed mappingiem):

1. **Wskaźnik kołowy** — duży okrąg z wynikiem (np. "78%") w odpowiednim kolorze
2. **Podsumowanie** — "3 błędy krytyczne | 12 ostrzeżeń | 5 informacji"
3. **Breakdown** — 3 mini-barki: Wymagane pola / Zalecane pola / Formaty
4. **Pokrycie pól** — lista pól z progress barami (wymagane = czerwone jeśli < 100%, zalecane = szare)
5. **Lista issues** z tabami: Błędy / Ostrzeżenia / Wszystko
6. Każdy issue pokazuje: ikonę poziomu, pole, komunikat, nazwę produktu

### Frontend — mini-badge na DashboardView

Na liście feedów wyjściowych w Dashboard — przy każdym feedzie kolorowe kółko z quality score:
- Kółko 32x32 z liczbą, kolor tła wg kategorii
- Hover: tooltip "Jakość feedu: 78% — Dobry"

Dane pobierane leniwie (nie blokują ładowania dashboardu). Osobny request per feed na `/validate`, wynik cache'owany w Pinia store na 5 minut.

---

## 3. Podgląd zdjęć produktów

### Podejście

Frontend-driven — zdjęcia wyświetlane bezpośrednio z URL-i które są w `product_value`. Brak pobierania zdjęć na backend (to Faza 4 — upload).

### Wyciąganie URL-i zdjęć z product_value

Frontend helper `extractImageUrls(productValue: Record<string, unknown>)`:

Szuka zdjęć w znanych ścieżkach:
- `g:image_link` (Google)
- `image_link` (Facebook)
- `@url` w `imgs/main` (Ceneo Shoper)
- `img` (Ceneo/Skąpiec)
- `image` (Allegro/Domodi)
- `imgs` → iteracja po dzieciach (dodatkowe zdjęcia)
- `additional_image_link` (Google/Facebook)

Zwraca `{ main: string | null, additional: string[] }`.

### Frontend — lista produktów w FeedInDetailView

Rozbudowa komponentu `ProductPreview`. Zamiast samej nazwy:

```
┌──────────┬─────────────────────────────────────────┬─────────────┐
│ [miniatura│ Folia przeciwsłoneczna R20 Silver      │ 76.20 PLN   │
│  48x48]   │ cat: Folie przeciwsłoneczne wewnętrzne │ avail: 1    │
├──────────┼─────────────────────────────────────────┼─────────────┤
│ [miniatura│ Folia matowa mleczna White Matte        │ 23.79 PLN   ���
│  48x48]   │ cat: Folie matowe kolory               │ avail: 1    │
└──────────┴─────────────��───────────────────────────┴─────────────┘
```

- Miniatura 48x48 z `object-cover`, zaokrąglone rogi
- Fallback na placeholder ikonę gdy brak zdjęcia lub URL zwraca błąd (`onerror`)
- Klik na miniaturę — modal/lightbox z pełnym zdjęciem + lista dodatkowych zdjęć

### Frontend — podgląd w MappingTable (feed wyjściowy)

W kolumnie "Podgląd" komponentu `MappingTable` — jeśli `path_in` wskazuje na pole ze zdjęciem (np. `g:image_link`, `img`, `imgs/main/@url`), zamiast tekstu URL-a pokazuje:
- Miniaturkę 32x32 inline
- Hover: powiększenie do 200x200

### Walidacja zdjęć w walidatorach

Reguły dotyczące zdjęć (w ramach walidatorów z sekcji 1):

**Wszystkie platformy:**
- Error: brak głównego zdjęcia (pole puste lub brak pola)
- Warning: URL po HTTP zamiast HTTPS

**Per platforma (warnings):**
- Google: zdjęcie zalecane >= 800x800 (info — nie sprawdzamy wymiarów w runtime, tylko komunikat)
- Facebook: zdjęcie zalecane >= 600x600
- Amazon: zdjęcie wymagane >= 1000x1000
- Allegro: zdjęcie wymagane >= 600x400

Wymiary nie są sprawdzane w runtime (wymagałoby pobierania zdjęć). Zamiast tego:
- Walidator sprawdza czy URL istnieje (pole niepuste)
- W przyszłości (Faza 4) — asynchroniczna walidacja wymiarów z cache w Redis

---

## Wpływ na istniejący kod

### Backend — zmiany

1. **Usunięcie** `backend/app/services/feed_validator.py` — zastąpiony przez `validators/`
2. **Modyfikacja** `backend/app/routers/feeds_out.py` — endpoint `/validate` zwraca nowy format
3. **Nowy moduł** `backend/app/services/validators/` — 8 plików

### Frontend ��� zmiany

1. **Modyfikacja** `frontend/src/views/FeedOutDetailView.vue` — nowa sekcja "Jakość feedu"
2. **Modyfikacja** `frontend/src/views/DashboardView.vue` — mini-badge quality score
3. **Modyfikacja** `frontend/src/components/ProductPreview.vue` — miniatury zdjęć
4. **Modyfikacja** `frontend/src/components/MappingTable.vue` — podgląd zdjęć w mappingu
5. **Nowy komponent** `frontend/src/components/QualityScore.vue` — wskaźnik kołowy
6. **Nowy komponent** `frontend/src/components/ValidationIssues.vue` — lista issues
7. **Nowy komponent** `frontend/src/components/ImagePreview.vue` — lightbox zdjęć
8. **Nowy helper** `frontend/src/utils/imageExtractor.ts` — wyciąganie URL-i zdjęć
9. **Modyfikacja** `frontend/src/stores/feedsOut.ts` — nowy typ `ValidationResult`, cache

### Migracja bazy danych

Brak — żadne nowe tabele ani kolumny. Quality Score obliczany w runtime.

---

## Poza zakresem (przyszłe fazy)

- Upload zdjęć na serwer Feedy (Faza 4)
- Sprawdzanie wymiarów zdjęć w runtime (Faza 4)
- Override wartości per produkt (Faza 2)
- AI rewriting opisów (Faza 4)
- Nowe szablony platform (Faza 3)
- Historia zmian feedu (Faza 4)
