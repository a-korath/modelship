from fastapi import APIRouter, HTTPException

from src.api.models.ml_model import is_loaded
from src.api.models.schemas import HealthResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
def liveness() -> HealthResponse:
    return HealthResponse(status="ok", model_loaded=is_loaded())


@router.get("/readyz", response_model=HealthResponse)
def readiness() -> HealthResponse:
    if not is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    return HealthResponse(status="ok", model_loaded=True)
