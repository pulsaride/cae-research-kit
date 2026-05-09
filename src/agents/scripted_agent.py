"""Agent B — scripted regime (deterministic cycle).

Pre-determined control: scans the grid cyclically. No feedback. Serves as a
"structured but non-adaptive" lower bound.
"""
from __future__ import annotations

import numpy as np

from src.agents.base import Agent


class ScriptedAgent(Agent):
    name = "B"

    def __init__(self, grid_size: int, stride: int = 7) -> None:
        if stride <= 0:
            raise ValueError("stride must be > 0")
        self._grid_size = int(grid_size)
        self._stride = int(stride)
        self._k = 0

    def select_action(self, observation: np.ndarray) -> int:
        if observation.ndim != 1 or observation.shape[0] != self._grid_size:
            raise ValueError("observation incompatible with grid_size")
        pos = (self._k * self._stride) % self._grid_size
        self._k += 1
        return int(pos)

    def reset(self) -> None:
        self._k = 0
