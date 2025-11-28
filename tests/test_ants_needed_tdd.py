# ROJO generado 2025-11-28 23:33:51
import pytest
import defense.core.service as svc

def test_ants_needed_ceil_rounding():
    assert svc.ants_needed(25, 10) == 3

def test_ants_needed_min_one():
    assert svc.ants_needed(1, 10) == 1

def test_ants_needed_negative_damage_raises():
    with pytest.raises(ValueError):
        svc.ants_needed(-1, 10)

def test_ants_needed_zero_or_negative_dpa_raises():
    for bad in [0, -5]:
        with pytest.raises(ValueError):
            svc.ants_needed(10, bad)
