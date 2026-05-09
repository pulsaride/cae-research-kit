# CAE Scientific Protocol — v1.0

This document defines the normative framework under which hypothesis H₅ is
tested. It is referenced by [RELEASE.md](../RELEASE.md) and
[docs/adr/ADR-021-h5-falsification.md](adr/ADR-021-h5-falsification.md).

## 1. Hypothesis H₅

> An online adaptive optimization regime produces, in a controlled environment
> E₀, a measurable redistribution of constraint pressure — a signature that
> cannot be reproduced by static, random, or offline pre-trained agents.

## 2. Normative lexicon (ADR-020)

To prevent interpretive contamination, the following terms are **forbidden**
in code, comments, reports, and commit messages:

> *intelligence, consciousness, intent, cognition, thought, brain,
> revolutionary.*

The **required** (technical, falsifiable) terms:

> *optimization regime, constraint flow, uncertainty pressure,
> Wasserstein distance, geometric invariant, falsification.*

## 3. Instrumentation standards

- **Total determinism.** Fixed seed `CAE_SEED=42`, `PYTHONHASHSEED=42`,
  BLAS threads = 1. The reference fingerprint is verified at every run.
- **Black-box isolation.** No agent has access to the internal state of E₀.
  Observation is exclusively a `np.ndarray` of the visible pressure field.
- **Measurements.** Inter-distribution distances are computed via
  `scipy.stats.wasserstein_distance` and `ot.emd2` (POT), with cross-check
  (tolerance 1e-6).

## 4. Build-to-Destroy loop

Every scientific iteration must follow this order:

1. **Analysis** — which aspect of H₅ is being tested?
2. **Destruction plan (ADT)** — how could this result be a false positive?
3. **Implementation** — modular, instrumented, deterministic code.
4. **Null-regime test** — systematic comparison A vs R, A vs B, A vs P.
   Without flagrant separation (≥ 3σ and p < α), the experiment fails.

## 5. Falsification criteria for H₅

H₅ is declared **DETECTED** if and only if, over n ≥ 30 paired seeds:

- `|cohen_d(A, R)| ≥ 3.0`
- `wilcoxon_p(A, R) < 0.01`
- `wilcoxon_p(A, B) < 0.01`
- `wilcoxon_p(A, P) < 0.01`
- `|Δ(A,R)| > 0.5 · |Δ(A,B)|` and `|Δ(A,R)| > 0.5 · |Δ(A,P)|`

Any other outcome leads to `H5_REJECTED` or `H5_INCONCLUSIVE` depending on
statistical power. No threshold may be adjusted *a posteriori* to rescue
H₅ without a new ADR (no p-hacking).

## 6. Project structure

| Directory | Role |
|---|---|
| `src/env/` | Environment E₀ (constraint field) |
| `src/agents/` | A (online adaptive), B (scripted), R (random), P (pre-trained) |
| `src/metrics/` | Pressure, Wasserstein-1, entropy, HHI |
| `tests/adt/` | Adversarial destruction tests |
| `research/` | Verdicts and raw data (CSV/JSON, no prose) |
| `docs/adr/` | Archived architectural decisions |

## 7. Motto

> *"Discipline is the product."*
