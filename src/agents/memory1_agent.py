"""Agent M_κ — memory-1 on local pressure (H7-κ pre-registered, ADR-030 §2).

State:
    m_t ∈ [0, 1]^G,  m_0 = 0

Update (after select_action):
    m_{t+1} ← O_t

Action policy (single-line, vectorial, deterministic):
    A_t = argmax_i ( m_t[i] − O_t[i] )

Tie-break: smallest index (NumPy `argmax` default).
At t=0: m_0 = 0 ⇒ A_0 = argmax(−O_0) = argmin(O_0).

No learnable parameter, no noise, no decay. Determinism is bit-identical
under a given environment seed.
"""
from __future__ import annotations

import numpy as np

from src.agents.base import Agent


class Memory1Agent(Agent):
    """Memory-1 agent on local pressure (cf. ADR-030)."""

    name = "Mκ"

    def __init__(self, grid_size: int) -> None:
        if grid_size <= 0:
            raise ValueError("grid_size must be > 0")
        self._grid_size = int(grid_size)
        self._memory = np.zeros(self._grid_size, dtype=np.float64)

    def select_action(self, observation: np.ndarray) -> int:
        if observation.ndim != 1 or observation.shape[0] != self._grid_size:
            raise ValueError("observation incompatible with grid_size")
        if not np.all((observation >= 0.0) & (observation <= 1.0)):
            raise ValueError("observation out of [0, 1]")

        # ADR-030 §2.4 — single-line, vectorial, deterministic policy.
        pos = int(np.argmax(self._memory - observation))

        # ADR-030 §2.3 — memory update: strictly the last observation.
        self._memory = observation.astype(np.float64, copy=True)
        return pos

    def reset(self) -> None:
        self._memory[:] = 0.0
