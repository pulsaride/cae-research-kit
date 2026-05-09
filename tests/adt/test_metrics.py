"""ADT — metric destruction tests."""
from __future__ import annotations

import numpy as np
import pytest

from src.config.determinism import apply_cae_determinism
from src.metrics.pressure import (
    Wasserstein1,
    pressure_concentration,
    pressure_entropy,
    trajectory_redistribution,
    wasserstein1_ot,
    wasserstein1_scipy,
)


@pytest.fixture(autouse=True)
def _bootstrap():
    apply_cae_determinism(strict=False)


# ADT-M1 — distance axioms
def test_adt_m1_axioms():
    rng = np.random.default_rng(0)
    p = rng.random(32) + 1e-3
    q = rng.random(32) + 1e-3
    w_pp = wasserstein1_ot(p, p)
    w_pq = wasserstein1_ot(p, q)
    w_qp = wasserstein1_ot(q, p)
    assert w_pp == pytest.approx(0.0, abs=1e-12), f"W(p,p)={w_pp} != 0"
    assert w_pq >= 0.0
    assert w_pq == pytest.approx(w_qp, abs=1e-9), "W not symmetric"


# ADT-M2 — scipy vs POT consistency
@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
def test_adt_m2_cross_library_consistency(seed):
    rng = np.random.default_rng(seed)
    n = 64
    p = rng.random(n) + 1e-3
    q = rng.random(n) + 1e-3
    w_ot = wasserstein1_ot(p, q)
    w_sp = wasserstein1_scipy(p, q)
    assert w_ot == pytest.approx(w_sp, abs=1e-6), \
        f"ADT-M2: scipy={w_sp:.9e} vs POT={w_ot:.9e}, Δ={abs(w_ot-w_sp):.2e}"


# ADT-M3 — Dirac translation: W ≈ Δ
def test_adt_m3_translation_invariance():
    n = 128
    support = np.linspace(0.0, 1.0, n, endpoint=False)
    p = np.zeros(n); p[20] = 1.0
    q = np.zeros(n); q[40] = 1.0
    expected = abs(support[40] - support[20])
    w = wasserstein1_ot(p, q, support=support)
    assert w == pytest.approx(expected, abs=1e-9), \
        f"ADT-M3: W={w} expected {expected}"


# ADT-M4 — float32 robustness
def test_adt_m4_float32_stability():
    rng = np.random.default_rng(7)
    p = (rng.random(64) + 1e-3)
    q = (rng.random(64) + 1e-3)
    w64 = wasserstein1_ot(p.astype(np.float64), q.astype(np.float64))
    w32 = wasserstein1_ot(p.astype(np.float32).astype(np.float64),
                          q.astype(np.float32).astype(np.float64))
    assert abs(w64 - w32) < 1e-3, f"ADT-M4: float32 instability, Δ={abs(w64-w32):.2e}"


# ADT-M5 — entropy bounds
def test_adt_m5_entropy_bounds():
    n = 64
    uniform = np.ones(n)
    dirac = np.zeros(n); dirac[5] = 1.0
    H_uni = pressure_entropy(uniform)
    H_dir = pressure_entropy(dirac)
    assert H_uni == pytest.approx(np.log(n), abs=1e-9), f"H_uniform={H_uni}"
    assert 0.0 <= H_dir < 1e-6, f"H_dirac={H_dir} (should ≈ 0)"


# ADT-M6 — invalid inputs rejected
@pytest.mark.parametrize("bad", [
    np.array([np.nan, 1.0, 2.0]),
    np.array([-0.1, 0.5, 0.6]),
    np.zeros(8),
])
def test_adt_m6_rejects_invalid_inputs(bad):
    p = np.ones(bad.shape[0])
    with pytest.raises((ValueError, TypeError)):
        wasserstein1_ot(bad, p)


def test_adt_m6_shape_mismatch():
    with pytest.raises(ValueError):
        wasserstein1_ot(np.ones(8), np.ones(16))


# ADT-M7 — redistribution trajectory reproducibility
def test_adt_m7_trajectory_redistribution_reproducible():
    rng = np.random.default_rng(42)
    fields = rng.random((20, 32)) + 1e-3
    r1 = trajectory_redistribution(fields)
    r2 = trajectory_redistribution(fields)
    assert np.array_equal(r1, r2), "ADT-M7: redistribution not reproducible."
    assert r1.shape == (19,)
    assert (r1 >= 0).all()


# ADT-M8 — bounded HHI concentration
def test_adt_m8_concentration_bounds():
    n = 64
    uniform = np.ones(n)
    dirac = np.zeros(n); dirac[0] = 1.0
    c_uni = pressure_concentration(uniform)
    c_dir = pressure_concentration(dirac)
    assert c_uni == pytest.approx(1.0 / n, abs=1e-9)
    assert c_dir == pytest.approx(1.0, abs=1e-9)


# ADT-M9 — Wasserstein1.compute with cross_check enabled
def test_adt_m9_cross_check_passes_on_valid_input():
    rng = np.random.default_rng(3)
    p = rng.random(48) + 1e-3
    q = rng.random(48) + 1e-3
    metric = Wasserstein1(cross_check=True, tol=1e-6)
    w = metric.compute(p, q)
    assert w >= 0.0
