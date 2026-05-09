# ADR-026 v2 (FROZEN — single-probe σ, all numeric constants substituted)

**Title:** H₇-σ — Stationary-Distribution Bias as a Feedback-Orthogonal Probe of Structural Coupling on E₀
**Status:** **FROZEN.** Numeric constants substituted from pilot run `pilot_run_20260509T094414Z` (sha256 of `pilot_summary.md`: `caad3901af64d8fb7e3b91fa85e2a8390f8accaa735af30a8aee129fd3b60af4`). All §3 parameters are now binding. No further tuning admissible. Pilot pool [9000–9009] **BURNED**.
**Predecessors (binding):** ADR-022 · ADR-023.bis · ADR-023.ter · ADR-024 · ADR-025 · ADR-026 v1 (this file's draft).
**Sibling (binding for main run):** ADR-027 (statistical chain inheritance — written in parallel, must be SHA-frozen before any main code commit).
**CEO selection:** "σ then κ contingent" (Path 1 of v0 §4), confirmed at v2 freeze.

---

## 0. Diff vs v1

| Field | v1 (draft) | v2 (frozen) |
|---|---|---|
| `T_warmup` | TBD by pilot | **5 000 ticks** |
| `T_stat`   | TBD by pilot | **50 000 ticks** |
| `B`        | TBD by pilot — rule `min_count_M ≥ 20` | **64** — physical-anchor rule (§3.2.bis) |
| `P_min`    | TBD by pilot | **0.0** |
| `P_max`    | TBD by pilot | **1.0** |
| Pressure reduction | unspecified | **flatten over (cell, tick)** (§3.2 added) |
| §4 conservatism claim | "MM is conservative under H₁-greater" | **Rescinded.** Replaced by §4 (revised): empirical sign of MM correction confirmed *anti-conservative* on (R, S) pairs (K_R < K_S empirically by 14–15 bins at B=64). Mitigation: double-reporting (§3.4 revised). |
| §3.4 CSV columns | 14 columns | **17 columns** — added `K_R_nonempty`, `K_S_nonempty`, `delta_sigma_naive`, `delta_sigma_corr` explicit pair (column rename for clarity) |
| Pilot pool status | reserved | **BURNED** |

The hypothesis statement (§2), the test (paired Wilcoxon "greater"), α (0.005), d-threshold (0.5), verdict table, and κ-trigger clause (§6) are **unchanged from v1**.

---

## 1. Mandat doctrinal

(Unchanged from v1 §1. Banned vocabulary list and permitted vocabulary list are binding for every H₇ artefact. Any drift triggers `git reset` of the offending commit before further work.)

---

## 2. Pre-registered hypothesis H₇-σ

(Unchanged from v1 §2. Reproduced verbatim for self-containment.)

**H₇-σ:** On environment E₀ (frozen per ADR-022, fingerprint `406ce26ec3aeefada7e2250f16d24a89361c1da2041c6775599be394008e7e5f`), the empirical stationary distribution of pressure observed under a real adaptive policy exhibits a *strictly larger* divergence from the Markov-null distribution than the empirical stationary distribution observed under an obs-shuffled adaptive policy.

With μ_R, μ_S, μ_M denoting the empirical pressure distributions under real / shuffled / Markov policies on a single seed s:

- δ_σ(s) := KL_corr(μ_R(s) ‖ μ_M(s)) − KL_corr(μ_S(s) ‖ μ_M(s))
- **H₀:** δ_σ(s) ≤ 0 across the seed pool.
- **H₁:** δ_σ(s) > 0 across the seed pool.

**Test:** paired Wilcoxon "greater" (per ADR-023.ter), `zero_method="wilcox"`, on the n = 30 paired δ_σ values. **α = 0.005**. Single test ⇒ no Bonferroni adjustment.

**Effect-size threshold (frozen):** Cohen `d ≥ 0.5` on paired δ_σ. Verdicts unchanged from v1:

| Outcome | Verdict |
|---|---|
| `d ≥ 0.5` AND `p < 0.005` | `H7_SIGMA_STRUCTURAL_COUPLING` |
| `p ≥ 0.005` AND `|d| < 0.2` | `H7_SIGMA_FEEDBACK_ONLY` (→ κ-trigger §6) |
| `p ≥ 0.005` AND `|d| ≥ 0.2` | `H7_SIGMA_INCONCLUSIVE` |
| `d < 0` AND `p < 0.005` | `H7_SIGMA_INVERTED` |

**Double-reporting clause (new in v2):** the verdict is computed on δ_σ_corr (the Miller-Madow-corrected statistic). The verdict JSON additionally reports the paired Wilcoxon statistic, p-value, and Cohen d computed on δ_σ_naive (uncorrected plug-in) **for transparency**. If the verdicts on δ_σ_corr and δ_σ_naive disagree at the α = 0.005 / d = 0.5 thresholds, the run is declared `H7_SIGMA_INCONCLUSIVE` regardless of which version "passes" — a verdict that depends on the bias correction is, by construction, not robust.

---

## 3. Pipeline (frozen)

### 3.1 Roll-out

For each seed s ∈ [1400, 1429] (n = 30, declared in §7):

- **R(s):** `AdaptiveAgent` (public `src/agents/adaptive_agent.py`, frozen per H₆ chain).
- **S(s):** `ObsShuffledAgent` from `.forge_private/h6_dev/src/h6/obs_shuffled.py` (BLAKE2b stable seed_root, ADR-024 §4 spec, byte-identical to H₆-γ).
- **M(s):** Markov-null policy (`fit_markov` + `sample_markov` from `.forge_private/h6_dev/src/h6/markov.py`, Laplace α=1.0 on transition counts per ADR-022 §4.3, byte-identical to H₆-β).

Each roll has length `T_warmup + T_stat = 5 000 + 50 000 = 55 000 ticks`. The first 5 000 ticks are discarded.

The Markov-null transition matrix is fitted on the action sequence emitted by R(s) (same seed s), exactly as in H₆-β. The replay seed for `sample_markov` is `seed = s` (numpy default_rng). The initial state is `actions_R[0]`.

### 3.2 Distribution estimation

- **Pressure scalar reduction:** `flatten over (cell, tick)`. Each tick contributes D = 64 scalar samples (one per E₀ cell). Total samples per policy after warmup: T_stat × D = 50 000 × 64 = **3 200 000**.
- **Support:** [P_min, P_max] = **[0.0, 1.0]**, frozen from the bound-scan on pilot seed 9000 (raw bounds were [0.0000, 1.0000] across all three policies). Any out-of-range value is **clipped** to the nearest endpoint. The number of clip events is recorded in the run CSV; a non-zero count must be reported in the verdict.
- **Discretisation:** equal-width bins on [0.0, 1.0], B = 64. Right edge inclusive (last bin captures p = 1.0 exactly).

### 3.2.bis Why B = 64 (replaces v1 §3.2 freezing rule)

The pilot established that the rule `min_count_M_bin ≥ 20` is **always false** under our chosen estimator (asymmetric Laplace +1 on Q-only): there is always at least one bin in μ_M with exactly 1 sample, even at T = 200 000 × 64 ≈ 13 M samples. The rule was a calibration artefact for plug-in KL; it is obsolete under the v1 §3.3 correction.

We replace it with a **physical-anchor rule**: B equals the spatial dimension D of E₀ (D = 64). One bin per cell on average. This:

1. Is fixed *a priori* by the environment specification (no data-driven tuning).
2. Sits in the centre of the pilot's tested grid {16, 32, 64, 128, 256, 512}, where convergence of KL(R‖M) is stable to within 1% of its T → ∞ value at T_stat ≥ 10 000 ticks.
3. Satisfies the alternative rule `K_M_nonempty ≥ 10` comfortably (pilot showed K_M ≈ 30–60 at B = 64).

### 3.3 KL with bias correction (unchanged from v1, kept verbatim)

Empirical entropies in nats. For each entropy term and each policy X ∈ {R, S, M} with non-empty count vector `n_X[b]`, total `T = Σ_b n_X[b]`, K_X = #{b : n_X[b] > 0}:

- Plug-in: `H_hat(X) = -Σ_{b : n_X[b]>0} (n_X[b]/T) · log(n_X[b]/T)`
- Miller-Madow: `H_MM(X) = H_hat(X) + (K_X − 1) / (2T)`

Cross entropy and Laplace handling:

- For `X ∈ {R, S}`, the cross-term `H(X, M) = -Σ_b p_X[b] · log p_M[b]` requires `p_M[b] > 0` whenever `p_X[b] > 0`.
- For each bin b such that `n_X[b] > 0` AND `n_M[b] = 0`: add **Laplace +1** to `n_M[b]` only (asymmetric: P-counts unchanged), then renormalise. Number of Laplace events recorded as `laplace_bins_X`.

Corrected KL:

`KL_corr(X ‖ M) = H_cross(X, M) − H_MM(X) + (K_M^post − 1) / (2T)`

where K_M^post is the count of non-empty bins in M *after* asymmetric Laplace.

The δ_σ statistic per seed:

- `delta_sigma_corr(s) = KL_corr(R(s) ‖ M(s)) − KL_corr(S(s) ‖ M(s))`
- `delta_sigma_naive(s) = KL_naive(R(s) ‖ M(s)) − KL_naive(S(s) ‖ M(s))` (plug-in cross entropy − plug-in entropy of P, no MM term, asymmetric Laplace still applied to M to keep finiteness)

### 3.4 CSV schema (frozen)

`research/h7_sigma_run_results.csv` columns, in order, no additions, no removals, no renames:

```
seed,
T_warmup, T_stat, B, P_min, P_max,
KL_R_M_corr, KL_S_M_corr,
KL_R_M_naive, KL_S_M_naive,
delta_sigma_corr, delta_sigma_naive,
K_R_nonempty, K_S_nonempty, K_M_nonempty,
laplace_bins_R, laplace_bins_S,
clip_events_R, clip_events_S, clip_events_M
```

`research/h7_sigma_verdict.json` schema additions over `h6_gamma_verdict.json`:

```
{
  "test": "wilcoxon",
  "alternative": "greater",
  "zero_method": "wilcox",
  "n": 30,
  "alpha": 0.005,
  "d_threshold": 0.5,
  "primary": {
    "statistic_field": "delta_sigma_corr",
    "wilcoxon_statistic": ...,
    "p_value": ...,
    "cohen_d": ...
  },
  "transparency": {
    "statistic_field": "delta_sigma_naive",
    "wilcoxon_statistic": ...,
    "p_value": ...,
    "cohen_d": ...
  },
  "verdicts_agree": true/false,
  "verdict": "H7_SIGMA_*",
  "decision_record_ref": "ADR-029-h7-sigma-release.md",
  "code_sha256": {...},
  "adr_sha256": {...}
}
```

---

## 4. The Miller-Madow correction sign — empirical inscription (REVISED v2)

**v1 claimed:** "MM is conservative under H₁-greater."
**v2 rescinds this claim.**

Algebraic identity (proven in `pilot_kl.py` test `test_miller_madow_reduces_kl_on_known_case`, ten lines of arithmetic):

> `KL_corr(P ‖ Q) − KL_naive(P ‖ Q) = (K_Q^post − K_P) / (2T)`

On the paired δ_σ statistic, the (K_M − 1)/(2T) terms attached to R and S **cancel exactly** (same M for both). The residual MM contribution to δ_σ is:

> `δ_σ_corr − δ_σ_naive = (K_S − K_R) / (2T)`

(modulo a ≤ 1-bin asymmetry from Laplace events on M, which differ between R-paired and S-paired MM terms; small relative to K_R, K_S in our regime.)

**Pilot empirical finding (binding inscription):** at B = 64, T = 50 000, on seeds [9000–9009]:

- median(K_R) = 22, median(K_S) = 37, median(K_R − K_S) = **−15**
- range of (K_R − K_S) across pilot seeds: [−18, −13]
- ⇒ MM correction adds, in median, `15 / (2 · 50 000 · 64) ≈ 2.3 × 10⁻⁶` to δ_σ_corr above δ_σ_naive
- compared to median KL ≈ 0.090 ⇒ relative inflation ≈ **2.6 × 10⁻⁵** (negligible at three decimal places of any expected effect)

**Doctrinal reading (this is the actual scientific content of §4):**

The signature `K_R < K_S` on E₀ — the real adaptive agent visits *fewer* pressure bins than the obs-shuffled adaptive agent — is the first non-trivial empirical fact on the σ-probe, **independent of the test outcome on δ_σ**. Operationally: structural coupling (when present) acts as a *concentrator* on the marginal pressure distribution; the obs-shuffled control disperses pressure over more bins. This is consistent with the "feedback baseline disperses, structural coupling concentrates" reading already implicit in ADR-024 §3, but here it is a *measured invariant of the stationary distribution*, not a trajectory property.

This finding is recorded as a **pilot-derived invariant** (not a hypothesis tested by the main run), and must be **re-measured on the main pool** [1400–1429] for confirmation. If the sign of `median(K_R − K_S)` flips on the main pool, the verdict JSON's `transparency.notes` field must record this and the result is `H7_SIGMA_INCONCLUSIVE`.

**Mitigation for the rescinded conservatism claim:** the double-reporting clause (§2) decides any δ_σ_corr-vs-δ_σ_naive disagreement against `H7_SIGMA_STRUCTURAL_COUPLING` automatically.

---

## 5. Pilot record (closed)

Pilot directory: `.forge_private/h7_dev/exploratory/pilot_run_20260509T094414Z/`
- `pilot_config.json` (P_min/P_max bounds scan, code SHAs)
- `pilot_curves.csv` (480 rows, 6 B × 9 T × 10 seeds, minus T = 200 000 truncations; columns include K_R/K_S for the §4 inscription)
- `pilot_burnin.csv` (60 rows, 6 t_start × 10 seeds at B = 64)
- `pilot_finiteness.json` (KL(S‖M) finiteness, all 10 seeds finite)
- `pilot_summary.md` + `pilot_summary.sha256` (SHA-256: `caad3901af64d8fb7e3b91fa85e2a8390f8accaa735af30a8aee129fd3b60af4`)

The pilot SHA above is **part of the binding chain**: the H₇-σ verdict is computable only against this exact pilot run.

Pilot anti-pattern check: the analysis of pilot data (`pilot_analyze.py`) consumed only `KL_R_M_corr`, K-counts, and `KL_S_M` (finiteness scalar). δ_σ was never computed on pilot data. Pilot blindness to H₁ is preserved.

Re-running the pilot under any code change is now **forbidden** under ADR-024 §6 (anti-pattern 3). If a flaw in `pilot_kl.py` is discovered post-freeze, the remediation is: declare the H₇-σ chain compromised, write ADR-026.bis explaining the flaw, restart from a fresh pilot pool [9100–9109] with a new ADR-026 v3.

---

## 6. κ-trigger clause (unchanged from v1)

(Reproduced verbatim from v1 §6 for self-containment. No changes.)

The κ-track activates iff `H7_SIGMA_FEEDBACK_ONLY` (`p ≥ 0.005` AND `|d| < 0.2`). κ work requires ADR-027 + ADR-028 frozen before any code, seed pool [1500–1599] n=100 reserved here.

---

## 7. Seed pool reservation (binding final)

| Pool | Range | Status | Use |
|---|---|---|---|
| H₅ | [1000, 1029] | consumed | v0.1.0-h5-rejected |
| H₆-α | [1100, 1129] | consumed | dev only |
| H₆-β | [1200, 1229] | consumed | v0.2.0-h6-rejected |
| H₆-γ | [1300, 1329] | consumed | v0.2.0-h6-rejected |
| **H₇-σ pilot** | **[9000, 9009]** | **BURNED at v2 freeze** | calibration consumed |
| **H₇-σ main** | **[1400, 1429]** | **active (this freeze authorises consumption)** | n = 30 |
| H₇-σ pilot fallback | [9100, 9109] | reserved (only on §5 remediation path) | n=10 |
| H₇-κ main (contingent) | [1500, 1599] | reserved | n = 100, fires only on κ-trigger |

---

## 8. Code scope and SHA-freeze policy

The following files must exist, be tested, and have their SHA-256 recorded in the verdict JSON before the main run is launched:

- `.forge_private/h7_dev/src/h7/sigma_runner.py` — orchestrator (one function `run_seed(s, env_config) → CsvRow`, no top-level state)
- `.forge_private/h7_dev/src/h7/sigma_adjudicator.py` — paired Wilcoxon + Cohen d on the 30-row CSV, emits verdict JSON
- `.forge_private/h7_dev/src/h7/__init__.py` (empty)
- `.forge_private/h7_dev/exploratory/pilot_kl.py` — re-imported as `h7.kl` (or symlinked) for the corrected KL function; SHA must match the pilot's SHA `dccb577efd050d9323b38a5553698ad7c4cb5e3cd1bc359df5e633b0d31700b9`
- `.forge_private/h6_dev/src/h6/obs_shuffled.py`, `markov.py` — re-imported, byte-identical to the H₆-γ frozen versions

Tests under `.forge_private/h7_dev/tests/`:

1. `test_sigma_runner_one_seed_smoke.py` — runs one seed, asserts CSV row has all 20 columns, all numeric values are finite, `KL_R_M_corr > 0`, `K_R_nonempty ≤ 64`.
2. `test_double_reporting_disagreement.py` — synthetic counts with `K_S − K_R` large enough that `δ_σ_corr` and `δ_σ_naive` disagree on the d ≥ 0.5 threshold; assert verdict = `H7_SIGMA_INCONCLUSIVE`.
3. `test_clip_events_recorded.py` — synthetic out-of-range pressure, assert clip count > 0 in CSV.
4. `test_kl_byte_match_pilot.py` — runs `kl_corrected` from h7.kl on a fixed input; asserts byte-identical output to the value computed by the pilot's `pilot_kl.py` on the same input (proves no drift across the symlink/re-import).

All four tests must pass before SHA freeze. Test failures invalidate the freeze.

---

## 9. NOT decided in v2 (legitimately deferred)

- The release vehicle name (`v0.3.0-h7-sigma-{verdict}`). Set by ADR-029 after the main run.
- The Docker image fingerprint for the H₇-σ run. **Decision:** reuse `cae-research-kit:0.1.0` (E₀ fingerprint `406ce26e…7e5f`); no new dependencies introduced by the H₇-σ pipeline. If this changes during implementation (e.g. a numpy version bump), a new image must be built and frozen before the main run.

---

## 10. Process gate (binding sequence from v2 freeze)

1. ✅ Pilot complete, summary frozen with SHA.
2. **Now (this commit):** v2 frozen. ADR-027 (statistical chain) drafted in parallel.
3. Implement `h7_dev/src/h7/sigma_runner.py` + `sigma_adjudicator.py`. Implement 4 tests of §8. All green.
4. Compute SHA-256 of: ADR-026 v2, ADR-027, sigma_runner.py, sigma_adjudicator.py, h7/kl symlink target, h6/obs_shuffled.py, h6/markov.py. Record in a `H7_SIGMA_FREEZE_MANIFEST.json` sibling file.
5. Run on [1400, 1429]. Generate `h7_sigma_run_results.csv` and `h7_sigma_verdict.json`.
6. Read verdict. Write ADR-029 (release decision, analogue of ADR-025).
7. Public release v0.3.0-h7-σ-{verdict}.

End of v2.
