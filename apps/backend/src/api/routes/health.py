from fastapi import APIRouter

from api.dependencies import get_session_store
from api.schemas import HealthResponse
from glyco_chroma.settings import ChromaSettings
from glyco_chroma.store import chroma_is_ready
from rag.config import RAGConfig

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    config = RAGConfig.from_env()
    store = get_session_store()
    chroma_settings = ChromaSettings.from_env(
        collection_name=config.collection_name,
        chroma_dir=config.chroma_dir,
    )
    return HealthResponse(
        status="ok",
        chroma_ready=chroma_is_ready(chroma_settings),
        database_ready=store.db_path.exists(),
    )
