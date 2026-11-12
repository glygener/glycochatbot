from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from api.schemas import ChatRequest, ChatResponse
from api.service import get_orchestrator
from session.users import UserRecord

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user: UserRecord = Depends(get_current_user),
) -> ChatResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    return get_orchestrator().chat(request.session_id, question, user.user_id)
