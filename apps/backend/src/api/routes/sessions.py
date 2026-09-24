from fastapi import APIRouter

from api.dependencies import get_session_store
from api.schemas import (
    SessionCreateResponse,
    SessionMessagesResponse,
    SessionSummaryResponse,
)
from api.service import get_orchestrator

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
def create_session() -> SessionCreateResponse:
    session = get_session_store().create_session()
    return SessionCreateResponse(session_id=session.id, created_at=session.created_at)


@router.get("", response_model=list[SessionSummaryResponse])
def list_sessions() -> list[SessionSummaryResponse]:
    store = get_session_store()
    return [
        SessionSummaryResponse(
            session_id=session.id,
            created_at=session.created_at,
            preview=session.preview,
        )
        for session in store.list_sessions()
    ]


@router.get("/{session_id}/messages", response_model=SessionMessagesResponse)
def get_messages(session_id: str) -> SessionMessagesResponse:
    return get_orchestrator().get_session_messages(session_id)
