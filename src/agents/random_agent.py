"""Agent R — uniform random regime (null control)."""
from __future__ import annotations

import numpy as np

from src.agents.base import Agent


class RandomAgent(Agent):
    """Selects a position uniformly. No adaptation."""

    name = "R"

    def __init__(self, grid_size: int, seed: int = 42) -> None:
        self._grid_size = int(grid_size)
        self._seed = int(seed)
        self._rng = np.random.default_rng(self._seed)

    def select_action(self, observation: np.ndarray) -> int:
        # Observation is ignored: R uses no information.
        if observation.ndim != 1 or observation.shape[0] != self._grid_size:
            raise ValueError("observation incompatible with grid_size")
        return int(self._rng.integers(0, self._grid_size))

    def reset(self) -> None:
        self._rng = np.random.default_rng(self._seed)
