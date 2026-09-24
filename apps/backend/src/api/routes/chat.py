from fastapi import APIRouter, HTTPException

from api.schemas import ChatRequest, ChatResponse
from api.service import get_orchestrator

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    return get_orchestrator().chat(request.session_id, question)
