import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from session.users import UserRecord, UserStore

ALGORITHM = "HS256"
TOKEN_HOURS = 24 * 14
security = HTTPBearer(auto_error=False)


def auth_secret() -> str:
    return os.getenv("AUTH_SECRET", "glycochat-dev-secret-change-me-32b")


def create_access_token(user: UserRecord) -> str:
    payload = {
        "sub": user.user_id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, auth_secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, auth_secret(), algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token.") from exc


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> UserRecord:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required.")
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload.")
    user = UserStore().get_by_id(str(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")
    if not user.is_enabled:
        raise HTTPException(
            status_code=403,
            detail=(
                "Your User ID does not have access to this application. "
                "Contact your system administrator to enable your account."
            ),
        )
    return user
