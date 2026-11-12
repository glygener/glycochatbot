from fastapi import APIRouter

from api.schemas import HealthResponse
from glyco_chroma.settings import ChromaSettings
from glyco_chroma.store import chroma_is_ready
from rag.config import RAGConfig
from session.db import connect, init_db

router = APIRouter(tags=["health"])


def _database_ready() -> bool:
    try:
        init_db()
        with connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
        return True
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    config = RAGConfig.from_env()
    chroma_settings = ChromaSettings.from_env(
        collection_name=config.collection_name,
        chroma_dir=config.chroma_dir,
    )
    return HealthResponse(
        status="ok",
        chroma_ready=chroma_is_ready(chroma_settings),
        database_ready=_database_ready(),
    )
