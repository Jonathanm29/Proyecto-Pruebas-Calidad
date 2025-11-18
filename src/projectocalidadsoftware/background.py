import nest_asyncio, threading, requests, time, random, os, statistics, asyncio
import src.projectocalidadsoftware.health as health
from typing import Optional

lock = threading.Lock()

def ants_needed(damage: int, dpa: int) -> int:
    import math
    return max(1, math.ceil(damage / dpa))

def is_ready(url: Optional[str]) -> bool:
    return bool(url) and isinstance(url, str) and url.startswith("http")

def tick_attacks_once(now=None):
    import time
    if now is None:
        now = time.time()

    finished = []
    # only detect, but no logic yet
    return len(finished)

def _push_event(msg):
    pass

def tick_attacks():
    now = time.time()

    finished = []
    with lock:
        for tid, data in list(health.active.items()):
            if now >= data["end_at"]:
                finished.append((tid, data))
                health.active.pop(tid, None)

    # We don't implement full processing yet
    for tid, data in finished:
        health.metrics["threats_resolved"] += 1
        health.metrics["survivors_total"] += 0
        health.metrics["attacks_count"] += 1
        health.metrics["attack_durations"].append(0)
        health.metrics["survival_rates"].append(0)

    time.sleep(1)


