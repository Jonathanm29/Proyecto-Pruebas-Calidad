pending = {}   # request_id -> threat_id
active  = {}   # threat_id -> {"ants":[ids], "end_at":ts, "started_at":ts}
metrics = {
    "threats_seen": 0,            # amenazas detectadas (activas) por el poll de entorno
    "threats_resolved": 0,        # amenazas que se resolvieron (tick_attacks)
    "ants_requested": 0,          # hormigas solicitadas (sumatoria de needs)
    "ants_assigned": 0,           # hormigas realmente asignadas por Comunicación
    "survivors_total": 0,         # total de hormigas sobrevivientes reportadas
    "attacks_count": 0,           # ataques completados (para promedios)
    "attack_durations": [],       # lista de duraciones reales de ataque para promedio
    "survival_rates": [],         # lista (sobrevivientes / asignadas) por ataque
    "last_events": []             # últimos eventos (máx 20) para auditoría rápida
}

def get_health_status():
    return {
        "active": list(active.keys()),
        "pending": list(pending.keys()),
        "metrics": {
            "threats_seen": metrics["threats_seen"],
            "threats_resolved": metrics["threats_resolved"],
            "ants_requested": metrics["ants_requested"],
            "ants_assigned": metrics["ants_assigned"],
            "survivors_total": metrics["survivors_total"],
            "attacks_count": metrics["attacks_count"],
        }
    }
