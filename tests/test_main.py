import pytest
from fastapi.testclient import TestClient
from src.projectocalidadsoftware.main import app
from src.projectocalidadsoftware.background import is_ready

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health/status")
    assert response.status_code == 200

@pytest.mark.parametrize(
    "url, expected",
    [
        ("http://example.com", True),
        ("https://example.com", True),
        ("ftp://example.com", False),   # does not start with http
        ("example.com", False),         # missing scheme
        ("", False),                    # empty string
        (None, False),                  # None is not valid
        (123, False),                   # not a string
    ]
)
def test_is_ready(url, expected):
    assert is_ready(url) == expected