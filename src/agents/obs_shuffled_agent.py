"""Agent S — observation-shuffled wrapper (H6-γ control, reused by H7-σ/κ).

Spec (verbatim) :
- ADR-024 §3.2 : "A per-tick column permutation π_t ∈ S_D is drawn fresh
  at each tick t from a dedicated PRNG seeded by (seed, 'obs_shuffle').
  The agent's update logic is unchanged. The action it emits is sent to
  the real (un-permuted) E₀."
- ADR-027 §7 : "BLAKE2b('obs_shuffle::s') seeds ObsShuffledAgent."
  → This supersedes ADR-024 §4's table entry that named Python's built-in
  hash(), which is non-deterministic under PYTHONHASHSEED. The byte-level
  seed source is BLAKE2b digest, first 8 bytes, little-endian uint64.

Black-box isolation : this wrapper has no reference to E₀. It receives
an observation array and returns a position int — same contract as any
other Agent (cf. PROTOCOL §3 and src.agents.base).

Determinism : two instances constructed with the same env_seed will
produce bit-identical action sequences when fed the same observation
sequence.
"""
from __future__ import annotations

import hashlib

import numpy as np

from src.agents.base import Agent


def _obs_shuffle_seed(env_seed: int) -> int:
    """BLAKE2b('obs_shuffle::s') first 8 bytes → uint64 LE.

    Spec ADR-027 §7. Stable across Python interpreter invocations,
    independent of PYTHONHASHSEED.
    """
    digest = hashlib.blake2b(
        f"obs_shuffle::{env_seed}".encode("ascii"),
        digest_size=8,
    ).digest()
    return int.from_bytes(digest, byteorder="little", signed=False)


class ObsShuffledAgent(Agent):
    """Wrap any Agent; permute its observations per tick.

    The action returned by the wrapped agent (an index into the *permuted*
    observation) is emitted unchanged to the real environment. This is
    intentional per ADR-024 §3.2 : it destroys the structural link between
    observation topology and action topology while preserving the marginal
    statistics of the observation each tick.
    """

    name = "S"

    def __init__(self, inner: Agent, grid_size: int, env_seed: int) -> None:
        if grid_size <= 0:
            raise ValueError("grid_size must be > 0")
        if not isinstance(inner, Agent):
            raise TypeError("inner must be an Agent instance")
        self._inner = inner
        self._grid_size = int(grid_size)
        self._env_seed = int(env_seed)
        self._rng = np.random.default_rng(_obs_shuffle_seed(self._env_seed))

    def select_action(self, observation: np.ndarray) -> int:
        if observation.ndim != 1 or observation.shape[0] != self._grid_size:
            raise ValueError("observation incompatible with grid_size")

        # Fresh permutation per tick (ADR-024 §3.2 : "drawn fresh at each tick").
        perm = self._rng.permutation(self._grid_size)
        permuted_obs = observation[perm]

        # Wrapped agent acts on permuted view; action is index in permuted space.
        action = self._inner.select_action(permuted_obs)
        if not (0 <= action < self._grid_size):
            raise ValueError(
                f"inner agent returned action {action} outside [0, {self._grid_size})"
            )
        # Emit as-is to the real env (ADR-024 §3.2 : "sent to the real un-permuted E₀").
        return int(action)

    def reset(self) -> None:
        # Reset both the wrapped agent and the permutation PRNG to the
        # deterministic starting point of this seed.
        self._inner.reset()
        self._rng = np.random.default_rng(_obs_shuffle_seed(self._env_seed))
