"""CAE — cold agent interface (A, B, R, P).

Black-box isolation contract (PROTOCOL §3):
- An agent NEVER receives a reference to E0.
- An agent receives only an `np.ndarray` observation and returns an integer
  `position` in [0, grid_size).
- No public method beyond `select_action` and `reset`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class Agent(ABC):
    """Single interface for any optimization regime compared under H5."""

    name: str = "abstract"

    @abstractmethod
    def select_action(self, observation: np.ndarray) -> int:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state to the deterministic starting point."""
        raise NotImplementedError
