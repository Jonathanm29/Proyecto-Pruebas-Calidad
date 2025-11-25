from src.projectocalidadsoftware.background import poll_comm_once
from unittest.mock import Mock
import threading
from tests.test_utils import DummyLock

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
