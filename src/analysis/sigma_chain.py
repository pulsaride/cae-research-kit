"""CAE — H7 σ-chain : public re-implementation per ADR-026 §3.1-§3.4 + ADR-027.

This module is the *public* sister of the private σ-chain runner used to
produce v0.3.0-h7-σ-inverted and v0.4.0-h7-κ-reverses. It exposes every
statistical decision as a pure numpy/scipy function so that the v0.4.0
artefacts can be re-derived bit-identically (audit ADR-033) before this
layer is trusted to produce v0.5.0.

Spec authority (verbatim):
- ADR-026 §3.2  : pressure scalar = flatten over (cell, tick), B=64,
                  support [0.0, 1.0], right-inclusive last bin, clip events
                  recorded.
- ADR-026 §3.3  : asymmetric Laplace +1 on M for any bin where n_X > 0
                  but n_M = 0. K_M^post counted *after* this addition.
                  Plug-in entropy in nats.
                  H_MM(X) = H_plug(X) + (K_X − 1) / (2T).
                  KL_corr(X ‖ M) = H_cross(X, M) − H_MM(X)
                                   + (K_M^post − 1) / (2T).
                  KL_naive(X ‖ M) = H_cross(X, M) − H_plug(X)
                                    (Laplace still applied to M for finiteness).
- ADR-022 §4.3  : Markov-null transition matrix uses Laplace α=1.0 on
                  transition counts.
- ADR-026 §3.1  : sample_markov uses np.random.default_rng(s); initial
                  state is actions_R[0].
- ADR-027 §2-4  : Wilcoxon paired, scipy.stats.wilcoxon, zero_method="wilcox",
                  alternative ∈ {"greater", "less"}, α = 0.005 per branch,
                  Cohen d = mean / std(ddof=1).

This file does NOT speak about verdict labels (KAPPA_REVERSES etc.) —
that mapping is in src.analysis.verdict_v05 to keep the chain decoupled
from the verdict grid.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import wilcoxon

# Constantes E₀ figées par ADR-026 §3.2 + ADR-030 §3.1.
B_DEFAULT: int = 64
P_MIN_DEFAULT: float = 0.0
P_MAX_DEFAULT: float = 1.0


# ----------------------------------------------------------------------
# 1. Histogramme & clipping
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class HistogramResult:
    """Counts per bin + number of out-of-range samples that were clipped."""

    counts: np.ndarray  # shape=(B,), dtype=int64
    clip_events: int    # samples clipped to [P_min, P_max]
    total: int          # sum(counts) == samples.size


def histogram_pressure(
    samples: np.ndarray,
    B: int = B_DEFAULT,
    P_min: float = P_MIN_DEFAULT,
    P_max: float = P_MAX_DEFAULT,
) -> HistogramResult:
    """Equal-width histogram on [P_min, P_max], B bins, right-inclusive last bin.

    Spec ADR-026 §3.2 :
    - "Discretisation: equal-width bins on [0.0, 1.0], B = 64.
       Right edge inclusive (last bin captures p = 1.0 exactly)."
    - "Any out-of-range value is clipped to the nearest endpoint.
       The number of clip events is recorded."

    Implementation choice (deterministic):
    - np.histogram with bins=np.linspace(P_min, P_max, B+1) gives left-inclusive,
      right-exclusive intervals except the last which is closed on both sides.
      That is exactly the behaviour ADR-026 §3.2 describes.
    """
    if samples.ndim != 1:
        raise ValueError(f"samples must be 1D, got ndim={samples.ndim}")
    if not np.isfinite(samples).all():
        raise ValueError("samples contain non-finite values")
    if B < 2:
        raise ValueError(f"B must be >= 2, got {B}")
    if not (P_max > P_min):
        raise ValueError(f"P_max must be > P_min ({P_min} >= {P_max})")

    # Clip and count clipped events.
    out_of_range = (samples < P_min) | (samples > P_max)
    clip_events = int(out_of_range.sum())
    clipped = np.clip(samples, P_min, P_max)

    edges = np.linspace(P_min, P_max, B + 1)
    counts, _ = np.histogram(clipped, bins=edges)
    # np.histogram already makes the last bin right-inclusive — verified by the
    # ADT histogram_includes_p_max.

    return HistogramResult(
        counts=counts.astype(np.int64),
        clip_events=clip_events,
        total=int(counts.sum()),
    )


# ----------------------------------------------------------------------
# 2. Entropies & KL (ADR-026 §3.3 verbatim)
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class KLResult:
    """KL(X ‖ M) decomposition with bias accounting."""

    kl_corrected: float       # KL_corr per ADR-026 §3.3
    kl_naive: float           # KL_naive per ADR-026 §3.3 (asymmetric Laplace on M)
    K_X_nonempty: int         # bins of X with n>0
    K_M_nonempty_post: int    # bins of M with n>0 AFTER asymmetric Laplace
    laplace_bins: int         # number of bins where Laplace +1 was added to M
    total_X: int              # Σ n_X
    total_M_post: int         # Σ n_M after asymmetric Laplace


def _plug_in_entropy(counts: np.ndarray, total: int) -> float:
    """H_plug(X) = -Σ_{b: n_X[b]>0} (n_X[b]/T) · log(n_X[b]/T), in nats."""
    nz = counts[counts > 0]
    if total <= 0:
        raise ValueError("total must be > 0")
    p = nz.astype(np.float64) / float(total)
    return float(-(p * np.log(p)).sum())


def _miller_madow_correction(K: int, total: int) -> float:
    """(K - 1) / (2T)."""
    return (K - 1) / (2.0 * total)


def kl_corrected_and_naive(
    counts_X: np.ndarray,
    counts_M: np.ndarray,
) -> KLResult:
    """Compute KL_corr and KL_naive per ADR-026 §3.3 with asymmetric Laplace.

    Both inputs are integer count vectors of identical length B.
    """
    if counts_X.shape != counts_M.shape:
        raise ValueError(
            f"shape mismatch: X={counts_X.shape}, M={counts_M.shape}"
        )
    if counts_X.ndim != 1:
        raise ValueError(f"counts must be 1D, got ndim={counts_X.ndim}")
    if (counts_X < 0).any() or (counts_M < 0).any():
        raise ValueError("counts must be non-negative")

    counts_X = counts_X.astype(np.int64, copy=True)
    counts_M = counts_M.astype(np.int64, copy=True)
    total_X = int(counts_X.sum())
    if total_X <= 0:
        raise ValueError("counts_X has zero total mass")

    # Asymmetric Laplace +1 on M for any bin where n_X > 0 AND n_M == 0.
    # Spec ADR-026 §3.3 : "asymmetric: P-counts unchanged, then renormalise."
    needs_laplace = (counts_X > 0) & (counts_M == 0)
    laplace_bins = int(needs_laplace.sum())
    counts_M[needs_laplace] += 1
    total_M_post = int(counts_M.sum())
    if total_M_post <= 0:
        raise ValueError("counts_M has zero total mass even after Laplace")

    K_X = int((counts_X > 0).sum())
    K_M_post = int((counts_M > 0).sum())

    # Plug-in entropy of X.
    H_X_plug = _plug_in_entropy(counts_X, total_X)

    # Cross entropy H(X, M) = -Σ_b p_X[b] · log p_M[b], summed over bins where n_X > 0.
    # Where n_X > 0 we have either n_M > 0 originally or n_M = 1 post-Laplace,
    # so log p_M is finite by construction.
    nz_X = counts_X > 0
    p_X_nz = counts_X[nz_X].astype(np.float64) / float(total_X)
    p_M_nz = counts_M[nz_X].astype(np.float64) / float(total_M_post)
    H_cross = float(-(p_X_nz * np.log(p_M_nz)).sum())

    # Miller-Madow corrected KL.
    H_X_MM = H_X_plug + _miller_madow_correction(K_X, total_X)
    kl_corr = H_cross - H_X_MM + _miller_madow_correction(K_M_post, total_M_post)

    # Naive KL (plug-in entropy of X, no MM term, asymmetric Laplace still applied to M).
    kl_naive = H_cross - H_X_plug

    return KLResult(
        kl_corrected=float(kl_corr),
        kl_naive=float(kl_naive),
        K_X_nonempty=K_X,
        K_M_nonempty_post=K_M_post,
        laplace_bins=laplace_bins,
        total_X=total_X,
        total_M_post=total_M_post,
    )


# ----------------------------------------------------------------------
# 3. Markov-null fit/sample (ADR-022 §4.3 + ADR-026 §3.1)
# ----------------------------------------------------------------------

def fit_markov_transition(
    actions: np.ndarray,
    n_states: int,
    alpha: float = 1.0,
) -> np.ndarray:
    """First-order Markov transition matrix with Laplace smoothing α=1.0.

    Spec ADR-022 §4.3 / ADR-026 §3.1 : "Laplace α=1.0 on transition counts".

    Returns P[i, j] = (count(i→j) + alpha) / (Σ_j count(i→j) + alpha · n_states).
    """
    if actions.ndim != 1:
        raise ValueError("actions must be 1D")
    if actions.size < 2:
        raise ValueError("need at least 2 actions to fit transitions")
    if n_states <= 0:
        raise ValueError("n_states must be > 0")
    if (actions < 0).any() or (actions >= n_states).any():
        raise ValueError("action out of [0, n_states)")
    if alpha < 0.0:
        raise ValueError("alpha must be >= 0")

    counts = np.zeros((n_states, n_states), dtype=np.float64)
    src = actions[:-1].astype(np.int64)
    dst = actions[1:].astype(np.int64)
    np.add.at(counts, (src, dst), 1.0)

    smoothed = counts + alpha
    row_sums = smoothed.sum(axis=1, keepdims=True)
    return smoothed / row_sums


def sample_markov(
    P: np.ndarray,
    length: int,
    seed: int,
    init_state: int,
) -> np.ndarray:
    """Sample a Markov chain of given length from transition matrix P.

    Spec ADR-026 §3.1 : "replay seed for sample_markov is seed = s
    (numpy default_rng); initial state is actions_R[0]".

    Implementation : at each step t, draw next state from P[state, :] using
    rng.choice.  Bit-identical given (P, length, seed, init_state).
    """
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        raise ValueError("P must be square")
    if length <= 0:
        raise ValueError("length must be > 0")
    n_states = P.shape[0]
    if not (0 <= init_state < n_states):
        raise ValueError("init_state out of [0, n_states)")
    # Sanity: rows must sum to 1.
    if not np.allclose(P.sum(axis=1), 1.0, atol=1e-10):
        raise ValueError("rows of P must sum to 1")

    rng = np.random.default_rng(seed)
    out = np.empty(length, dtype=np.int64)
    out[0] = init_state
    states = np.arange(n_states)
    for t in range(1, length):
        out[t] = rng.choice(states, p=P[out[t - 1]])
    return out


# ----------------------------------------------------------------------
# 4. Wilcoxon + Cohen d (ADR-027 §2-4)
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class WilcoxonResult:
    """Output of paired one-sided Wilcoxon."""

    statistic: float
    p_value: float
    n_post_drop: int
    n_dropped: int


def wilcoxon_paired_one_sided(
    deltas: np.ndarray,
    alternative: str,
) -> WilcoxonResult:
    """Paired Wilcoxon, scipy default mode, zero_method='wilcox'.

    Spec ADR-027 §2 : alternative ∈ {'greater', 'less'},
    zero_method='wilcox' (drop exact zeros, then rank).
    """
    if alternative not in ("greater", "less"):
        raise ValueError("alternative must be 'greater' or 'less'")
    if deltas.ndim != 1:
        raise ValueError("deltas must be 1D")

    n_total = int(deltas.size)
    nonzero = deltas[deltas != 0.0]
    n_post_drop = int(nonzero.size)

    if n_post_drop == 0:
        # Degenerate: all deltas are exactly zero.
        return WilcoxonResult(
            statistic=float("nan"),
            p_value=1.0,
            n_post_drop=0,
            n_dropped=n_total,
        )

    res = wilcoxon(
        deltas,
        alternative=alternative,
        zero_method="wilcox",
    )
    return WilcoxonResult(
        statistic=float(res.statistic),
        p_value=float(res.pvalue),
        n_post_drop=n_post_drop,
        n_dropped=n_total - n_post_drop,
    )


def cohen_d_paired(deltas: np.ndarray) -> float:
    """Cohen d = mean(deltas) / std(deltas, ddof=1).

    Spec ADR-027 §4 : "d = mean(δ_σ) / std(δ_σ, ddof=1)".
    """
    if deltas.ndim != 1:
        raise ValueError("deltas must be 1D")
    if deltas.size < 2:
        raise ValueError("need at least 2 deltas for ddof=1 std")
    s = float(np.std(deltas, ddof=1))
    if s == 0.0:
        return float("nan")
    return float(np.mean(deltas) / s)
