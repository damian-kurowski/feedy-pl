"""Tests for feed fetch & parse tasks."""

import uuid
from pathlib import Path
from unittest.mock import patch

from app.models.feed_in import FeedIn
from app.models.product import ProductIn
from app.models.user import User
from app.models.xml_element import XmlElementIn
from app.services.auth_service import hash_password
from app.tasks.feed_tasks import fetch_and_parse_sync

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_fetch_and_parse_sync_gmc(db_session):
    xml_bytes = (FIXTURES_DIR / "sample_gmc.xml").read_bytes()

    # Create user
    user = User(
        email=f"tasktest-{uuid.uuid4().hex[:8]}@example.com",
        password_hash=hash_password("secret123"),
        plan_id=1,
    )
    db_session.add(user)
    db_session.flush()

    # Create feed
    feed = FeedIn(
        user_id=user.id,
        name="Test GMC Feed",
        source_url="https://example.com/feed.xml",
        record_path="feed/entry",
        product_name="feed/entry/title",
    )
    db_session.add(feed)
    db_session.flush()

    with patch(
        "app.tasks.feed_tasks.fetch_xml_from_url", return_value=xml_bytes
    ):
        fetch_and_parse_sync(db_session, feed.id)

    db_session.refresh(feed)
    assert feed.fetch_status == "success"
    assert feed.last_fetched_at is not None

    xml_elements = (
        db_session.query(XmlElementIn)
        .filter(XmlElementIn.feed_in_id == feed.id)
        .all()
    )
    assert len(xml_elements) > 0

    products = (
        db_session.query(ProductIn)
        .filter(ProductIn.feed_in_id == feed.id)
        .all()
    )
    assert len(products) == 2
    assert products[0].product_name == "Płyn do montażu folii"
