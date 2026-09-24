from fastapi import APIRouter

from api.schemas import StatusResponse
from api.service import get_orchestrator

router = APIRouter(prefix="/api/v1", tags=["status"])


@router.get("/status", response_model=StatusResponse)
def status() -> StatusResponse:
    data = get_orchestrator().get_status()
    return StatusResponse(**data)
