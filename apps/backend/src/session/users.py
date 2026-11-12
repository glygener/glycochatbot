import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from session.db import connect, fetchone, init_db

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


@dataclass
class UserRecord:
    user_id: str
    username: str
    first_name: str
    last_name: str
    email: str | None
    created_at: str


def _format_ts(value) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


class UserStore:
    def __init__(self) -> None:
        init_db()

    def register(
        self,
        username: str,
        first_name: str,
        last_name: str,
        email: str | None = None,
    ) -> UserRecord:
        username = username.strip()
        first_name = first_name.strip()
        last_name = last_name.strip()
        email = (email or "").strip() or None

        if not USERNAME_RE.match(username):
            raise ValueError(
                "Username must be 3–32 characters and use only letters, numbers, or underscore."
            )
        if not first_name or not last_name:
            raise ValueError("First name and last name are required.")

        if self.get_by_username(username) is not None:
            raise ValueError("Username is already taken.")
        if email is not None:
            with connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM users WHERE email = %s", (email,))
                if fetchone(cursor) is not None:
                    raise ValueError("Email is already registered.")

        user_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (user_id, username, first_name, last_name, email, created_at)
                VALUES (%s::uuid, %s, %s, %s, %s, %s)
                """,
                (user_id, username.lower(), first_name, last_name, email, created_at),
            )

        return UserRecord(
            user_id=user_id,
            username=username.lower(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            created_at=_format_ts(created_at),
        )

    def get_by_username(self, username: str) -> UserRecord | None:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, username, first_name, last_name, email, created_at
                FROM users
                WHERE username = %s
                """,
                (username.strip().lower(),),
            )
            row = fetchone(cursor)
        if row is None:
            return None
        return UserRecord(
            user_id=str(row["user_id"]),
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            created_at=_format_ts(row["created_at"]),
        )

    def get_by_id(self, user_id: str) -> UserRecord | None:
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_id, username, first_name, last_name, email, created_at
                FROM users
                WHERE user_id = %s::uuid
                """,
                (user_id,),
            )
            row = fetchone(cursor)
        if row is None:
            return None
        return UserRecord(
            user_id=str(row["user_id"]),
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            created_at=_format_ts(row["created_at"]),
        )
