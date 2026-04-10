"""One-off migration: add fetch_error column to feed_in table."""
from sqlalchemy import create_engine, text
from app.config import settings

if __name__ == "__main__":
    engine = create_engine(settings.database_url_sync)
    with engine.connect() as conn:
        conn.execute(
            text(
                "ALTER TABLE config.feed_in "
                "ADD COLUMN IF NOT EXISTS fetch_error VARCHAR(1024) DEFAULT NULL"
            )
        )
        conn.commit()
    engine.dispose()
    print("Done: fetch_error column added.")
