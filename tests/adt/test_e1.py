"""ADT tests for E1 (ADR-032 §3.5).

Tests obligatoires avant tirage [2000-2029] :
  - test_determinism_bitwise         (C1)
  - test_blackbox_isolation          (C2)
  - test_structural_difference_from_e0
  - test_spatial_autocorrelation_nonlocal  (amendment §12 / 2026-05-09)
  - test_kappa_definability          (C4)
  - test_calibration_reproducibility (C5)

These tests must pass in CI BEFORE the freeze commit
"E₁ spec frozen per ADR-032 §3.1-§3.3" can be issued (verrou V1 ADR-032 §7.1).
"""
from __future__ import annotations

import inspect

import numpy as np
import pytest

from src.env.e0 import E0, E0Config
from src.env.e1 import E1, E1Config


# ---------------------------------------------------------------------------
# C1 — Bitwise determinism
# ---------------------------------------------------------------------------

def _run_trajectory(env: E1, actions: list[int]) -> tuple[np.ndarray, list[dict]]:
    telemetry = []
    for t, pos in enumerate(actions):
        if pos is not None:
            env.act(pos)
        telemetry.append(env.step())
    return env.observe(), telemetry


@pytest.mark.parametrize("seed", [42, 1234, 2026])
def test_determinism_bitwise(seed: int) -> None:
    """C1: identical seed + identical action sequence => bit-identical trajectory."""
    cfg = E1Config(seed=seed, horizon=64)
    actions = [(i * 7 + 3) % cfg.grid_size for i in range(64)]

    env_a = E1(cfg)
    env_b = E1(cfg)
    field_a, tel_a = _run_trajectory(env_a, actions)
    field_b, tel_b = _run_trajectory(env_b, actions)

    np.testing.assert_array_equal(field_a, field_b)
    assert tel_a == tel_b


# ---------------------------------------------------------------------------
# C2 — Black-box isolation
# ---------------------------------------------------------------------------

def test_blackbox_isolation_public_api() -> None:
    """C2: public API of E1 is exactly the same set as E0 (measurability ADR-032 C4)."""
    e0_public = {n for n in dir(E0()) if not n.startswith("_")}
    e1_public = {n for n in dir(E1()) if not n.startswith("_")}
    assert e0_public == e1_public, (
        f"public API divergence: E0-only={e0_public - e1_public}, "
        f"E1-only={e1_public - e0_public}"
    )


def test_blackbox_isolation_no_internal_leak() -> None:
    """C2: observe() returns a copy; mutating it must NOT affect internal state."""
    env = E1(E1Config(seed=42))
    obs = env.observe()
    obs[:] = -999.0
    obs2 = env.observe()
    assert not np.any(obs2 == -999.0), "observe() leaked an aliased reference"


def test_blackbox_isolation_signatures() -> None:
    """C2: observe/act/step have the same signatures as E0."""
    for method_name in ("observe", "act", "step"):
        sig_e0 = inspect.signature(getattr(E0, method_name))
        sig_e1 = inspect.signature(getattr(E1, method_name))
        assert sig_e0 == sig_e1, f"signature mismatch on {method_name}"


# ---------------------------------------------------------------------------
# Structural difference from E0 (axis 1: spatial coupling)
# ---------------------------------------------------------------------------

def _matched_e0_config(c: E1Config) -> E0Config:
    return E0Config(
        grid_size=c.grid_size,
        horizon=c.horizon,
        n_modes=c.n_modes,
        seed=c.seed,
        drift_rate=c.drift_rate,
        action_kernel_width=c.action_kernel_width,
        action_amplitude=c.action_amplitude,
        relaxation=c.relaxation,
    )


def test_reference_field_bitidentical_to_e0() -> None:
    """E1._reference_field is bit-identical to E0._reference_field across t.

    This proves that the ONLY source of structural difference is the Laplacian
    term in step() — see ADR-032 §3.3 amendment §12 / 2026-05-09.
    """
    cfg = E1Config(seed=42)
    e0 = E0(_matched_e0_config(cfg))
    e1 = E1(cfg)
    for t in (0, 1, 17, 100, 511):
        np.testing.assert_array_equal(
            e0._reference_field(t), e1._reference_field(t),
            err_msg=f"reference field divergence at t={t}",
        )


def test_action_kernel_bitidentical_to_e0() -> None:
    """E1._action_kernel is bit-identical to E0._action_kernel.

    Confirms that the action kernel uses NON-modular euclidean distance,
    not periodic wrap-around (ADR-032 §3.3 amendment §12 / 2026-05-09).
    """
    cfg = E1Config(seed=42)
    e0 = E0(_matched_e0_config(cfg))
    e1 = E1(cfg)
    for pos in (0, 1, 31, 32, 63):
        np.testing.assert_array_equal(
            e0._action_kernel(pos), e1._action_kernel(pos),
            err_msg=f"action kernel divergence at pos={pos}",
        )


@pytest.mark.parametrize("seed", [3000, 3001, 3002, 3003, 3004])
def test_structural_difference_from_e0(seed: int) -> None:
    """ADR-032 §3.5: pointwise correlation between E0 and E1 trajectories < 0.95.

    Uses calibration pool [3000-3009] — disjoint from draw pools per ADR-032 §3.4.
    """
    cfg_e1 = E1Config(seed=seed, horizon=200)
    cfg_e0 = _matched_e0_config(cfg_e1)
    e0 = E0(cfg_e0)
    e1 = E1(cfg_e1)

    fields_e0 = []
    fields_e1 = []
    # Stationary regime only (post-warmup)
    T_warmup = 50
    for t in range(cfg_e1.horizon):
        e0.step()
        e1.step()
        if t >= T_warmup:
            fields_e0.append(e0.observe())
            fields_e1.append(e1.observe())
    arr_e0 = np.stack(fields_e0)
    arr_e1 = np.stack(fields_e1)

    # Pointwise correlation across (t, x)
    a = arr_e0.flatten() - arr_e0.mean()
    b = arr_e1.flatten() - arr_e1.mean()
    corr = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
    assert abs(corr) < 0.95, (
        f"E1 trajectory too close to E0 (corr={corr:.4f}); "
        f"diffusion_coeff={cfg_e1.diffusion_coeff} may be too small."
    )


# ---------------------------------------------------------------------------
# Non-local spatial autocorrelation (amendment §12 / 2026-05-09)
# ---------------------------------------------------------------------------

def _spatial_autocorr(field_t: np.ndarray, delta: int) -> float:
    """Spatial autocorrelation at lag `delta`, averaged over time.

    field_t has shape (T, G); returns C(Δ) = <f(i) f(i+Δ)> - <f>^2 averaged
    over i and t (using periodic shift consistent with the ring topology).
    """
    f = field_t - field_t.mean(axis=1, keepdims=True)  # zero-mean per row
    shifted = np.roll(f, -delta, axis=1)
    cov = (f * shifted).mean()
    var = (f * f).mean() + 1e-12
    return float(cov / var)


@pytest.mark.parametrize("seed", [3000, 3001, 3002, 3003, 3004])
def test_spatial_autocorrelation_nonlocal(seed: int) -> None:
    """ADR-032 §3.5 (amendment §12): |C^E1(Δ=2)| > 0.10 AND > 2 × |C^E0(Δ=2)|.

    Proves that the Laplacian coupling is structurally non-local, beyond the
    mere trajectorial divergence verified by test_structural_difference_from_e0.
    """
    cfg_e1 = E1Config(seed=seed, horizon=200)
    cfg_e0 = _matched_e0_config(cfg_e1)
    e0 = E0(cfg_e0)
    e1 = E1(cfg_e1)

    T_warmup = 50
    fields_e0, fields_e1 = [], []
    for t in range(cfg_e1.horizon):
        e0.step()
        e1.step()
        if t >= T_warmup:
            fields_e0.append(e0.observe())
            fields_e1.append(e1.observe())

    c_e1 = abs(_spatial_autocorr(np.stack(fields_e1), delta=2))
    c_e0 = abs(_spatial_autocorr(np.stack(fields_e0), delta=2))
    assert c_e1 > 0.10, f"E1 autocorr at Δ=2 too weak: {c_e1:.4f}"
    assert c_e1 > 2.0 * c_e0, (
        f"E1 autocorr ({c_e1:.4f}) not significantly above E0 ({c_e0:.4f})"
    )


# ---------------------------------------------------------------------------
# C4 — κ definability
# ---------------------------------------------------------------------------

def test_kappa_definability_observation_dim() -> None:
    """C4: observation dimension on E1 is identical to E0 (=> M_κ definable)."""
    o_e0 = E0().observe()
    o_e1 = E1().observe()
    assert o_e0.shape == o_e1.shape
    assert o_e0.dtype == o_e1.dtype


def test_kappa_definability_action_repertoire() -> None:
    """C4: action repertoire on E1 is identical to E0 (positions [0, grid_size))."""
    cfg = E1Config()
    env = E1(cfg)
    env.act(0)
    env.act(cfg.grid_size - 1)
    with pytest.raises(ValueError):
        env.act(-1)
    with pytest.raises(ValueError):
        env.act(cfg.grid_size)


# ---------------------------------------------------------------------------
# C5 — Calibration reproducibility
# ---------------------------------------------------------------------------

def test_calibration_reproducibility() -> None:
    """C5: two runs with identical (seed, diffusion_coeff) produce bit-identical fields."""
    cfg = E1Config(seed=3000, diffusion_coeff=0.020, horizon=100)
    env_a = E1(cfg)
    env_b = E1(cfg)
    for _ in range(100):
        env_a.step()
        env_b.step()
    np.testing.assert_array_equal(env_a.observe(), env_b.observe())


def test_diffusion_coeff_zero_recovers_e0() -> None:
    """Sanity: D=0 makes E1 trajectorially identical to E0 (no spatial coupling).

    NOT a guarantee of identity — relaxation rounding can differ. We check
    near-equality (atol=1e-12) over a short horizon without actions.
    """
    cfg_e1 = E1Config(seed=42, diffusion_coeff=0.0, horizon=50)
    cfg_e0 = _matched_e0_config(cfg_e1)
    e1 = E1(cfg_e1)
    e0 = E0(cfg_e0)
    for _ in range(50):
        e0.step()
        e1.step()
    np.testing.assert_allclose(e0.observe(), e1.observe(), atol=1e-12)
