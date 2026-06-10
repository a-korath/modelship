import pytest

from src.api.models import ml_model


def test_model_not_loaded_by_default(monkeypatch):
    monkeypatch.setattr(ml_model, "_classifier", None)
    assert not ml_model.is_loaded()


def test_predict_raises_if_model_not_loaded(monkeypatch):
    monkeypatch.setattr(ml_model, "_classifier", None)
    with pytest.raises(RuntimeError, match="Model is not loaded"):
        ml_model.predict("Test input")


@pytest.mark.integration
def test_model_loads_from_mlflow():
    """Requires a running MLflow server — excluded from CI."""
    ml_model.load_model()
    assert ml_model.is_loaded()
