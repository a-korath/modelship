from fastapi import APIRouter, Depends, HTTPException

from src.api.middleware.auth import validate_api_key
from src.api.models import ml_model
from src.api.models.ml_model import is_loaded, predict
from src.api.models.schemas import PredictRequest, PredictResponse

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictResponse,
    dependencies=[Depends(validate_api_key)],
)
def run_predict(request: PredictRequest) -> PredictResponse:
    if not is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded")
    results = predict(request.text)
    return PredictResponse(predictions=results, model_version=ml_model.MODEL_VERSION)
