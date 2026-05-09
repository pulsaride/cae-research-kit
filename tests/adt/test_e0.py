"""ADT — E0 destruction tests."""
from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import wasserstein_distance

from src.config.determinism import apply_cae_determinism
from src.env.e0 import E0, E0Config


@pytest.fixture(autouse=True)
def _bootstrap():
    apply_cae_determinism(strict=False)


# ADT-E1 — bit-exact trajectory reproducibility
def test_adt_e1_trajectory_bitwise_reproducibility():
    cfg = E0Config()
    env_a, env_b = E0(cfg), E0(cfg)
    traj_a, traj_b = [], []
    for _ in range(64):
        traj_a.append(env_a.observe())
        env_a.step()
        traj_b.append(env_b.observe())
        env_b.step()
    A = np.stack(traj_a)
    B = np.stack(traj_b)
    assert np.array_equal(A, B), "ADT-E1: trajectories diverge under same config."


# ADT-E2 — integrated pressure bounded (no uncontrolled energy leak)
def test_adt_e2_pressure_integral_bounded():
    env = E0(E0Config(horizon=128))
    integrals = []
    while not env.is_done:
        integrals.append(env.observe().sum())
        env.step()
    integrals = np.array(integrals)
    G = env.config.grid_size
    assert (integrals >= 0).all() and (integrals <= G).all(), \
        "ADT-E2: pressure integral outside theoretical bounds [0, grid_size]."


# ADT-E3 — strict local boundedness
def test_adt_e3_local_bounds():
    env = E0(E0Config(horizon=64))
    while not env.is_done:
        f = env.observe()
        assert (f >= 0.0).all() and (f <= 1.0).all(), \
            f"ADT-E3: field outside [0,1] at t={env.t} (min={f.min()}, max={f.max()})"
        env.step()


# ADT-E4 — non-stationarity is real
def test_adt_e4_non_stationarity_is_real():
    cfg = E0Config(horizon=512)
    env = E0(cfg)
    f0 = env.observe().copy()
    target_t = cfg.horizon // 2
    while env.t < target_t:
        env.step()
    f_mid = env.observe().copy()

    support = np.linspace(0.0, 1.0, cfg.grid_size)
    # Normalization into probability distributions
    p0 = f0 / (f0.sum() + 1e-12)
    pm = f_mid / (f_mid.sum() + 1e-12)
    w = wasserstein_distance(support, support, p0, pm)
    assert w > 1e-3, (
        f"ADT-E4: non-stationarity not detectable "
        f"(W(p0, p_mid)={w:.2e}). E0 is effectively stationary."
    )


# ADT-E5 — black-box isolation
def test_adt_e5_blackbox_isolation():
    env = E0(E0Config())
    # Name-mangled internals must not be reachable via their declared name
    for forbidden in ("__freqs", "__phases", "__omegas", "__amplitudes", "__basis"):
        assert not hasattr(env, forbidden), \
            f"ADT-E5: internal attribute {forbidden!r} exposed."

    # Minimal stable public API
    public = {a for a in dir(env) if not a.startswith("_")}
    expected = {"observe", "act", "step", "is_done", "t", "config"}
    missing = expected - public
    assert not missing, f"ADT-E5: incomplete public API, missing {missing}."


# ADT-E6 — action has a measurable effect on local pressure
def test_adt_e6_action_modifies_local_pressure():
    cfg = E0Config()
    env_ctrl = E0(cfg)
    env_act = E0(cfg)

    # Stabilize a few steps
    for _ in range(5):
        env_ctrl.step()
        env_act.step()

    pos = cfg.grid_size // 2
    f_before = env_act.observe().copy()
    env_act.act(pos)
    f_after = env_act.observe()

    delta = f_before - f_after  # action decreases pressure
    assert delta[pos] > 0.0, \
        f"ADT-E6: action with no measurable effect at position {pos} (delta={delta[pos]})."

    # No divergence on the control side (env without action)
    f_ctrl = env_ctrl.observe()
    assert not np.array_equal(f_ctrl, f_after), \
        "ADT-E6: env with action is identical to env without action."


# ADT-E0 — action domain protection
def test_adt_e0_action_domain():
    env = E0(E0Config())
    with pytest.raises(ValueError):
        env.act(-1)
    with pytest.raises(ValueError):
        env.act(env.config.grid_size)
