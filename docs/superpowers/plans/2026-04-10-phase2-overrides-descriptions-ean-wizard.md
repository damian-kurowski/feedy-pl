# Phase 2: Product Overrides + Description Templates + EAN Dashboard + Wizard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add per-product overrides in output feeds, description template rules, EAN coverage visualization, and a step-by-step feed creation wizard.

**Architecture:** New `product_override` table for per-product field overrides. Override merge happens before rules engine. Description template is a new rule type. EAN dashboard is frontend-only (data from existing `/validate`). Wizard replaces the simple create form with 3 steps.

**Tech Stack:** Python, FastAPI, SQLAlchemy, Alembic, Vue 3, Tailwind CSS, Pinia

---

## File Structure

### Backend — New files
- `backend/app/models/product_override.py` — ProductOverride SQLAlchemy model
- `backend/app/schemas/product_override.py` — Pydantic schemas
- `backend/app/services/override_service.py` — `apply_overrides()` helper
- `backend/app/services/platform_info.py` — static platform info data
- `backend/alembic/versions/xxxx_add_product_override.py` — migration
- `backend/tests/test_overrides.py` — override service + API tests
- `backend/tests/test_description_template.py` — description template rule tests
- `backend/tests/test_platform_info.py` — platform info endpoint tests

### Backend — Modified files
- `backend/app/services/rules_engine.py` — add `description_template` rule type
- `backend/app/routers/feeds_out.py` — add products, override CRUD, platform-info endpoints
- `backend/app/routers/public_feed.py` — apply overrides before rules

### Frontend — New files
- `frontend/src/components/FeedOutProducts.vue` — product table with overrides
- `frontend/src/components/ProductOverrideModal.vue` — override editor modal
- `frontend/src/components/EanCoverage.vue` — EAN coverage visualization
- `frontend/src/components/DescriptionTemplateRule.vue` — template rule editor

### Frontend — Modified files
- `frontend/src/views/FeedOutDetailView.vue` — add products section, EAN section, description template
- `frontend/src/views/FeedOutCreateView.vue` — replace with 3-step wizard
- `frontend/src/stores/feedsOut.ts` — add override + platform-info methods

---

### Task 1: ProductOverride model + migration

**Files:**
- Create: `backend/app/models/product_override.py`
- Create: `backend/alembic/versions/xxxx_add_product_override.py`

- [ ] **Step 1: Create the model**

```python
# backend/app/models/product_override.py
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductOverride(Base):
    __tablename__ = "product_override"
    __table_args__ = (
        UniqueConstraint("feed_out_id", "product_in_id"),
        {"schema": "data"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    feed_out_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("config.feed_out.id", ondelete="CASCADE"), nullable=False
    )
    product_in_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("data.product_in.id", ondelete="CASCADE"), nullable=False
    )
    field_overrides: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    excluded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
```

- [ ] **Step 2: Create the Alembic migration**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. alembic revision --autogenerate -m "add product_override table"`

If autogenerate doesn't detect the model (common when schema differs), create manually:

```python
# backend/alembic/versions/xxxx_add_product_override.py
"""add product_override table"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = 'a1b2c3d4e5f7'
down_revision = '6304485bd4dd'  # current head
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'product_override',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('feed_out_id', sa.Integer(), sa.ForeignKey('config.feed_out.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_in_id', sa.BigInteger(), sa.ForeignKey('data.product_in.id', ondelete='CASCADE'), nullable=False),
        sa.Column('field_overrides', JSONB(), nullable=False, server_default='{}'),
        sa.Column('excluded', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('feed_out_id', 'product_in_id'),
        schema='data',
    )


def downgrade():
    op.drop_table('product_override', schema='data')
```

- [ ] **Step 3: Run migration**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. alembic upgrade head`

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/product_override.py backend/alembic/versions/
git commit -m "feat: add ProductOverride model and migration"
```

---

### Task 2: Override service + Pydantic schemas

**Files:**
- Create: `backend/app/services/override_service.py`
- Create: `backend/app/schemas/product_override.py`
- Test: `backend/tests/test_overrides.py`

- [ ] **Step 1: Write tests for override service**

```python
# backend/tests/test_overrides.py
from app.services.override_service import apply_overrides


def _product(pid: int, pv: dict) -> dict:
    return {"id": pid, "product_value": pv}


def _override(pid: int, fields: dict | None = None, excluded: bool = False) -> dict:
    return {"product_in_id": pid, "field_overrides": fields or {}, "excluded": excluded}


def test_no_overrides():
    products = [_product(1, {"name": "Original"})]
    result = apply_overrides(products, [])
    assert len(result) == 1
    assert result[0]["product_value"]["name"] == "Original"


def test_field_override_merges():
    products = [_product(1, {"name": "Original", "price": "10.00"})]
    overrides = [_override(1, {"name": "Changed"})]
    result = apply_overrides(products, overrides)
    assert result[0]["product_value"]["name"] == "Changed"
    assert result[0]["product_value"]["price"] == "10.00"


def test_excluded_product_removed():
    products = [_product(1, {"name": "A"}), _product(2, {"name": "B"})]
    overrides = [_override(1, excluded=True)]
    result = apply_overrides(products, overrides)
    assert len(result) == 1
    assert result[0]["product_value"]["name"] == "B"


def test_override_does_not_mutate_original():
    original_pv = {"name": "Original"}
    products = [_product(1, original_pv)]
    overrides = [_override(1, {"name": "Changed"})]
    result = apply_overrides(products, overrides)
    assert result[0]["product_value"]["name"] == "Changed"
    assert original_pv["name"] == "Original"


def test_empty_field_overrides_no_change():
    products = [_product(1, {"name": "Same"})]
    overrides = [_override(1, {})]
    result = apply_overrides(products, overrides)
    assert result[0]["product_value"]["name"] == "Same"


def test_multiple_overrides():
    products = [_product(1, {"name": "A"}), _product(2, {"name": "B"}), _product(3, {"name": "C"})]
    overrides = [_override(1, {"name": "A2"}), _override(3, excluded=True)]
    result = apply_overrides(products, overrides)
    assert len(result) == 2
    assert result[0]["product_value"]["name"] == "A2"
    assert result[1]["product_value"]["name"] == "B"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_overrides.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement override service**

```python
# backend/app/services/override_service.py
"""Apply per-product overrides to product list."""


def apply_overrides(
    products: list[dict], overrides: list[dict]
) -> list[dict]:
    """Merge field_overrides into products and exclude marked products.

    *products* — list of dicts with ``id`` and ``product_value`` keys.
    *overrides* — list of dicts with ``product_in_id``, ``field_overrides``, ``excluded``.

    Returns a new list (does not mutate originals).
    """
    if not overrides:
        return products

    override_map: dict[int, dict] = {o["product_in_id"]: o for o in overrides}
    result: list[dict] = []

    for product in products:
        pid = product.get("id")
        ov = override_map.get(pid)

        if ov and ov.get("excluded"):
            continue

        if ov and ov.get("field_overrides"):
            merged_pv = {**product["product_value"], **ov["field_overrides"]}
            result.append({**product, "product_value": merged_pv})
        else:
            result.append(product)

    return result
```

- [ ] **Step 4: Create Pydantic schemas**

```python
# backend/app/schemas/product_override.py
from pydantic import BaseModel


class ProductOverrideUpsert(BaseModel):
    field_overrides: dict = {}
    excluded: bool = False


class ProductWithOverrideResponse(BaseModel):
    id: int
    product_name: str
    product_value: dict
    override: dict | None
    status: str  # "original" | "modified" | "excluded"

    class Config:
        from_attributes = True
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_overrides.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/override_service.py backend/app/schemas/product_override.py backend/tests/test_overrides.py
git commit -m "feat: add override service and schemas"
```

---

### Task 3: Override API endpoints + public feed integration

**Files:**
- Modify: `backend/app/routers/feeds_out.py`
- Modify: `backend/app/routers/public_feed.py`

- [ ] **Step 1: Add override endpoints to feeds_out.py**

Add these imports at the top of `backend/app/routers/feeds_out.py`:

```python
from app.models.product_override import ProductOverride
from app.schemas.product_override import ProductOverrideUpsert, ProductWithOverrideResponse
from app.services.override_service import apply_overrides
```

Add these 3 new endpoints before the `validate_feed_endpoint`:

```python
@router.get("/{feed_out_id}/products", response_model=list[ProductWithOverrideResponse])
async def list_feed_products(
    feed_out_id: int,
    search: str = "",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed_out = await _get_user_feed_out(db, feed_out_id, user.id)

    # Get products from linked feed_in
    query = select(ProductIn).where(ProductIn.feed_in_id == feed_out.feed_in_id)
    if search:
        query = query.where(ProductIn.product_name.ilike(f"%{search}%"))
    products_result = await db.execute(query.limit(100))
    products = products_result.scalars().all()

    # Get overrides for this feed_out
    overrides_result = await db.execute(
        select(ProductOverride).where(ProductOverride.feed_out_id == feed_out_id)
    )
    override_map = {o.product_in_id: o for o in overrides_result.scalars().all()}

    result = []
    for p in products:
        ov = override_map.get(p.id)
        if ov and ov.excluded:
            status = "excluded"
        elif ov and ov.field_overrides:
            status = "modified"
        else:
            status = "original"

        merged_pv = p.product_value
        if ov and ov.field_overrides:
            merged_pv = {**p.product_value, **ov.field_overrides}

        result.append(ProductWithOverrideResponse(
            id=p.id,
            product_name=p.product_name,
            product_value=merged_pv,
            override={"field_overrides": ov.field_overrides, "excluded": ov.excluded} if ov else None,
            status=status,
        ))
    return result


@router.put("/{feed_out_id}/products/{product_id}/override")
async def upsert_override(
    feed_out_id: int,
    product_id: int,
    data: ProductOverrideUpsert,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed_out = await _get_user_feed_out(db, feed_out_id, user.id)

    # Verify product belongs to the linked feed_in
    product_result = await db.execute(
        select(ProductIn).where(
            ProductIn.id == product_id,
            ProductIn.feed_in_id == feed_out.feed_in_id,
        )
    )
    if not product_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found in this feed")

    # Upsert
    existing = await db.execute(
        select(ProductOverride).where(
            ProductOverride.feed_out_id == feed_out_id,
            ProductOverride.product_in_id == product_id,
        )
    )
    override = existing.scalar_one_or_none()
    if override:
        override.field_overrides = data.field_overrides
        override.excluded = data.excluded
    else:
        override = ProductOverride(
            feed_out_id=feed_out_id,
            product_in_id=product_id,
            field_overrides=data.field_overrides,
            excluded=data.excluded,
        )
        db.add(override)
    await db.commit()
    return {"status": "ok", "field_overrides": data.field_overrides, "excluded": data.excluded}


@router.delete("/{feed_out_id}/products/{product_id}/override", status_code=204)
async def delete_override(
    feed_out_id: int,
    product_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_feed_out(db, feed_out_id, user.id)
    await db.execute(
        select(ProductOverride).where(
            ProductOverride.feed_out_id == feed_out_id,
            ProductOverride.product_in_id == product_id,
        )
    )
    result = await db.execute(
        select(ProductOverride).where(
            ProductOverride.feed_out_id == feed_out_id,
            ProductOverride.product_in_id == product_id,
        )
    )
    override = result.scalar_one_or_none()
    if override:
        await db.delete(override)
        await db.commit()
```

- [ ] **Step 2: Update public_feed.py to apply overrides**

In `backend/app/routers/public_feed.py`, add import:

```python
from app.models.product_override import ProductOverride
from app.services.override_service import apply_overrides
```

Replace the product fetching section (lines 32-44) with:

```python
    # Get products from linked feed_in
    products_result = await db.execute(
        select(ProductIn).where(ProductIn.feed_in_id == feed_out.feed_in_id)
    )
    products = products_result.scalars().all()

    product_dicts = [
        {"id": p.id, "product_value": p.product_value}
        for p in products
    ]

    # Apply per-product overrides
    overrides_result = await db.execute(
        select(ProductOverride).where(ProductOverride.feed_out_id == feed_out.id)
    )
    overrides = [
        {"product_in_id": o.product_in_id, "field_overrides": o.field_overrides, "excluded": o.excluded}
        for o in overrides_result.scalars().all()
    ]
    product_dicts = apply_overrides(product_dicts, overrides)

    if feed_out.rules:
        product_dicts = apply_rules(product_dicts, feed_out.rules)
```

Also update the validate endpoint in `feeds_out.py` similarly — add override loading between product fetching and rules application.

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/feeds_out.py backend/app/routers/public_feed.py
git commit -m "feat: add override CRUD endpoints and integrate with feed generation"
```

---

### Task 4: Description template rule

**Files:**
- Modify: `backend/app/services/rules_engine.py`
- Test: `backend/tests/test_description_template.py`

- [ ] **Step 1: Write tests**

```python
# backend/tests/test_description_template.py
from app.services.rules_engine import apply_rules


def _product(pv: dict) -> dict:
    return {"product_value": pv}


def test_description_template_basic():
    products = [_product({"name": "Folia", "brand": "Lite Solar", "desc": "Opis oryginalny"})]
    rules = [{"type": "description_template", "field": "desc", "template": "Kup {name} marki {brand}!"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "Kup Folia marki Lite Solar!"


def test_description_template_missing_placeholder():
    products = [_product({"name": "Folia"})]
    rules = [{"type": "description_template", "field": "desc", "template": "{name} - {brand}"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "Folia -"


def test_description_template_with_at_prefix():
    products = [_product({"@price": "49.99", "name": "Produkt"})]
    rules = [{"type": "description_template", "field": "desc", "template": "{name} za {@price} zl"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "Produkt za 49.99 zl"


def test_description_template_cleans_double_spaces():
    products = [_product({"name": "Folia"})]
    rules = [{"type": "description_template", "field": "desc", "template": "{name}  {missing}  koniec"}]
    result = apply_rules(products, rules)
    assert "  " not in result[0]["product_value"]["desc"]


def test_description_template_default_field():
    products = [_product({"name": "Test"})]
    rules = [{"type": "description_template", "template": "{name} opis"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "Test opis"


def test_description_template_multiple_products():
    products = [
        _product({"name": "A", "cat": "X"}),
        _product({"name": "B", "cat": "Y"}),
    ]
    rules = [{"type": "description_template", "field": "desc", "template": "{name} w {cat}"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "A w X"
    assert result[1]["product_value"]["desc"] == "B w Y"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_description_template.py -v`
Expected: FAIL — "desc" key not in product_value

- [ ] **Step 3: Implement description_template in rules_engine.py**

Add to `_apply_rule()` function in `backend/app/services/rules_engine.py`, after the `optimize_titles` elif:

```python
    elif rule_type == "description_template":
        return _description_template(products, rule)
```

Add the function at the end of the file:

```python
def _description_template(products: list[dict], rule: dict) -> list[dict]:
    """Replace a field value with a template. Placeholders {key} are resolved from product_value."""
    field = rule.get("field", "desc")
    template = rule.get("template", "")
    for p in products:
        pv = p.get("product_value", {})
        result = template
        for key, val in pv.items():
            if isinstance(val, str):
                result = result.replace(f"{{{key}}}", val.strip())
        # Remove unresolved placeholders
        result = re.sub(r"\{[^}]+\}", "", result)
        # Clean double spaces
        result = re.sub(r"  +", " ", result).strip()
        pv[field] = result
    return products
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_description_template.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/rules_engine.py backend/tests/test_description_template.py
git commit -m "feat: add description_template rule type"
```

---

### Task 5: Platform info endpoint

**Files:**
- Create: `backend/app/services/platform_info.py`
- Modify: `backend/app/routers/feeds_out.py`
- Test: `backend/tests/test_platform_info.py`

- [ ] **Step 1: Write tests**

```python
# backend/tests/test_platform_info.py
from app.services.platform_info import get_platform_info


def test_gmc_info():
    info = get_platform_info("gmc")
    assert info is not None
    assert info["platform"] == "gmc"
    assert len(info["required_fields"]) > 0
    assert all("field" in f and "description" in f for f in info["required_fields"])


def test_ceneo_info():
    info = get_platform_info("ceneo")
    assert info is not None
    assert info["platform"] == "ceneo"
    assert len(info["tips"]) > 0


def test_all_platforms_have_info():
    for platform in ["ceneo", "gmc", "facebook", "allegro", "skapiec", "domodi"]:
        info = get_platform_info(platform)
        assert info is not None, f"Missing info for {platform}"
        assert "required_fields" in info
        assert "recommended_fields" in info
        assert "tips" in info


def test_unknown_platform():
    info = get_platform_info("nonexistent")
    assert info is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_platform_info.py -v`
Expected: FAIL

- [ ] **Step 3: Implement platform_info.py**

```python
# backend/app/services/platform_info.py
"""Static platform information for the feed creation wizard."""

_PLATFORMS: dict[str, dict] = {
    "ceneo": {
        "platform": "ceneo",
        "name": "Ceneo",
        "description": "Ceneo.pl — najwieksza porownywarka cen w Polsce",
        "required_fields": [
            {"field": "@id", "description": "Unikalny identyfikator produktu"},
            {"field": "@url", "description": "URL strony produktu w sklepie"},
            {"field": "@price", "description": "Cena brutto, format numeryczny BEZ waluty (np. '49.99')"},
            {"field": "@avail", "description": "Dostepnosc: 1 (dostepny), 3, 7, 14, 99 (na zamowienie)"},
            {"field": "name", "description": "Pelna nazwa produktu z marka i kluczowymi cechami"},
            {"field": "cat", "description": "Kategoria produktu ze sklepu"},
            {"field": "desc", "description": "Opis produktu"},
        ],
        "recommended_fields": [
            {"field": "producer", "description": "Marka / producent"},
            {"field": "code", "description": "Kod EAN/GTIN — pomaga dopasowac do karty produktu na Ceneo"},
            {"field": "imgs", "description": "Zdjecie glowne produktu"},
            {"field": "old_price", "description": "Cena przed obnizka — wyswietla przekreslona cene"},
            {"field": "shipping", "description": "Koszt dostawy"},
        ],
        "tips": [
            "Cena NIE moze zawierac waluty — sam numer, np. '49.99'",
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
            {"field": "title", "description": "Tytul produktu, max 150 znakow, z marka i kluczowymi cechami"},
            {"field": "description", "description": "Opis produktu, max 5000 znakow, bez HTML"},
            {"field": "link", "description": "URL strony produktu"},
            {"field": "g:image_link", "description": "URL glownego zdjecia, min 100x100 px, zalecane 800x800+"},
            {"field": "g:availability", "description": "in_stock, out_of_stock, preorder lub backorder"},
            {"field": "g:price", "description": "Cena Z waluta, format: '29.99 PLN'"},
            {"field": "g:condition", "description": "Stan: new, refurbished, used"},
            {"field": "g:brand / g:gtin", "description": "Marka lub kod EAN — co najmniej jedno wymagane"},
        ],
        "recommended_fields": [
            {"field": "g:google_product_category", "description": "Kategoria z taksonomii Google — lepsza klasyfikacja"},
            {"field": "g:gtin", "description": "Kod EAN-13 — produkty z EAN maja ~40% wiecej wyswietlen"},
            {"field": "g:mpn", "description": "Kod producenta — wymagany gdy brak EAN"},
            {"field": "g:product_type", "description": "Twoja kategoria produktu"},
            {"field": "g:additional_image_link", "description": "Dodatkowe zdjecia (do 10)"},
        ],
        "tips": [
            "Cena MUSI zawierac walute: '29.99 PLN'",
            "Produkty z poprawnym EAN maja ~40% wiecej wyswietlen",
            "Tytul: Marka + Typ produktu + Kluczowe cechy",
            "Zdjecia min 800x800 px — mniejsze nie pozwola na zoom",
            "Bez tekstu promocyjnego w tytule i opisie ('kup teraz', 'darmowa dostawa')",
        ],
    },
    "facebook": {
        "platform": "facebook",
        "name": "Facebook / Meta Catalog",
        "description": "Meta Commerce — reklamy produktowe na Facebooku i Instagramie",
        "required_fields": [
            {"field": "id", "description": "Unikalny identyfikator, max 100 znakow"},
            {"field": "title", "description": "Tytul, max 200 znakow (pierwsze 65 widoczne w reklamach)"},
            {"field": "description", "description": "Opis, max 9999 znakow"},
            {"field": "availability", "description": "in stock, out of stock, available for order, discontinued"},
            {"field": "condition", "description": "new, refurbished, used"},
            {"field": "price", "description": "Cena z waluta: '29.99 PLN'"},
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
            "Pierwsze 65 znakow tytulu jest widoczne w reklamach",
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
            {"field": "name", "description": "Nazwa produktu, MAX 75 znakow (Allegro obcina)"},
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
            "Allegro uzywa API, nie tradycyjnych feedow XML",
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
            {"field": "price", "description": "Cena brutto, format numeryczny bez waluty"},
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
            {"field": "image", "description": "URL zdjecia — zdjecia na modelu preferowane (moda)"},
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
            "Zdjecia na modelu znacznie lepiej konwertuja niz flat-lay",
            "Kolor i rozmiar sa kluczowe dla filtrow",
            "Nazwa powinna zawierac: Marka + Typ + Kolor + Material",
        ],
    },
}


def get_platform_info(platform: str) -> dict | None:
    """Return platform info dict or None if unknown."""
    return _PLATFORMS.get(platform)


def get_all_platforms() -> list[dict]:
    """Return summary of all platforms (for wizard step 1)."""
    return [
        {
            "platform": p["platform"],
            "name": p["name"],
            "description": p["description"],
            "required_count": len(p["required_fields"]),
        }
        for p in _PLATFORMS.values()
    ]
```

- [ ] **Step 4: Add endpoint to feeds_out.py**

```python
from app.services.platform_info import get_platform_info, get_all_platforms

@router.get("/platforms")
async def list_platforms(user: User = Depends(get_current_user)):
    return get_all_platforms()


@router.get("/platform-info/{platform}")
async def platform_info(platform: str, user: User = Depends(get_current_user)):
    info = get_platform_info(platform)
    if not info:
        raise HTTPException(status_code=404, detail="Unknown platform")
    return info
```

Note: these endpoints must be placed BEFORE the `/{feed_out_id}` routes to avoid path conflicts.

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_platform_info.py -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/platform_info.py backend/app/routers/feeds_out.py backend/tests/test_platform_info.py
git commit -m "feat: add platform info service and wizard endpoints"
```

---

### Task 6: Frontend — Override components

**Files:**
- Create: `frontend/src/components/FeedOutProducts.vue`
- Create: `frontend/src/components/ProductOverrideModal.vue`
- Modify: `frontend/src/stores/feedsOut.ts`

- [ ] **Step 1: Add store methods**

Add to `frontend/src/stores/feedsOut.ts` inside the store, before the return:

```typescript
  async function getFeedProducts(feedOutId: number, search: string = ''): Promise<any[]> {
    const params = search ? { search } : {}
    const { data } = await api.get(`/feeds-out/${feedOutId}/products`, { params })
    return data
  }

  async function upsertOverride(feedOutId: number, productId: number, body: { field_overrides: Record<string, string>; excluded: boolean }) {
    const { data } = await api.put(`/feeds-out/${feedOutId}/products/${productId}/override`, body)
    return data
  }

  async function deleteOverride(feedOutId: number, productId: number) {
    await api.delete(`/feeds-out/${feedOutId}/products/${productId}/override`)
  }

  async function getPlatformInfo(platform: string) {
    const { data } = await api.get(`/feeds-out/platform-info/${platform}`)
    return data
  }

  async function getPlatforms() {
    const { data } = await api.get('/feeds-out/platforms')
    return data
  }
```

Add all 5 to the return statement.

- [ ] **Step 2: Create ProductOverrideModal.vue**

```vue
<!-- frontend/src/components/ProductOverrideModal.vue -->
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { extractImageUrls } from '../utils/imageExtractor'

const props = defineProps<{
  show: boolean
  product: any | null
}>()

const emit = defineEmits<{
  close: []
  save: [overrides: Record<string, string>, excluded: boolean]
  restore: []
}>()

const overrides = ref<Record<string, string>>({})
const excluded = ref(false)

watch(() => props.product, (p) => {
  if (p?.override) {
    overrides.value = { ...p.override.field_overrides }
    excluded.value = p.override.excluded
  } else {
    overrides.value = {}
    excluded.value = false
  }
}, { immediate: true })

const fields = computed(() => {
  if (!props.product) return []
  const pv = props.product.product_value
  return Object.entries(pv)
    .filter(([_, v]) => typeof v === 'string' || typeof v === 'number')
    .map(([key, val]) => ({ key, original: String(val) }))
})

const mainImage = computed(() => {
  if (!props.product) return null
  return extractImageUrls(props.product.product_value).main
})

function setOverride(key: string, value: string) {
  if (value === '' || value === fields.value.find(f => f.key === key)?.original) {
    const copy = { ...overrides.value }
    delete copy[key]
    overrides.value = copy
  } else {
    overrides.value = { ...overrides.value, [key]: value }
  }
}

function handleSave() {
  emit('save', overrides.value, excluded.value)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show && product" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="emit('close')">
      <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[85vh] flex flex-col">
        <!-- Header -->
        <div class="p-4 border-b flex items-center gap-3">
          <img v-if="mainImage" :src="mainImage" class="w-10 h-10 object-cover rounded border" />
          <div class="min-w-0 flex-1">
            <h3 class="font-semibold text-gray-900 truncate">{{ product.product_name }}</h3>
            <span class="text-xs" :class="product.status === 'modified' ? 'text-yellow-600' : product.status === 'excluded' ? 'text-red-600' : 'text-gray-400'">
              {{ product.status === 'modified' ? 'Zmieniony' : product.status === 'excluded' ? 'Wykluczony' : 'Oryginal' }}
            </span>
          </div>
          <button class="text-gray-400 hover:text-gray-600 cursor-pointer" @click="emit('close')">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <!-- Body -->
        <div class="p-4 overflow-y-auto flex-1 space-y-3">
          <!-- Exclude checkbox -->
          <label class="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md cursor-pointer">
            <input type="checkbox" v-model="excluded" class="rounded" />
            <span class="text-sm text-red-700">Wyklucz z feedu wyjsciowego</span>
          </label>

          <!-- Fields -->
          <div v-for="field in fields" :key="field.key" class="border rounded-md p-3">
            <label class="text-xs font-medium text-gray-500 block mb-1">{{ field.key }}</label>
            <div class="text-xs text-gray-400 mb-1 truncate">Oryginal: {{ field.original }}</div>
            <input
              type="text"
              :value="overrides[field.key] ?? ''"
              :placeholder="field.original"
              class="w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              @input="setOverride(field.key, ($event.target as HTMLInputElement).value)"
            />
          </div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t flex items-center justify-between">
          <button
            v-if="product.override"
            class="text-sm text-red-600 hover:text-red-800 cursor-pointer"
            @click="emit('restore')"
          >
            Przywroc oryginal
          </button>
          <div v-else></div>
          <div class="flex gap-2">
            <button class="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md cursor-pointer" @click="emit('close')">Anuluj</button>
            <button class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-md cursor-pointer" @click="handleSave">Zapisz</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
```

- [ ] **Step 3: Create FeedOutProducts.vue**

```vue
<!-- frontend/src/components/FeedOutProducts.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useFeedsOutStore } from '../stores/feedsOut'
import { extractImageUrls } from '../utils/imageExtractor'
import ProductOverrideModal from './ProductOverrideModal.vue'

const props = defineProps<{
  feedOutId: number
}>()

const store = useFeedsOutStore()
const products = ref<any[]>([])
const search = ref('')
const loading = ref(false)
const editProduct = ref<any>(null)
const showModal = ref(false)

const placeholderSvg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Crect fill='%23f3f4f6' width='40' height='40' rx='4'/%3E%3C/svg%3E"

async function loadProducts() {
  loading.value = true
  try {
    products.value = await store.getFeedProducts(props.feedOutId, search.value)
  } finally {
    loading.value = false
  }
}

function getImage(product: any): string | null {
  return extractImageUrls(product.product_value).main
}

function getPrice(product: any): string | null {
  const pv = product.product_value
  return pv['@price'] ?? pv['g:price'] ?? pv['price'] ?? null
}

function openEdit(product: any) {
  editProduct.value = product
  showModal.value = true
}

async function handleSave(overrides: Record<string, string>, excluded: boolean) {
  if (!editProduct.value) return
  await store.upsertOverride(props.feedOutId, editProduct.value.id, {
    field_overrides: overrides,
    excluded,
  })
  showModal.value = false
  await loadProducts()
}

async function handleRestore() {
  if (!editProduct.value) return
  await store.deleteOverride(props.feedOutId, editProduct.value.id)
  showModal.value = false
  await loadProducts()
}

let searchTimeout: ReturnType<typeof setTimeout>
function onSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(loadProducts, 300)
}

onMounted(loadProducts)
</script>

<template>
  <div>
    <!-- Search -->
    <div class="mb-3">
      <input
        v-model="search"
        type="text"
        placeholder="Szukaj produktu..."
        class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        @input="onSearch"
      />
    </div>

    <!-- Product table -->
    <div class="border rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-700 w-12"></th>
            <th class="text-left px-4 py-3 font-medium text-gray-700">Nazwa</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700 w-24">Cena</th>
            <th class="text-left px-4 py-3 font-medium text-gray-700 w-28">Status</th>
            <th class="px-4 py-3 w-20"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">Ladowanie...</td>
          </tr>
          <tr v-else-if="products.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-gray-400">Brak produktow</td>
          </tr>
          <tr
            v-for="product in products"
            :key="product.id"
            class="border-t hover:bg-gray-50"
            :class="product.status === 'excluded' ? 'opacity-50' : ''"
          >
            <td class="px-4 py-2">
              <img
                :src="getImage(product) || placeholderSvg"
                class="w-10 h-10 object-cover rounded border border-gray-200"
                loading="lazy"
              />
            </td>
            <td class="px-4 py-2">
              <span class="text-gray-900 truncate block max-w-xs">{{ product.product_name }}</span>
            </td>
            <td class="px-4 py-2 text-gray-600">{{ getPrice(product) || '-' }}</td>
            <td class="px-4 py-2">
              <span
                class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium"
                :class="{
                  'bg-green-100 text-green-700': product.status === 'original',
                  'bg-yellow-100 text-yellow-700': product.status === 'modified',
                  'bg-red-100 text-red-700': product.status === 'excluded',
                }"
              >
                {{ product.status === 'original' ? 'Oryginal' : product.status === 'modified' ? 'Zmieniony' : 'Wykluczony' }}
              </span>
            </td>
            <td class="px-4 py-2 text-right">
              <button
                class="text-sm text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
                @click="openEdit(product)"
              >
                Edytuj
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ProductOverrideModal
      :show="showModal"
      :product="editProduct"
      @close="showModal = false"
      @save="handleSave"
      @restore="handleRestore"
    />
  </div>
</template>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/FeedOutProducts.vue frontend/src/components/ProductOverrideModal.vue frontend/src/stores/feedsOut.ts
git commit -m "feat: add product override components and store methods"
```

---

### Task 7: Frontend — EAN Coverage + Description Template Rule components

**Files:**
- Create: `frontend/src/components/EanCoverage.vue`
- Create: `frontend/src/components/DescriptionTemplateRule.vue`

- [ ] **Step 1: Create EanCoverage.vue**

```vue
<!-- frontend/src/components/EanCoverage.vue -->
<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  fieldCoverage: any[]
  issues: any[]
}>()

const eanField = computed(() => {
  return props.fieldCoverage.find(f =>
    ['g:gtin', 'code', 'ean'].includes(f.field)
  )
})

const eanIssues = computed(() => {
  return props.issues.filter(i =>
    i.rule && (i.rule.includes('ean') || i.rule.includes('gtin'))
  )
})

const show = computed(() => eanField.value != null)
</script>

<template>
  <div v-if="show" class="bg-white border rounded-lg p-4">
    <h3 class="text-sm font-medium text-gray-700 mb-3">Pokrycie EAN/GTIN</h3>

    <div class="flex items-center gap-3 mb-2">
      <div class="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
        <div
          class="h-full rounded-full"
          :class="eanField!.percent >= 80 ? 'bg-green-500' : eanField!.percent >= 40 ? 'bg-yellow-400' : 'bg-red-400'"
          :style="{ width: eanField!.percent + '%' }"
        />
      </div>
      <span class="text-sm font-medium text-gray-700 w-24 text-right">
        {{ eanField!.filled }}/{{ eanField!.total }} ({{ eanField!.percent }}%)
      </span>
    </div>

    <p class="text-xs text-blue-600 bg-blue-50 p-2 rounded mb-3">
      Produkty z poprawnym kodem EAN maja ok. 40% wiecej wyswietlen na Google Shopping.
    </p>

    <div v-if="eanIssues.length > 0">
      <p class="text-xs font-medium text-gray-600 mb-1">Bledne kody EAN ({{ eanIssues.length }}):</p>
      <div class="space-y-1 max-h-32 overflow-y-auto">
        <div v-for="(issue, idx) in eanIssues.slice(0, 10)" :key="idx" class="text-xs text-red-600 flex gap-1">
          <span>x</span>
          <span>{{ issue.product_name }} — {{ issue.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Create DescriptionTemplateRule.vue**

```vue
<!-- frontend/src/components/DescriptionTemplateRule.vue -->
<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  sampleProduct: Record<string, any> | null
}>()

const emit = defineEmits<{
  confirm: [rule: any]
  cancel: []
}>()

const field = ref('desc')
const template = ref('')

const availableKeys = computed(() => {
  if (!props.sampleProduct) return []
  return Object.entries(props.sampleProduct)
    .filter(([_, v]) => typeof v === 'string' || typeof v === 'number')
    .map(([k]) => k)
})

const preview = computed(() => {
  if (!props.sampleProduct || !template.value) return ''
  let result = template.value
  for (const [key, val] of Object.entries(props.sampleProduct)) {
    if (typeof val === 'string' || typeof val === 'number') {
      result = result.replace(new RegExp(`\\{${key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\}`, 'g'), String(val).trim())
    }
  }
  result = result.replace(/\{[^}]+\}/g, '')
  result = result.replace(/ +/g, ' ').trim()
  return result
})

function insertKey(key: string) {
  template.value += `{${key}}`
}

function handleConfirm() {
  emit('confirm', {
    type: 'description_template',
    field: field.value,
    template: template.value,
  })
}
</script>

<template>
  <div class="p-3 bg-white border border-indigo-200 rounded-md space-y-3">
    <div class="text-sm font-medium text-gray-700">Szablon opisu</div>

    <div>
      <label class="text-xs text-gray-500">Pole docelowe</label>
      <select v-model="field" class="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm mt-1">
        <option value="desc">desc</option>
        <option value="description">description</option>
        <option value="name">name</option>
        <option value="title">title</option>
      </select>
    </div>

    <div>
      <label class="text-xs text-gray-500">Szablon (uzyj {nazwa_pola} jako placeholder)</label>
      <textarea
        v-model="template"
        rows="3"
        class="w-full border border-gray-300 rounded-md px-3 py-2 text-sm mt-1 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        placeholder="np. Kup {name} marki {brand}. {desc}"
      />
    </div>

    <!-- Available placeholders -->
    <div v-if="availableKeys.length > 0">
      <label class="text-xs text-gray-500">Dostepne pola (kliknij aby wstawic):</label>
      <div class="flex flex-wrap gap-1 mt-1">
        <button
          v-for="key in availableKeys"
          :key="key"
          class="px-2 py-0.5 text-xs bg-gray-100 hover:bg-indigo-100 text-gray-600 hover:text-indigo-700 rounded cursor-pointer"
          @click="insertKey(key)"
        >
          {{'{'}}{{ key }}{{'}'}}
        </button>
      </div>
    </div>

    <!-- Preview -->
    <div v-if="preview" class="bg-gray-50 rounded p-2">
      <label class="text-xs text-gray-500">Podglad (pierwszy produkt):</label>
      <p class="text-sm text-gray-700 mt-1">{{ preview }}</p>
    </div>

    <div class="flex gap-2">
      <button class="py-1 px-3 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 cursor-pointer" @click="handleConfirm">Dodaj</button>
      <button class="py-1 px-3 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 cursor-pointer" @click="emit('cancel')">Anuluj</button>
    </div>
  </div>
</template>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/EanCoverage.vue frontend/src/components/DescriptionTemplateRule.vue
git commit -m "feat: add EAN coverage and description template rule components"
```

---

### Task 8: Frontend — Update FeedOutDetailView

**Files:**
- Modify: `frontend/src/views/FeedOutDetailView.vue`

- [ ] **Step 1: Add imports and integrate new components**

Add imports at top of `<script setup>`:

```typescript
import FeedOutProducts from '../components/FeedOutProducts.vue'
import EanCoverage from '../components/EanCoverage.vue'
import DescriptionTemplateRule from '../components/DescriptionTemplateRule.vue'
```

Add `description_template` to `ruleTypeLabels`:
```typescript
description_template: 'Szablon opisu',
```

Add to `ruleDescription` function:
```typescript
case 'description_template': return `Szablon opisu: "${(rule.template || '').substring(0, 50)}..." -> ${rule.field || 'desc'}`
```

Update `selectRuleType` to handle description_template — it should set `pendingRuleType` (same as filter_exclude).

- [ ] **Step 2: Add Products section to template**

After the "Category Mapping" section and before the "Link section", add:

```html
      <!-- Products section -->
      <section class="mb-10">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">
          Produkty
        </h2>
        <FeedOutProducts :feed-out-id="feedId" />
      </section>
```

- [ ] **Step 3: Add EanCoverage to quality section**

In the quality score section, after the "Pokrycie pol" div and before the "Problemy" div, add:

```html
          <EanCoverage
            v-if="validation.field_coverage?.length && validation.issues?.length"
            :field-coverage="validation.field_coverage"
            :issues="validation.issues"
            class="mt-4"
          />
```

- [ ] **Step 4: Handle description_template rule type in pending rule UI**

In the pending rule input section, add a template for `description_template`:

```html
            <template v-if="pendingRuleType === 'description_template'">
              <DescriptionTemplateRule
                :sample-product="sampleProduct"
                @confirm="(rule) => { rules.push(rule); pendingRuleType = null }"
                @cancel="cancelPendingRule"
              />
            </template>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/FeedOutDetailView.vue
git commit -m "feat: integrate products, EAN coverage, description template into feed out view"
```

---

### Task 9: Frontend — Feed creation wizard

**Files:**
- Modify: `frontend/src/views/FeedOutCreateView.vue`

- [ ] **Step 1: Replace FeedOutCreateView with 3-step wizard**

Replace the entire file content:

```vue
<!-- frontend/src/views/FeedOutCreateView.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFeedsOutStore } from '../stores/feedsOut'

const route = useRoute()
const router = useRouter()
const store = useFeedsOutStore()

const feedInId = Number(route.query.feed_in_id)
const step = ref(1)
const selectedPlatform = ref('')
const platformInfo = ref<any>(null)
const platforms = ref<any[]>([])
const name = ref('')
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    platforms.value = await store.getPlatforms()
  } catch {}
})

async function selectPlatform(platform: string) {
  selectedPlatform.value = platform
  try {
    platformInfo.value = await store.getPlatformInfo(platform)
  } catch {}
  step.value = 2
}

function goBack() {
  if (step.value === 2) {
    step.value = 1
    platformInfo.value = null
  } else if (step.value === 3) {
    step.value = 2
  }
}

function goToStep3() {
  step.value = 3
}

async function handleCreate() {
  if (!name.value.trim()) {
    error.value = 'Nazwa jest wymagana'
    return
  }
  error.value = ''
  loading.value = true
  try {
    const templateMap: Record<string, string | undefined> = {
      ceneo: 'ceneo',
      allegro: 'allegro',
      gmc: undefined,
      facebook: undefined,
      skapiec: undefined,
      domodi: undefined,
      custom: undefined,
    }
    const feed = await store.createFeed({
      feed_in_id: feedInId,
      name: name.value.trim(),
      type: selectedPlatform.value,
      template: templateMap[selectedPlatform.value],
    })
    router.push(`/feeds-out/${feed.id}`)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Blad podczas tworzenia feedu'
  } finally {
    loading.value = false
  }
}

const platformIcons: Record<string, string> = {
  ceneo: 'Ceneo',
  gmc: 'Google',
  facebook: 'Facebook',
  allegro: 'Allegro',
  skapiec: 'Skapiec',
  domodi: 'Domodi',
}
</script>

<template>
  <div class="max-w-3xl mx-auto py-10 px-4">
    <!-- Progress -->
    <div class="flex items-center gap-2 mb-8">
      <div v-for="s in 3" :key="s" class="flex items-center gap-2">
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
          :class="step >= s ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'"
        >
          {{ s }}
        </div>
        <span class="text-sm" :class="step >= s ? 'text-gray-900' : 'text-gray-400'">
          {{ s === 1 ? 'Platforma' : s === 2 ? 'Informacje' : 'Utworz' }}
        </span>
        <div v-if="s < 3" class="w-8 h-px bg-gray-300" />
      </div>
    </div>

    <!-- Step 1: Platform selection -->
    <div v-if="step === 1">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Wybierz platforme</h1>
      <p class="text-sm text-gray-500 mb-6">Na jaka platforme chcesz wygenerowac feed produktowy?</p>

      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <button
          v-for="p in platforms"
          :key="p.platform"
          class="border-2 rounded-lg p-5 text-left cursor-pointer transition-colors hover:border-indigo-300 hover:bg-indigo-50"
          :class="selectedPlatform === p.platform ? 'border-indigo-600 bg-indigo-50' : 'border-gray-200'"
          @click="selectPlatform(p.platform)"
        >
          <div class="font-semibold text-gray-900 mb-1">{{ p.name }}</div>
          <div class="text-xs text-gray-500 mb-2">{{ p.description }}</div>
          <div class="text-xs text-indigo-600 font-medium">{{ p.required_count }} pol wymaganych</div>
        </button>
      </div>
    </div>

    <!-- Step 2: Platform info -->
    <div v-if="step === 2 && platformInfo">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ platformInfo.name }}</h1>
      <p class="text-sm text-gray-500 mb-6">{{ platformInfo.description }}</p>

      <div class="space-y-6">
        <!-- Required fields -->
        <div>
          <h2 class="text-sm font-semibold text-gray-700 mb-2">Pola wymagane</h2>
          <div class="space-y-2">
            <div v-for="f in platformInfo.required_fields" :key="f.field" class="flex items-start gap-2 text-sm">
              <span class="text-green-500 mt-0.5 shrink-0">V</span>
              <div>
                <span class="font-medium text-gray-800">{{ f.field }}</span>
                <span class="text-gray-500 ml-1">— {{ f.description }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recommended fields -->
        <div>
          <h2 class="text-sm font-semibold text-gray-700 mb-2">Pola zalecane</h2>
          <div class="space-y-2">
            <div v-for="f in platformInfo.recommended_fields" :key="f.field" class="flex items-start gap-2 text-sm">
              <span class="text-gray-400 mt-0.5 shrink-0">o</span>
              <div>
                <span class="font-medium text-gray-600">{{ f.field }}</span>
                <span class="text-gray-500 ml-1">— {{ f.description }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tips -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 class="text-sm font-semibold text-blue-800 mb-2">Wskazowki</h2>
          <ul class="space-y-1">
            <li v-for="(tip, idx) in platformInfo.tips" :key="idx" class="text-sm text-blue-700 flex gap-2">
              <span class="shrink-0">-</span>
              <span>{{ tip }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="flex items-center gap-4 mt-8">
        <button class="text-sm text-gray-600 hover:text-gray-800 cursor-pointer" @click="goBack">Wstecz</button>
        <button class="py-2 px-6 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-md cursor-pointer" @click="goToStep3">Dalej</button>
      </div>
    </div>

    <!-- Step 3: Name and create -->
    <div v-if="step === 3">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Utworz feed wyjsciowy</h1>

      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">{{ error }}</div>

      <div class="bg-gray-50 border rounded-lg p-4 mb-6">
        <div class="text-sm text-gray-500">Platforma: <span class="font-medium text-gray-900">{{ platformInfo?.name }}</span></div>
        <div class="text-sm text-gray-500 mt-1">Pola wymagane: <span class="font-medium text-gray-900">{{ platformInfo?.required_fields?.length }}</span></div>
      </div>

      <div class="mb-6">
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Nazwa feeda</label>
        <input
          id="name"
          v-model="name"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          :placeholder="`np. ${platformInfo?.name} - Moj Sklep`"
        />
      </div>

      <div class="flex items-center gap-4">
        <button class="text-sm text-gray-600 hover:text-gray-800 cursor-pointer" @click="goBack">Wstecz</button>
        <button
          :disabled="loading"
          class="py-2 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium rounded-md cursor-pointer"
          @click="handleCreate"
        >
          {{ loading ? 'Tworzenie...' : 'Utworz feed' }}
        </button>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/FeedOutCreateView.vue
git commit -m "feat: replace feed create form with 3-step wizard"
```

---

### Task 10: Run full test suite and verify

- [ ] **Step 1: Run all backend tests**

Run: `cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/ -v --ignore=venv`
Expected: All pass (except the pre-existing plan limit test)

- [ ] **Step 2: Verify frontend builds**

Run: `cd frontend && npx vite build`
Expected: Build succeeds

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: Phase 2 complete — overrides, description templates, EAN dashboard, wizard"
```
