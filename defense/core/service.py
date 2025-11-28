import time, math, threading, requests

# Config por defecto (puedes sobreescribir desde tu script principal)
ENV_URL  = "http://env-placeholder"
COMM_URL = "http://comm-placeholder"

DAMAGE_PER_ANT     = 10
POLL_ENV_EVERY_SEC = 5

pending = {}  # req_id -> threat_id
active  = {}  # threat_id -> {...}
metrics = {"threats_seen":0, "ants_requested":0, "last_events":[]}
lock = threading.Lock()

def _push_event(msg:str):
    with lock:
        metrics["last_events"].append({"ts": time.time(), "msg": msg})
        if len(metrics["last_events"])>20:
            metrics["last_events"] = metrics["last_events"][-20:]

def is_ready(url:str|None)->bool:
    return bool(url) and isinstance(url, str) and url.startswith("http")

def ants_needed(damage:int, dpa:int=DAMAGE_PER_ANT)->int:
    return max(1, math.ceil(damage/dpa))

def poll_env_step():
    """Una pasada del loop: consulta amenazas, calcula 'need' y crea request en Comunicación."""
    try:
        if not is_ready(ENV_URL):
            return "env_not_ready"
        r = requests.get(f"{ENV_URL}/threats", params={"status":"active"}, timeout=10)
        r.raise_for_status()
        threats = r.json() or []
        for t in threats:
            tid = t["id"]
            with lock:
                if tid in active or tid in pending.values():
                    continue
                metrics["threats_seen"] += 1
            need = ants_needed(int(t["damage"]))
            with lock:
                metrics["ants_requested"] += need
            if not is_ready(COMM_URL):
                _push_event(f"Detectada {tid}, pero sin COMM_URL todavía.")
                continue
            rr = requests.post(f"{COMM_URL}/messages/defense/requests",
                               json={"ants_needed": need}, timeout=10)
            rr.raise_for_status()
            rid = (rr.json() or {}).get("request_id")
            if rid:
                with lock:
                    pending[rid] = tid
                    _push_event(f"Solicitud enviada: threat={tid}, need={need}, req_id={rid}")
        return "ok"
    except Exception as e:
        _push_event(f"poll_env error: {type(e).__name__}")
        return "error"

def poll_env(should_stop=None, sleep_s=None, step_fn=None):
    """Loop de entorno (GRETTEL), **testeable**:
    - En producción: sin argumentos → loop infinito con POLL_ENV_EVERY_SEC.
    - En pruebas: usar should_stop/step_fn/sleep_s para cortar y espiar.
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
                break
            time.sleep(sleep_s)
