"""CAE — constraint-pressure metrics and inter-distribution distances.

Every measurement here must be:
- mathematically defined (no homemade "score"),
- bounded and declared,
- cross-checked between at least two implementations (scipy vs POT) for
  Wasserstein.
"""
from __future__ import annotations

import numpy as np
import ot
from scipy.stats import wasserstein_distance as _scipy_w1

from src.metrics.base import ConstraintMetric

_EPS = 1e-12


def _validate_distribution(p: np.ndarray, name: str) -> np.ndarray:
    if not isinstance(p, np.ndarray):
        raise TypeError(f"{name} must be np.ndarray")
    if p.ndim != 1:
        raise ValueError(f"{name} must be 1D (got ndim={p.ndim})")
    if not np.isfinite(p).all():
        raise ValueError(f"{name} contains non-finite values (NaN/Inf)")
    if (p < 0).any():
        raise ValueError(f"{name} contains negative values")
    s = float(p.sum())
    if s <= _EPS:
        raise ValueError(f"{name} has zero total mass")
    return p.astype(np.float64) / s


def wasserstein1_scipy(p: np.ndarray, q: np.ndarray,
                       support: np.ndarray | None = None) -> float:
    """Wasserstein-1 via scipy. Default support = uniform grid [0,1)."""
    p = _validate_distribution(p, "p")
    q = _validate_distribution(q, "q")
    if p.shape != q.shape:
        raise ValueError(f"incompatible shapes: {p.shape} vs {q.shape}")
    if support is None:
        support = np.linspace(0.0, 1.0, p.shape[0], endpoint=False)
    return float(_scipy_w1(support, support, p, q))


def wasserstein1_ot(p: np.ndarray, q: np.ndarray,
                    support: np.ndarray | None = None) -> float:
    """Wasserstein-1 via POT (ot.emd2) with cost |x-y|."""
    p = _validate_distribution(p, "p")
    q = _validate_distribution(q, "q")
    if p.shape != q.shape:
        raise ValueError(f"incompatible shapes: {p.shape} vs {q.shape}")
    if support is None:
        support = np.linspace(0.0, 1.0, p.shape[0], endpoint=False)
    M = np.abs(support[:, None] - support[None, :])
    return float(ot.emd2(p, q, M))


class Wasserstein1(ConstraintMetric):
    """Primary W1 distance implementation (via POT, cross-checked with scipy)."""

    name = "W1"

    def __init__(self, support: np.ndarray | None = None,
                 cross_check: bool = False, tol: float = 1e-6) -> None:
        self._support = support
        self._cross_check = bool(cross_check)
        self._tol = float(tol)

    def compute(self, distribution_a: np.ndarray,
                distribution_b: np.ndarray) -> float:
        w_ot = wasserstein1_ot(distribution_a, distribution_b, self._support)
        if self._cross_check:
            w_sp = wasserstein1_scipy(distribution_a, distribution_b, self._support)
            if abs(w_ot - w_sp) > self._tol:
                raise RuntimeError(
                    f"[CAE_METRIC] scipy/POT disagreement: "
                    f"W_ot={w_ot:.9e}, W_scipy={w_sp:.9e}, "
                    f"|Δ|={abs(w_ot - w_sp):.2e} > tol={self._tol:.0e}"
                )
        return w_ot


# ---------------------------------------------------------------------------
# Constraint pressure — trajectory estimators
# ---------------------------------------------------------------------------

def pressure_entropy(field: np.ndarray) -> float:
    """Shannon entropy (base e) of the normalized pressure distribution.

    Bounds: [0, log(n)]. 0 = mass concentrated. log(n) = uniform.
    Standard convention: 0·log(0) = 0 (no epsilon regularization in the log,
    which would introduce a negative bias on Diracs).
    """
    p = _validate_distribution(field, "field")
    nz = p > 0.0
    return float(-np.sum(p[nz] * np.log(p[nz])))


def pressure_concentration(field: np.ndarray) -> float:
    """Normalized Herfindahl-Hirschman index: Σ p_i². Bounded [1/n, 1]."""
    p = _validate_distribution(field, "field")
    return float(np.sum(p ** 2))


def trajectory_redistribution(
    fields: np.ndarray,
    *,
    metric: ConstraintMetric | None = None,
) -> np.ndarray:
    """Sequence of W1 distances between successive fields of a trajectory.

    `fields`: shape (T, grid_size). Returns shape (T-1,).
    Measures the instantaneous **redistribution flow** — the H5 quantity
    of interest.
    """
    if fields.ndim != 2:
        raise ValueError("fields must be 2D (T, grid_size)")
    if fields.shape[0] < 2:
        raise ValueError("at least 2 steps required")
    metric = metric if metric is not None else Wasserstein1()
    out = np.empty(fields.shape[0] - 1, dtype=np.float64)
    for i in range(fields.shape[0] - 1):
        out[i] = metric.compute(fields[i], fields[i + 1])
    return out
