# Release v0.2.0-h6-rejected

**Title:** *H₆ Falsified: Topological Signatures Reclassified as Feedback Artefacts*
**Date:** 2026-05-09
**Scientific status:** `H6_GAMMA_FEEDBACK_ONLY` — H₆ as pre-registered (ADR-022 §3) is **not supported**.
**Operational status:** falsification published with full data, ADR chain, per-seed CSVs, both verdict files.
**Predecessor:** [v0.1.0-h5-rejected](#release-v010-h5-rejected) (sibling falsification).
**DOI concept:** [10.5281/zenodo.20091626](https://doi.org/10.5281/zenodo.20091626) (this release requests a new version DOI).

---

## 1. Abstract (no marketing)

H₆ predicted that an online adaptive agent interacting with the controlled
constraint field **E₀** would produce a phase-space trajectory with a
**topological signature** distinguishable from any reasonable Markov
surrogate of its action sequence. The hypothesis was pre-registered in
ADR-022 (frozen 2026-05-09, SHA `86b49ac1…`) before any code was run.

Phase **β** appeared to confirm H₆ massively. The frozen paired Wilcoxon
test (ADR-023.ter, alternative `"greater"`) produced **Cohen d = +2.5068**,
**p = 1.86 × 10⁻⁹**, **n = 30** seeds. By any conventional reading, this is
a strong positive result.

We did not publish it.

Phase **γ** (ADR-024, frozen before execution) introduced a control branch:
**`ObsShuffledAgent`** — a wrapper of the same adaptive policy that
receives `env.observe()` with a fresh per-tick column permutation, so the
agent *acts on the observation* but cannot extract any usable spatial
information from it. Two pre-registered tests, both one-sided Wilcoxon,
both run once on a disjoint seed pool [1300, 1329]:

| Test | Hypothesis | Cohen d | p-value | Threshold | Outcome |
|------|-----------|---------|---------|-----------|---------|
| γ.1 | δ(real, shuffled) > δ(real, Markov) | **−0.5027** | **0.998** | d ≥ 0.5, p < 0.005 (Bonferroni) | **fail to reject H₀** |
| γ.2 | δ(shuffled, Markov) > 0 | — | **9.31 × 10⁻¹⁰** | p < 0.05 | **reject H₀** |

The result is unambiguous and unfavourable to the structural claim. The
real agent's trajectory is, on average, **closer** to the obs-shuffled
agent's trajectory than to the Markov-null. The shuffled agent — which by
construction cannot use the observation's structure — is itself
significantly different from the Markov-null. Conclusion: the β signal is
the trivial signature of *conditioning on the environment at all*, not
the signature of a non-trivial coupling between the agent's policy and
the field's structure.

Combined verdict per ADR-024 §3.5 verdict matrix: **`H6_GAMMA_FEEDBACK_ONLY`**.

## 2. What this release ships

| Path | Description | SHA-256 |
|------|-------------|---------|
| `research/h6_beta_verdict.json` | H6-β verdict (apparent signal) | `e529194b…7d88d693` |
| `research/h6_beta_run_results.csv` | per-seed δ values, β | `7689a129…3814782e` |
| `research/h6_gamma_verdict.json` | H6-γ verdict (control) | `d89d15a2…b3fa8d1f` |
| `research/h6_gamma_run_results.csv` | per-seed (δ_RS, δ_RM, δ_SM), γ | `88e98e20…927dbcdc` |
| `research/MANIFEST.v0.2.0.yaml` | full release manifest | — |
| `docs/adr/ADR-022-h6-pre-registration.md` | H₆ pre-registration | `86b49ac1…69cd068` |
| `docs/adr/ADR-023-h6-beta-phase-space.md` | H6-β metric | `93a63b49…c5205649` |
| `docs/adr/ADR-023.bis-pressure-vector-trajectory.md` | β pipeline correction | `df5e7f68…f8bcd757` |
| `docs/adr/ADR-023.ter-paired-wilcoxon.md` | β test specification | `5fe12025…db9856c9` |
| `docs/adr/ADR-024-h6-gamma-obs-shuffled-control.md` | γ control pre-registration | `20098aef…05819b75` |
| `docs/adr/ADR-025-h6-release-decision.md` | release decision | `db3093a7…b512246b` |

**Not shipped:** the H6 development tree (`.forge_private/h6_dev/`) is not
included in this release. See ADR-025 §3 — code archive decision deferred
to a possible `v0.2.1-h6-code-archive`. The published verdicts and CSVs
are sufficient to audit the statistical claim.

## 3. Where the value is

This release does not deliver a new positive scientific finding. Its
deliverable is **methodological**:

- A worked example of a pre-registered control (ADR-024) frozen *before*
  being run, that overturned an apparent positive result (Cohen d ≈ 2.5).
- Direct evidence that **trajectory-coupling probes on E₀ in their
  current form cannot discriminate "feedback effect" from "structural
  coupling"** — a confound that is not specific to this kit and that
  affects any work claiming "emergent structure" in agent-environment
  loops without a feedback-naïve control branch.
- A second consecutive published falsification with a Zenodo DOI,
  consolidating the precedent set by v0.1.0-h5-rejected.

## 4. What this release is NOT

- Not a claim about emergence, structure, signature, intelligence,
  cognition, agency, or any cousin term.
- Not a claim that *no* topological signature exists in agent-environment
  trajectories — only that the present probe cannot detect one above the
  trivial feedback baseline.
- Not preliminary. Per ADR-025 §6, the H₆ pre-registration is spent and
  no further runs of the H6-β/γ pipelines under the present probe are
  authorised.

## 5. Reproducibility note

The H₅ Docker image (`cae-research-kit:0.1.0`, fingerprint
`406ce26e…008e7e5f`) is unchanged in this release. The H₆ development
environment used Python 3.12.3 with `numpy==1.26.4`, `scipy==1.12.0`,
`ripser==0.6.10`, `persim==0.3.5`, `pytest==8.1.1`. Per-seed CSVs are
sufficient to reproduce the verdict computation independently of the
trajectory pipeline.

## 6. Next steps

Per ADR-025 §5: any successor experiment (H₇ / H_δ) requires a new ADR
defining a probe **orthogonal to feedback**. No further H₆ work under
the present probe.

---

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
