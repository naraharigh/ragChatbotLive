"""Create application tables without seeding or replacing existing data."""

from pathlib import Path

import psycopg2

from app.config import settings


def initialize_database() -> None:
    migration = Path(__file__).resolve().parents[1] / "seed/schema.sql"
    conn = psycopg2.connect(settings.database_url, connect_timeout=10)
    try:
        with conn:
            with conn.cursor() as cursor:
                # Serialize initialization when multiple instances start together.
                cursor.execute("SELECT pg_advisory_xact_lock(734102001)")
                cursor.execute(migration.read_text(encoding="utf-8"))
    finally:
        conn.close()
    print("Database initialization complete: application tables ready.", flush=True)


if __name__ == "__main__":
    initialize_database()
