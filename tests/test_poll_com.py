from src.projectocalidadsoftware.background import poll_comm_once
from unittest.mock import Mock
import threading
from tests.test_utils import DummyLock, DummyResp, make_http_get

def test_skips_when_not_ready():
    comm_url = "http://comm"
    pending = {"r1": "t1"}
    active = {}
    metrics = {}
    is_ready = lambda url: False
    http_get = Mock()
    push = Mock()
    now = lambda: 1000.0
    lock = DummyLock()

    poll_comm_once(comm_url, pending, active, metrics,
                   is_ready, http_get, push, now,
                   lock, attack_duration_sec=60)

    assert pending == {"r1": "t1"}   # unchanged
    push.assert_not_called()
    http_get.assert_not_called()

def test_accepted_updates_active_and_metrics_and_pushes_event():
    comm_url = "http://comm"
    rid = "r1"; tid = "t1"

    pending = {rid: tid}
    active = {}
    metrics = {"ants_assigned": 0}

    is_ready = lambda url: True

    # Fake response with accepted status
    data = {"status": "accepted", "ants": [{"id": "a1"}, {"id": "a2"}]}
    resp = DummyResp(json_data=data)

    http_get = make_http_get({
        f"{comm_url}/messages/defense/requests/{rid}": resp
    })

    push = Mock()
    now = lambda: 1000
    lock = DummyLock()

    poll_comm_once(
        comm_url, pending, active, metrics,
        is_ready, http_get, push, now,
        lock, attack_duration_sec=60
    )

    # pending must be cleared
    assert rid not in pending

    # ants must be added
    assert active[tid]["ants"] == ["a1", "a2"]

    # metrics incremented
    assert metrics["ants_assigned"] == 2

    # event pushed
    push.assert_called_once()
    assert "Aceptada" in push.call_args[0][0]

def test_poll_comm_process_accepted_request(monkeypatch):
    # Fake data
    rid = "req1"
    tid = "threat1"
    pending.clear()
    active.clear()
    metrics["ants_assigned"] = 0

    pending[rid] = tid

    # Fake server response
    def mock_get(url, timeout):
        class Resp:
            def raise_for_status(self): pass
            def json(self):
                return {
                    "status": "accepted",
                    "ants": [{"id": "A1"}, {"id": "A2"}]
                }
        return Resp()

    # Patch requests.get
    monkeypatch.setattr("requests.get", mock_get)

    # Patch is_ready to always be true
    monkeypatch.setattr("module_under_test.is_ready", lambda url: True)

    # Reduce sleep to 0 to avoid waiting
    monkeypatch.setattr("time.sleep", lambda x: None)

    # Capture events
    events = []
    monkeypatch.setattr("module_under_test._push_event", lambda msg: events.append(msg))

    # Run ONE iteration only
    monkeypatch.setattr("module_under_test.POLL_COMM_EVERY_SEC", 0)

    poll_comm(iterations=1)

    # Assertions
    assert rid not in pending                   # request removed
    assert tid in active                        # threat added
    assert active[tid]["ants"] == ["A1", "A2"]  # ants stored
    assert metrics["ants_assigned"] == 2        # metrics updated
    assert "Aceptada req1" in events[0]         # event pushed
