# CAE Research Kit

A frozen, deterministic, falsification-driven measurement instrument for the
**H₅ hypothesis** on adaptive optimization regimes.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20091626.svg)](https://doi.org/10.5281/zenodo.20091626)
[![Status: H5_REJECTED](https://img.shields.io/badge/verdict-H5__REJECTED-critical)](research/h5_verdict.json)
[![ADT: 50/50](https://img.shields.io/badge/ADT-50%2F50%20PASS-brightgreen)](tests/adt)
[![Python: 3.11.9](https://img.shields.io/badge/python-3.11.9-blue)](Dockerfile)

> **The discipline is the product.**

---

## What this is

A self-contained scientific kit that tries to **falsify** one precise claim:

> H₅ — *An online adaptive agent produces, in a controlled environment E₀, a
> measurable redistribution of constraint pressure (Wasserstein-1 signature)
> that cannot be reproduced by static, random, or offline pre-trained agents.*

The kit ships:

- A deterministic environment **E₀** (constraint field).
- Four instrumented agents: **A** (adaptive), **B** (scripted), **R** (random),
  **P** (offline pre-trained).
- A pressure metric based on **Wasserstein-1** (`scipy` + `POT`).
- A frozen Docker image with strict `==` pinning and a reference fingerprint.
- 50 Adversarial Destruction Tests (ADT) designed to break the result.

## What this is NOT

- Not a claim about "intelligence", "consciousness", "intent", or "cognition".
- Not a benchmark, not a leaderboard, not a model release.
- Not generalisable beyond E₀ without a new ADR.

## Verdict (frozen, v0.1.0)

**`H5_REJECTED`** — Adaptive agent A is **not** distinguishable from scripted
agent B under the Wasserstein-1 redistribution metric (`n=30`, `α=0.01`,
`threshold=3σ`).

| pair | Cohen's d | Wilcoxon p | conclusion |
|---|---:|---:|---|
| A vs R | 0.595 | 5.55e-04 | significant but underpowered |
| A vs B | 0.145 | 2.37e-01 | **indistinguishable** |
| A vs P | 6.293 | 1.86e-09 | distinguishable (P degraded) |

Canonical artefacts: [research/h5_verdict.json](research/h5_verdict.json) ·
[research/h5_run_results.csv](research/h5_run_results.csv)

## Reproducibility

Reference fingerprint (SHA-256 of `np.random.default_rng(42).standard_normal(1024)`
under the frozen image):

```
406ce26ec3aeefada7e2250f16d24a89361c1da2041c6775599be394008e7e5f
```

Any reproduction that does not return exactly this fingerprint is invalid.

```bash
docker build -t cae-research-kit:0.1.0 .
make adt    # 50/50 ADT must pass
make h5     # regenerate research/h5_verdict.json bit-identical
```

## Repository layout

```
src/env/        E₀ — controlled constraint field
src/agents/     A (adaptive), B (scripted), R (random), P (pre-trained)
src/metrics/    Wasserstein-1 pressure, entropy, HHI
src/experiments/  H₅ harness + adjudication
tests/adt/      Adversarial Destruction Tests (must all pass)
research/       Frozen run outputs (CSV, JSON, manifest)
docs/           Public protocol and ADRs
```

## Documents

- [docs/PROTOCOL-v1.0.md](docs/PROTOCOL-v1.0.md) — public scientific protocol
- [docs/adr/ADR-021-h5-falsification.md](docs/adr/ADR-021-h5-falsification.md) — falsification record
- [RELEASE.md](RELEASE.md) — v0.1.0 release notes (image identity, deps, verdict)
- [research/MANIFEST.v0.1.0.yaml](research/MANIFEST.v0.1.0.yaml) — measurement manifest

## Citation

```bibtex
@software{cae_research_kit_v0_1_0,
  title   = {CAE Research Kit: H₅ Falsification},
  author  = {{The CAE Research Kit Authors}},
  year    = {2026},
  version = {v0.1.0-h5-rejected},
  doi     = {10.5281/zenodo.20091626},
  url     = {https://doi.org/10.5281/zenodo.20091626},
  note    = {Verdict: H5\_REJECTED. Reference fingerprint:
             406ce26ec3aeefada7e2250f16d24a89361c1da2041c6775599be394008e7e5f}
}
```

## License

[Apache License 2.0](LICENSE) — Copyright 2026 The CAE Research Kit Authors.
