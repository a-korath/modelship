import pytest
from src.api.models import ml_model


def test_model_not_loaded_by_default():
    ml_model._classifier = None  
    assert not ml_model.is_loaded()
    


def test_model_loads_successfully():
    ml_model.load_model()
    assert ml_model.is_loaded()


def test_predict_raises_if_model_not_loaded():
    ml_model._classifier = None  
    with pytest.raises(RuntimeError, match="Model is not loaded"):
        ml_model.predict("Test input")
