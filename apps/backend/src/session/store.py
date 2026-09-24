import json
import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from glyco_chroma.settings import find_project_root


def _resolve_db_path(db_path: Path | None) -> Path:
    if db_path is not None:
        return db_path
    root = find_project_root()
    data_dir = Path(os.getenv("DATA_DIR", root / "data"))
    return data_dir / "chat.db"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SessionSummary:
    id: str
    created_at: str
    preview: str


@dataclass
class SessionRecord:
    id: str
    created_at: str
    user_display_name: str | None


@dataclass
class MessageRecord:
    id: str
    session_id: str
    role: str
    content: str
    question_type: str | None
    citations_json: str | None
    created_at: str


class SessionStore:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = _resolve_db_path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    user_display_name TEXT
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    question_type TEXT,
                    citations_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
                );

                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id, created_at);
                """
            )

    def create_session(self) -> SessionRecord:
        session_id = str(uuid.uuid4())
        created_at = _utc_now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO chat_sessions (id, created_at, user_display_name) VALUES (?, ?, ?)",
                (session_id, created_at, None),
            )
        return SessionRecord(id=session_id, created_at=created_at, user_display_name=None)

    def get_session(self, session_id: str) -> SessionRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, created_at, user_display_name FROM chat_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return SessionRecord(
            id=row["id"],
            created_at=row["created_at"],
            user_display_name=row["user_display_name"],
        )

    def update_display_name(self, session_id: str, name: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE chat_sessions SET user_display_name = ? WHERE id = ?",
                (name, session_id),
            )

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        question_type: str | None = None,
        citations: list | None = None,
    ) -> MessageRecord:
        message_id = str(uuid.uuid4())
        created_at = _utc_now()
        citations_json = json.dumps(citations) if citations else None
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO messages
                (id, session_id, role, content, question_type, citations_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (message_id, session_id, role, content, question_type, citations_json, created_at),
            )
        return MessageRecord(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            question_type=question_type,
            citations_json=citations_json,
            created_at=created_at,
        )

    def get_messages(self, session_id: str) -> list[MessageRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, session_id, role, content, question_type, citations_json, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC
                """,
                (session_id,),
            ).fetchall()
        return [
            MessageRecord(
                id=row["id"],
                session_id=row["session_id"],
                role=row["role"],
                content=row["content"],
                question_type=row["question_type"],
                citations_json=row["citations_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_user_questions(self, session_id: str) -> list[str]:
        return [
            message.content
            for message in self.get_messages(session_id)
            if message.role == "user"
        ]

    def list_sessions(self, limit: int = 30) -> list[SessionSummary]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at
                FROM chat_sessions
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        summaries: list[SessionSummary] = []
        for row in rows:
            preview = "New chat"
            messages = self.get_messages(row["id"])
            for message in messages:
                if message.role == "user":
                    preview = message.content[:60] + ("..." if len(message.content) > 60 else "")
                    break
            summaries.append(
                SessionSummary(
                    id=row["id"],
                    created_at=row["created_at"],
                    preview=preview,
                )
            )
        return summaries
