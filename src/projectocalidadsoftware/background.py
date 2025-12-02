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
def poll_comm_once(
        comm_url,
        pending,
        active,
        metrics,
        is_ready,
        http_get,
        push,
        now,
        lock,
        attack_duration_sec
):
    try:
        if not is_ready(comm_url):
            return

        with lock:
            items = list(pending.items())

        for rid, tid in items:
            resp = http_get(f"{comm_url}/messages/defense/requests/{rid}", timeout=10)
            resp.raise_for_status()
            data = resp.json()

            status = data.get("status")

            if status == "accepted":
                ant_ids = [a["id"] for a in data.get("ants", [])]

                with lock:
                    metrics["ants_assigned"] = metrics.get("ants_assigned", 0) + len(ant_ids)

                end_at = now() + attack_duration_sec

                with lock:
                    if tid in active:
                        active[tid]["ants"].extend(ant_ids)
                    else:
                        active[tid] = {
                            "ants": ant_ids,
                            "end_at": end_at,
                            "started_at": now()
                        }

                    pending.pop(rid, None)

                push(f"Aceptada {rid} → threat={tid}, ants={len(ant_ids)}")
                continue

            if status == "rejected":
                with lock:
                    pending.pop(rid, None)
                push(f"Rechazada {rid} → threat={tid}")

    except Exception as e:
        push(f"poll_comm error: {type(e).__name__}")

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


