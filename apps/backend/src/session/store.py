import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from session.db import connect, fetchall, fetchone, init_db


def _utc_now():
    return datetime.now(timezone.utc)


def _format_ts(value) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


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
    user_id: str | None = None
    title: str | None = None


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
    def __init__(self) -> None:
        init_db()

    def create_session(self, user_id: str) -> SessionRecord:
        session_id = str(uuid.uuid4())
        created_at = _utc_now()
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO chat_sessions
                    (session_id, user_id, title, user_display_name, is_active, created_at)
                VALUES (%s::uuid, %s::uuid, %s, NULL, TRUE, %s)
                """,
                (session_id, user_id, "New chat", created_at),
            )
        return SessionRecord(
            id=session_id,
            created_at=_format_ts(created_at),
            user_display_name=None,
            user_id=user_id,
            title="New chat",
        )

    def get_session(self, session_id: str, user_id: str | None = None) -> SessionRecord | None:
        query = """
            SELECT session_id, user_id, title, user_display_name, created_at, is_active
            FROM chat_sessions
            WHERE session_id = %s::uuid AND is_active = TRUE
        """
        params: list = [session_id]
        if user_id is not None:
            query += " AND user_id = %s::uuid"
            params.append(user_id)

        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = fetchone(cursor)
        if row is None:
            return None
        return SessionRecord(
            id=str(row["session_id"]),
            created_at=_format_ts(row["created_at"]),
            user_display_name=row["user_display_name"],
            user_id=str(row["user_id"]),
            title=row["title"],
        )

    def delete_session(self, session_id: str, user_id: str) -> bool:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE chat_sessions
                SET is_active = FALSE, ended_at = NOW()
                WHERE session_id = %s::uuid AND user_id = %s::uuid AND is_active = TRUE
                """,
                (session_id, user_id),
            )
            return cursor.rowcount > 0

    def update_display_name(self, session_id: str, name: str) -> None:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE chat_sessions
                SET user_display_name = %s
                WHERE session_id = %s::uuid
                """,
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
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages
                    (message_id, session_id, role, content, question_type, citations_json, created_at)
                VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, %s)
                """,
                (
                    message_id,
                    session_id,
                    role,
                    content,
                    question_type,
                    citations_json,
                    created_at,
                ),
            )
            if role == "user":
                preview = content[:60] + ("..." if len(content) > 60 else "")
                cursor.execute(
                    """
                    UPDATE chat_sessions
                    SET title = %s
                    WHERE session_id = %s::uuid AND (title IS NULL OR title = 'New chat')
                    """,
                    (preview, session_id),
                )
        return MessageRecord(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            question_type=question_type,
            citations_json=citations_json,
            created_at=_format_ts(created_at),
        )

    def get_messages(self, session_id: str) -> list[MessageRecord]:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT message_id, session_id, role, content, question_type,
                       citations_json, created_at
                FROM messages
                WHERE session_id = %s::uuid
                ORDER BY created_at ASC
                """,
                (session_id,),
            )
            rows = fetchall(cursor)
        return [
            MessageRecord(
                id=str(row["message_id"]),
                session_id=str(row["session_id"]),
                role=row["role"],
                content=row["content"],
                question_type=row["question_type"],
                citations_json=row["citations_json"],
                created_at=_format_ts(row["created_at"]),
            )
            for row in rows
        ]

    def get_user_questions(self, session_id: str) -> list[str]:
        return [
            message.content
            for message in self.get_messages(session_id)
            if message.role == "user"
        ]

    def list_sessions(self, user_id: str, limit: int = 30) -> list[SessionSummary]:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT s.session_id, s.created_at, s.title,
                       (
                           SELECT m.content
                           FROM messages m
                           WHERE m.session_id = s.session_id AND m.role = 'user'
                           ORDER BY m.created_at ASC
                           LIMIT 1
                       ) AS first_user_message
                FROM chat_sessions s
                WHERE s.user_id = %s::uuid AND s.is_active = TRUE
                ORDER BY s.created_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            rows = fetchall(cursor)

        summaries: list[SessionSummary] = []
        for row in rows:
            preview = row["title"] or "New chat"
            if row["first_user_message"]:
                text = row["first_user_message"]
                preview = text[:60] + ("..." if len(text) > 60 else "")
            summaries.append(
                SessionSummary(
                    id=str(row["session_id"]),
                    created_at=_format_ts(row["created_at"]),
                    preview=preview,
                )
            )
        return summaries
