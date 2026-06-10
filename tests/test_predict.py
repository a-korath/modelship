from fastapi.testclient import TestClient

import src.api.models.ml_model
from src.api.main import app


def test_predict():
    # Load the model
    src.api.models.ml_model.load_model()
    assert src.api.models.ml_model.is_loaded()

    # Test predict endpoint
    client = TestClient(app)
    response = client.post("/predict", json={"text": "I love this movie!"})
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) > 0
    assert data["predictions"][0]["label"] in ("POSITIVE", "NEGATIVE")
    assert 0.0 <= data["predictions"][0]["score"] <= 1.0
    assert "model_version" in data
    assert data["model_version"] == "1.0.0"