"""ADT — destruction tests for the A / B / R agent triple."""
from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import kstest

from src.agents.adaptive_agent import AdaptiveAgent
from src.agents.base import Agent
from src.agents.random_agent import RandomAgent
from src.agents.scripted_agent import ScriptedAgent
from src.config.determinism import apply_cae_determinism
from src.env.e0 import E0, E0Config


@pytest.fixture(autouse=True)
def _bootstrap():
    apply_cae_determinism(strict=False)


def _run(agent: Agent, env: E0) -> tuple[np.ndarray, np.ndarray]:
    """Run a full trajectory; return (actions, integrated_pressure)."""
    actions, integrals = [], []
    while not env.is_done:
        obs = env.observe()
        a = agent.select_action(obs)
        env.act(a)
        tel = env.step()
        actions.append(a)
        integrals.append(tel["pressure_integral"])
    return np.array(actions), np.array(integrals)


# ADT-A1 — common interface
def test_adt_a1_common_interface():
    cfg = E0Config()
    agents = [
        AdaptiveAgent(cfg.grid_size),
        ScriptedAgent(cfg.grid_size),
        RandomAgent(cfg.grid_size, seed=42),
    ]
    for ag in agents:
        assert isinstance(ag, Agent)
        assert hasattr(ag, "select_action") and hasattr(ag, "reset")
        assert ag.name in {"A", "B", "R"}


# ADT-A2 — black-box isolation: no access to E0 from the agent
def test_adt_a2_blackbox_isolation():
    cfg = E0Config()
    for ag in (AdaptiveAgent(cfg.grid_size), ScriptedAgent(cfg.grid_size),
               RandomAgent(cfg.grid_size)):
        for attr in vars(ag).values():
            assert not isinstance(attr, E0), \
                f"{ag.name}: reference to E0 detected in internal state."


# ADT-A3 — bit-exact reproducibility for all three agents
@pytest.mark.parametrize("factory", [
    lambda gs: AdaptiveAgent(gs),
    lambda gs: ScriptedAgent(gs),
    lambda gs: RandomAgent(gs, seed=42),
])
def test_adt_a3_bitwise_reproducibility(factory):
    cfg = E0Config(horizon=128)
    a1, _ = _run(factory(cfg.grid_size), E0(cfg))
    a2, _ = _run(factory(cfg.grid_size), E0(cfg))
    assert np.array_equal(a1, a2), "ADT-A3: actions diverge under same config."


# ADT-A4 — R is uniform (KS test against discrete uniform)
def test_adt_a4_random_is_uniform():
    cfg = E0Config(horizon=512)
    actions, _ = _run(RandomAgent(cfg.grid_size, seed=42), E0(cfg))
    # KS test against U[0, grid_size)
    cdf = lambda x: np.clip(x / cfg.grid_size, 0.0, 1.0)
    stat, p = kstest(actions, cdf)
    assert p > 0.01, f"ADT-A4: R not uniform (p={p:.3f}, stat={stat:.3f})."


# ADT-A5 — the three regimes produce distinct sequences
def test_adt_a5_regimes_are_distinct():
    cfg = E0Config(horizon=256)
    aA, _ = _run(AdaptiveAgent(cfg.grid_size), E0(cfg))
    aB, _ = _run(ScriptedAgent(cfg.grid_size), E0(cfg))
    aR, _ = _run(RandomAgent(cfg.grid_size, seed=42), E0(cfg))
    assert not np.array_equal(aA, aB), "ADT-A5: A == B."
    assert not np.array_equal(aA, aR), "ADT-A5: A == R."
    assert not np.array_equal(aB, aR), "ADT-A5: B == R."


# ADT-A6 — A is reactive: perturbing the observation changes its actions
def test_adt_a6_adaptive_reacts_to_observation():
    cfg = E0Config()
    agA = AdaptiveAgent(cfg.grid_size)
    obs = np.zeros(cfg.grid_size)
    obs[10] = 1.0
    a1 = agA.select_action(obs)

    agA.reset()
    obs2 = np.zeros(cfg.grid_size)
    obs2[40] = 1.0
    a2 = agA.select_action(obs2)

    assert a1 != a2, "ADT-A6: A insensitive to observation (hence non-adaptive)."
    assert a1 == 10 and a2 == 40, "ADT-A6: A does not follow peak pressure."


# ADT-A7 — B remains deterministic and observation-independent
def test_adt_a7_scripted_is_observation_independent():
    cfg = E0Config()
    agB = ScriptedAgent(cfg.grid_size)
    obs1 = np.random.default_rng(1).random(cfg.grid_size)
    obs2 = np.random.default_rng(2).random(cfg.grid_size)
    a1 = agB.select_action(obs1)
    agB.reset()
    a2 = agB.select_action(obs2)
    assert a1 == a2, "ADT-A7: B depends on observation."
