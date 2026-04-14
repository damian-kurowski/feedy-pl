# Stripe Setup — Feedy.pl

Backend już ma kompletny kod do Stripe Checkout. Aby aktywować płatności, wykonaj poniższe kroki **jednorazowo**.

## 1. Załóż konto Stripe

1. Zarejestruj się: https://dashboard.stripe.com/register
2. Aktywuj konto dla Polski (PLN, NIP, dane firmowe)
3. Włącz tryb live (Activate account) — dla testów najpierw użyj test mode

## 2. Stwórz produkty + ceny

W Dashboard Stripe → Products → Add product:

### Starter — 49 zł/mies.
- Name: `Feedy Starter`
- Description: `1 000 produktów, 3 feedy wyjściowe, auto-refresh`
- Pricing model: `Recurring`
- Price: `49.00 PLN` / month
- → po zapisie, **skopiuj Price ID** (zaczyna się od `price_...`)

### Pro — 149 zł/mies.
- Name: `Feedy Pro`
- Description: `10 000 produktów, 10 feedów, AI optymalizacja, Quality Score`
- Recurring, `149.00 PLN` / month
- → skopiuj Price ID

### Business — 349 zł/mies.
- Name: `Feedy Business`
- Description: `50 000 produktów, bez limitu feedów, white-label, multi-user`
- Recurring, `349.00 PLN` / month
- → skopiuj Price ID

## 3. Skonfiguruj webhook

W Dashboard Stripe → Developers → Webhooks → Add endpoint:

- **Endpoint URL:** `https://feedy.pl/api/billing/webhook`
- **Events to send:**
  - `checkout.session.completed`
  - `customer.subscription.deleted`
- → po utworzeniu, kliknij endpoint i **skopiuj Signing secret** (`whsec_...`)

## 4. Wpisz klucze do `.env` na VPS

```bash
ssh debian@137.74.12.235
cd /home/debian/feedy
sudo nano .env
```

Dodaj/uzupełnij:

```env
STRIPE_SECRET_KEY=sk_live_...          # z Dashboard → Developers → API keys
STRIPE_WEBHOOK_SECRET=whsec_...        # z kroku 3
STRIPE_PRICE_STARTER=price_...         # ID z kroku 2 (Starter)
STRIPE_PRICE_PRO=price_...             # ID z kroku 2 (Pro)
STRIPE_PRICE_BUSINESS=price_...        # ID z kroku 2 (Business)
```

## 5. Włącz polskie metody płatności

W Dashboard Stripe → Settings → Payment methods → Polski rynek:
- ✅ **BLIK**
- ✅ **Przelewy24** (P24)
- ✅ **Karty** (Visa, Mastercard, Maestro)

Backend już przekazuje `payment_method_types=["card", "blik", "p24"]` w sesji checkout.

## 6. Tax (faktura VAT)

Settings → Tax → Włącz Stripe Tax:
- Region: Poland
- VAT rate: 23%
- Włącz `tax_id_collection` (wpisuje NIP klienta automatycznie)
- Włącz `automatic_tax`

Backend już wysyła `tax_id_collection={"enabled": True}`.

## 7. Customer Portal

Settings → Billing → Customer portal:
- Włącz portal
- Pozwól użytkownikom anulować subskrypcję (`subscription_cancel`)
- Pozwól na update karty
- Brand: logo Feedy + kolory

Endpoint `GET /api/billing/portal` już jest gotowy w backendzie.

## 8. Restart backendu

```bash
sudo docker-compose -f docker-compose.prod.yml restart backend
```

## 9. Test

1. Otwórz https://feedy.pl/ (incognito)
2. Zarejestruj się: testuser@example.com
3. Kliknij "Spróbuj Pro 14 dni za darmo"
4. → przekierowuje do Stripe Checkout
5. Test mode: użyj karty `4242 4242 4242 4242`, dowolny CVC, dowolna data
6. Po płatności → wraca na `/dashboard?billing=success`
7. Webhook → backend ustawia `user.plan_id = 3`
8. W Dashboard Stripe → Customers powinien być nowy klient z subskrypcją

## Trial 14 dni — co warto wiedzieć

- Karty są weryfikowane od razu (Stripe robi $0 auth)
- Pierwsza realna płatność dopiero po 14 dniach
- Klient dostaje email 3 dni przed końcem triala (Stripe automatycznie)
- Webhook `customer.subscription.trial_will_end` można obsłużyć, jeśli chcesz wysłać własny mail

## Anulacja

Klient klika "Zarządzaj subskrypcją" w dashboardzie → Customer Portal → Cancel.
Webhook `customer.subscription.deleted` przyjdzie i backend automatycznie ustawi `user.plan_id = 1` (Free).

---

**Wszystko poniżej jest TYLKO Twoja akcja** — w kodzie nic nie trzeba zmieniać. Backend `app/routers/billing.py` ma kompletną implementację checkout + webhook + portal.
