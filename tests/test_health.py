from fastapi.testclient import TestClient

from src.api.main import app


def test_health_returns_ok_when_model_loaded():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
