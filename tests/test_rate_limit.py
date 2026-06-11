from fastapi.testclient import TestClient

from src.api.main import app
from src.api.middleware.rate_limit import rate_limiter

client = TestClient(app)

PREDICT_PAYLOAD = {"text": "I love this movie!"}


def test_requests_within_limit_succeed(api_key):
    response = client.post(
        "/predict",
        json=PREDICT_PAYLOAD,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200


def test_exceeding_rate_limit_returns_429(api_key, monkeypatch):
    # first request creates the bucket for this key
    client.post(
        "/predict",
        json=PREDICT_PAYLOAD,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    # drain the bucket
    monkeypatch.setattr(rate_limiter._buckets[api_key], "tokens", 0)
    # next request should be rate limited
    response = client.post(
        "/predict",
        json=PREDICT_PAYLOAD,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 429
