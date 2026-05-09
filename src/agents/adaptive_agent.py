"""Agent A — online adaptive regime.

Policy: target the position of the maximum observed pressure, broken by a
deterministic bounded-momentum mechanism (no neural network, no
stochasticity — adaptation is purely structural, the minimum required to
test H5 without introducing confounding variables).

The agent maintains an inertia trace that penalizes recently visited
positions: it thus avoids hammering the same cell and redistributes its
actions according to the current constraint flow.
"""
from __future__ import annotations

import numpy as np

from src.agents.base import Agent


class AdaptiveAgent(Agent):
    name = "A"

    def __init__(
        self,
        grid_size: int,
        memory_decay: float = 0.85,
        memory_penalty: float = 0.4,
    ) -> None:
        if not (0.0 <= memory_decay < 1.0):
            raise ValueError("memory_decay in [0,1)")
        if memory_penalty < 0.0:
            raise ValueError("memory_penalty >= 0")
        self._grid_size = int(grid_size)
        self._decay = float(memory_decay)
        self._penalty = float(memory_penalty)
        self._memory = np.zeros(self._grid_size, dtype=np.float64)

    def select_action(self, observation: np.ndarray) -> int:
        if observation.ndim != 1 or observation.shape[0] != self._grid_size:
            raise ValueError("observation incompatible with grid_size")

        score = observation - self._penalty * self._memory
        # Deterministic argmax (first maximum on ties)
        pos = int(np.argmax(score))

        # Inertia memory update: exponential decay.
        self._memory *= self._decay
        self._memory[pos] += 1.0
        return pos

    def reset(self) -> None:
        self._memory[:] = 0.0
