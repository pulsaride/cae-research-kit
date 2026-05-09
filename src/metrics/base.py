"""CAE — cold interface for constraint-pressure measurements."""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class ConstraintMetric(ABC):
    """Contract for any distance between constraint distributions.

    An implementation must be falsifiable by /tests/adt:
    - symmetry (or declared non-symmetry),
    - identity of indiscernibles,
    - bit-exact reproducibility under CAE_SEED=42.
    """

    name: str = "abstract"

    @abstractmethod
    def compute(
        self,
        distribution_a: np.ndarray,
        distribution_b: np.ndarray,
    ) -> float:
        """Return the scalar distance. Must raise NotImplementedError on the base."""
        raise NotImplementedError("ADT must be able to falsify any subclass.")
