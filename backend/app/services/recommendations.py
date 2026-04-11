"""Smart feed recommendations and alerts engine."""

from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feed_in import FeedIn
from app.models.feed_out import FeedOut
from app.models.product import ProductIn
from app.services.validators import validate_feed


async def generate_recommendations(db: AsyncSession, user_id: int) -> dict:
    """Analyze user's feeds and return recommendations, alerts, and suggestions."""
    recommendations = []
    alerts = []
    suggestions = []
    stats = {}

    now = datetime.now(timezone.utc)

    # Get all user feeds
    feeds_in_result = await db.execute(
        select(FeedIn).where(FeedIn.user_id == user_id)
    )
    feeds_in = feeds_in_result.scalars().all()

    feeds_out_result = await db.execute(
        select(FeedOut).where(FeedOut.user_id == user_id)
    )
    feeds_out = feeds_out_result.scalars().all()

    # Stats
    total_products = 0
    for fi in feeds_in:
        count_result = await db.execute(
            select(func.count()).select_from(ProductIn).where(ProductIn.feed_in_id == fi.id)
        )
        total_products += count_result.scalar() or 0

    stats = {
        "total_feeds_in": len(feeds_in),
        "total_feeds_out": len(feeds_out),
        "total_products": total_products,
    }

    # --- ALERTS (problems that need attention) ---

    # Check for feed errors
    for fi in feeds_in:
        if fi.fetch_status == "error":
            alerts.append({
                "type": "feed_error",
                "severity": "critical",
                "icon": "error",
                "title": f"Feed \"{fi.name}\" ma błąd",
                "description": fi.fetch_error[:200] if fi.fetch_error else "Nieznany błąd podczas pobierania feedu",
                "action": {"label": "Zobacz szczegóły", "url": f"/feeds-in/{fi.id}"},
                "feed_id": fi.id,
            })

        # Check for stale feeds (not refreshed in 48h when auto-refresh is on)
        if fi.refresh_interval and fi.last_fetched_at:
            hours_since = (now - fi.last_fetched_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600
            if hours_since > 48:
                alerts.append({
                    "type": "stale_feed",
                    "severity": "warning",
                    "icon": "clock",
                    "title": f"Feed \"{fi.name}\" nie odświeżył się od {int(hours_since)}h",
                    "description": "Automatyczne odświeżanie może nie działać. Sprawdź źródło danych.",
                    "action": {"label": "Odśwież teraz", "url": f"/feeds-in/{fi.id}"},
                    "feed_id": fi.id,
                })

        # Check for pending feeds (never fetched)
        if fi.fetch_status == "pending" and fi.last_fetched_at is None:
            alerts.append({
                "type": "pending_feed",
                "severity": "info",
                "icon": "info",
                "title": f"Feed \"{fi.name}\" czeka na pobranie",
                "description": "Kliknij aby pobrać XML i przeanalizować produkty.",
                "action": {"label": "Pobierz XML", "url": f"/feeds-in/{fi.id}"},
                "feed_id": fi.id,
            })

    # --- RECOMMENDATIONS (things to improve) ---

    # Validate each output feed and find issues
    for fo in feeds_out:
        products_result = await db.execute(
            select(ProductIn).where(ProductIn.feed_in_id == fo.feed_in_id).limit(200)
        )
        products = [{"id": p.id, "product_value": p.product_value} for p in products_result.scalars().all()]

        if not products:
            continue

        result = validate_feed(fo.type, products)

        if result.quality_score < 70:
            error_count = sum(1 for i in result.issues if i.level == "error")
            warning_count = sum(1 for i in result.issues if i.level == "warning")
            recommendations.append({
                "type": "low_quality",
                "severity": "warning",
                "icon": "quality",
                "title": f"Feed \"{fo.name}\" — jakość {result.quality_score}%",
                "description": f"{error_count} błędów, {warning_count} ostrzeżeń. Napraw aby poprawić widoczność produktów.",
                "action": {"label": "Napraw błędy", "url": f"/feeds-out/{fo.id}"},
                "feed_out_id": fo.id,
                "quality_score": result.quality_score,
            })

        # Check EAN coverage
        ean_field = None
        for fc in result.field_coverage:
            if fc.field in ("g:gtin", "code", "ean"):
                ean_field = fc
                break
        if ean_field and ean_field.percent < 50 and fo.type in ("gmc", "ceneo"):
            recommendations.append({
                "type": "low_ean",
                "severity": "info",
                "icon": "barcode",
                "title": f"Tylko {int(ean_field.percent)}% produktów ma EAN",
                "description": "Produkty z EAN mają ~40% więcej wyświetleń na Google Shopping i lepsze dopasowanie na Ceneo.",
                "action": {"label": "Zobacz produkty", "url": f"/feeds-out/{fo.id}"},
                "feed_out_id": fo.id,
            })

        # Check missing images
        img_field = None
        for fc in result.field_coverage:
            if fc.field in ("g:image_link", "imgs", "image", "img"):
                img_field = fc
                break
        if img_field and img_field.percent < 90:
            missing_count = img_field.total - img_field.filled
            recommendations.append({
                "type": "missing_images",
                "severity": "warning",
                "icon": "image",
                "title": f"{missing_count} produktów bez zdjęcia w \"{fo.name}\"",
                "description": "Produkty bez zdjęć są zwykle odrzucane przez porównywarki.",
                "action": {"label": "Dodaj zdjęcia", "url": f"/feeds-out/{fo.id}"},
                "feed_out_id": fo.id,
            })

    # --- SUGGESTIONS (growth opportunities) ---

    # Suggest new platforms
    existing_types = {fo.type for fo in feeds_out}
    platform_suggestions = {
        "ceneo": {"name": "Ceneo", "desc": "Największa porównywarka cen w Polsce"},
        "gmc": {"name": "Google Shopping", "desc": "Reklamy produktowe w Google"},
        "allegro": {"name": "Allegro", "desc": "Największy marketplace w Polsce"},
        "facebook": {"name": "Facebook Catalog", "desc": "Reklamy produktowe na FB/IG"},
        "skapiec": {"name": "Skąpiec", "desc": "Porównywarka cen Wirtualna Polska"},
    }
    for ptype, pinfo in platform_suggestions.items():
        if ptype not in existing_types and feeds_in:
            suggestions.append({
                "type": "new_platform",
                "icon": "plus",
                "title": f"Dodaj feed {pinfo['name']}",
                "description": f"{pinfo['desc']}. Masz już dane — konfiguracja zajmie 30 sekund.",
                "action": {"label": "Utwórz feed", "url": f"/feeds-out/new?feed_in_id={feeds_in[0].id}"},
                "platform": ptype,
            })
            if len(suggestions) >= 3:
                break

    # Suggest auto-refresh if not set
    for fi in feeds_in:
        if fi.refresh_interval is None and fi.fetch_status == "success":
            suggestions.append({
                "type": "enable_refresh",
                "icon": "refresh",
                "title": f"Włącz auto-odświeżanie dla \"{fi.name}\"",
                "description": "Ceny i dostępność będą automatycznie aktualne. Ustaw co 1h, 6h lub 24h.",
                "action": {"label": "Ustaw", "url": f"/feeds-in/{fi.id}"},
                "feed_id": fi.id,
            })
            break  # Only suggest once

    return {
        "stats": stats,
        "alerts": sorted(alerts, key=lambda x: {"critical": 0, "warning": 1, "info": 2}.get(x["severity"], 3)),
        "recommendations": recommendations,
        "suggestions": suggestions[:3],
    }
