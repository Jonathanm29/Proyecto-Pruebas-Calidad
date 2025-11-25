import nest_asyncio, threading, requests, time, random, os, statistics, asyncio
import src.projectocalidadsoftware.health as health
from typing import Optional

ENV_URL  = "https://ENV_PUBLIC_URL"   # <-- URL pública de Entorno
COMM_URL = "https://COMM_PUBLIC_URL"  # <-- URL pública de Comunicación
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

#def poll_env(): # GRETTEL
#def poll_comm():  # JONATHAN

def tick_attacks(): #LORENZO
    while True:
        finished = []
        now = time.time()
        with lock:
            for tid, data in list(health.active.items()):
                if now >= data["end_at"]:
                    finished.append((tid, data))
                    health.active.pop(tid, None)
        # Procesar finalizados fuera del lock
        for tid, data in finished:
            assigned = list(data["ants"])
            survivors = [a for a in assigned if random.random() < 0.5]
            duration = max(0.0, now - data.get("started_at", now))
            with lock:
                health.metrics["threats_resolved"] += 1
                health.metrics["survivors_total"] += len(survivors)
                health.metrics["attacks_count"] += 1
                health.metrics["attack_durations"].append(duration)
                rate = (len(survivors) / len(assigned)) if assigned else 0.0
                health.metrics["survival_rates"].append(rate)
                _push_event(f"Finalizó threat={tid} | assigned={len(assigned)} | survivors={len(survivors)} | dur={round(duration,2)}s | rate={round(rate,2)}")

            if is_ready(ENV_URL):
                try:
                    requests.post(f"{ENV_URL}/threats/{tid}/resolve", json={}, timeout=10)
                except Exception as e:
                    _push_event(f"resolve error: {type(e).__name__}")

            if is_ready(COMM_URL):
                try:
                    requests.post(f"{COMM_URL}/messages/defense/results",
                                  json={"threat_id": tid, "survivors": [{"id": i} for i in survivors]},
                                  timeout=10)
                except Exception as e:
                    _push_event(f"results error: {type(e).__name__}")

        time.sleep(1)


