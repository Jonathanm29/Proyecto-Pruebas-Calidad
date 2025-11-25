from src.projectocalidadsoftware.background import poll_comm_once
from unittest.mock import Mock
import threading
from tests.test_utils import DummyLock, DummyResp, make_http_get


def test_poll_comm_process_accepted_request(monkeypatch):
    # Fake data
    rid = "req1"
    tid = "threat1"

    pending = {rid: tid}
    active = {}
    metrics = {"ants_assigned": 0}

    # 👉 Nombre REAL del módulo bajo prueba
    module_path = "src.projectocalidadsoftware.background"

    # Fake is_ready
    monkeypatch.setattr(f"{module_path}.is_ready", lambda url: True)

    # Fake HTTP response
    class DummyResp:
        def __init__(self, data):
            self._data = data
        def raise_for_status(self):
            pass
        def json(self):
            return self._data

    def fake_get(url, timeout=None):
        return DummyResp({
            "status": "accepted",
            "ants": [{"id": "A1"}, {"id": "A2"}]
        })

    # Patch requests.get
    monkeypatch.setattr(f"{module_path}.requests.get", fake_get)

    # Capturar eventos
    events = []
    monkeypatch.setattr(f"{module_path}._push_event", lambda msg: events.append(msg))

    lock = DummyLock()

    poll_comm_once(
        "http://comm",
        pending,
        active,
        metrics,
        lambda u: True,
        fake_get,
        lambda msg: events.append(msg),
        lambda: 1000.0,
        lock,
        attack_duration_sec=60
    )

    # Assertions
    assert rid not in pending
    assert tid in active
    assert active[tid]["ants"] == ["A1", "A2"]
    assert metrics["ants_assigned"] == 2
