from fastapi.testclient import TestClient

from src.api.main import app


def test_predict_returns_prediction(api_key):
    client = TestClient(app)
    response = client.post(
        "/predict",
        json={"text": "I love this movie!"},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) > 0
    assert data["predictions"][0]["label"] in ("POSITIVE", "NEGATIVE")
    assert 0.0 <= data["predictions"][0]["score"] <= 1.0
    assert "model_version" in data


def test_predict_without_auth_returns_4xx():
    client = TestClient(app)
    response = client.post("/predict", json={"text": "I love this movie!"})
    assert response.status_code in (401, 403)


def test_predict_with_invalid_token_returns_401():
    client = TestClient(app)
    response = client.post(
        "/predict",
        json={"text": "I love this movie!"},
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
