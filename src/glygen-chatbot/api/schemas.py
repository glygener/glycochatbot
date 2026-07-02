from generation.schemas import RAGResponse, SourceCitation
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    question: str
    question_type: str
    answer: str
    confidence: str
    in_scope: bool
    sources: list[SourceCitation] = Field(default_factory=list)
    refusal_reason: str | None = None


class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: str


class MessageItem(BaseModel):
    id: str
    role: str
    content: str
    question_type: str | None = None
    sources: list[SourceCitation] = Field(default_factory=list)
    created_at: str


class SessionMessagesResponse(BaseModel):
    session_id: str
    user_display_name: str | None = None
    messages: list[MessageItem]


class HealthResponse(BaseModel):
    status: str
    chroma_ready: bool
    database_ready: bool


class StatusResponse(BaseModel):
    embedding_model: str
    reranker_model: str
    llm_model: str
    collection_name: str
    chroma_dir: str


def rag_to_chat(
    session_id: str,
    question: str,
    question_type: str,
    rag: RAGResponse,
) -> ChatResponse:
    return ChatResponse(
        session_id=session_id,
        question=question,
        question_type=question_type,
        answer=rag.answer,
        confidence=rag.confidence,
        in_scope=rag.in_scope,
        sources=rag.sources,
        refusal_reason=rag.refusal_reason,
    )
