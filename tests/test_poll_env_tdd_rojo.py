import defense.core.service as svc

def setup_function():
    with svc.lock:
        svc.pending.clear()
        svc.active.clear()
        svc.metrics.update({"threats_seen":0,"ants_requested":0,"last_events":[]})

def test_poll_env_devuelve_stopped_y_cuenta_iteraciones(monkeypatch):
    # Espía de 'step'
    llamadas = {"n": 0}
    def fake_step():
        llamadas["n"] += 1

    # Espía de sleep
    sleeps = []
    monkeypatch.setattr(svc.time, "sleep", lambda s: sleeps.append(s))

    # Cortar tras 3 iteraciones
    cnt = {"n": 0}
    def should_stop():
        cnt["n"] += 1
        return cnt["n"] >= 3

    # NUEVA expectativa: debe devolver "stopped"
    result = svc.poll_env(should_stop=should_stop, sleep_s=1, step_fn=fake_step)
    assert result == "stopped"

    # 3 iteraciones, 2 sleeps de 1s
    assert llamadas["n"] == 3
    assert sleeps == [1,1]

def test_poll_env_respeta_sleep_por_defecto(monkeypatch):
    # Si no paso sleep_s, debe usar POLL_ENV_EVERY_SEC
    recorded = []
    monkeypatch.setattr(svc.time, "sleep", lambda s: recorded.append(s))

    # Paso con 2 iteraciones
    cnt = {"n": 0}
    def should_stop():
        cnt["n"] += 1
        return cnt["n"] >= 2

    # No paso sleep_s => usa svc.POLL_ENV_EVERY_SEC
    res = svc.poll_env(should_stop=should_stop, step_fn=lambda: None)
    assert res == "stopped"
    # 1 sleep entre 2 iteraciones y debe ser POLL_ENV_EVERY_SEC
    assert recorded == [svc.POLL_ENV_EVERY_SEC]
