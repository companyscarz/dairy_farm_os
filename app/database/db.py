from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from ..config import settings

_pool: ConnectionPool | None = None


def init_pool() -> None:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=settings.database_url,
            min_size=settings.db_min_size,
            max_size=settings.db_max_size,
            kwargs={"row_factory": dict_row},
            open=True,
        )


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


@contextmanager
def get_db() -> Iterator[psycopg.Connection]:
    if _pool is None:
        init_pool()
    assert _pool is not None
    with _pool.connection() as conn:
        yield conn


def fetch_one(sql: str, params: tuple = ()):
    with get_db() as db:
        return db.execute(sql, params).fetchone()


def fetch_all(sql: str, params: tuple = ()):
    with get_db() as db:
        return db.execute(sql, params).fetchall()


def execute(sql: str, params: tuple = ()) -> None:
    with get_db() as db:
        db.execute(sql, params)
        db.commit()


def execute_returning(sql: str, params: tuple = ()):
    with get_db() as db:
        row = db.execute(sql, params).fetchone()
        db.commit()
        return row


def execute_script(path: Path) -> None:
    script = path.read_text(encoding="utf-8")
    with get_db() as db:
        db.execute(script)
        db.commit()
