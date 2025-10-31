from fastapi.testclient import TestClient
from src.projectocalidadsoftware.main import app

client = TestClient(app)

def test_health_response_no_attack():
    response = client.get("/health/status")
    data = response.json()

    assert response.status_code == 200
    assert "colony_is_attacked" in data, "Response missing 'colony_is_attacked'"
    assert data["colony_is_attacked"] is False, "'colony_is_attacked' should be False"
