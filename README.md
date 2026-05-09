# CAE Research Kit

A frozen, deterministic, falsification-driven measurement instrument.
Two published hypotheses: **H₅** (rejected, v0.1.0) and **H₆** (rejected by
control, v0.2.0).

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20091626.svg)](https://doi.org/10.5281/zenodo.20091626)
[![Status: H5_REJECTED](https://img.shields.io/badge/H5-REJECTED-critical)](research/h5_verdict.json)
[![Status: H6_FEEDBACK_ONLY](https://img.shields.io/badge/H6-FEEDBACK__ONLY-critical)](research/h6_gamma_verdict.json)
[![ADT: 50/50](https://img.shields.io/badge/ADT--H5-50%2F50%20PASS-brightgreen)](tests/adt)
[![Python: 3.11.9](https://img.shields.io/badge/python-3.11.9-blue)](Dockerfile)

> **The discipline is the product.**
>
> Two consecutive published falsifications. The instrument earns trust by
> refusing to confirm itself.

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

## Verdicts

### v0.1.0 — H₅ (frozen)

**`H5_REJECTED`** — Adaptive agent A is **not** distinguishable from scripted
agent B under the Wasserstein-1 redistribution metric (`n=30`, `α=0.01`,
`threshold=3σ`).

| pair | Cohen's d | Wilcoxon p | conclusion |
|---|---:|---:|---|
| A vs R | 0.595 | 5.55e-04 | significant but underpowered |
| A vs B | 0.145 | 2.37e-01 | **indistinguishable** |
| A vs P | 6.293 | 1.86e-09 | distinguishable (P degraded) |

Artefacts: [research/h5_verdict.json](research/h5_verdict.json) ·
[research/h5_run_results.csv](research/h5_run_results.csv)

### v0.2.0 — H₆ (frozen)

**`H6_GAMMA_FEEDBACK_ONLY`** — A naïve test (β phase) initially produced
an apparent topological signature (Cohen d = 2.51, p = 1.86 × 10⁻⁹). A
pre-registered control (γ phase, ADR-024) introducing an **observation-shuffled
agent** invalidated the structural interpretation: the real agent's trajectory
is statistically *closer* to the obs-shuffled agent's trajectory than to the
Markov-null. The β signal is reclassified as a **feedback artefact**, not a
structural signature.

| Test | Cohen's d | Wilcoxon p | Verdict |
|---|---:|---:|---|
| H6-β (paired vs Markov-null) | +2.5068 | 1.86e-09 | apparent signal |
| H6-γ.1 (real vs shuffled vs Markov) | −0.5027 | 0.998 | **fail to reject H₀** |
| H6-γ.2 (shuffled-vs-Markov > 0) | — | 9.31e-10 | confound confirmed |

Artefacts:
[research/h6_beta_verdict.json](research/h6_beta_verdict.json) ·
[research/h6_beta_run_results.csv](research/h6_beta_run_results.csv) ·
[research/h6_gamma_verdict.json](research/h6_gamma_verdict.json) ·
[research/h6_gamma_run_results.csv](research/h6_gamma_run_results.csv)

Decision record: [docs/adr/ADR-025-h6-release-decision.md](docs/adr/ADR-025-h6-release-decision.md)

**Plain reading.** *Any* policy that conditions on `env.observe()` — even on
permuted, information-free observations — produces a trajectory observably
distinct from a feedback-naïve Markov-null. This is mechanically guaranteed,
not evidence of structure. Trajectory-coupling probes on E₀ in their current
form cannot discriminate "feedback effect" from "structural coupling". Future
work (H₇ / H_δ) requires a probe orthogonal to feedback.

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
- [docs/adr/ADR-021-h5-falsification.md](docs/adr/ADR-021-h5-falsification.md) — H₅ falsification record
- [docs/adr/ADR-022-h6-pre-registration.md](docs/adr/ADR-022-h6-pre-registration.md) — H₆ pre-registration
- [docs/adr/ADR-023-h6-beta-phase-space.md](docs/adr/ADR-023-h6-beta-phase-space.md) — H6-β metric
- [docs/adr/ADR-023.bis-pressure-vector-trajectory.md](docs/adr/ADR-023.bis-pressure-vector-trajectory.md) — H6-β pipeline correction
- [docs/adr/ADR-023.ter-paired-wilcoxon.md](docs/adr/ADR-023.ter-paired-wilcoxon.md) — H6-β test specification
- [docs/adr/ADR-024-h6-gamma-obs-shuffled-control.md](docs/adr/ADR-024-h6-gamma-obs-shuffled-control.md) — H6-γ control pre-registration
- [docs/adr/ADR-025-h6-release-decision.md](docs/adr/ADR-025-h6-release-decision.md) — H₆ release decision
- [RELEASE.md](RELEASE.md) — release notes (v0.1.0 + v0.2.0)
- [research/MANIFEST.v0.1.0.yaml](research/MANIFEST.v0.1.0.yaml) — H₅ manifest
- [research/MANIFEST.v0.2.0.yaml](research/MANIFEST.v0.2.0.yaml) — H₆ manifest

## Citation

```bibtex
@software{cae_research_kit_v0_2_0,
  title   = {CAE Research Kit: H6 Falsified — Topological Signatures Reclassified as Feedback Artefacts},
  author  = {{The CAE Research Kit Authors}},
  year    = {2026},
  version = {v0.2.0-h6-rejected},
  doi     = {10.5281/zenodo.20091626},
  url     = {https://doi.org/10.5281/zenodo.20091626},
  note    = {Verdict: H6\_GAMMA\_FEEDBACK\_ONLY. Sibling release of v0.1.0-h5-rejected.}
}

@software{cae_research_kit_v0_1_0,
  title   = {CAE Research Kit: H5 Falsification},
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
