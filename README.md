# CAE Research Kit

> ## 🧊 Observation phase (May 2026 → August 2026)
>
> The protocol is **stable and frozen** at [`v0.7.0-cert-protocol`](https://github.com/pulsaride/cae-research-kit/releases/tag/v0.7.0-cert-protocol) (DOI [10.5281/zenodo.20112693](https://doi.org/10.5281/zenodo.20112693)). Active development is **paused** to let the community study, replicate, or contest the protocol on its own terms. During this window:
>
> - issues and pull requests will be answered, but no new ADR, schema change, or release is planned;
> - the [`docs/case-studies/`](docs/case-studies/) directory waits for the first **external** issuer (any project other than `cae-research-kit` itself);
> - active engineering effort has shifted to the operational downstream consumer that exercises the science of CAE under production constraints. That consumer is developed in a separate repository on its own cadence and is **not** governed by this repository's protocol.
>
> The protocol resumes active development when at least one of the following is true: (a) a first independent case study lands in `docs/case-studies/`; (b) a third party publishes a critique or a replication; (c) the downstream consumer reaches production deployment and surfaces a concrete protocol gap.

A frozen, deterministic, falsification-driven measurement instrument.
Five published hypotheses: **H₅** (rejected, v0.1.0), **H₆** (rejected by
control, v0.2.0), **H₇-σ** (inverted directional signal, v0.3.0),
**H₇-κ** (σ-inversion reversed by single-tick memory on E₀, v0.4.0),
and **H₇-κ portability** (the κ signature transfers to a calibrated
diffusive E₁ under a publicly audited runner, v0.5.0).

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![DOI concept](https://zenodo.org/badge/DOI/10.5281/zenodo.20091626.svg)](https://doi.org/10.5281/zenodo.20091626)
[![DOI v0.2.0](https://zenodo.org/badge/DOI/10.5281/zenodo.20094993.svg)](https://doi.org/10.5281/zenodo.20094993)
[![DOI v0.3.0](https://zenodo.org/badge/DOI/10.5281/zenodo.20096664.svg)](https://doi.org/10.5281/zenodo.20096664)
[![DOI v0.4.0](https://zenodo.org/badge/DOI/10.5281/zenodo.20097880.svg)](https://doi.org/10.5281/zenodo.20097880)
[![DOI v0.5.0](https://zenodo.org/badge/DOI/10.5281/zenodo.20107855.svg)](https://doi.org/10.5281/zenodo.20107855)
[![Status: H5_REJECTED](https://img.shields.io/badge/H5-REJECTED-critical)](research/h5_verdict.json)
[![Status: H6_FEEDBACK_ONLY](https://img.shields.io/badge/H6-FEEDBACK__ONLY-critical)](research/h6_gamma_verdict.json)
[![Status: H7_SIGMA_INVERTED](https://img.shields.io/badge/H7--%CF%83-INVERTED-orange)](research/h7_sigma_verdict.json)
[![Status: KAPPA_REVERSES](https://img.shields.io/badge/H7--%CE%BA-REVERSES-blue)](research/h7_kappa_verdict.json)
[![Status: KAPPA_TRANSFERS](https://img.shields.io/badge/H7--%CE%BA--portability-TRANSFERS-brightgreen)](research/h7_kappa_portability_verdict.json)
[![ADT: 50/50](https://img.shields.io/badge/ADT--H5-50%2F50%20PASS-brightgreen)](tests/adt)
[![Python: 3.11.9](https://img.shields.io/badge/python-3.11.9-blue)](Dockerfile)

> **The discipline is the product.**
>
> Five consecutive published, pre-registered, frozen experiments. The
> instrument earns trust by refusing to confirm itself, by publishing
> inverted directional signals as cleanly as confirmations, *and* by
> decomposing those inversions into their minimal structural component
> under the same protocol.

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

### v0.3.0 — H₇-σ (frozen)

**`H7_SIGMA_INVERTED`** — H7-σ pre-registered (ADR-026 v2) the prediction
that the real adaptive agent's stationary action-pressure distribution would
diverge *more* from a Markov-null baseline than an obs-shuffled control's
would (`δ_σ = D_KL(P_R‖P_M) − D_KL(P_S‖P_M) > 0`). The frozen main run on
the disjoint pre-reserved pool [1400-1429] produced the **opposite**
directional signal at strong effect size: 26 / 30 seeds with `δ_σ < 0`,
median `δ_σ = −0.148`, **Cohen d = −0.7581**, **p_less = 1.04 × 10⁻⁵**
(paired Wilcoxon, mirrored alternative formalised in ADR-026 v2.1).

| Branch | Cohen's d | Wilcoxon p (less) | Verdict |
|---|---:|---:|---|
| Primary (`δ_σ_corr`, Miller-Madow corrected) | −0.7581 | 1.04e-05 | `H7_SIGMA_INVERTED` |
| Transparency (`δ_σ_naive`, plug-in entropy) | −0.7581 | 1.04e-05 | `H7_SIGMA_INVERTED` |

`verdicts_agree = true`, `total_clip_events = 0`, `n_post_drop = 30`.

Diagnostic structural signature (replicated pilot → main, out-of-sample, no
re-fit): median non-empty bins K_R = 42, K_S = 61.5, K_M = 57 (out of B = 64);
median K_R − K_S = **−19** (vs pilot −15, sign preserved).

Artefacts:
[research/h7_sigma_verdict.json](research/h7_sigma_verdict.json) ·
[research/h7_sigma_run_results.csv](research/h7_sigma_run_results.csv)

Decision record: [docs/adr/ADR-029-h7-sigma-release.md](docs/adr/ADR-029-h7-sigma-release.md)

**Plain reading.** Under the real feedback loop, the agent concentrates
pressure on a *strict subset* of state cells; this concentrated profile is
statistically *closer* to the environment's Markov-stationary baseline than
the dispersed profile produced when observation order is destroyed. The
pre-registered direction was wrong; the existence of a non-trivial,
reproducible coupling signature is established. Permitted operational
vocabulary (ADR-026 v2.1 §7): *inverted coupling*, *stabilising feedback*
in the strict sense `d ≤ −0.5 ∧ p_less < 0.005`. All cognitive vocabulary
remains banned.

### v0.4.0 — H₇-κ (frozen)

**`KAPPA_REVERSES`** — H₇-κ pre-registered (ADR-030) the question of whether
a **single tick of memory** on the previous local-pressure observation
suffices to break the H7-σ inverted-coupling signature. Same pre-registered
statistical chain (paired Wilcoxon, mirrored alternatives, α = 0.005,
Miller-Madow + plug-in double reporting) applied to the per-seed test
quantity $\Delta_s = \delta_\sigma^{M_\kappa}(s) - \delta_\sigma^{R}(s)$ on
the disjoint pre-reserved pool [1500-1529]. The agent under test (`M_κ`,
[src/agents/memory1_agent.py](src/agents/memory1_agent.py)) carries one
buffer $m_t \in [0,1]^G$, $m_0 = \mathbf{0}$, updated by $m_{t+1} \leftarrow O_t$
(no parameter), policy $A_t = \arg\max_i (m_t[i] - O_t[i])$ — zero learning,
zero gradient.

| Branch | Cohen's d | Wilcoxon p (greater) | Verdict |
|---|---:|---:|---|
| Primary (`Δ_κ_corr`, Miller-Madow corrected) | **+2.6619** | **9.31e-10** | `KAPPA_REVERSES` |
| Transparency (`Δ_κ_naive`, plug-in entropy) | +2.6620 | 9.31e-10 | `KAPPA_REVERSES` |

`verdicts_agree = true`, `total_clip_events = 0`, `n_post_drop = 30`,
**30 / 30 seeds with $\Delta_s > 0$** (no counter-example).

Diagnostic action-repertoire shift: median K_R = 39.5 (R, no memory; consistent
with the σ "concentration on a strict subset") → median K_Mκ = 62.0 (one-tick
memory; matches K_S = 62.0 of the obs-shuffled control). The +23 cell recovery
is the agent leaving passive stabilisation and entering active local-gradient
navigation; median $\delta_\sigma^{M_\kappa}$ crosses zero (+0.256) while
median $\delta_\sigma^{R}$ remains inverted (−0.167) on the same disjoint pool.

Artefacts:
[research/h7_kappa_verdict.json](research/h7_kappa_verdict.json) ·
[research/h7_kappa_run_results.csv](research/h7_kappa_run_results.csv)

Decision records:
[docs/adr/ADR-028-h7-kappa-or-h8-pivot.md](docs/adr/ADR-028-h7-kappa-or-h8-pivot.md) ·
[docs/adr/ADR-030-h7-kappa-pre-registration.md](docs/adr/ADR-030-h7-kappa-pre-registration.md)

**Plain reading.** A single tick of memory ($t-1$ on local pressure, zero
parameters, zero learning) is sufficient to **reverse** the σ inversion. The
H7-σ inverted-coupling regime is therefore not an architectural dead end —
it is the *memoryless* regime. The minimal structural-coupling component
identified in E₀ is **local temporal differentiation**. The paradox is
kinetic, not geometric. ADR-028's Option A (decompose with H7-κ before
attempting the deeper H8 pivot) is vindicated.

### v0.5.0 — H₇-κ portability on E₁ (frozen, audited)

**`KAPPA_TRANSFERS`** — H₇-κ portability pre-registered (ADR-032) the
question of whether the v0.4.0 κ signature survives an out-of-distribution
change to a calibrated diffusive environment E₁ on a fresh seed pool
[2000-2029] never observed before the tirage. Same statistical chain as
ADR-027 (paired Wilcoxon, mirrored alternatives, α = 0.005, Miller-Madow +
plug-in double reporting). M_κ inherited bit-identical from ADR-030.

Admissibility was gated by an **audit-against-the-private-runner**
(ADR-033): the public reimplementation
([src/experiments/portability_draw.py](src/experiments/portability_draw.py))
had to reproduce the v0.4.0 per-seed CSV on the reference pool [1500-1529]
under fixed tolerances (atol = 1e-9, rtol = 0, `==` strict on integer
columns) **before** the portability tirage was authorised. Iter1 failed
strictly on the obs-shuffled witness branch; the bounded investigation of
ADR-033 §6.2 #5 (BLAKE2b convention, exhaustive S-only brute force on
witness seed 1500) yielded a single-bit fix in
[src/agents/obs_shuffled_agent.py](src/agents/obs_shuffled_agent.py)
(`byteorder = "big"`). Iter2 PASS: max $|\Delta| \leq 4.5 \times 10^{-11}$
on all 14 float columns; 0 mismatches on all 15 integer columns. Tag
`audit-passed-v1` placed before the portability tirage.

| Branch | Cohen's d | Wilcoxon p (greater) | Verdict |
|---|---:|---:|---|
| Primary (`Δ_κ_corr`, Miller-Madow corrected) | **+3.0906** | **9.31e-10** | `KAPPA_TRANSFERS` |
| Transparency (`Δ_κ_naive`, plug-in entropy) | +3.0907 | 9.31e-10 | `KAPPA_TRANSFERS` |

`verdicts_agree = true`, `total_clip_events = 0`, `n_post_drop = 30`,
**30 / 30 seeds with $\Delta_s > 0$** (no counter-example). Diagnostic
action-repertoire shift on E₁: median K_R = 35 → K_Mκ = 57, a +22-cell
recovery of the same order as the +23 reported on E₀ in v0.4.0.

Artefacts:
[research/h7_kappa_portability_verdict.json](research/h7_kappa_portability_verdict.json) ·
[research/h7_kappa_portability.csv](research/h7_kappa_portability.csv) ·
[research/h7_kappa_audit_v04_iter2.report.txt](research/h7_kappa_audit_v04_iter2.report.txt)

Decision records:
[docs/adr/ADR-031-post-kappa-trilemma-b-first.md](docs/adr/ADR-031-post-kappa-trilemma-b-first.md) ·
[docs/adr/ADR-031.bis-supersede-section-5-3.md](docs/adr/ADR-031.bis-supersede-section-5-3.md) ·
[docs/adr/ADR-032-h7-kappa-portability-e1.md](docs/adr/ADR-032-h7-kappa-portability-e1.md) ·
[docs/adr/ADR-033-audit-gate-public-runner.md](docs/adr/ADR-033-audit-gate-public-runner.md)

**Plain reading.** The κ mechanism — local temporal differentiation — is
not an artefact of E₀'s specific pressure dynamics: it transfers across a
calibrated change of medium with no loss of effect size. The κ pipeline is
now end-to-end publicly executable; the runner that produced the
portability CSV is the same runner that reproduces the v0.4.0 reference
CSV bit-against-bit. v0.5.0 closes the *cross-environment portability*
question raised in v0.4.0 §6. Portability beyond the calibrated E₁ used
here is **not** claimed.

## Reproducibility

The v0.1.0 reference fingerprint is the immutable substrate for all
subsequent releases (E₀, agents base, KL chain). Any reproduction that
does not return exactly this fingerprint is invalid.

```
406ce26ec3aeefada7e2250f16d24a89361c1da2041c6775599be394008e7e5f
```

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
- [docs/adr/ADR-026-h7-sigma.md](docs/adr/ADR-026-h7-sigma.md) — H₇-σ pre-registration (v2 frozen)
- [docs/adr/ADR-026-v2.1-h7-sigma-amendment-inverted.md](docs/adr/ADR-026-v2.1-h7-sigma-amendment-inverted.md) — H₇-σ amendment formalising INVERTED bin
- [docs/adr/ADR-027-h7-sigma-statistical-chain.md](docs/adr/ADR-027-h7-sigma-statistical-chain.md) — H₇-σ statistical chain (paired Wilcoxon)
- [docs/adr/ADR-028-h7-kappa-or-h8-pivot.md](docs/adr/ADR-028-h7-kappa-or-h8-pivot.md) — H₇-κ vs H8 decision (Option A)
- [docs/adr/ADR-029-h7-sigma-release.md](docs/adr/ADR-029-h7-sigma-release.md) — H₇-σ release decision
- [docs/adr/ADR-030-h7-kappa-pre-registration.md](docs/adr/ADR-030-h7-kappa-pre-registration.md) — H₇-κ pre-registration
- [RELEASE.md](RELEASE.md) — release notes (v0.1.0 + v0.2.0 + v0.3.0 + v0.4.0)
- [research/MANIFEST.v0.1.0.yaml](research/MANIFEST.v0.1.0.yaml) — H₅ manifest
- [research/MANIFEST.v0.2.0.yaml](research/MANIFEST.v0.2.0.yaml) — H₆ manifest
- [research/MANIFEST.v0.3.0.yaml](research/MANIFEST.v0.3.0.yaml) — H₇-σ manifest
- [research/MANIFEST.v0.4.0.yaml](research/MANIFEST.v0.4.0.yaml) — H₇-κ manifest

## Citation

```bibtex
@software{cae_research_kit_v0_4_0,
  title   = {CAE Research Kit: H7-κ Reverses — A Single Tick of Memory Breaks the σ Inversion},
  author  = {{The CAE Research Kit Authors}},
  year    = {2026},
  version = {v0.4.0-h7-κ-reverses},
  doi     = {10.5281/zenodo.20097880},
  url     = {https://doi.org/10.5281/zenodo.20097880},
  note    = {Verdict: KAPPA\_REVERSES (Cohen d = +2.6619, p\_greater = 9.31e-10, n=30,
             pool [1500-1529], 30/30 seeds with Δ > 0, 0 clip events).
             Tested quantity: Δ\_s = δ\_σ\textasciicircum{}M\_κ(s) - δ\_σ\textasciicircum{}R(s).
             Agent M\_κ carries one buffer m\_t \in [0,1]\textasciicircum{}G updated by
             m\_\{t+1\} \leftarrow O\_t (no parameter, no learning); policy A\_t = argmax\_i(m\_t[i] - O\_t[i]).
             Resolves the H7-σ inversion paradox. Concept DOI: 10.5281/zenodo.20091626.}
}

@software{cae_research_kit_v0_3_0,
  title   = {CAE Research Kit: H7-σ Inverted — Real Feedback Loop Closer to Markov-Null than Obs-Shuffled Control},
  author  = {{The CAE Research Kit Authors}},
  year    = {2026},
  version = {v0.3.0-h7-σ-inverted},
  doi     = {10.5281/zenodo.20096664},
  url     = {https://doi.org/10.5281/zenodo.20096664},
  note    = {Verdict: H7\_SIGMA\_INVERTED (Cohen d = -0.7581, p\_less = 1.04e-05, n=30,
             pool [1400-1429]). Pre-registered inversion of the H1-greater prediction;
             mirrored bin formalised in ADR-026 v2.1. Concept DOI: 10.5281/zenodo.20091626.}
}

@software{cae_research_kit_v0_2_0,
  title   = {CAE Research Kit: H6 Falsified — Topological Signatures Reclassified as Feedback Artefacts},
  author  = {{The CAE Research Kit Authors}},
  year    = {2026},
  version = {v0.2.0-h6-rejected},
  doi     = {10.5281/zenodo.20094993},
  url     = {https://doi.org/10.5281/zenodo.20094993},
  note    = {Verdict: H6\_GAMMA\_FEEDBACK\_ONLY. Sibling release of v0.1.0-h5-rejected.
             Concept DOI: 10.5281/zenodo.20091626.}
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
