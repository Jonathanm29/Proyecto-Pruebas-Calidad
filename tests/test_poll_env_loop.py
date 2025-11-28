import defense.core.service as svc

def setup_function():
    # Estado limpio global antes de cada test
    with svc.lock:
        svc.pending.clear()
        svc.active.clear()
        svc.metrics.update({"threats_seen":0,"ants_requested":0,"last_events":[]})

def test_poll_env_llama_step_y_duerme(monkeypatch):
    # Espía de llamadas al 'step' del loop
    llamadas = {"n": 0}
    def fake_step():
        llamadas["n"] += 1

    # Espía de sleeps
    sleeps = []
    monkeypatch.setattr(svc.time, "sleep", lambda s: sleeps.append(s))

    # Cortar el loop tras 3 iteraciones
    max_iters = 3
    contador = {"n": 0}
    def should_stop():
        contador["n"] += 1
        return contador["n"] >= max_iters

    # Esperado: 3 llamadas al step y 2 sleeps entre medios
    # NOTA: hoy tu poll_env no acepta estos args -> test fallará (ROJO)
    svc.poll_env(should_stop=should_stop, sleep_s=1, step_fn=fake_step)

    assert llamadas["n"] == 3
    assert len(sleeps) == 2
    assert all(s == 1 for s in sleeps)

def test_poll_env_permte_step_inyectado(monkeypatch):
    hits = []
    def step_espia():
        hits.append("x")

    # Evitamos dormir en este test
    monkeypatch.setattr(svc.time, "sleep", lambda s: None)

    # Cortar tras 5 iteraciones
    cnt = {"n": 0}
    def should_stop():
        cnt["n"] += 1
        return cnt["n"] >= 5

    svc.poll_env(should_stop=should_stop, sleep_s=0, step_fn=step_espia)
    assert len(hits) == 5
