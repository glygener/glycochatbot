from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from api.dependencies import get_session_store
from api.schemas import (
    SessionCreateResponse,
    SessionMessagesResponse,
    SessionSummaryResponse,
)
from api.service import get_orchestrator
from session.users import UserRecord

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
def create_session(user: UserRecord = Depends(get_current_user)) -> SessionCreateResponse:
    session = get_session_store().create_session(user.user_id)
    return SessionCreateResponse(session_id=session.id, created_at=session.created_at)


@router.get("", response_model=list[SessionSummaryResponse])
def list_sessions(user: UserRecord = Depends(get_current_user)) -> list[SessionSummaryResponse]:
    store = get_session_store()
    return [
        SessionSummaryResponse(
            session_id=session.id,
            created_at=session.created_at,
            preview=session.preview,
        )
        for session in store.list_sessions(user.user_id)
    ]


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    user: UserRecord = Depends(get_current_user),
) -> dict[str, bool]:
    deleted = get_session_store().delete_session(session_id, user.user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"deleted": True}


@router.get("/{session_id}/messages", response_model=SessionMessagesResponse)
def get_messages(
    session_id: str,
    user: UserRecord = Depends(get_current_user),
) -> SessionMessagesResponse:
    return get_orchestrator().get_session_messages(session_id, user.user_id)
