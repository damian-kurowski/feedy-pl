# Faza 4: Upload zdjęć + Historia zmian + AI rewriting + Plany cenowe

**Data:** 2026-04-10
**Status:** Draft
**Scope:** Upload i hosting zdjęć, changelog feedu źródłowego, AI przepisywanie opisów (premium), nowe plany cenowe z feature-gating

---

## Kontekst

Po Fazach 1-3 Feedy ma kompletne walidatory, quality score, podgląd zdjęć, overrides per produkt, szablon opisów, generatory 6 platform, taksonomię Google i kreator. Brakuje: hostingu zdjęć (podmiana URL-i), śledzenia zmian w feedach źródłowych, AI do opisów (premium), i aktualizacji planów cenowych pod nowe funkcje.

## Cele

1. Upload zdjęć z lokalnym storage (abstrakcja pod S3)
2. Historia zmian feedu źródłowego (automatyczna przy każdym fetch)
3. AI rewriting opisów per platforma (Claude API, premium)
4. Nowe plany cenowe z feature-gating

---

## 1. Upload zdjęć

### Storage

Pliki zapisywane w `backend/uploads/{user_id}/{uuid}.{ext}`. Serwowane przez FastAPI endpoint. Abstrakcja `StorageBackend` z metodami `save(file, user_id) -> path`, `delete(path)`, `get_url(path) -> str`.

Implementacja: `LocalStorage` — zapis na dysk, URL = `/uploads/{path}`.

Konfiguracja `.env`:
```
UPLOAD_DIR=uploads
UPLOAD_MAX_SIZE_MB=5
```

### Nowa tabela `data.uploaded_image`

```sql
CREATE TABLE data.uploaded_image (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    original_filename VARCHAR(512) NOT NULL,
    stored_path VARCHAR(1024) NOT NULL,
    file_size INTEGER NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### Model SQLAlchemy

`backend/app/models/uploaded_image.py`:
```python
class UploadedImage(Base):
    __tablename__ = "uploaded_image"
    __table_args__ = {"schema": "data"}
    id, user_id, original_filename, stored_path, file_size, content_type, created_at
```

### API Endpoints

`POST /api/images/upload` — multipart upload
- Walidacja: max 5MB, typy: image/jpeg, image/png, image/webp
- Generuje UUID filename, zapisuje przez StorageBackend
- Zwraca: `{"id": 1, "url": "/uploads/51/abc123.jpg", "filename": "abc123.jpg"}`
- Sprawdza limit storage per plan

`GET /uploads/{path:path}` — serwuje plik (FileResponse)

`DELETE /api/images/{id}` — usuwa plik + rekord. Tylko właściciel.

### Integracja z overrides

W `ProductOverrideModal.vue` — przy polach zdjęciowych (rozpoznawanych przez `isImageField()`) dodatkowy przycisk "Wgraj zdjęcie". Po uploadzeniu URL wstawiany jako override w `field_overrides`.

### Nowe pliki backend
- `backend/app/models/uploaded_image.py`
- `backend/app/services/storage.py` — `StorageBackend`, `LocalStorage`
- `backend/app/routers/images.py` — upload/delete/serve endpoints
- `backend/alembic/versions/xxx_add_uploaded_image.py`
- `backend/tests/test_image_upload.py`

### Nowe pliki frontend
- Modyfikacja `frontend/src/components/ProductOverrideModal.vue` — przycisk upload przy polach zdjęciowych

---

## 2. Historia zmian feedu

### Nowa tabela `data.feed_change_log`

```sql
CREATE TABLE data.feed_change_log (
    id BIGSERIAL PRIMARY KEY,
    feed_in_id INTEGER NOT NULL REFERENCES config.feed_in(id) ON DELETE CASCADE,
    change_type VARCHAR(20) NOT NULL,
    product_name VARCHAR(512),
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

`change_type`: `"added"`, `"removed"`, `"price_changed"`, `"modified"`

`details` przykłady:
- added: `{"product_id": "69"}`
- removed: `{"product_id": "69"}`
- price_changed: `{"product_id": "69", "old_price": "76.20", "new_price": "82.00"}`
- modified: `{"product_id": "69", "changed_fields": ["name", "desc"]}`

### Logika generowania changelog

W `fetch_and_parse_sync` (backend/app/tasks/feed_tasks.py) — po pobraniu nowych produktów a przed usunięciem starych:

1. Pobierz stare produkty z bazy (`ProductIn` dla tego `feed_in_id`)
2. Porównaj z nowymi (po `product_name` jako kluczu):
   - Nowy produkt (nazwa nie istniała) → `"added"`
   - Usunięty produkt (nazwa zniknęła) → `"removed"`
   - Zmieniona cena → `"price_changed"`
   - Inne zmiany w `product_value` → `"modified"`
3. Zapisz wpisy do `feed_change_log`
4. Kontynuuj normalny flow (usunięcie starych + zapis nowych)

Serwis: `backend/app/services/changelog_service.py`
- `generate_changelog(old_products, new_products, feed_in_id) -> list[FeedChangeLog]`
- Porównanie po `product_name`. Cena szukana w kluczach: `@price`, `g:price`, `price`.

### API

`GET /api/feeds-in/{id}/changelog?limit=50&offset=0` — paginowana lista zmian, najnowsze pierwsze.

Zwraca:
```json
{
  "changes": [
    {"id": 1, "change_type": "price_changed", "product_name": "Folia R20", "details": {"old_price": "76.20", "new_price": "82.00"}, "created_at": "2026-04-10T14:30:00Z"},
    {"id": 2, "change_type": "added", "product_name": "Folia XYZ", "details": {}, "created_at": "2026-04-10T14:30:00Z"}
  ],
  "total": 15
}
```

### Retencja per plan

Przy fetch — usuwaj wpisy starsze niż `plan.changelog_days` dni.

### Frontend

Nowa sekcja "Historia zmian" na `FeedInDetailView` (po sekcji "Produkty"):
- Lista zmian z ikonami: + (dodany, zielony), - (usunięty, czerwony), Δ (zmieniony, żółty), $ (cena, niebieski)
- Każdy wpis: data + typ + nazwa produktu + szczegóły
- "Pokaż więcej" jeśli >20 wpisów

### Nowe pliki
- `backend/app/models/feed_change_log.py`
- `backend/app/services/changelog_service.py`
- `backend/alembic/versions/xxx_add_feed_change_log.py`
- `backend/tests/test_changelog_service.py`
- `frontend/src/components/FeedChangelog.vue`
- Modyfikacja: `backend/app/tasks/feed_tasks.py`, `backend/app/routers/feeds_in.py`, `frontend/src/views/FeedInDetailView.vue`

---

## 3. AI rewriting opisów

### Serwis AI

`backend/app/services/ai_service.py`:

```python
async def rewrite_description(
    product_name: str,
    original_desc: str,
    platform: str,
    max_length: int = 5000,
) -> str:
```

Używa `anthropic` SDK (Python). Konfiguracja: `ANTHROPIC_API_KEY` w `.env`.

Prompty per platforma (hardcoded w serwisie):
- **gmc/facebook**: "Przepisz opis produktu dla Google Shopping. Max {max_length} znaków. Bez HTML, bez tekstu promocyjnego. Kluczowe cechy produktu na początku."
- **ceneo/skapiec**: "Przepisz opis produktu dla porównywarki cen. 200-1000 znaków. Techniczny, ze specyfikacjami."
- **domodi**: "Przepisz opis produktu modowego. Podkreśl styl, materiał, okazje do noszenia."
- **allegro**: "Przepisz opis produktu dla Allegro. Max 75 znaków w tytule. Szczegółowy opis z parametrami."

Model: `claude-haiku-4-5-20251001` (szybki, tani).

### Rate limiting i zużycie

- Max 50 produktów per request
- Przetwarzanie sekwencyjne (nie parallel)
- Śledzone w tabeli `auth.usage` per miesiąc
- Sprawdzenie limitu przed każdym request

### API

`POST /api/feeds-out/{id}/ai-rewrite`
- Body: `{"limit": 10}` (ile produktów przepisać, domyślnie 10)
- Sprawdza plan usera → limit AI rewrites
- Zwraca preview: `[{"product_name": "X", "original": "...", "rewritten": "..."}]`

`POST /api/feeds-out/{id}/ai-rewrite/apply`
- Body: `{"rewrites": [{"product_id": 1, "field": "desc", "value": "nowy opis"}]}`
- Zapisuje jako overrides (`ProductOverride.field_overrides`)

`GET /api/usage` — zwraca zużycie: `{"ai_rewrites_used": 12, "ai_rewrites_limit": 50, "storage_used_mb": 15, "storage_limit_mb": 100}`

### Frontend

Nowa sekcja "AI Opisy" na `FeedOutDetailView` (po "Optymalizacja tytułów"):
- Widoczna tylko gdy plan to pozwala (`ai_rewrites_monthly > 0`)
- Przycisk "Generuj opisy AI (zostało X/Y)"
- Tabela podglądu: Produkt | Oryginał | AI wersja
- Przycisk "Zastosuj wszystkie" → zapisuje jako overrides
- Checkboxy do wyboru które zastosować

### Nowe pliki
- `backend/app/services/ai_service.py`
- `backend/app/routers/ai.py` — endpoint AI rewrite
- `backend/tests/test_ai_service.py` (z mockiem API)
- `frontend/src/components/AiRewriteSection.vue`
- Modyfikacja: `frontend/src/views/FeedOutDetailView.vue`

### Zależność

Wymaga `anthropic` w `requirements.txt`. Dodać: `anthropic>=0.39.0`

---

## 4. Nowe plany cenowe

### Nowe kolumny na `auth.plans`

```sql
ALTER TABLE auth.plans ADD COLUMN ai_rewrites_monthly INTEGER;
ALTER TABLE auth.plans ADD COLUMN upload_storage_mb INTEGER;
ALTER TABLE auth.plans ADD COLUMN changelog_days INTEGER;
```

### Nowa tabela `auth.usage`

```sql
CREATE TABLE auth.usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    month VARCHAR(7) NOT NULL,
    ai_rewrites_used INTEGER NOT NULL DEFAULT 0,
    UNIQUE (user_id, month)
);
```

### Seed data update

| Plan | Cena | max_products | max_feeds_out | ai_rewrites_monthly | upload_storage_mb | changelog_days |
|------|------|-------------|--------------|-------------------|------------------|---------------|
| Free | 0 | 100 | 1 | 0 | 0 | 7 |
| Starter | 49 | 1000 | 3 | 0 | 10 | 30 |
| Pro | 149 | 10000 | 10 | 50 | 100 | 90 |
| Business | 349 | 50000 | null (∞) | 500 | 1000 | null (∞) |

### Feature gating

Middleware/deps sprawdzające:
- Upload: `user.plan.upload_storage_mb > 0` + aktualne zużycie < limit
- AI: `user.plan.ai_rewrites_monthly > 0` + `usage.ai_rewrites_used < limit`
- Changelog: retencja wg `plan.changelog_days`

### Przywrócenie plan limit check

W `feeds_out.py` — odkomentowanie sprawdzania limitu feedów wyjściowych (wykomentowane na początku sesji).

### Frontend

- Update `LandingView.vue` sekcja pricing — dodanie planu Business, aktualizacja cen
- Badge "Business" w nawigacji
- Feature-gate UI: sekcja AI widoczna tylko gdy plan pozwala, upload widoczny gdy plan pozwala

### Nowe pliki
- `backend/app/models/usage.py`
- `backend/alembic/versions/xxx_add_plans_columns_and_usage.py`
- Modyfikacja: seeder planów, `feeds_out.py` (restore limit check), landing page

---

## Wpływ na istniejący kod

### Backend — nowe pliki (10)
- `backend/app/models/uploaded_image.py`
- `backend/app/models/feed_change_log.py`
- `backend/app/models/usage.py`
- `backend/app/services/storage.py`
- `backend/app/services/changelog_service.py`
- `backend/app/services/ai_service.py`
- `backend/app/routers/images.py`
- `backend/app/routers/ai.py`
- `backend/tests/test_image_upload.py`
- `backend/tests/test_changelog_service.py`
- `backend/tests/test_ai_service.py`

### Backend — modyfikowane pliki (5)
- `backend/app/tasks/feed_tasks.py` — changelog przy fetch
- `backend/app/routers/feeds_in.py` — changelog endpoint
- `backend/app/routers/feeds_out.py` — przywrócenie plan limit, usage endpoint
- `backend/app/main.py` — rejestracja nowych routerów (images, ai)
- `backend/requirements.txt` — dodanie `anthropic`

### Frontend — nowe pliki (2)
- `frontend/src/components/FeedChangelog.vue`
- `frontend/src/components/AiRewriteSection.vue`

### Frontend — modyfikowane pliki (4)
- `frontend/src/views/FeedInDetailView.vue` — sekcja changelog
- `frontend/src/views/FeedOutDetailView.vue` — sekcja AI, upload w override modal
- `frontend/src/components/ProductOverrideModal.vue` — upload zdjęć
- `frontend/src/views/LandingView.vue` — nowy pricing

### Migracje bazy danych (3)
- Tabela `data.uploaded_image`
- Tabela `data.feed_change_log`
- Kolumny na `auth.plans` + tabela `auth.usage` + seed update
