from fastapi.testclient import TestClient
from src.projectocalidadsoftware.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health/status")
    assert response.status_code == 200
