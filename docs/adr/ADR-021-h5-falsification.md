# ADR-021 — Experimental falsification of H₅ (E₀ regime, v0.1.0)

**Status:** ACCEPTED
**Date:** 2026-05-09
**Image:** `cae-research-kit:0.1.0` (`sha256:f30bf02ce6e4…`)
**Deterministic fingerprint:** `406ce26ec3aeefada7e2250f16d24a89361c1da2041c6775599be394008e7e5f`

## Context

H₅ ([docs/PROTOCOL-v1.0.md](../PROTOCOL-v1.0.md)) postulates that an online
adaptive agent A produces, in E₀, a constraint pressure redistribution
qualitatively distinct from the static (B), random (R), and offline
pre-trained (P) controls, at a 3σ threshold with p < 0.01 over n ≥ 30
paired seeds.

## Protocol

- Deterministic environment E₀, n_seeds = 30 (1000–1029), horizon = 512.
- Black-box-instrumented agents (observation is exclusively a `np.ndarray`).
- P trained offline on seed 99 (disjoint), 16-bin tabular policy, immutable
  (`setflags(write=False)`).
- Metric: Wasserstein-1 over the pressure trajectory, scipy ↔ POT cross-check
  (tolerance 1e-6).
- Tests: paired Wilcoxon + Cohen's d. α = 0.01.

## Raw result

| pair | Cohen's d | Wilcoxon p |
|---|---:|---:|
| A vs R | 0.595 | 5.55e-04 |
| A vs B | 0.145 | 2.37e-01 |
| A vs P | 6.293 | 1.86e-09 |

## Decision

**H₅ is falsified.** A is not distinguishable from B at the required
threshold. The A-vs-P separation is not admissible as support for H₅: it
reflects the structural degradation of P (16-bin quantization, frozen
policy), not a superiority of online adaptation.

## Consequences

1. The v0.1.0 kit is frozen as-is. No edits to A, B, R, P, or the metrics
   are allowed under this ADR to "rescue" H₅.
2. Any reformulation requires a new ADR (H₅', H₅'', …) preceding any code
   modification.
3. Extending the E₀ parameter space (grid_size, drift_rate, n_modes…) is
   admissible but constitutes a different test and requires ADR-022.

## Discipline commitments

- No p-hacking on the 3σ threshold.
- No reinterpretation of the observed redistribution as "emergent
  intelligence" or any other forbidden lexicon (ADR-020).
- The verdict is archived in
  [research/h5_verdict.json](../../research/h5_verdict.json) and remains
  the binding reference.
