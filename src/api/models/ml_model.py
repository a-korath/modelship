import mlflow
import mlflow.transformers
from mlflow.tracking import MlflowClient
from src.api.models.schemas import PredictResult
import datetime as dt

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
MODEL_ALIAS = "Production"
MODEL_VERSION = MODEL_ALIAS  # exposed for routes; updated to numeric version after load

_classifier = None
_loaded_at = None
_loaded_version = None

client = MlflowClient()

def load_model() -> None:
    global _classifier, _loaded_at, _loaded_version, MODEL_VERSION
    try:
        model_uri = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
        _classifier = mlflow.transformers.load_model(model_uri)
        _loaded_at = dt.datetime.now()
        mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        _loaded_version = mv.version
        MODEL_VERSION = mv.version
        print(f"Model '{MODEL_NAME}' version '{_loaded_version}' (@{MODEL_ALIAS}) loaded successfully at {_loaded_at}.")
    except Exception as e:
        print(f"Error loading model '{MODEL_NAME}' alias '{MODEL_ALIAS}': {e}")
        raise

def reload_if_changed() -> None:
    global _loaded_version
    try:
        mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        latest_version = mv.version
        if _loaded_version != latest_version:
            print(f"New model version detected: {latest_version}. Reloading model...")
            load_model()
    except Exception as e:
        print(f"Error checking for model updates: {e}")

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
    return [PredictResult(label=r["label"], score=round(r["score"], 4)) for r in results]
