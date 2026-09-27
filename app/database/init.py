from pathlib import Path

from .db import execute_script, fetch_all, execute

BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / "migrations"


def initialize_database() -> None:
    with open(MIGRATIONS_DIR / "001_initial.sql", "r", encoding="utf-8") as f:
        script = f.read()
    from .db import get_db
    with get_db() as db:
        db.execute(script)
        db.commit()

    migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
    for migration in migrations[1:]:
        name = migration.name
        existing = fetch_all("SELECT name FROM schema_migrations WHERE name = %s", (name,))
        if existing:
            continue
        execute_script(migration)
        execute("INSERT INTO schema_migrations (name) VALUES (%s)", (name,))
