import src.projectocalidadsoftware.health as health


def setup_function():
    health.pending.clear()
    health.active.clear()
    health.metrics.update({
        "threats_seen": 0,
        "threats_resolved": 0,
        "ants_requested": 0,
        "ants_assigned": 0,
        "survivors_total": 0,
        "attacks_count": 0,
        "attack_durations": [],
        "survival_rates": [],
        "last_events": [],
    })

def test_health_status_empty():
    result = health.get_health_status()

    assert result["active"] == []
    assert result["pending"] == []
    assert result["metrics"] == {
        "threats_seen": 0,
        "threats_resolved": 0,
        "ants_requested": 0,
        "ants_assigned": 0,
        "survivors_total": 0,
        "attacks_count": 0,
    }
