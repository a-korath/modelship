import datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.middleware.auth import key_db


@pytest.fixture(autouse=True)
def mock_model(monkeypatch):
    """Patch the ML model state for every test — no torch or MLflow needed."""
    from src.api.models import ml_model

    monkeypatch.setattr(
        ml_model,
        "_classifier",
        MagicMock(return_value=[{"label": "POSITIVE", "score": 0.9999}]),
    )
    monkeypatch.setattr(ml_model, "_loaded_at", datetime.datetime(2026, 1, 1))
    monkeypatch.setattr(ml_model, "_loaded_version", "1")
    monkeypatch.setattr(ml_model, "MODEL_VERSION", "1")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def api_key():
    """Create a fresh user-role API key for each test that needs auth."""
    key = key_db.generate_key(role="user")
    yield key.key
    key_db.deactivate_key(key.key)


@pytest.fixture
def admin_key():
    """Create a fresh admin-role API key for each test that needs admin auth."""
    key = key_db.generate_key(role="admin")
    yield key.key
    key_db.deactivate_key(key.key)
