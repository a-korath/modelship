from src.api.main import app
import src.api.models.ml_model
from fastapi.testclient import TestClient
def test_health():

    # Load the model
    src.api.models.ml_model.load_model()
    assert src.api.models.ml_model.is_loaded()

    # Test health endpoint
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True