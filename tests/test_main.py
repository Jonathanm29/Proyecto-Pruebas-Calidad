import pytest
import time
import src.projectocalidadsoftware.background as bg
from fastapi.testclient import TestClient
from unittest.mock import Mock
from src.projectocalidadsoftware.main import app
from src.projectocalidadsoftware.background import is_ready
from src.projectocalidadsoftware.background import ants_needed

client = TestClient(app)

class ExitTick(Exception):
    pass

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

def test_tick_attacks_full_flow(monkeypatch):
    now = time.time()

    bg.health.active = {
        "T123": {
            "ants": [10, 11, 12],
            "end_at": now - 5,
            "started_at": now - 20,
        }
    }

    bg.health.metrics = {
        "threats_resolved": 0,
        "survivors_total": 0,
        "attacks_count": 0,
        "attack_durations": [],
        "survival_rates": [],
    }

    monkeypatch.setattr(bg, "lock", bg.threading.Lock())
    monkeypatch.setattr(bg.random, "random", lambda: 0.3)

    push_events = []
    monkeypatch.setattr(bg, "_push_event", lambda msg: push_events.append(msg))
    monkeypatch.setattr(bg, "ENV_URL", "http://env")
    monkeypatch.setattr(bg, "COMM_URL", "http://comm")
    monkeypatch.setattr(bg, "is_ready", lambda url: True)

    mock_post = Mock()
    monkeypatch.setattr(bg, "requests", Mock(post=mock_post))

    monkeypatch.setattr(bg.time, "sleep", lambda _: (_ for _ in ()).throw(ExitTick()))

    try:
        bg.tick_attacks()
    except ExitTick:
        pass

    assert "T123" not in bg.health.active
    assert bg.health.metrics["survivors_total"] == 3
    assert bg.health.metrics["threats_resolved"] == 1
    assert bg.health.metrics["attacks_count"] == 1

    duration = bg.health.metrics["attack_durations"][0]
    assert 15 <= duration <= 25
    assert bg.health.metrics["survival_rates"][0] == 1.0
    assert any("Finalizó threat=T123" in ev for ev in push_events)
    assert mock_post.call_count == 2

    resolve_call = mock_post.call_args_list[0]
    results_call = mock_post.call_args_list[1]

    assert "/threats/T123/resolve" in resolve_call[0][0]
    assert "/messages/defense/results" in results_call[0][0]
    assert results_call[1]["json"]["survivors"] == [{"id": 10}, {"id": 11}, {"id": 12}]
