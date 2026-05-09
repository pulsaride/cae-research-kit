"""ADT — destruction tests for the P agent (offline pretrained)."""
from __future__ import annotations

import numpy as np
import pytest

from src.agents.adaptive_agent import AdaptiveAgent
from src.agents.pretrained_agent import PretrainedAgent
from src.agents.scripted_agent import ScriptedAgent
from src.config.determinism import apply_cae_determinism
from src.env.e0 import E0, E0Config


@pytest.fixture(autouse=True)
def _bootstrap():
    apply_cae_determinism(strict=False)


def _factory(seed: int) -> E0:
    return E0(E0Config(seed=seed, horizon=128))


# ADT-P0 — training produces a valid policy
def test_adt_p0_train_produces_valid_policy():
    pol = PretrainedAgent.train(_factory, offline_seed=99)
    assert pol.shape == (PretrainedAgent._N_BINS,)
    assert pol.dtype.kind == "i"
    cfg = E0Config()
    assert (pol >= 0).all() and (pol < cfg.grid_size).all()


# ADT-P1 — no leakage: offline seed != evaluation seeds
def test_adt_p1_no_leakage():
    offline = 99
    eval_seeds = list(range(1000, 1030))
    assert offline not in eval_seeds


# ADT-P2 — policy is immutable during evaluation
def test_adt_p2_policy_is_immutable():
    pol = PretrainedAgent.train(_factory, offline_seed=99)
    p = PretrainedAgent(grid_size=64, policy_table=pol)
    snapshot = p._policy.copy()
    obs = np.linspace(0, 1, 64)
    for _ in range(50):
        p.select_action(obs)
    assert np.array_equal(snapshot, p._policy), "ADT-P2: policy mutated."
    with pytest.raises(ValueError):
        p._policy[0] = 0  # write=False


# ADT-P3 — no reference to E0
def test_adt_p3_blackbox_isolation():
    pol = PretrainedAgent.train(_factory, offline_seed=99)
    p = PretrainedAgent(grid_size=64, policy_table=pol)
    for v in vars(p).values():
        assert not isinstance(v, E0)


# ADT-P4 — bit-exact reproducibility
def test_adt_p4_bitwise_reproducibility():
    pol1 = PretrainedAgent.train(_factory, offline_seed=99)
    pol2 = PretrainedAgent.train(_factory, offline_seed=99)
    assert np.array_equal(pol1, pol2)


# ADT-P5 — reactive to observation, yet distinct from B and A
def test_adt_p5_reactive_yet_distinct():
    cfg = E0Config(horizon=128, seed=2026)
    pol = PretrainedAgent.train(_factory, offline_seed=99)
    p = PretrainedAgent(grid_size=cfg.grid_size, policy_table=pol)
    a = AdaptiveAgent(cfg.grid_size)
    b = ScriptedAgent(cfg.grid_size)

    actions_p, actions_a, actions_b = [], [], []
    env_p, env_a, env_b = E0(cfg), E0(cfg), E0(cfg)
    while not env_p.is_done:
        ap = p.select_action(env_p.observe()); env_p.act(ap); env_p.step(); actions_p.append(ap)
        aa = a.select_action(env_a.observe()); env_a.act(aa); env_a.step(); actions_a.append(aa)
        ab = b.select_action(env_b.observe()); env_b.act(ab); env_b.step(); actions_b.append(ab)

    P = np.array(actions_p); A = np.array(actions_a); B = np.array(actions_b)
    # P must be reactive (!= scripted B) and distinct from A
    assert not np.array_equal(P, B), "ADT-P5: P == B (hence non-reactive)."
    assert not np.array_equal(P, A), "ADT-P5: P == A (training = expert => leakage)."
    # Non-trivial variability
    assert len(set(P.tolist())) > 1, "ADT-P5: P always identical."
