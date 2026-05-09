"""ADT — ObsShuffledAgent."""
from __future__ import annotations

import hashlib

import numpy as np
import pytest

from src.agents.adaptive_agent import AdaptiveAgent
from src.agents.base import Agent
from src.agents.memory1_agent import Memory1Agent
from src.agents.obs_shuffled_agent import ObsShuffledAgent, _obs_shuffle_seed


GRID = 64


# ----------------------------------------------------------------------
# Seed derivation (BLAKE2b spec, ADR-027 §7)
# ----------------------------------------------------------------------

def test_obs_shuffle_seed_deterministic() -> None:
    """Same env_seed → same uint64 seed across calls and across processes
    (BLAKE2b is hash-stable, unlike Python's hash())."""
    s1 = _obs_shuffle_seed(1500)
    s2 = _obs_shuffle_seed(1500)
    assert s1 == s2
    # And the value is exactly the BLAKE2b digest interpreted as expected.
    expected = int.from_bytes(
        hashlib.blake2b(b"obs_shuffle::1500", digest_size=8).digest(),
        byteorder="little",
    )
    assert s1 == expected


def test_obs_shuffle_seed_distinct_across_env_seeds() -> None:
    seeds = [_obs_shuffle_seed(s) for s in range(1500, 1510)]
    assert len(set(seeds)) == len(seeds)  # all distinct


# ----------------------------------------------------------------------
# Interface conformance
# ----------------------------------------------------------------------

def test_is_an_agent() -> None:
    inner = AdaptiveAgent(GRID)
    s = ObsShuffledAgent(inner, GRID, env_seed=1500)
    assert isinstance(s, Agent)
    assert s.name == "S"


def test_rejects_non_agent_inner() -> None:
    with pytest.raises(TypeError, match="inner must be an Agent"):
        ObsShuffledAgent("not_an_agent", GRID, env_seed=1500)  # type: ignore


def test_rejects_invalid_grid_size() -> None:
    with pytest.raises(ValueError, match="grid_size must be > 0"):
        ObsShuffledAgent(AdaptiveAgent(GRID), 0, env_seed=1500)


def test_rejects_observation_wrong_shape() -> None:
    s = ObsShuffledAgent(AdaptiveAgent(GRID), GRID, env_seed=1500)
    with pytest.raises(ValueError, match="incompatible with grid_size"):
        s.select_action(np.zeros(GRID + 1))
    with pytest.raises(ValueError, match="incompatible with grid_size"):
        s.select_action(np.zeros((GRID, 2)))


def test_returns_int_in_range() -> None:
    s = ObsShuffledAgent(AdaptiveAgent(GRID), GRID, env_seed=1500)
    rng = np.random.default_rng(0)
    obs = rng.uniform(0, 1, size=GRID)
    action = s.select_action(obs)
    assert isinstance(action, int)
    assert 0 <= action < GRID


# ----------------------------------------------------------------------
# Determinism (ADR-027 §7 — bit-identical replay required)
# ----------------------------------------------------------------------

def test_determinism_bitwise_under_same_seed() -> None:
    """Two ObsShuffledAgent instances with the same env_seed and same
    observation sequence must emit bit-identical action sequences."""
    rng = np.random.default_rng(42)
    obs_seq = [rng.uniform(0, 1, size=GRID) for _ in range(200)]

    s1 = ObsShuffledAgent(AdaptiveAgent(GRID), GRID, env_seed=1500)
    s2 = ObsShuffledAgent(AdaptiveAgent(GRID), GRID, env_seed=1500)

    actions1 = [s1.select_action(o) for o in obs_seq]
    actions2 = [s2.select_action(o) for o in obs_seq]

    assert actions1 == actions2


def test_distinct_seeds_yield_distinct_action_sequences() -> None:
    """Sanity: different env_seed → different permutation streams ⇒
    different actions on the same obs sequence (with high probability)."""
    rng = np.random.default_rng(7)
    obs_seq = [rng.uniform(0, 1, size=GRID) for _ in range(200)]

    s1 = ObsShuffledAgent(AdaptiveAgent(GRID), GRID, env_seed=1500)
    s2 = ObsShuffledAgent(AdaptiveAgent(GRID), GRID, env_seed=1501)
    actions1 = [s1.select_action(o) for o in obs_seq]
    actions2 = [s2.select_action(o) for o in obs_seq]
    assert actions1 != actions2  # extremely unlikely to collide


def test_reset_returns_to_starting_state() -> None:
    """After reset, the agent must produce the same first action as a
    freshly-constructed instance with the same env_seed."""
    rng = np.random.default_rng(0)
    obs = rng.uniform(0, 1, size=GRID)

    s = ObsShuffledAgent(AdaptiveAgent(GRID), GRID, env_seed=1500)
    a0 = s.select_action(obs)
    # consume some state
    for _ in range(50):
        s.select_action(rng.uniform(0, 1, size=GRID))
    s.reset()
    a0_after_reset = s.select_action(obs)
    assert a0 == a0_after_reset


# ----------------------------------------------------------------------
# Permutation properties (ADR-024 §3.2)
# ----------------------------------------------------------------------

def test_permutation_preserves_marginal_distribution() -> None:
    """A permutation does not change the multiset of values — only their
    positions. So the inner agent sees the same set of values per tick,
    just at scrambled positions."""
    obs = np.linspace(0.0, 1.0, GRID, endpoint=False)

    captured: list[np.ndarray] = []

    class CapturingAgent(Agent):
        name = "capture"

        def select_action(self, observation: np.ndarray) -> int:
            captured.append(observation.copy())
            return 0

        def reset(self) -> None:  # pragma: no cover
            pass

    s = ObsShuffledAgent(CapturingAgent(), GRID, env_seed=1500)
    for _ in range(10):
        s.select_action(obs)

    # Each captured permuted obs should be a permutation of obs (same multiset).
    for permuted in captured:
        np.testing.assert_array_equal(np.sort(permuted), np.sort(obs))


def test_permutation_changes_per_tick() -> None:
    """Spec ADR-024 §3.2 : 'drawn fresh at each tick'.
    With high probability two consecutive permutations differ."""
    obs = np.arange(GRID, dtype=np.float64) / GRID

    captured: list[np.ndarray] = []

    class CapturingAgent(Agent):
        name = "capture"

        def select_action(self, observation: np.ndarray) -> int:
            captured.append(observation.copy())
            return 0

        def reset(self) -> None:  # pragma: no cover
            pass

    s = ObsShuffledAgent(CapturingAgent(), GRID, env_seed=1500)
    for _ in range(5):
        s.select_action(obs)

    # All five permuted observations should be distinct (proba of collision
    # on GRID=64 is vanishingly small).
    for i in range(len(captured)):
        for j in range(i + 1, len(captured)):
            assert not np.array_equal(captured[i], captured[j])


def test_action_is_passed_through_unchanged() -> None:
    """Spec ADR-024 §3.2 : 'The action it emits is sent to the real
    (un-permuted) E₀.' So whatever index the inner agent returns is
    emitted as-is, NOT inverse-permuted."""

    class FixedAgent(Agent):
        name = "fixed"

        def select_action(self, observation: np.ndarray) -> int:
            return 7  # always returns 7

        def reset(self) -> None:  # pragma: no cover
            pass

    s = ObsShuffledAgent(FixedAgent(), GRID, env_seed=1500)
    for _ in range(20):
        assert s.select_action(np.zeros(GRID)) == 7


def test_blackbox_no_env_reference() -> None:
    """ObsShuffledAgent must not hold any reference to E₀ (PROTOCOL §3)."""
    s = ObsShuffledAgent(AdaptiveAgent(GRID), GRID, env_seed=1500)
    # Public surface: name, select_action, reset (inherited from Agent).
    public_attrs = {a for a in dir(s) if not a.startswith("_")}
    # Allow the standard Agent surface only.
    allowed = {"name", "select_action", "reset"}
    leaked = public_attrs - allowed
    assert not leaked, f"public leaks: {leaked}"


# ----------------------------------------------------------------------
# Composability with Memory1Agent (κ context)
# ----------------------------------------------------------------------

def test_wraps_memory1_agent_deterministically() -> None:
    """In the κ context (ADR-026 §3.1), S can wrap M_κ as well to test
    the obs-shuffled control on the memory-1 policy. Determinism must
    hold there too."""
    rng = np.random.default_rng(0)
    obs_seq = [rng.uniform(0, 1, size=GRID) for _ in range(100)]

    s1 = ObsShuffledAgent(Memory1Agent(GRID), GRID, env_seed=1500)
    s2 = ObsShuffledAgent(Memory1Agent(GRID), GRID, env_seed=1500)
    a1 = [s1.select_action(o) for o in obs_seq]
    a2 = [s2.select_action(o) for o in obs_seq]
    assert a1 == a2
