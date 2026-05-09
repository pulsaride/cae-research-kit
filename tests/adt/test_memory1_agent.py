"""ADT — destruction tests for Memory1Agent (H7-κ, ADR-030 §4)."""
from __future__ import annotations

import numpy as np
import pytest

from src.agents.memory1_agent import Memory1Agent
from src.config.determinism import apply_cae_determinism
from src.env.e0 import E0, E0Config


@pytest.fixture(autouse=True)
def _bootstrap():
    apply_cae_determinism(strict=False)


# ADT-κ-1 — bit-identical determinism over 1000 ticks across two instances
def test_adt_kappa_1_determinism_two_instances():
    cfg = E0Config(horizon=1000)
    env_a = E0(cfg)
    env_b = E0(cfg)
    agent_a = Memory1Agent(cfg.grid_size)
    agent_b = Memory1Agent(cfg.grid_size)
    actions_a, actions_b = [], []
    while not env_a.is_done:
        a = agent_a.select_action(env_a.observe())
        env_a.act(a); env_a.step()
        actions_a.append(a)
        b = agent_b.select_action(env_b.observe())
        env_b.act(b); env_b.step()
        actions_b.append(b)
    assert actions_a == actions_b
    assert len(actions_a) == 1000


# ADT-κ-2 — interface conformance (Agent contract)
def test_adt_kappa_2_interface_conformance():
    cfg = E0Config()
    agent = Memory1Agent(cfg.grid_size)
    obs = np.full(cfg.grid_size, 0.5, dtype=np.float64)
    a = agent.select_action(obs)
    assert isinstance(a, int)
    assert 0 <= a < cfg.grid_size
    # reset must zero the memory
    agent.reset()
    assert np.array_equal(agent._memory, np.zeros(cfg.grid_size))


# ADT-κ-3 — memory update: after select_action(O_t), internal m == O_t bit-identical
def test_adt_kappa_3_memory_update_is_last_observation():
    cfg = E0Config()
    agent = Memory1Agent(cfg.grid_size)
    rng = np.random.default_rng(0)
    obs = rng.uniform(0.0, 1.0, size=cfg.grid_size)
    agent.select_action(obs)
    assert np.array_equal(agent._memory, obs.astype(np.float64))
    # second tick: memory becomes the new observation
    obs2 = rng.uniform(0.0, 1.0, size=cfg.grid_size)
    agent.select_action(obs2)
    assert np.array_equal(agent._memory, obs2.astype(np.float64))


# ADT-κ-4 — t=0 case: A_0 = argmin(O_0)
def test_adt_kappa_4_initial_action_is_argmin():
    cfg = E0Config()
    agent = Memory1Agent(cfg.grid_size)
    obs = np.linspace(0.1, 0.9, cfg.grid_size)
    obs[17] = 0.05  # explicit minimum
    a = agent.select_action(obs)
    assert a == int(np.argmin(obs))
    assert a == 17


# ADT-κ-5 — invalid observation rejection
def test_adt_kappa_5_invalid_observation_rejected():
    cfg = E0Config()
    agent = Memory1Agent(cfg.grid_size)
    # wrong shape
    with pytest.raises(ValueError):
        agent.select_action(np.zeros(cfg.grid_size + 1))
    # out of [0,1]
    with pytest.raises(ValueError):
        agent.select_action(np.full(cfg.grid_size, 1.5))
    with pytest.raises(ValueError):
        agent.select_action(np.full(cfg.grid_size, -0.1))
    # 2D
    with pytest.raises(ValueError):
        agent.select_action(np.zeros((cfg.grid_size, 2)))
