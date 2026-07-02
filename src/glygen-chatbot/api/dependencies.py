from functools import lru_cache

from RAG.pipeline import RAGPipeline
from session.store import SessionStore


@lru_cache
def get_rag_pipeline() -> RAGPipeline:
    return RAGPipeline()


@lru_cache
def get_session_store() -> SessionStore:
    return SessionStore()
