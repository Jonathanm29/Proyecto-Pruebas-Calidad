import pytest
import time
import src.projectocalidadsoftware.background as bg
import src.projectocalidadsoftware.health as health
from fastapi.testclient import TestClient
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

def test_tick_attacks_removes_finished_attacks(monkeypatch):
    now = time.time()

    bg.active = {
        "t1": {"ants": [1, 2], "end_at": now - 1, "started_at": now - 5}
    }

    monkeypatch.setattr(bg, "_push_event", lambda msg: None)
    monkeypatch.setattr(bg, "is_ready", lambda url: False)
    monkeypatch.setattr(bg, "requests", None)

    monkeypatch.setattr(bg.time, "sleep", lambda x: (_ for _ in ()).throw(ExitTick()))

    try:
        bg.tick_attacks()
    except ExitTick:
        pass

    assert "t1" not in health.active

def test_tick_attacks_survivor_calculation(monkeypatch):
    now = time.time()

    bg.active = {
        "t1": {"ants": [1,2,3], "end_at": now - 1, "started_at": now - 10}
    }
    monkeypatch.setattr(bg.random, "random", lambda: 0.1)
    monkeypatch.setattr(health, "metrics", {
        "threats_resolved": 0,
        "survivors_total": 0,
        "attacks_count": 0,
        "attack_durations": [],
        "survival_rates": [],
    })

    monkeypatch.setattr(bg, "lock", bg.threading.Lock())

    monkeypatch.setattr(bg, "_push_event", lambda msg: None)
    monkeypatch.setattr(bg.time, "sleep", lambda x: (_ for _ in ()).throw(ExitTick()))

    try:
        bg.tick_attacks()
    except ExitTick:
        pass

    assert health.metrics["survivors_total"] == 3

def test_tick_attacks_calculates_duration_and_rate(monkeypatch):
    now = time.time()

    bg.active = {
        "t1": {"ants": [1, 2], "end_at": now - 1, "started_at": now - 4}
    }

    monkeypatch.setattr(bg.random, "random", lambda: 0.9)  # no survivors

    monkeypatch.setattr(bg, "lock", bg.threading.Lock())
    monkeypatch.setattr(health, "metrics", {
        "threats_resolved": 0,
        "survivors_total": 0,
        "attacks_count": 0,
        "attack_durations": [],
        "survival_rates": [],
    })

    monkeypatch.setattr(bg, "_push_event", lambda msg: None)
    monkeypatch.setattr(bg.time, "sleep", lambda x: (_ for _ in ()).throw(ExitTick()))

    try:
        bg.tick_attacks()
    except ExitTick:
        pass

    assert 3 <= health.metrics["attack_durations"][0] <= 4
    assert health.metrics["survival_rates"][0] == 0.0
