"""Celery tasks for fetching and parsing XML feeds."""

from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.celery_app import celery
from app.config import settings
from app.models.feed_change_log import FeedChangeLog
from app.models.feed_in import FeedIn
from app.models.product import ProductIn
from app.models.user import User
from app.models.xml_element import XmlElementIn
from app.services.email_service import send_feed_error_notification
from app.services.changelog_service import generate_changelog
from app.services.product_extractor import extract_products
from app.services.xml_parser import parse_xml_to_elements


def fetch_xml_from_url(url: str) -> bytes:
    """Fetch XML content from a URL."""
    response = httpx.get(url, timeout=60, follow_redirects=True)
    response.raise_for_status()
    return response.content


def fetch_and_parse_sync(session: Session, feed_in_id: int) -> None:
    """Fetch and parse a feed. Testable without Celery."""
    feed = session.get(FeedIn, feed_in_id)
    if feed is None:
        raise ValueError(f"FeedIn with id={feed_in_id} not found")

    feed.fetch_status = "fetching"
    session.commit()

    try:
        xml_bytes = fetch_xml_from_url(feed.source_url)

        # Generate changelog by comparing old vs new products
        old_products_q = session.query(ProductIn).filter(
            ProductIn.feed_in_id == feed_in_id,
            ProductIn.custom_product == False,  # noqa: E712
        ).all()
        old_products = [{"product_name": p.product_name, "product_value": p.product_value} for p in old_products_q]

        new_products_for_changelog = []
        if feed.record_path and feed.product_name:
            new_products_for_changelog = [
                {"product_name": p["product_name"], "product_value": p["product_value"]}
                for p in extract_products(xml_bytes, feed.record_path, feed.product_name)
            ]

        if old_products:
            changes = generate_changelog(old_products, new_products_for_changelog)
            for change in changes[:200]:  # limit to 200 changes per fetch
                session.add(FeedChangeLog(
                    feed_in_id=feed_in_id,
                    change_type=change["change_type"],
                    product_name=change["product_name"],
                    details=change.get("details"),
                ))

        # Delete old xml elements and non-custom products for this feed
        session.query(XmlElementIn).filter(
            XmlElementIn.feed_in_id == feed_in_id
        ).delete()
        session.query(ProductIn).filter(
            ProductIn.feed_in_id == feed_in_id,
            ProductIn.custom_product == False,  # noqa: E712
        ).delete()

        # Parse XML and save elements
        elements = parse_xml_to_elements(xml_bytes)
        for elem in elements:
            xml_el = XmlElementIn(
                feed_in_id=feed_in_id,
                path=elem["path"],
                parent_path=elem["parent_path"],
                level=elem["level"],
                element_name=elem["element_name"],
                value=elem["value"],
                is_leaf=elem["is_leaf"],
                attribute=elem["attribute"],
            )
            session.add(xml_el)

        # Extract products if record_path and product_name are set
        if feed.record_path and feed.product_name:
            products = extract_products(
                xml_bytes, feed.record_path, feed.product_name
            )
            for prod in products:
                product_in = ProductIn(
                    feed_in_id=feed_in_id,
                    product_name=prod["product_name"],
                    product_value=prod["product_value"],
                    custom_product=False,
                )
                session.add(product_in)

        feed.fetch_error = None
        feed.fetch_status = "success"
        feed.last_fetched_at = datetime.now(timezone.utc)
        session.commit()

    except Exception as e:
        session.rollback()
        feed.fetch_status = "error"
        feed.fetch_error = str(e)[:1024]
        session.commit()
        try:
            user = session.get(User, feed.user_id)
            if user:
                send_feed_error_notification(user.email, feed.name, str(e)[:500])
        except Exception:
            pass  # Don't fail the task if email fails
        raise


@celery.task(name="feedy.refresh_due_feeds")
def refresh_due_feeds_task() -> dict:
    """Check all feeds with refresh_interval and re-fetch if due."""
    engine = create_engine(settings.database_url_sync)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        feeds = session.execute(
            select(FeedIn).where(
                FeedIn.active == True,  # noqa: E712
                FeedIn.refresh_interval.isnot(None),
                FeedIn.record_path.isnot(None),
            )
        ).scalars().all()

        refreshed = []
        for feed in feeds:
            if feed.last_fetched_at is None:
                needs_refresh = True
            else:
                next_refresh = feed.last_fetched_at + timedelta(minutes=feed.refresh_interval)
                needs_refresh = now >= next_refresh

            if needs_refresh:
                try:
                    fetch_and_parse_sync(session, feed.id)
                    refreshed.append(feed.id)
                except Exception:
                    pass  # fetch_and_parse_sync already sets status to "error"

        return {"refreshed": refreshed, "checked": len(feeds)}
    finally:
        session.close()
        engine.dispose()


@celery.task(name="feedy.fetch_and_parse")
def fetch_and_parse_task(feed_in_id: int) -> dict:
    """Celery task wrapper for fetch_and_parse_sync."""
    engine = create_engine(settings.database_url_sync)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        fetch_and_parse_sync(session, feed_in_id)
        return {"status": "success", "feed_in_id": feed_in_id}
    finally:
        session.close()
        engine.dispose()
