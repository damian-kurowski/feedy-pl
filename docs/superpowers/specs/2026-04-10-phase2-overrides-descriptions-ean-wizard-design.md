# Faza 2: Product Overrides + Szablon opisów + GTIN/EAN Dashboard + Kreator

**Data:** 2026-04-10
**Status:** Draft
**Scope:** Per-product overrides w feedach wyjściowych, szablon opisów jako reguła, wizualizacja EAN, rozbudowa kreatora feedu wyjściowego

---

## Kontekst

Po Fazie 1 Feedy ma pełną walidację 6 platform, quality score i podgląd zdjęć. Brakuje możliwości edycji pojedynczych produktów w feedzie wyjściowym, dedykowanego edytora opisów, wizualizacji pokrycia EAN i instrukcji przy tworzeniu feedu.

## Cele

1. Override wartości per produkt w feedzie wyjściowym (źródło nienaruszone)
2. Szablon opisów z placeholderami jako nowy typ reguły
3. Wizualizacja pokrycia GTIN/EAN w dashboardzie jakości
4. Kreator feedu wyjściowego z informacjami o wymaganych polach per platforma

---

## 1. Product Overrides

### Nowa tabela `product_override`

```sql
CREATE TABLE data.product_override (
    id BIGSERIAL PRIMARY KEY,
    feed_out_id INTEGER NOT NULL REFERENCES config.feed_out(id) ON DELETE CASCADE,
    product_in_id BIGINT NOT NULL REFERENCES data.product_in(id) ON DELETE CASCADE,
    field_overrides JSONB NOT NULL DEFAULT '{}',
    excluded BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (feed_out_id, product_in_id)
);
```

- `field_overrides` = `{"name": "Nowa nazwa", "desc": "Zmieniony opis"}` — tylko nadpisane pola, reszta z oryginału
- `excluded` = true → produkt pomijany w feedzie wyjściowym
- Unique constraint gwarantuje jeden override per produkt per feed wyjściowy
- CASCADE delete — usunięcie feedu lub produktu czyści overrides

### Model SQLAlchemy

Nowy plik `backend/app/models/product_override.py`:

```python
class ProductOverride(Base):
    __tablename__ = "product_override"
    __table_args__ = (
        UniqueConstraint("feed_out_id", "product_in_id"),
        {"schema": "data"},
    )
    id = Column(BigInteger, primary_key=True)
    feed_out_id = Column(Integer, ForeignKey("config.feed_out.id", ondelete="CASCADE"), nullable=False)
    product_in_id = Column(BigInteger, ForeignKey("data.product_in.id", ondelete="CASCADE"), nullable=False)
    field_overrides = Column(JSONB, nullable=False, default=dict)
    excluded = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Migracja Alembic

Nowa migracja dodająca tabelę `data.product_override`.

### API Endpoints

Dodane do `backend/app/routers/feeds_out.py`:

**`GET /api/feeds-out/{id}/products`**

Zwraca listę produktów z feedu wejściowego powiązanego z tym feedem wyjściowym, z zastosowanymi overrides:

```json
[
  {
    "id": 1,
    "product_name": "Folia R20 Silver",
    "product_value": {"@id": "69", "@price": "76.20", "name": "Folia R20 Silver", ...},
    "override": null,
    "status": "original"
  },
  {
    "id": 2,
    "product_name": "Folia matowa",
    "product_value": {"@id": "109", "@price": "23.79", "name": "Folia matowa zmieniona", ...},
    "override": {"field_overrides": {"name": "Folia matowa zmieniona"}, "excluded": false},
    "status": "modified"
  },
  {
    "id": 3,
    "product_name": "Folia biała",
    "product_value": {...},
    "override": {"field_overrides": {}, "excluded": true},
    "status": "excluded"
  }
]
```

Status: `"original"` (brak override), `"modified"` (ma field_overrides), `"excluded"` (excluded=true).

Endpoint obsługuje opcjonalny query param `?search=folia` do filtrowania po nazwie.

**`PUT /api/feeds-out/{id}/products/{product_id}/override`**

Upsert override. Body:

```json
{
  "field_overrides": {"name": "Nowa nazwa", "desc": "Nowy opis"},
  "excluded": false
}
```

Zwraca utworzony/zaktualizowany override.

**`DELETE /api/feeds-out/{id}/products/{product_id}/override`**

Usuwa override (przywraca oryginał). Zwraca 204.

### Integracja z generatorem feedu

Modyfikacja `backend/app/routers/public_feed.py` i endpoint `/validate` w `feeds_out.py`:

1. Po pobraniu produktów z `ProductIn`, pobierz overrides z `ProductOverride` dla danego `feed_out_id`
2. Dla każdego produktu z overridem: `merged = {**product_value, **field_overrides}`
3. Pomiń produkty z `excluded=True`
4. Potem zastosuj reguły (rules engine)

Nowa funkcja pomocnicza `apply_overrides(products, overrides)` w nowym pliku `backend/app/services/override_service.py`.

### Schemat Pydantic

Nowy plik `backend/app/schemas/product_override.py`:

```python
class ProductOverrideUpsert(BaseModel):
    field_overrides: dict = {}
    excluded: bool = False

class ProductWithOverride(BaseModel):
    id: int
    product_name: str
    product_value: dict
    override: dict | None
    status: str  # "original" | "modified" | "excluded"
```

### Frontend — sekcja "Produkty" w FeedOutDetailView

Nowa sekcja między "Reguły filtrowania" a "Link do feeda":

**Tabela produktów:**
- Kolumny: Zdjęcie (miniatura 40x40) | Nazwa | Cena | Status (badge) | Akcje (przycisk "Edytuj")
- Wyszukiwarka na górze (filtruje po nazwie)
- Paginacja lub wirtualny scroll (jeśli >50 produktów, pokaż pierwsze 50 z "Pokaż więcej")
- Badge statusu: zielony "Oryginał", żółty "Zmieniony", czerwony "Wykluczony"

**Modal edycji (komponent `ProductOverrideModal.vue`):**
- Nagłówek: nazwa produktu + miniatura zdjęcia
- Lista pól z product_value:
  - Lewa kolumna: nazwa pola
  - Środkowa kolumna: oryginalna wartość (szary, readonly)
  - Prawa kolumna: input do nadpisania (puste = brak override)
- Checkbox "Wyklucz z feedu wyjściowego"
- Przyciski: "Zapisz" | "Przywróć oryginał" (DELETE) | "Anuluj"

Nowe komponenty:
- `frontend/src/components/FeedOutProducts.vue` — tabela produktów z wyszukiwarką
- `frontend/src/components/ProductOverrideModal.vue` — modal edycji

---

## 2. Szablon opisów

### Nowy typ reguły w rules_engine.py

Typ: `description_template`

```json
{
  "type": "description_template",
  "field": "desc",
  "template": "Kup {name} marki {brand}. {desc}. Kategoria: {cat}."
}
```

**Logika:**
- Iteruje po product_value, zamienia `{klucz}` na wartość
- Obsługuje klucze z prefixami: `{@price}`, `{g:brand}`
- Niezamienione placeholdery (brak klucza w product_value) → usuwane
- Podwójne spacje → pojedyncze
- Wynik zapisywany do pola `field` (domyślnie `desc`)

### Implementacja

Dodanie do `backend/app/services/rules_engine.py`:

```python
def _apply_description_template(products: list[dict], rule: dict) -> list[dict]:
    field = rule.get("field", "desc")
    template = rule.get("template", "")
    for product in products:
        pv = product["product_value"]
        result = template
        for key, val in pv.items():
            if isinstance(val, str):
                result = result.replace(f"{{{key}}}", val.strip())
        result = re.sub(r"\{[^}]+\}", "", result)
        result = re.sub(r"  +", " ", result).strip()
        pv[field] = result
    return products
```

Dodanie do głównego dispatchera w `apply_rules()`:
```python
elif rule_type == "description_template":
    products = _apply_description_template(products, rule)
```

### Frontend

W sekcji "Reguły filtrowania" na `FeedOutDetailView`:

Nowy typ w `ruleTypeLabels`:
```typescript
description_template: 'Szablon opisu'
```

Formularz po wybraniu:
- Dropdown "Pole docelowe": `desc`, `description`, `name`, `title`
- Textarea "Szablon" z dużym polem
- Pod textarea: lista dostępnych placeholderów (klikalne chipy z kluczami z product_value, klik → wstawia `{klucz}` do textarea)
- Podgląd na żywo: tekst wyniku dla pierwszego produktu, aktualizowany przy wpisywaniu

---

## 3. GTIN/EAN Dashboard

### Podejście

Wyłącznie frontend — dane już dostępne z endpointu `/validate` (Faza 1). Nowy komponent wizualizuje pokrycie EAN i listuje błędne kody.

### Komponent `EanCoverage.vue`

Wyświetlany w sekcji "Jakość feedu" na `FeedOutDetailView`, pod "Pokrycie pól", gdy w danych walidacji istnieje pole EAN/GTIN.

**Wygląd:**
- Progress bar z procentem pokrycia EAN
- Komunikat informacyjny: "Produkty z poprawnym EAN mają ~40% więcej wyświetleń na Google Shopping"
- Lista produktów z błędnymi EAN-ami (z issues gdzie `rule == "invalid_ean_checksum"` lub `rule == "invalid_ean_length"`)
- Licznik: "12/45 produktów ma EAN (27%)"

**Dane wejściowe (z odpowiedzi /validate):**
- `field_coverage` → szuka pola pasującego do `g:gtin`, `code`, `ean`
- `issues` → filtruje po `rule` zawierającym `ean`

---

## 4. Kreator feedu wyjściowego

### Rozbudowa `FeedOutCreateView.vue`

Obecny widok (prosty formularz) zastąpiony 3-krokowym wizardem.

### Backend — nowy endpoint

`GET /api/feeds-out/platform-info/{platform}`

Zwraca statyczne dane o platformie:

```json
{
  "platform": "gmc",
  "name": "Google Merchant Center",
  "description": "Google Shopping — największa platforma zakupowa na świecie",
  "required_fields": [
    {"field": "g:id", "description": "Unikalny identyfikator produktu, max 50 znaków"},
    {"field": "title", "description": "Tytuł produktu, max 150 znaków, powinien zawierać markę i kluczowe cechy"},
    {"field": "description", "description": "Opis produktu, max 5000 znaków, bez HTML i tekstu promocyjnego"},
    {"field": "link", "description": "URL strony produktu, musi być dostępny i zawierać cenę"},
    {"field": "g:image_link", "description": "URL głównego zdjęcia, min 100x100 px, zalecane 800x800+"},
    {"field": "g:availability", "description": "Dostępność: in_stock, out_of_stock, preorder, backorder"},
    {"field": "g:price", "description": "Cena z walutą, format: '29.99 PLN'"},
    {"field": "g:condition", "description": "Stan: new, refurbished, used"},
    {"field": "g:brand lub g:gtin", "description": "Marka lub kod EAN — co najmniej jedno wymagane"}
  ],
  "recommended_fields": [
    {"field": "g:google_product_category", "description": "Kategoria z taksonomii Google — lepsza klasyfikacja"},
    {"field": "g:gtin", "description": "Kod EAN-13 — produkty z EAN mają ~40% więcej wyświetleń"},
    {"field": "g:mpn", "description": "Kod producenta — wymagany gdy brak EAN"}
  ],
  "tips": [
    "Cena w feedzie MUSI zawierać walutę, np. '29.99 PLN'",
    "Produkty z poprawnym EAN mają znacznie lepszą widoczność",
    "Tytuł powinien zawierać: Marka + Typ produktu + Kluczowe cechy",
    "Zdjęcia min 800x800 px — mniejsze nie pozwolą na zoom"
  ]
}
```

Dane hardcoded w nowym serwisie `backend/app/services/platform_info.py` — dict per platforma. Analogicznie dla ceneo, facebook, allegro, skapiec, domodi.

### Frontend — 3-krokowy wizard

**Krok 1: Wybór platformy**

6 kart z ikonami i opisami. Każda karta pokazuje:
- Nazwa platformy
- Krótki opis (1 linia)
- Liczba wymaganych pól

Klik na kartę → przejście do kroku 2.

**Krok 2: Informacje o platformie**

Po pobraniu danych z `/platform-info/{platform}`:
- Lista wymaganych pól z opisami (zielona ikona ✓)
- Lista zalecanych pól z opisami (szara ikona ○)
- Sekcja "Wskazówki" z tipsami
- Przyciski: "Wstecz" | "Dalej"

**Krok 3: Nazwa i potwierdzenie**

- Input na nazwę feedu
- Podsumowanie: platforma, feed źródłowy (dropdown), liczba wymaganych pól
- Przycisk "Utwórz feed wyjściowy"

Po utworzeniu → redirect do `FeedOutDetailView` jak dotychczas.

---

## Wpływ na istniejący kod

### Backend — nowe pliki
- `backend/app/models/product_override.py` — model SQLAlchemy
- `backend/app/schemas/product_override.py` — schematy Pydantic
- `backend/app/services/override_service.py` — `apply_overrides(products, overrides)`
- `backend/app/services/platform_info.py` — statyczne dane o platformach
- `backend/alembic/versions/xxx_add_product_override.py` — migracja
- `backend/tests/test_overrides.py` — testy overrides
- `backend/tests/test_description_template.py` — testy szablonu opisów
- `backend/tests/test_platform_info.py` — testy endpointu platform-info

### Backend — modyfikowane pliki
- `backend/app/routers/feeds_out.py` — nowe endpointy (products, override CRUD, platform-info)
- `backend/app/routers/public_feed.py` — apply overrides przy generowaniu
- `backend/app/services/rules_engine.py` — nowy typ reguły `description_template`

### Frontend — nowe pliki
- `frontend/src/components/FeedOutProducts.vue` — tabela produktów z overrides
- `frontend/src/components/ProductOverrideModal.vue` — modal edycji produktu
- `frontend/src/components/EanCoverage.vue` — wizualizacja pokrycia EAN
- `frontend/src/components/DescriptionTemplateRule.vue` — formularz szablonu opisu

### Frontend — modyfikowane pliki
- `frontend/src/views/FeedOutDetailView.vue` — nowe sekcje (produkty, EAN, szablon opisu)
- `frontend/src/views/FeedOutCreateView.vue` — zamiana na 3-krokowy wizard
- `frontend/src/stores/feedsOut.ts` — nowe metody (getProducts, upsertOverride, deleteOverride, getPlatformInfo)

### Migracja bazy danych
- Nowa tabela `data.product_override`

---

## Poza zakresem

- Upload zdjęć (Faza 4)
- AI rewriting opisów (Faza 4)
- Nowe szablony platform w generatorze (Faza 3)
- Historia zmian feedu (Faza 4)
- Auto-mapping sugestie ("@price → g:price") — przesunięte do Fazy 3
