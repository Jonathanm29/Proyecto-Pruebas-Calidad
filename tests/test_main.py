import pytest
from fastapi.testclient import TestClient
from src.projectocalidadsoftware.main import app
from src.projectocalidadsoftware.background import is_ready
from src.projectocalidadsoftware.background import ants_needed

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health/status")
    assert response.status_code == 200

@pytest.mark.parametrize(
    "url, expected",
    [
        ("http://example.com", True),
        ("https://example.com", True),
        ("ftp://example.com", False),
        ("example.com", False),
        ("", False),
        (None, False),
        (123, False),
    ]
)
def test_is_ready(url, expected):
    assert is_ready(url) == expected

@pytest.mark.parametrize(
    "damage, dpa, expected",
    [
        (10, 5, 2),
        (9, 5, 2),
        (1, 5, 1),
        (0, 5, 1),
        (10, 3, 4),
        (100, 100, 1),
    ]
)
def test_ants_needed(damage, dpa, expected):
    assert ants_needed(damage, dpa) == expected