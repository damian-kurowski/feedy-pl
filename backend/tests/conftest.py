import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.limiter import limiter

limiter.enabled = False

from app.config import settings

engine = create_engine(settings.database_url_sync)
TestingSession = sessionmaker(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
