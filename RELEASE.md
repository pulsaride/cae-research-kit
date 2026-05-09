# Release v0.3.0-h7-σ-inverted

**Title:** *H₇-σ Inverted: Real Feedback Loop Closer to Markov-Null than Obs-Shuffled Control*
**Date:** 2026-05-09
**Scientific status:** `H7_SIGMA_INVERTED` — H₇-σ as pre-registered (ADR-026 v2 §2, alternative `"greater"`) is **rejected in the opposite direction**. The mirrored bin formalised in ADR-026 v2.1 §1 (alternative `"less"`, `|d| ≥ 0.5`, `p < 0.005`) is supported with verdicts agreeing across primary and transparency reportings.
**Operational status:** inverted directional signal published with full data, ADR chain, per-seed CSV, verdict file, and SHA-pinned freeze manifest.
**Predecessor:** [v0.2.0-h6-rejected](#release-v020-h6-rejected) (sibling falsification).
**DOI (v0.3.0):** [10.5281/zenodo.20096664](https://doi.org/10.5281/zenodo.20096664) — concept: [10.5281/zenodo.20091626](https://doi.org/10.5281/zenodo.20091626).

---

## 1. Abstract (no marketing)

H₇-σ predicted that an online adaptive agent interacting with E₀ would
produce, under a stationary action-pressure measure, a divergence from a
Markov-null surrogate of its action sequence *strictly greater* than the
divergence produced by an obs-shuffled control of the same policy. The
hypothesis was pre-registered in ADR-026 v2 (frozen 2026-05-09 morning,
SHA `7e8e4ea8…`) before the main run, with full constants
(`B = 64`, `T_warmup = 5_000`, `T_stat = 50_000`, `P ∈ [0,1]` strict),
statistical chain (paired Wilcoxon, α = 0.005, Cohen d ≥ 0.5,
ADR-027), and double-reporting clause (Miller-Madow corrected primary
vs plug-in transparency, disagreement → INCONCLUSIVE override) all
inscribed in advance. A separate pilot on burned pool [9000-9009] had
already validated the constants, finiteness, and per-seed wall time
(pilot summary SHA `caad3901…`) without seeing the main pool.

The frozen main run on the disjoint, pre-reserved pool [1400-1429]
(n = 30) produced the **opposite** directional signal at strong effect:

| branch | Cohen d | Wilcoxon p (greater) | Wilcoxon p (less) | n_post-drop | verdict |
|---|---:|---:|---:|---:|---|
| primary `δ_σ_corr` | **−0.7581** | 0.99999 | **1.04 × 10⁻⁵** | 30 | `H7_SIGMA_INVERTED` |
| transparency `δ_σ_naive` | −0.7581 | 0.99999 | 1.04 × 10⁻⁵ | 30 | `H7_SIGMA_INVERTED` |

`verdicts_agree = true`. `total_clip_events = 0`. 26 / 30 seeds with `δ_σ < 0`.
median `δ_σ = −0.148`.

Because ADR-026 v2 §2 listed `H7_SIGMA_INVERTED` as a verdict bin but
provided no instrument to assert it (the test was one-sided `greater`
only), ADR-026 v2.1 (frozen *post-main-run, pre-re-adjudication*) added
the mirrored alternative `"less"` with the *same* α and the *same* `|d|`
threshold. This is procedurally equivalent to having pre-registered a
two-sided Wilcoxon with α = 0.005 from the start (the rejection regions
`d ≥ +0.5` and `d ≤ −0.5` are disjoint, no Bonferroni correction is
required). The amendment is procedural, not theoretical.

Diagnostic structural signature, replicated pilot → main without re-fit:
median non-empty bins K_R = 42, K_S = 61.5, K_M = 57 (out of B = 64);
median `K_R − K_S = −19` (vs pilot −15, **sign preserved, magnitude
strengthened out-of-sample**).

## 2. What this release ships

| Path | Description | SHA-256 |
|---|---|---|
| `research/h7_sigma_verdict.json` | adjudicator output (verdict + p, d, diagnostics) | `62a376b7…45d22fe0` |
| `research/h7_sigma_run_results.csv` | per-seed (30 rows × 20 cols) | `90ee2b80…22e674a3` |
| `research/MANIFEST.v0.3.0.yaml` | full release manifest + private freeze chain | — |
| `docs/adr/ADR-026-h7-sigma.md` | H₇-σ pre-registration (v2 frozen) | `7e8e4ea8…84abc9ae` |
| `docs/adr/ADR-026-v2.1-h7-sigma-amendment-inverted.md` | amendment formalising INVERTED bin | `2bdf8ae9…fc4e35c8` |
| `docs/adr/ADR-027-h7-sigma-statistical-chain.md` | paired Wilcoxon spec | `7d755b94…294d76fb` |
| `docs/adr/ADR-029-h7-sigma-release.md` | release decision | `db730ab0…5e2c69bc` |

**Not shipped (per ADR-029 §4.4):** the H₇ source tree
(`.forge_private/h7_dev/src/h7/`) and the pilot tree
(`.forge_private/h7_dev/exploratory/`) are *not* included in this release.
The H₇ code archive is deferred to v0.4.0 to avoid fragmenting the H₇
module across releases. SHA-256 of all private files is recorded inline
in `research/MANIFEST.v0.3.0.yaml` under `private_freeze_chain_sha256`
for audit. The published per-seed CSV + verdict JSON + adjudicator I/O
contract are sufficient to reproduce the statistical claim independently.

## 3. Where the value is

This release does deliver a positive empirical finding, but in a direction
*opposite* to its pre-registered prediction. Its deliverables are:

- The first reproducible non-trivial directional signature in the CAE
  protocol (replicated pilot → main, pre-registered, frozen).
- A worked example of an honest inverted-direction publication, with the
  same statistical rigour, ADR chain, freeze manifest, and Zenodo DOI as
  a confirmation would have received.
- A formalised procedural amendment (ADR-026 v2.1) showing how to handle
  a one-sided pre-registration that needs to assert its mirrored bin
  *without* relaxing α or introducing post-hoc degrees of freedom.
- A published structural invariant (`K_R < K_S < K_M` with median
  `K_R − K_S = −19` on B = 64 bins) that constrains any future model of
  feedback in CAE.

## 4. What this release is NOT

- Not a confirmation of H₇-σ as stated in ADR-026 v2 §2 (alternative
  `greater`). That hypothesis is rejected.
- Not a claim about emergence, structure (in any non-operational sense),
  intelligence, cognition, agency, or any cousin term. The permitted
  vocabulary additions in ADR-026 v2.1 §7 — *inverted coupling*,
  *stabilising feedback* — are operational only, gated on the strict
  thresholds `d ≤ −0.5 ∧ p_less < 0.005`.
- Not an automatic trigger for H₇-κ. The κ pool [1500-1599] remains
  reserved and **frozen**; ADR-028 must first decide whether the inverted
  verdict is eligible to investigation by κ (out of scope of ADR-029).
- Not preliminary. Per ADR-029 §4 and ADR-026 v2 §10, the H₇-σ
  pre-registration is spent and no further runs of the H₇-σ pipeline
  under the present probe are authorised.

## 5. Reproducibility note

The H₅ Docker image (`cae-research-kit:0.1.0`, fingerprint
`406ce26e…008e7e5f`) is unchanged. The H₇ development environment used
Python 3.12.3 with `numpy==1.26.4`, `scipy==1.12.0`, `pytest==8.1.1`
(plus `ripser==0.6.10` and `persim==0.3.5` inherited from the H₆ venv,
neither on the H₇-σ critical path). The 30-row per-seed CSV is
sufficient to reproduce the verdict computation independently of the
runner pipeline; the adjudicator's I/O contract is documented in
ADR-027 §3 and the verdict-table thresholds in ADR-026 v2.1 §1.

## 6. Next steps

Per ADR-029 §6, ADR-028 (to be drafted) must decide whether H₇-κ remains
pertinent on the inverted verdict — either by re-interpreting κ as a
decomposition of the observed stabilising feedback, or by abandoning κ in
favour of a re-pre-registered H₈. The κ pool [1500-1599] stays frozen
until ADR-028 is signed.

---

# Release v0.2.0-h6-rejected

**Title:** *H₆ Falsified: Topological Signatures Reclassified as Feedback Artefacts*
**Date:** 2026-05-09
**Scientific status:** `H6_GAMMA_FEEDBACK_ONLY` — H₆ as pre-registered (ADR-022 §3) is **not supported**.
**Operational status:** falsification published with full data, ADR chain, per-seed CSVs, both verdict files.
**Predecessor:** [v0.1.0-h5-rejected](#release-v010-h5-rejected) (sibling falsification).
**DOI (v0.2.0):** [10.5281/zenodo.20094993](https://doi.org/10.5281/zenodo.20094993) — concept: [10.5281/zenodo.20091626](https://doi.org/10.5281/zenodo.20091626).

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
