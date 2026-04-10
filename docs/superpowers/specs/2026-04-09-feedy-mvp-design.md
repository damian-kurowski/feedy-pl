# Feedy MVP — Design Spec

## Overview

Feedy to SaaS do zarządzania feedami produktowymi XML dla e-commerce. System pobiera feedy XML ze sklepów internetowych (Shoper-first, ale uniwersalny parser), parsuje je, umożliwia mapowanie pól i generuje feedy wyjściowe w formatach wymaganych przez porównywarki (Ceneo, Google Merchant Center).

**Target:** Właściciele sklepów Shoper, agencje e-commerce, freelancerzy.
**Model cenowy:** Freemium + tiery produktowe.
**Stack:** Python (FastAPI) + Vue 3 + Tailwind + PostgreSQL + Celery + Redis.
**Architektura:** Monolit na jednym VPS.

---

## 1. Architektura systemu

```
┌─────────────────────────────────────────────┐
│                   VPS                        │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Vue 3    │  │ FastAPI   │  │ PostgreSQL│  │
│  │ (Nginx)  │──│ (Uvicorn) │──│           │  │
│  └──────────┘  └────┬─────┘  └───────────┘  │
│                     │                        │
│               ┌─────┴─────┐                  │
│               │   Redis   │                  │
│               └─────┬─────┘                  │
│               ┌─────┴─────┐                  │
│               │  Celery   │                  │
│               │ (worker)  │                  │
│               └───────────┘                  │
└─────────────────────────────────────────────┘
```

| Komponent | Rola |
|---|---|
| **Vue 3 + Tailwind** | Panel użytkownika (SPA) |
| **FastAPI** | REST API — auth, CRUD feedów, triggerowanie parsowania |
| **PostgreSQL** | Baza danych |
| **Celery + Redis** | Asynchroniczne zadania: pobieranie XML, parsowanie, generowanie feedów out |
| **Nginx** | Reverse proxy, serwowanie Vue + statycznych feedów wyjściowych |

### Flow danych

1. User wkleja URL → FastAPI zapisuje do `feed_in` → Celery pobiera XML
2. Celery parsuje XML → zapisuje elementy do `xml_element_in` + produkty do `product_in`
3. User mapuje pola → zapisuje do `xml_structure_out`
4. Celery generuje XML wyjściowy → zapisuje jako plik lub cache w Redis
5. Nginx serwuje feed pod `link_out`

---

## 2. Schemat bazy danych

### auth.plans

| Kolumna | Typ | Opis |
|---|---|---|
| id | int, PK | |
| name | text | Nazwa planu (Free, Starter, Pro, Business) |
| max_products | int | Limit produktów |
| max_feeds_out | int | Limit feedów wyjściowych |
| price_pln | decimal | Cena miesięczna w PLN |

**Dane początkowe:**

| Plan | Produkty | Feedy out | Cena |
|---|---|---|---|
| Free | 200 | 1 | 0 PLN |
| Starter | 1 000 | 3 | 29 PLN |
| Pro | 5 000 | 10 | 59 PLN |
| Business | 20 000 | unlimited (null) | 99 PLN |

### auth.users

| Kolumna | Typ | Opis |
|---|---|---|
| id | int, PK | |
| email | text, unique | |
| password_hash | text | bcrypt |
| plan_id | int, FK → plans | Domyślnie Free |
| created_at | timestamp | |
| updated_at | timestamp | |

### config.feed_in

| Kolumna | Typ | Opis |
|---|---|---|
| id | int, PK | |
| created_at | timestamp | |
| updated_at | timestamp | |
| user_id | int, FK → users | |
| name | text | Nazwa feeda |
| source_url | text | URL do XML |
| record_path | text | Ścieżka do produktów (np. `feed/entry`) |
| product_name | text | Ścieżka do nazwy produktu |
| active | boolean | Domyślnie true |
| last_fetched_at | timestamp | Ostatnie pobranie |
| fetch_status | text | pending/fetching/success/error |

### data.xml_element_in

| Kolumna | Typ | Opis |
|---|---|---|
| id | bigint, PK | |
| created_at | timestamp | |
| updated_at | timestamp | |
| feed_in_id | int, FK → feed_in | |
| attribute | boolean | Czy jest atrybutem XML |
| path | text | Pełna ścieżka (np. `feed/entry/title`) |
| parent_path | text | Ścieżka rodzica |
| level | int | Poziom w drzewie |
| is_leaf | boolean | Czy element końcowy |
| element_name | text | Nazwa elementu |
| value | text | Wartość (przykładowa) |

### data.product_in

| Kolumna | Typ | Opis |
|---|---|---|
| id | bigint, PK | |
| created_at | timestamp | |
| updated_at | timestamp | |
| feed_in_id | int, FK → feed_in | |
| custom_product | boolean | false = z XML, true = dodany ręcznie |
| product_name | text | Nazwa produktu |
| product_value | jsonb | Cały produkt jako JSON |

### config.feed_out

| Kolumna | Typ | Opis |
|---|---|---|
| id | int, PK | |
| created_at | timestamp | |
| updated_at | timestamp | |
| user_id | int, FK → users | |
| feed_in_id | int, FK → feed_in | |
| name | text | Nazwa feeda wyjściowego |
| type | text | ceneo / gmc / custom |
| template | text | Użyty szablon |
| active | boolean | |
| link_out | text | UUID-based public URL |

### data.xml_structure_out

| Kolumna | Typ | Opis |
|---|---|---|
| id | bigint, PK | |
| created_at | timestamp | |
| updated_at | timestamp | |
| feed_out_id | int, FK → feed_out | |
| sort_key | text | Kolejność w strukturze (np. `1.4.2`) |
| custom_element | boolean | Własny vs mapowany z wejścia |
| path_in | text | Ścieżka źródłowa (jeśli mapowany) |
| level_out | int | Poziom w XML wyjściowym |
| path_out | text | Pełna ścieżka w XML wyjściowym |
| parent_path_out | text | Ścieżka rodzica w XML wyjściowym |
| element_name_out | text | Nazwa elementu |
| is_leaf | boolean | Czy końcowy |
| attribute | boolean | Czy atrybut |

---

## 3. API Endpoints

### Auth

```
POST /api/auth/register        — rejestracja (email + hasło)
POST /api/auth/login            — login → JWT token
GET  /api/auth/me               — dane usera + aktualny plan
```

### Feed In (źródła)

```
GET    /api/feeds-in             — lista feedów wejściowych usera
POST   /api/feeds-in             — dodaj nowy feed (url + nazwa)
GET    /api/feeds-in/:id         — szczegóły feeda
PUT    /api/feeds-in/:id         — edytuj (record_path, product_name, active)
DELETE /api/feeds-in/:id         — usuń feed + powiązane dane
POST   /api/feeds-in/:id/fetch   — ręczne triggerowanie parsowania
```

### Struktura XML (podgląd po parsowaniu)

```
GET /api/feeds-in/:id/elements   — drzewo elementów XML
GET /api/feeds-in/:id/products   — lista sparsowanych produktów
```

### Feed Out (wyjścia)

```
GET    /api/feeds-out             — lista feedów wyjściowych
POST   /api/feeds-out             — utwórz (feed_in_id, nazwa, template)
GET    /api/feeds-out/:id         — szczegóły + struktura
PUT    /api/feeds-out/:id         — edytuj
DELETE /api/feeds-out/:id         — usuń
```

### Struktura wyjściowa (mapowanie pól)

```
GET  /api/feeds-out/:id/structure  — aktualna struktura XML out
PUT  /api/feeds-out/:id/structure  — zapisz/zmień mapowanie pól
POST /api/feeds-out/:id/generate   — ręczne generowanie XML
```

### Publiczny feed (bez auth)

```
GET /feed/:uuid.xml               — wygenerowany XML
```

---

## 4. Flow użytkownika

### Krok 1: Rejestracja
User rejestruje się (email + hasło) → dostaje plan Free (200 produktów, 1 feed out).

### Krok 2: Dodanie źródła
User wkleja URL do XML i nadaje nazwę → system pobiera XML i pokazuje drzewo elementów.

### Krok 3: Wskazanie produktów
System wyświetla drzewo XML. User klika element, który reprezentuje produkt (np. `feed/entry`). System ustawia `record_path` i `product_name`, parsuje produkty, zapisuje do bazy.

### Krok 4: Tworzenie feeda wyjściowego
User wybiera szablon (Ceneo / GMC / Custom). Szablon automatycznie wypełnia mapowanie pól w `xml_structure_out`.

### Krok 5: Podgląd i edycja mapowania
User widzi tabelę: pole docelowe ↔ źródło ↔ podgląd wartości. Może zmienić mapowanie, dodać/usunąć pola.

### Krok 6: Generowanie
System generuje XML wyjściowy. User dostaje publiczny link (`/feed/:uuid.xml`) do wklejenia w Ceneo/GMC.

---

## 5. Szablony feedów

### Szablon Ceneo XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<offers>
  <o id="123" url="https://sklep.pl/produkt/123" price="9.50"
     avail="1" weight="0.5" stock="10">
    <cat><![CDATA[Chemia > Folie okienne]]></cat>
    <name><![CDATA[Płyn do montażu folii]]></name>
    <desc><![CDATA[Opis produktu...]]></desc>
    <imgs>
      <main url="https://sklep.pl/img/1.jpg"/>
    </imgs>
    <attrs>
      <a name="Producent"><![CDATA[EU]]></a>
      <a name="EAN"><![CDATA[5901234567890]]></a>
    </attrs>
  </o>
</offers>
```

**Mapowanie Ceneo:**

| Pole Ceneo | Typ | Źródło z GMC | Uwagi |
|---|---|---|---|
| `o/@id` | atrybut | `g:id` | wymagane |
| `o/@url` | atrybut | `link` | wymagane |
| `o/@price` | atrybut | `g:price` | bez "PLN", samo число |
| `o/@avail` | atrybut | `g:availability` | "in stock"→1, "out of stock"→0 |
| `o/cat` | element | `g:product_type` | user może nadpisać ręcznie |
| `o/name` | element | `title` | wymagane |
| `o/desc` | element | `description` | strip HTML |
| `o/imgs/main/@url` | atrybut | `g:image_link` | wymagane |
| `o/attrs/a[@name="Producent"]` | element | `g:brand` | opcjonalne |
| `o/attrs/a[@name="EAN"]` | element | `g:gtin` | opcjonalne ale ważne |

### Szablon GMC

Standardowy Atom/RSS. Shoper generuje poprawny format — szablon GMC służy do filtrowania i modyfikacji istniejącego feeda.

### Transformacje wbudowane

| Transformacja | Przykład |
|---|---|
| Strip "PLN" z ceny | `"9.5 PLN"` → `"9.50"` |
| Availability mapping | `"in stock"` → `"1"` |
| Strip HTML z opisów | `<b>tekst</b>` → `tekst` |
| CDATA wrapping | automatyczne dla tekstu |
| Formatowanie ceny | `"9.5"` → `"9.50"` |

---

## 6. Auth, billing i limity

### Autentykacja
- Email + hasło (bcrypt)
- JWT token (access 15min + refresh 7 dni)
- OAuth (Google) w v2

### Egzekwowanie limitów

```
POST /feeds-in/:id/fetch
  → policz produkty po parsowaniu
  → jeśli > plan.max_products → zapisz tylko max_products
  → komunikat: "Masz X produktów, Twój plan obsługuje Y. Upgrade żeby odblokować."

POST /feeds-out
  → policz istniejące feeds_out usera
  → jeśli >= plan.max_feeds_out → 403 + komunikat o upgrade
```

### Billing na MVP
Ręczny — user kontaktuje się mailowo, przelew/faktura. Stripe w v2.

---

## 7. Scope — MVP vs Later

### MVP (v1)
1. Wklej URL do XML → parsowanie i podgląd struktury
2. Wskaż produkty (record_path) → ekstrakcja do bazy
3. Tworzenie feeda wyjściowego z mapowaniem pól
4. Gotowe szablony: Ceneo + GMC
5. Generowanie XML pod publicznym linkiem
6. Rejestracja/logowanie + panel
7. Limity wg planu cenowego (egzekwowane, billing ręczny)

### Later (v2+)
- Automatyczne mapowanie kategorii Ceneo (ML/słownikowe)
- Reguły filtrowania/modyfikacji (zamień, filtruj, dodaj prefix)
- Harmonogram odświeżania feedów (co 1h, 6h, 24h)
- Multi-sklep dla agencji
- API publiczne
- Optymalizacja tytułów
- Stripe billing
- OAuth (Google login)
