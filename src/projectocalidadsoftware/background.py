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
        assigned = data["ants"]
        survivors = [a for a in assigned if random.random() < 0.5]
        health.metrics["survivors_total"] += len(survivors)

        duration = max(0.0, now - data.get("started_at", now))
        health.metrics["attack_durations"].append(duration)

        rate = len(survivors) / len(assigned) if assigned else 0.0
        health.metrics["survival_rates"].append(rate)

    time.sleep(1)


