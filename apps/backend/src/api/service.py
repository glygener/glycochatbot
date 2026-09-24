from functools import lru_cache

from api.dependencies import get_rag_pipeline, get_session_store
from api.orchestrator import ChatOrchestrator


@lru_cache
def get_orchestrator() -> ChatOrchestrator:
    return ChatOrchestrator(get_rag_pipeline(), get_session_store())
