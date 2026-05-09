"""ADT — sigma_chain.py.

These tests are unitary: they validate each pure function on hand-computable
synthetic inputs. They do NOT validate cross-check against the v0.4.0 private
runner output — that audit is ADR-033 (separate gate).
"""
from __future__ import annotations

import numpy as np
import pytest

from src.analysis.sigma_chain import (
    HistogramResult,
    KLResult,
    WilcoxonResult,
    B_DEFAULT,
    P_MAX_DEFAULT,
    P_MIN_DEFAULT,
    cohen_d_paired,
    fit_markov_transition,
    histogram_pressure,
    kl_corrected_and_naive,
    sample_markov,
    wilcoxon_paired_one_sided,
)


# ----------------------------------------------------------------------
# histogram_pressure
# ----------------------------------------------------------------------

def test_histogram_includes_p_max() -> None:
    """The right edge must be inclusive: a sample at exactly P_max=1.0
    must fall in the LAST bin, not be discarded or clipped."""
    samples = np.array([1.0, 0.5, 0.0])
    res = histogram_pressure(samples, B=4, P_min=0.0, P_max=1.0)
    assert res.clip_events == 0  # 1.0 is in range
    assert res.total == 3
    assert res.counts[-1] == 1  # the 1.0 sample
    assert res.counts[0] == 1   # the 0.0 sample
    assert res.counts[2] == 1   # the 0.5 sample (bins 0.5-0.75)


def test_histogram_clips_out_of_range() -> None:
    samples = np.array([-0.1, 1.1, 0.5])
    res = histogram_pressure(samples, B=4, P_min=0.0, P_max=1.0)
    assert res.clip_events == 2
    assert res.total == 3
    assert res.counts[0] == 1   # -0.1 clipped to 0.0
    assert res.counts[-1] == 1  # 1.1 clipped to 1.0


def test_histogram_default_bins() -> None:
    """With defaults B=64, P=[0,1], samples uniform on [0,1] should fill all bins."""
    rng = np.random.default_rng(42)
    samples = rng.uniform(0, 1, size=10_000)
    res = histogram_pressure(samples)
    assert res.total == 10_000
    assert res.clip_events == 0
    assert res.counts.shape == (B_DEFAULT,)
    assert (res.counts > 0).sum() == B_DEFAULT  # all bins non-empty


def test_histogram_rejects_non_finite() -> None:
    with pytest.raises(ValueError, match="non-finite"):
        histogram_pressure(np.array([np.nan, 0.5]))


# ----------------------------------------------------------------------
# kl_corrected_and_naive — analytical cases
# ----------------------------------------------------------------------

def test_kl_identical_distributions_naive_is_zero() -> None:
    """KL_naive(X || X) = 0 when X = M (no Laplace needed)."""
    counts = np.array([10, 20, 30, 40], dtype=np.int64)
    res = kl_corrected_and_naive(counts, counts.copy())
    assert res.laplace_bins == 0
    assert res.K_X_nonempty == 4
    assert res.K_M_nonempty_post == 4
    assert abs(res.kl_naive) < 1e-12


def test_kl_corrected_identity_has_only_MM_residual() -> None:
    """When X = M, KL_corr reduces to (K_M^post - K_X)/(2T) * (correction terms only).
    Since K_X = K_M^post and total_X = total_M_post, KL_corr should be 0."""
    counts = np.array([10, 20, 30, 40], dtype=np.int64)
    res = kl_corrected_and_naive(counts, counts.copy())
    # H_cross = H_X_plug, and (K_X - 1)/(2T) cancels with (K_M^post - 1)/(2T)
    # since both are equal here. So KL_corr = 0.
    assert abs(res.kl_corrected) < 1e-12


def test_kl_asymmetric_laplace_when_M_zero_and_X_positive() -> None:
    """If X has mass on bin 0 but M does not, M[0] gets +1 (P unchanged)."""
    counts_X = np.array([5, 5, 0, 0], dtype=np.int64)
    counts_M = np.array([0, 5, 5, 0], dtype=np.int64)
    res = kl_corrected_and_naive(counts_X, counts_M)
    # Bin 0 of M should have been Laplace-incremented once (X[0]=5>0, M[0]=0).
    # Bin 2 of M unchanged because X[2]=0.
    # Bin 3: X=0 and M=0 → no Laplace needed (we only sum over X>0).
    assert res.laplace_bins == 1
    assert res.K_X_nonempty == 2
    assert res.K_M_nonempty_post == 3  # was 2, became 3 after Laplace
    assert res.total_X == 10
    assert res.total_M_post == 11  # 10 + 1 Laplace


def test_kl_naive_known_value() -> None:
    """Hand-computed: X = [10, 0], M = [5, 5].
    p_X = [1, 0], p_M = [0.5, 0.5].
    H_cross = -1*log(0.5) = log(2). H_X_plug = 0 (singleton).
    KL_naive = log(2) - 0 = log(2) ≈ 0.6931.
    """
    counts_X = np.array([10, 0], dtype=np.int64)
    counts_M = np.array([5, 5], dtype=np.int64)
    res = kl_corrected_and_naive(counts_X, counts_M)
    assert res.laplace_bins == 0  # M[0]>0
    assert abs(res.kl_naive - np.log(2)) < 1e-10


def test_kl_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="shape mismatch"):
        kl_corrected_and_naive(
            np.array([1, 2, 3]), np.array([1, 2])
        )


# ----------------------------------------------------------------------
# fit_markov_transition + sample_markov
# ----------------------------------------------------------------------

def test_fit_markov_smoothing_uniform_when_no_data() -> None:
    """With α=1.0 and minimal data, smoothing dominates."""
    actions = np.array([0, 1])  # only one transition observed: 0→1
    P = fit_markov_transition(actions, n_states=3, alpha=1.0)
    # row 0: counts=[0,1,0]+1=[1,2,1], normalised = [0.25, 0.5, 0.25]
    np.testing.assert_allclose(P[0], [0.25, 0.5, 0.25])
    # rows 1, 2: no transitions out → uniform [1/3, 1/3, 1/3]
    np.testing.assert_allclose(P[1], [1 / 3] * 3)
    np.testing.assert_allclose(P[2], [1 / 3] * 3)


def test_fit_markov_rows_sum_to_one() -> None:
    rng = np.random.default_rng(7)
    actions = rng.integers(0, 8, size=1000)
    P = fit_markov_transition(actions, n_states=8, alpha=1.0)
    np.testing.assert_allclose(P.sum(axis=1), 1.0, atol=1e-12)


def test_sample_markov_deterministic_under_seed() -> None:
    rng = np.random.default_rng(0)
    actions = rng.integers(0, 4, size=200)
    P = fit_markov_transition(actions, n_states=4, alpha=1.0)
    s1 = sample_markov(P, length=500, seed=42, init_state=0)
    s2 = sample_markov(P, length=500, seed=42, init_state=0)
    np.testing.assert_array_equal(s1, s2)


def test_sample_markov_initial_state_respected() -> None:
    P = np.eye(3)  # absorbing chains
    out = sample_markov(P, length=10, seed=0, init_state=2)
    assert out[0] == 2
    assert (out == 2).all()  # absorbing


def test_sample_markov_rejects_non_stochastic_P() -> None:
    P_bad = np.array([[0.5, 0.4], [0.5, 0.5]])  # row 0 sums to 0.9
    with pytest.raises(ValueError, match="rows of P must sum to 1"):
        sample_markov(P_bad, length=10, seed=0, init_state=0)


# ----------------------------------------------------------------------
# wilcoxon_paired_one_sided + cohen_d_paired
# ----------------------------------------------------------------------

def test_wilcoxon_strongly_positive_yields_small_p_greater() -> None:
    deltas = np.linspace(0.1, 1.0, 20)
    res = wilcoxon_paired_one_sided(deltas, alternative="greater")
    assert res.n_post_drop == 20
    assert res.n_dropped == 0
    assert res.p_value < 0.001
    res_less = wilcoxon_paired_one_sided(deltas, alternative="less")
    assert res_less.p_value > 0.99


def test_wilcoxon_drops_exact_zeros() -> None:
    deltas = np.array([0.0, 0.0, 0.0, 1.0, 2.0, 3.0])
    res = wilcoxon_paired_one_sided(deltas, alternative="greater")
    assert res.n_dropped == 3
    assert res.n_post_drop == 3


def test_wilcoxon_all_zeros_returns_pvalue_one() -> None:
    deltas = np.zeros(10)
    res = wilcoxon_paired_one_sided(deltas, alternative="greater")
    assert res.n_post_drop == 0
    assert res.p_value == 1.0


def test_cohen_d_known_value() -> None:
    # mean = 1, std (ddof=1) = sqrt(2/2) = 1 → d = 1.
    deltas = np.array([0.0, 1.0, 2.0])
    d = cohen_d_paired(deltas)
    # std(ddof=1) = sqrt(((0-1)^2 + 0 + (2-1)^2)/2) = 1
    assert abs(d - 1.0) < 1e-12


def test_cohen_d_constant_returns_nan() -> None:
    d = cohen_d_paired(np.array([5.0, 5.0, 5.0]))
    assert np.isnan(d)


# ----------------------------------------------------------------------
# Integration : end-to-end on small synthetic case
# ----------------------------------------------------------------------

def test_end_to_end_concentrated_X_uniform_M_yields_positive_KL() -> None:
    """Sanity: a concentrated X against a uniform M should give KL > 0."""
    counts_X = np.zeros(B_DEFAULT, dtype=np.int64)
    counts_X[0] = 1000
    counts_M = np.full(B_DEFAULT, 100, dtype=np.int64)
    res = kl_corrected_and_naive(counts_X, counts_M)
    assert res.kl_naive > 0
    assert res.kl_corrected > 0
    assert res.laplace_bins == 0  # M is uniform, no zeros


def test_constants_match_ADR_026() -> None:
    """Spec freeze : these constants must match ADR-026 §3.2."""
    assert B_DEFAULT == 64
    assert P_MIN_DEFAULT == 0.0
    assert P_MAX_DEFAULT == 1.0
