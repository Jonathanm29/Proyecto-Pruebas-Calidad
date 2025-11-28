import pytest
import defense.core.service as svc

def test_ants_needed_ceil_rounding():
    # 25 de daño, 10 por hormiga => 3 hormigas
    assert svc.ants_needed(25, 10) == 3

def test_ants_needed_min_one():
    # daño pequeño => mínimo 1
    assert svc.ants_needed(1, 10) == 1

def test_ants_needed_negative_damage_raises():
    with pytest.raises(ValueError):
        svc.ants_needed(-1, 10)

def test_ants_needed_zero_or_negative_dpa_raises():
    for bad in [0, -5]:
        with pytest.raises(ValueError):
            svc.ants_needed(10, bad)
