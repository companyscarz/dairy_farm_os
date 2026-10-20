from pathlib import Path
from .db import get_db

BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / "migrations"


def initialize_database() -> None:
    """Apply SQL migrations safely when multiple Gunicorn workers start together."""
    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    with get_db() as db:
        db.execute("SELECT pg_advisory_xact_lock(81423917)")
        for migration in migrations:
            name = migration.name
            if name != "001_initial.sql":
                exists = db.execute("SELECT 1 FROM schema_migrations WHERE name=%s", (name,)).fetchone()
                if exists:
                    continue
            db.execute(migration.read_text(encoding="utf-8"))
            db.execute("INSERT INTO schema_migrations(name) VALUES(%s) ON CONFLICT(name) DO NOTHING", (name,))
        db.commit()
