import time, math, threading, requests
from typing import Optional

# Config por defecto (puedes sobreescribirlas desde tu app principal)
ENV_URL: str = "http://env-placeholder"
COMM_URL: str = "http://comm-placeholder"

DAMAGE_PER_ANT: int     = 10
POLL_ENV_EVERY_SEC: int = 5

pending = {}  # req_id -> threat_id
active  = {}  # threat_id -> {...}
metrics = {"threats_seen": 0, "ants_requested": 0, "last_events": []}
lock = threading.Lock()

def _push_event(msg: str) -> None:
    with lock:
        metrics["last_events"].append({"ts": time.time(), "msg": msg})
        if len(metrics["last_events"]) > 20:
            metrics["last_events"] = metrics["last_events"][-20:]

def is_ready(url: Optional[str]) -> bool:
    return bool(url) and isinstance(url, str) and url.startswith("http")

def _validate_ants_args(damage: int, dpa: int) -> None:
    if damage < 0:
        raise ValueError("damage must be >= 0")
    if dpa <= 0:
        raise ValueError("dpa must be > 0")


def ants_needed(damage: int, dpa: int = DAMAGE_PER_ANT) -> int:
    return max(1, math.ceil(damage / dpa))

def poll_env_step() -> str:
    """Una pasada del loop: consulta amenazas y acumula métricas básicas.
    En esta versión mínima no hace POST a comunicación (suficiente para tests de loop).
    """
    try:
        if not is_ready(ENV_URL):
            return "env_not_ready"
        r = requests.get(f"{ENV_URL}/threats", params={"status": "active"}, timeout=10)
        r.raise_for_status()
        threats = r.json() or []
        for t in threats:
            tid = t.get("id")
            if tid is None:
                continue
            with lock:
                if tid in active or tid in pending.values():
                    continue
                metrics["threats_seen"] += 1
            need = ants_needed(int(t.get("damage", 0)))
            with lock:
                metrics["ants_requested"] += need
        return "ok"
    except Exception as e:
        _push_event(f"poll_env error: {type(e).__name__}")
        return "error"

def poll_env(should_stop=None, sleep_s: Optional[int] = None, step_fn=None):
    """Loop de entorno (testeable).
    - Producción: sin should_stop -> loop infinito, duerme POLL_ENV_EVERY_SEC.
    - Pruebas: usar should_stop/step_fn/sleep_s para cortar y espiar.
    Devuelve "stopped" cuando should_stop corta el loop (para TDD).
    """
    if sleep_s is None:
        sleep_s = POLL_ENV_EVERY_SEC
    if step_fn is None:
        step_fn = poll_env_step

    if should_stop is None:
        while True:
            step_fn()
            time.sleep(sleep_s)
    else:
        while True:
            step_fn()
            if callable(should_stop) and should_stop():
                return "stopped"
            time.sleep(sleep_s)


# --- VERDE (ants_needed con validación) ---

def ants_needed(damage: int, dpa: int = DAMAGE_PER_ANT) -> int:
    if damage < 0:
        raise ValueError("damage must be >= 0")
    if dpa <= 0:
        raise ValueError("dpa must be > 0")
    return max(1, math.ceil(damage / dpa))
