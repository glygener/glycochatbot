from functools import lru_cache

from api.dependencies import get_session_store
from api.orchestrator import ChatOrchestrator


@lru_cache
def get_orchestrator() -> ChatOrchestrator:
    # RAG models load on the first textbook question, not when listing chats.
    return ChatOrchestrator(get_session_store())
