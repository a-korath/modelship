from fastapi.testclient import TestClient

from src.api.main import app
from src.api.models import ml_model

client = TestClient(app)


def test_healthz_always_returns_200():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_healthz_returns_200_when_model_not_loaded(monkeypatch):
    monkeypatch.setattr(ml_model, "_classifier", None)
    response = client.get("/healthz")
    assert response.status_code == 200


def test_readyz_returns_200_when_model_loaded():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["model_loaded"] is True


def test_readyz_returns_503_when_model_not_loaded(monkeypatch):
    monkeypatch.setattr(ml_model, "_classifier", None)
    response = client.get("/readyz")
    assert response.status_code == 503
