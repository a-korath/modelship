from fastapi import APIRouter

from src.api.models.ml_model import is_loaded
from src.api.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_loaded=is_loaded())
