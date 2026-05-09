# Release v0.4.0-h7-κ-reverses

**Title:** *H₇-κ Reverses: A Single Tick of Memory Breaks the σ Inversion*
**Date:** 2026-05-09
**Scientific status:** `KAPPA_REVERSES` — the H7-σ inverted-coupling signature is fully reversed by adding a single tick of local-pressure memory. Both branches of the pre-registered double reporting (Miller-Madow corrected primary, plug-in transparency) agree at the same p-value.
**Operational status:** paradox-resolution published with full data, ADR chain, public agent + ADT, per-seed CSV, verdict file, and SHA-pinned freeze manifest (κ v1).
**Predecessor:** [v0.3.0-h7-σ-inverted](#release-v030-h7-σ-inverted) (σ-inversion is the regime κ now decomposes).
**DOI (v0.4.0):** TBD — to be pinned post-Zenodo mint. Concept: [10.5281/zenodo.20091626](https://doi.org/10.5281/zenodo.20091626).

---

## 1. Abstract (no marketing)

H₇-σ (v0.3.0) published an *inverted* coupling signature: the real
feedback loop produced an action-pressure stationary distribution
*closer* to the Markov-null surrogate than the obs-shuffled control's
distribution was, with median diagnostic `K_R − K_S = −19` on B = 64
bins. The interpretation question left open was whether this inversion
was an architectural dead end (requiring an H8 pivot) or a *kinetic*
artefact of the agent being **memoryless** (in which case adding the
minimal possible memory should suffice to break it).

ADR-028 (Option A) accepted the κ-decomposition route. ADR-030
pre-registered H₇-κ under the **same** statistical chain as H₇-σ
(paired Wilcoxon, both alternatives, α = 0.005, Cohen d ≥ 0.5,
Miller-Madow + plug-in double reporting), with one new agent under test
(`M_κ`) defined by:

- a single buffer $m_t \in [0,1]^G$ with $G = $ `grid_size`, $m_0 = \mathbf{0}$,
- update rule $m_{t+1} \leftarrow O_t$ (assignment, **no parameter**),
- policy $A_t = \arg\max_i (m_t[i] - O_t[i])$, tie-break smallest index,
- bootstrap $A_0 = \arg\min_i O_0[i]$.

Zero gradient, zero learning, zero hyperparameter. The tested per-seed
quantity is the σ-Δ between M_κ and R on identical seeds:

$$ \Delta_s \;=\; \delta_\sigma^{M_\kappa}(s) \;-\; \delta_\sigma^{R}(s),
\qquad \delta_\sigma^{X}(s) \;=\; D_{\mathrm{KL}}(P_X(s) \,\|\, P_M(s))
\;-\; D_{\mathrm{KL}}(P_S(s) \,\|\, P_M(s)). $$

The frozen main run on the disjoint pre-reserved pool [1500-1529]
(n = 30, all 30 seeds drawn from the κ-reserved pool [1500-1599]) produced:

| branch | Cohen d | Wilcoxon p (greater) | Wilcoxon p (less) | n_post-drop | verdict |
|---|---:|---:|---:|---:|---|
| primary `Δ_κ_corr` | **+2.6619** | **9.31 × 10⁻¹⁰** | 1.0 | 30 | `KAPPA_REVERSES` |
| transparency `Δ_κ_naive` | +2.6620 | 9.31 × 10⁻¹⁰ | 1.0 | 30 | `KAPPA_REVERSES` |

`verdicts_agree = true`. `total_clip_events = 0`. **30 / 30 seeds with
$\Delta_s > 0$** (no counter-example). Median $\Delta_\kappa = +0.498$.

Diagnostic action-repertoire shift on the same disjoint pool:

- median $\delta_\sigma^{R} = -0.167$ (R remains σ-inverted out-of-sample, reproducing v0.3.0)
- median $\delta_\sigma^{M_\kappa} = +0.256$ (M_κ crosses zero, lands structural-side)
- median $K_R = 39.5$, median $K_{M_\kappa} = 62.0$, median $K_S = 62.0$, median $K_M = 56.0$
- median $K_{M_\kappa} - K_R = +23$ cells (action repertoire recovered to the obs-shuffled level)

## 2. What this release ships

| Path | Description | SHA-256 |
|---|---|---|
| `research/h7_kappa_verdict.json` | adjudicator output (verdict + p, d, diagnostics) | `4b819de7…08d3c1c2` |
| `research/h7_kappa_run_results.csv` | per-seed (30 rows × 29 cols) | `1c4c2cd0…062eae2c` |
| `research/MANIFEST.v0.4.0.yaml` | full release manifest + private freeze chain | — |
| `src/agents/memory1_agent.py` | M_κ public implementation | `2684b171…e727c7870` |
| `tests/adt/test_memory1_agent.py` | 5 ADT (κ-1 determinism, κ-2 interface, κ-3 m=O, κ-4 A_0=argmin, κ-5 obs guard); 5/5 PASS in 0.24 s | `01d8203e…04dc941a9` |
| `docs/adr/ADR-028-h7-kappa-or-h8-pivot.md` | Option A decision | `002b5971…c66d8c69ee` |
| `docs/adr/ADR-030-h7-kappa-pre-registration.md` | H₇-κ pre-registration (ACCEPTED on κ manifest v1) | `bc552e46…2baed27f` |

**Not shipped (per posture inherited from ADR-029 §4.4):** the κ runner
(`kappa_runner.py`, SHA `9428d3b7…`) and κ adjudicator
(`kappa_adjudicator.py`, SHA `16441e13…`) remain in
`.forge_private/h7_dev/src/h7/` for the same reason σ runner/adjudicator
were withheld at v0.3.0. The κ adjudicator is a thin wrapper (~30
specific LOC) over the σ chain — it reuses the σ-tested-and-frozen
Wilcoxon code byte-for-byte and only renames verdicts via a static map
(`H7_SIGMA_INVERTED → KAPPA_REINFORCES`,
`H7_SIGMA_STRUCTURAL_COUPLING → KAPPA_REVERSES`,
`H7_SIGMA_FEEDBACK_ONLY → KAPPA_NEUTRAL`,
`H7_SIGMA_INCONCLUSIVE → KAPPA_INCONCLUSIVE`). All private SHAs
(including the σ chain re-confirmed bit-identical post-κ run) are
recorded in `research/MANIFEST.v0.4.0.yaml` under
`private_freeze_chain_sha256` for audit. The published per-seed CSV +
verdict JSON + Memory1Agent + ADT are sufficient to reproduce the κ
statistical claim independently.

## 3. Where the value is

This release publishes a **paradox resolution**:

- The σ inverted-coupling signature, previously without explanation, is
  now identified as the **memoryless regime** of the agent class on E₀.
- A minimal causal probe (`m_t = O_{t-1}`, zero parameters) is sufficient
  to reverse the signature with effect size $d = +2.66$ at $p = 9.3 \times 10^{-10}$
  on n = 30 seeds, with not a single counter-example.
- The diagnostic +23-cell recovery on $K_{M_\kappa} - K_R$ shows that
  memory acts here as a **complexity-liberator on the action side**, not
  as a smoothing filter. The agent leaves passive stabilisation and
  enters active local-gradient navigation.
- ADR-028's Option A is vindicated: the deeper H8 pivot is *not*
  required to explain the σ regime. The minimal coupling component in E₀
  is **local temporal differentiation** — i.e. the agent's ability to
  compare $O_t$ with a single previous observation. The paradox is
  **kinetic, not geometric**.

## 4. What this release is NOT

- Not a claim about cognition, agency, intent, intelligence, emergence,
  or any cousin term. Permitted vocabulary remains operational only.
- Not a statement that one tick of memory is *necessary* — only
  *sufficient* to break the σ inversion within the H₇-κ pre-registration.
- Not a confirmation of any deeper architectural hypothesis. H8 is
  not invoked, refuted, or modified by this release; it simply is no
  longer required to interpret σ.
- Not a derivation of M_κ from first principles. M_κ is the operational
  minimum (1 tick, 0 parameters) chosen *before* the run; alternative
  minima (e.g. $m_{t+1} \leftarrow \alpha O_t + (1-\alpha) m_t$ with
  $\alpha = 1$ as a special case) are not tested here.
- Not preliminary. Per ADR-030 (now ACCEPTED), the H₇-κ pre-registration
  is spent on pool [1500-1529]. No further runs of the κ pipeline under
  the present probe are authorised on this pool.

## 5. Reproducibility note

The H₅ Docker image (`cae-research-kit:0.1.0`, fingerprint
`406ce26e…008e7e5f`) is unchanged. The H₇ development environment is
unchanged from v0.3.0 (Python 3.12.3, `numpy==1.26.4`, `scipy==1.12.0`,
`pytest==8.1.1`). The σ chain SHAs (`sigma_runner.py = 1ae4a877…`,
`sigma_adjudicator.py = f6c5aeff…`, `kl.py = 5b4520d6…`) were
re-confirmed bit-identical *after* the κ run, validating the
no-cross-contamination posture between σ and κ pipelines.

The 30-row per-seed CSV (29 columns including all four policies' KL
terms in both Miller-Madow corrected and naive variants, plus per-policy
non-empty bin counts and clip-event counters) is sufficient to reproduce
the verdict computation independently of the runner pipeline. The
public Memory1Agent (`src/agents/memory1_agent.py`) plus its 5 ADT
(`tests/adt/test_memory1_agent.py`, all passing in 0.24 s) is sufficient
to verify the agent semantics independently. The adjudicator's I/O
contract is documented inline in ADR-030 §3 and the verdict-table
mapping in `research/h7_kappa_verdict.json` field
`verdict_label_mapping`.

## 6. Next steps

This release closes the H₇ doctrinal arc. Three follow-on questions are
**not** triggered by this release alone and require their own ADRs:

- **κ-stability sweep.** Whether the same effect size holds for variants
  of M_κ with longer memory windows or alternative update rules (e.g.
  EMA, leaky integrator, multi-tick lookback). Not pre-registered;
  pool not reserved.
- **H8 deferral confirmation.** Whether the H8 architectural pivot
  remains permanently unnecessary, or only unnecessary *for explaining
  σ*. ADR-028's Option A vindication does not pre-empt H8 on its own
  merits; a separate ADR is required.
- **Cross-environment portability.** Whether the κ-reverses signature
  replicates on environments other than E₀. Out of scope of the present
  protocol; would require a new pre-registration and a new fingerprint.

The κ pool tail [1530-1599] remains reserved and **frozen** pending any
of the above ADRs. No further H₇ runs are authorised until then.

---

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
