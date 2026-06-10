from fastapi import APIRouter, HTTPException
from src.api.models import ml_model
from src.api.models.ml_model import MODEL_NAME, loaded_at, is_loaded
from src.api.models.schemas import ModelInfoResponse



router = APIRouter()
@router.get("/model/info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    try:
        loaded = is_loaded()
        return ModelInfoResponse(
            model_name=MODEL_NAME,
            model_version=ml_model.MODEL_VERSION,
            model_loaded=loaded,
            loaded_at=loaded_at()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
