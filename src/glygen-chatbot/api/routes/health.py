from fastapi import APIRouter

from api.dependencies import get_session_store
from api.schemas import HealthResponse, SessionCreateResponse
from query.config import RAGConfig

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    config = RAGConfig.from_env()
    store = get_session_store()
    return HealthResponse(
        status="ok",
        chroma_ready=config.chroma_dir.exists(),
        database_ready=store.db_path.exists(),
    )
