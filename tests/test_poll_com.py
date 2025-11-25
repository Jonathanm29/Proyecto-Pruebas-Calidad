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
