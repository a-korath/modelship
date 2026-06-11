import datetime as dt
import logging
import types

from mlflow.tracking import MlflowClient

logger = logging.getLogger(__name__)

from src.api.models.schemas import PredictResult

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
MODEL_ALIAS = "Production"

_classifier = None
_loaded_at = None
_loaded_version: str | None = None
_client: MlflowClient | None = None
_mlflow_transformers: types.ModuleType | None = None


def _get_client() -> MlflowClient:
    global _client
    if _client is None:
        _client = MlflowClient()
    return _client


def _get_mlflow_transformers() -> types.ModuleType:
    global _mlflow_transformers
    if _mlflow_transformers is None:
        import mlflow.transformers as _mt
        _mlflow_transformers = _mt
    return _mlflow_transformers


def loaded_version() -> str | None:
    return _loaded_version


def load_model() -> None:
    global _classifier, _loaded_at, _loaded_version
    client = _get_client()
    transformers = _get_mlflow_transformers()
    try:
        model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
        _classifier = transformers.load_model(model_uri)
        _loaded_at = dt.datetime.now()
        mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        _loaded_version = mv.version
        logger.info("Model v%s (@%s) loaded at %s.", _loaded_version, MODEL_ALIAS, _loaded_at)
    except Exception:
        logger.exception("Error loading model '%s' alias '%s'", MODEL_NAME, MODEL_ALIAS)
        raise


def reload_if_changed() -> None:
    global _loaded_version
    client = _get_client()
    try:
        mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        latest_version = mv.version
        if _loaded_version != latest_version:
            logger.info("New model version detected: %s. Reloading model...", latest_version)
            load_model()
    except Exception:
        logger.exception("Error checking for model updates")


def is_loaded() -> bool:
    return _classifier is not None


def loaded_at() -> dt.datetime | None:
    if not is_loaded():
        return None
    return _loaded_at


def predict(text: str) -> list[PredictResult]:
    if _classifier is None:
        raise RuntimeError("Model is not loaded")
    results = _classifier(text)
    return [
        PredictResult(label=r["label"], score=round(r["score"], 4)) for r in results
    ]
