"""Agent P — offline pre-trained policy, frozen at evaluation time.

Training phase (offline):
    A reference trajectory is simulated with an AdaptiveAgent on a dedicated
    E0 seed (offline_seed). A "tabular policy" is extracted: for each
    discretized observation profile, the mean action position chosen by the
    offline expert.

Evaluation phase (online):
    P consults its frozen table. No learning. No internal state update
    beyond the read.

H5 criterion: P must be REACTIVE (uses the observation) but STATIONARY
(time-invariant policy).
"""
from __future__ import annotations

import numpy as np

from src.agents.adaptive_agent import AdaptiveAgent
from src.agents.base import Agent


class PretrainedAgent(Agent):
    name = "P"

    # Observation discretization into N_BINS mean-pressure bins
    _N_BINS: int = 16

    def __init__(self, grid_size: int, policy_table: np.ndarray | None = None) -> None:
        self._grid_size = int(grid_size)
        if policy_table is None:
            raise ValueError("policy_table required (use PretrainedAgent.train())")
        if policy_table.shape != (self._N_BINS,):
            raise ValueError(
                f"policy_table shape {policy_table.shape} != ({self._N_BINS},)"
            )
        if not np.issubdtype(policy_table.dtype, np.integer):
            raise TypeError("policy_table must be integer")
        if ((policy_table < 0) | (policy_table >= self._grid_size)).any():
            raise ValueError("policy_table contains out-of-grid positions")
        # Frozen policy: copy to prevent external mutation.
        self._policy = policy_table.copy()
        self._policy.setflags(write=False)

    def select_action(self, observation: np.ndarray) -> int:
        if observation.ndim != 1 or observation.shape[0] != self._grid_size:
            raise ValueError("observation incompatible with grid_size")
        bin_idx = self._observation_to_bin(observation)
        return int(self._policy[bin_idx])

    def reset(self) -> None:
        # Stationary policy: nothing to reset.
        pass

    # ---- Deterministic discretization ------------------------------------

    @classmethod
    def _observation_to_bin(cls, observation: np.ndarray) -> int:
        # Index = position of the maximum, mapped onto N_BINS bins.
        argmax_pos = int(np.argmax(observation))
        n = observation.shape[0]
        return min(cls._N_BINS - 1, (argmax_pos * cls._N_BINS) // n)

    # ---- Offline training ------------------------------------------------

    @classmethod
    def train(cls, env_factory, offline_seed: int = 99) -> np.ndarray:
        """Build a tabular policy by observing an expert AdaptiveAgent.

        env_factory(seed:int)->E0 must produce an E0 disjoint from the
        evaluation seeds (the protocol forbids data leakage).
        """
        env = env_factory(offline_seed)
        expert = AdaptiveAgent(env.config.grid_size)
        # Buckets: sums of chosen positions + counts
        sums = np.zeros(cls._N_BINS, dtype=np.int64)
        counts = np.zeros(cls._N_BINS, dtype=np.int64)
        while not env.is_done:
            obs = env.observe()
            a = expert.select_action(obs)
            b = cls._observation_to_bin(obs)
            sums[b] += a
            counts[b] += 1
            env.act(a)
            env.step()
        # Mean position per bin (integer). Unvisited bins -> grid center.
        policy = np.where(
            counts > 0,
            sums // np.maximum(counts, 1),
            env.config.grid_size // 2,
        ).astype(np.int64)
        return policy
