import os
from contextlib import contextmanager
from functools import lru_cache
from urllib.parse import urlparse

import pg8000.dbapi


def database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://glyco:glyco@127.0.0.1:5432/glycochat",
    )


def _connect_kwargs() -> dict:
    parsed = urlparse(database_url())
    return {
        "user": parsed.username or "glyco",
        "password": parsed.password or "glyco",
        "host": parsed.hostname or "127.0.0.1",
        "port": parsed.port or 5432,
        "database": (parsed.path or "/glycochat").lstrip("/") or "glycochat",
    }


def _rows_as_dicts(cursor) -> list[dict]:
    if cursor.description is None:
        return []
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _row_as_dict(cursor) -> dict | None:
    rows = _rows_as_dicts(cursor)
    return rows[0] if rows else None


@contextmanager
def connect():
    conn = pg8000.dbapi.connect(**_connect_kwargs())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@lru_cache
def _ensure_schema() -> bool:
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY,
                username VARCHAR(64) NOT NULL UNIQUE,
                first_name VARCHAR(120) NOT NULL,
                last_name VARCHAR(120) NOT NULL,
                email VARCHAR(255) UNIQUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id UUID PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                title VARCHAR(500),
                user_display_name VARCHAR(255),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                ended_at TIMESTAMPTZ
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id UUID PRIMARY KEY,
                session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
                role VARCHAR(32) NOT NULL,
                content TEXT NOT NULL,
                question_type VARCHAR(64),
                citations_json TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sessions_user
                ON chat_sessions(user_id, created_at DESC)
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id, created_at)
            """
        )
    return True


def init_db() -> None:
    _ensure_schema()


def fetchone(cursor) -> dict | None:
    return _row_as_dict(cursor)


def fetchall(cursor) -> list[dict]:
    return _rows_as_dicts(cursor)
