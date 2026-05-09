# ADR-024 — H6-β scope limitation & H6-γ obs-shuffled control pre-registration

**Status:** Pre-registered
**Date:** 2026-05-09
**Supersedes:** none
**Extends:** ADR-022, ADR-023, ADR-023.bis, ADR-023.ter
**Predecessor verdict:** H6-β = `H6_SIGNATURE_DETECTED` (d=2.5068, p=1.86e-9, n=30) — see `.forge_private/h6_dev/research/h6_verdict.json`

---

## 1. Context

H6-β rendered `H6_SIGNATURE_DETECTED` per the test frozen by ADR-023.ter:
paired Wilcoxon on δ(real, markov_null) vs δ(markov_null_A, markov_null_B),
n=30 seeds in [1200, 1229]. The effect is large (Cohen d ≈ 2.5) and
statistically unambiguous (p ≈ 2 × 10⁻⁹), with 29/30 seeds producing
positive paired differences.

**This ADR refuses to publish that verdict as evidence of a "structural
signature" without first running a control that distinguishes "structure"
from a trivial confound.**

## 2. The confound H6-β does not rule out

The H6-β protocol compares two trajectory generators:

- **Real branch (Ω):** `AdaptiveAgent` consumes `env.observe()` *before*
  emitting each action. The action distribution is therefore conditional
  on the live pressure field.
- **Markov-null branch (M):** A first-order Markov model fitted on the
  real action sequence emits actions *unconditionally* — it has no access
  to `env.observe()` at replay time.

A non-zero δ between Ω and M can be produced by **either** of:

1. **(H6 hypothesis)** The agent's interaction with E₀ produces a
   trajectory whose phase-space topology differs from any reasonable
   Markov surrogate, indicating non-trivial coupling.
2. **(Trivial confound)** Any policy that conditions on the live
   environment will produce a trajectory observably distinct from any
   policy that does not, because the *fact of conditioning* leaves a
   first-order autocorrelation signature in the action sequence that is
   absent from a fitted Markov chain.

**Confound (2) makes any policy-with-feedback look "structured" relative
to its Markov fit, regardless of what the agent actually does.** We do
not currently have evidence to discriminate (1) from (2).

## 3. H6-γ — pre-registered control experiment

### 3.1 Goal

Discriminate (1) from (2) by introducing a third trajectory generator
that **conditions on `env.observe()` but with the conditioning structure
deliberately destroyed**. If the agent's contribution is purely the act
of conditioning, this third branch should produce a δ similar to the
real branch. If the agent's contribution is a non-trivial coupling, the
third branch should produce a δ between the Markov-null and the real
branch — strictly closer to the Markov-null.

### 3.2 The shuffled-observation agent (S-Agent)

A new agent class, `ObsShuffledAgent`, wraps the same `AdaptiveAgent`
hyperparameters used in H₅/H6-β but applies a **per-tick column
permutation** to `env.observe()` before passing the vector to the agent's
policy:

- The permutation `π_t ∈ S_D` is drawn fresh at each tick `t` from a
  dedicated PRNG seeded by `(seed, "obs_shuffle")`.
- The agent's update logic is unchanged. The action it emits is sent
  to the real (un-permuted) `E₀`.

This preserves:
- The agent's read-act loop (so the *fact* of conditioning is identical
  to the real branch).
- The marginal statistics of the observation each tick.

This destroys:
- The spatial structure linking observation entries to underlying field
  positions, and therefore any non-trivial coupling between observation
  topology and action topology.

### 3.3 Pipeline per seed s ∈ [1300, 1329]

For each seed, generate **three** trajectories on a fresh `E₀(seed=s)`:

1. **R(s)** — real run with `AdaptiveAgent` (identical to ADR-023.ter §3.1).
2. **S(s)** — shuffled-obs run with `ObsShuffledAgent`, same seed.
3. **M(s)** — Markov-null replay fitted on R(s)'s actions, sampled with
   `np.random.default_rng(s)`. **Single null, not two.**

Compute three δ values per seed via `phase_delta` after z-scoring with
R(s)'s μ, σ (ADR-023.bis §3.5):

- δ_RS(s) = δ( z(R), z(S) )
- δ_RM(s) = δ( z(R), z(M) )
- δ_SM(s) = δ( z(S), z(M) )

### 3.4 Decision rule

Two paired Wilcoxon tests, both one-sided "greater":

- **Test γ.1:** H₀: δ_RS = δ_RM. H₁: δ_RS > δ_RM.
  - **Rejecting H₀ (p < 0.005, d ≥ 0.5)** means the real run is *farther*
    from shuffled than from Markov — i.e. the agent's structural
    contribution exceeds mere conditioning. **STRUCTURE ATTESTED.**
- **Test γ.2:** H₀: δ_SM = 0. H₁: δ_SM > 0 (one-sample paired Wilcoxon
  via `wilcoxon(δ_SM)` with `alternative="greater"`).
  - **Failing to reject** (p ≥ 0.05) would mean shuffled and Markov are
    indistinguishable — **CONFOUND CONFIRMED**, H6-β verdict downgraded
    to "feedback effect, not structure".

Bonferroni correction (k=2) tightens γ.1 to **α = 0.005**.

### 3.5 Combined verdict matrix

| γ.1 (RS > RM)? | γ.2 (SM > 0)? | Verdict           |
|----------------|---------------|-------------------|
| yes            | yes           | `H6_GAMMA_STRUCTURE_ATTESTED` |
| yes            | no            | `H6_GAMMA_STRUCTURE_ATTESTED` (stronger: shuffled itself collapses to Markov) |
| no             | yes           | `H6_GAMMA_FEEDBACK_ONLY` (H6-β verdict downgraded) |
| no             | no            | `H6_GAMMA_INCONCLUSIVE` |

## 4. Frozen parameters

| Parameter            | Value                              | Authority |
|----------------------|------------------------------------|-----------|
| seeds                | [1300, 1329] (n=30)                | this ADR §3.3 |
| α (Bonferroni-corr.) | 0.005 for γ.1, 0.05 for γ.2        | §3.4 |
| Cohen d threshold γ.1| 0.5 (detect), 0.2 (reject)         | inherits ADR-022 §3 |
| ObsShuffledAgent perm PRNG | `np.random.default_rng(seed_root)` where `seed_root = hash(("obs_shuffle", seed))` | §3.2 |
| Number of null draws | 1 per seed (not 2)                 | §3.3 |
| Test                 | paired Wilcoxon, alternative="greater", `zero_method="wilcox"` | §3.4 |
| n_required           | 30                                 | inherits ADR-022 §4.5 |

## 5. Seed disjointness

| Hypothesis | Seed range            |
|------------|------------------------|
| H₅         | [1000, 1029] ∪ {99}    |
| H6-α syn   | [1100, 1129]           |
| H6-β       | [1200, 1229]           |
| **H6-γ**   | **[1300, 1329]**       |

No seed overlap. Verified at test time.

## 6. Anti-patterns (binding)

In addition to ADR-022 §8, ADR-023 §7, ADR-023.ter §6:

1. **No re-running** the H6-γ pipeline after seeing partial results.
   One shot.
2. **No tweaking** the shuffle PRNG seed scheme after observing any δ.
3. **No additional null draws.** The Markov branch in H6-γ uses one
   null per seed, period. If you want two, write ADR-024.bis first.
4. **No comparing** H6-β δ values to H6-γ δ values. They use different
   seed pools and different protocols — comparing them across ADRs is
   meaningless and forbidden.
5. **No public release** of any H6 verdict (β or γ) until both H6-β AND
   H6-γ have rendered. The β verdict alone is doctrinally insufficient.

## 7. Pre-conditions for execution

Before running H6-γ:

1. ADR-024 file SHA-256 frozen and committed to `.forge_private/`.
2. `ObsShuffledAgent` implemented in `.forge_private/h6_dev/src/h6/`.
3. RED tests for `ObsShuffledAgent` validate:
   - the per-tick permutation differs across ticks
   - the permutation is reproducible from the seed
   - the action sent to `E₀` is the agent's response to the *permuted*
     observation, not the raw one
4. `runner_gamma.py` written and code-frozen (SHA-256 alongside the
   other H6-β code SHAs in `.forge_private/h6_beta_code.sha256`, or a
   sibling file).
5. All H6-β tests still pass (regression gate).

## 8. Outputs

- `.forge_private/h6_dev/research/h6_gamma_verdict.json`
- `.forge_private/h6_dev/research/h6_gamma_run_results.csv` (per-seed:
  seed, δ_RS, δ_RM, δ_SM)

## 9. Public release decision tree (binding)

After both verdicts:

| H6-β     | H6-γ                          | Release |
|----------|-------------------------------|---------|
| DETECTED | STRUCTURE_ATTESTED            | `v0.2.0-h6-attested` (full claim) |
| DETECTED | FEEDBACK_ONLY                 | `v0.2.0-h6-feedback-only` (downgraded scope) |
| DETECTED | INCONCLUSIVE                  | private debrief, no release |
| anything else | n/a                      | follow ADR-022 §10 |

The `v0.2.0-h6-feedback-only` release would be honest and publishable
— but it would NOT support a "signature of structure" claim, only a
"feedback-induced trajectory difference" claim. The README, RELEASE.md
and any abstract MUST reflect that downgrade verbatim.

---
End of ADR-024.
