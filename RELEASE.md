# Release v0.1.0-h5-rejected

**Date:** 2026-05-09
**Scientific status:** H₅ falsified (null regime confirmed)
**Operational status:** kit frozen, reproducible, delivered.

---

## 1. Compute image identity (cold forge)

| Field | Value |
|---|---|
| Name | `cae-research-kit:0.1.0` |
| Image ID | `sha256:f30bf02ce6e486153980c79e43e65bf5c195b4fd6ebf052f04ff10537e3ea78e` |
| Base | `python:3.11.9-slim-bookworm` |
| Deterministic fingerprint | `406ce26ec3aeefada7e2250f16d24a89361c1da2041c6775599be394008e7e5f` |

Fingerprint = SHA256 of `np.random.default_rng(42).standard_normal(1024)` under
`PYTHONHASHSEED=42`, NumPy 1.26.4, Python 3.11.9, BLAS threads = 1.
Any reproduction that does not return exactly this fingerprint is invalid.

## 2. Dependency manifest (strict `==` pinning)

```
numpy==1.26.4   scipy==1.12.0   POT==0.9.3
pandas==2.2.1   matplotlib==3.8.3   pytest==8.1.1
```

## 3. Experimental verdict — H₅

**H₅ (protocol statement):** an online adaptive agent produces, in environment
E₀, a measurable redistribution of constraint pressure, a signature that
cannot be reproduced by static, random, or offline pre-trained agents, at a
threshold ≥ 3σ with p < 0.01 over n ≥ 30 seeds.

**Result (n = 30, seeds 1000–1029):**

| pair | mean Δ | Cohen's d | Wilcoxon p | conclusion |
|---|---:|---:|---:|---|
| A vs R | +6.03e-04 | 0.595 | 5.55e-04 | significant but underpowered |
| A vs B | +1.56e-04 | 0.145 | 2.37e-01 | **indistinguishable** |
| A vs P | +6.23e-03 | 6.293 | 1.86e-09 | distinguishable (P degraded) |

**Verdict: `H5_REJECTED`.** Adaptive agent A is not distinguishable from
scripted agent B under the Wasserstein-1 redistribution metric. The
falsification criterion for H₅ is satisfied.

Canonical artifacts:
- [research/h5_verdict.json](research/h5_verdict.json)
- [research/h5_run_results.csv](research/h5_run_results.csv)

## 4. ADT coverage (Adversarial Destruction Tests)

50 / 50 PASS under the frozen image.

| Suite | Tests | Target |
|---|---:|---|
| `test_bootstrap.py` | 7 | bit-exact reproducibility, strict pinning |
| `test_e0.py` | 7 | E₀ determinism, black-box isolation |
| `test_agents.py` | 9 | ABC interface, isolation, distinctness |
| `test_metrics.py` | 16 | W₁ axioms, scipy↔POT, entropy, HHI |
| `test_h5.py` | 5 | H₅ harness, persistence, underpower |
| `test_pretrained.py` | 6 | offline training, immutability, no leakage |

## 5. Reproduction

```bash
docker build -t cae-research-kit:0.1.0 .
make adt           # 50 tests
make h5            # produces research/h5_verdict.json
```

## 6. What is NOT claimed

- No claim about agent "intelligence", "consciousness", "intent", or
  "cognition". The kit measures pressure flows under Wasserstein-1, nothing
  else (ADR-020).
- No generalisation beyond E₀. H₅ was tested on **one** environment topology,
  **one** hyperparameter set, **one** instrumented agent quadruplet. Any
  extension requires a new ADR.
- Rejecting H₅ is not rejecting CAE. It is rejecting **this formulation**
  of H₅ under **this** experimental regime.

## 7. Operational protocol

Reference: [`docs/PROTOCOL-v1.0.md`](docs/PROTOCOL-v1.0.md).
Future iterations must respect its ADRs (notably ADR-020 on lexicon, and
the falsification-over-validation principle).

> *"Discipline is the product."*
