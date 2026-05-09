# ADR-027 — H₇-σ Statistical Chain Inheritance

**Title:** H₇-σ Statistical Chain — Inheritance from ADR-023.ter (paired Wilcoxon "greater") and ADR-024 (α = 0.005).
**Status:** **FROZEN** in parallel with ADR-026 v2.
**Predecessors:** ADR-022, ADR-023.ter (paired Wilcoxon spec), ADR-024 (α uniformity).
**Sibling:** ADR-026 v2.

---

## 1. Purpose

ADR-026 v2 §2 references "paired Wilcoxon greater per ADR-023.ter" and "α = 0.005 to match ADR-024 γ.1". This ADR makes the inheritance **explicit** and **closed**, so that no statistical degree of freedom remains open at main-run time.

---

## 2. Inherited from ADR-023.ter (verbatim)

- Test family: **paired** Wilcoxon signed-rank.
- Implementation: `scipy.stats.wilcoxon`.
- `alternative="greater"`.
- `zero_method="wilcox"` (Wilcoxon's original treatment of zero differences: drop them, then rank; the count `n` reported in the verdict is the *post-drop* count).
- Reported statistics: the test statistic `W`, the p-value `p`.
- The p-value reported is the **exact** p-value when n_post-drop ≤ 25; the **asymptotic normal approximation** otherwise. `mode="auto"` left at scipy default — the cut-off is internal to scipy and treated as a constant of that library version.

The scipy version is pinned by the docker image (`scipy 1.12.0` per `.venv-h6` lock), and the version is recorded in the verdict JSON under `code_sha256.scipy_version`.

---

## 3. Inherited from ADR-024 (verbatim)

- Significance level: **α = 0.005** (one-sided).
- The α was set by the Bureau des Standards in ADR-024 γ.1 and is held *uniform* across all H₆ and H₇ probes for inter-comparability of strength of evidence. No probe-specific α adjustment.

---

## 4. Effect-size estimator: Cohen's d on paired differences

For the n paired δ_σ values:

`d = mean(δ_σ) / std(δ_σ, ddof=1)`

where `std` is the sample standard deviation with Bessel's correction. This is the form already used by H₆-γ adjudication (`adjudicator_gamma.py`, ADR-024 §5).

Threshold for `H7_SIGMA_STRUCTURAL_COUPLING`: **d ≥ 0.5** (per ADR-026 v2 §2). Threshold for `H7_SIGMA_FEEDBACK_ONLY` (FEEDBACK saturation declaration): **|d| < 0.2**. The interval `0.2 ≤ |d| < 0.5` ⇒ `H7_SIGMA_INCONCLUSIVE`. The order of decision (p first, then d, then sign) is fixed by the verdict table of ADR-026 v2 §2.

---

## 5. Multiple-test policy

The H₇-σ probe is a **single** statistical test. Therefore:

- No Bonferroni or Holm adjustment.
- No FDR control.
- The two reported test results (primary on `δ_σ_corr`, transparency on `δ_σ_naive`) are **not** independent tests of the same hypothesis: the transparency block is a robustness diagnostic with a pre-registered "disagreement ⇒ INCONCLUSIVE" rule (ADR-026 v2 §2 double-reporting clause). This rule is a *conservativeness mechanism*, not a multiple-test correction.

---

## 6. Tie / zero handling

`zero_method="wilcox"` drops exact zero differences from the ranking. With pressure values stored at IEEE-754 double precision and KL_corr involving multi-million-bin sums, exact zeros in δ_σ are floating-point pathologies, not substantive ties. If `n_post-drop < n` for any reason, the verdict JSON records `n_dropped > 0` and the run is flagged for manual review (but not automatically invalidated). If `n_post-drop < 20`, the verdict is `H7_SIGMA_INCONCLUSIVE` regardless of p (the asymptotic regime is no longer reliable; the exact-test branch of scipy was needed but the count is too low for a meaningful exact rank distribution at α = 0.005).

---

## 7. Determinism

- Seed pool [1400, 1429], n = 30, fixed.
- Each seed s feeds three deterministic policies on the same E₀(s).
- `numpy.random.default_rng(s)` is the *only* RNG used by sample_markov; `BLAKE2b("obs_shuffle::s")` seeds ObsShuffledAgent (ADR-024 §4); E₀ is a deterministic function of (s, n_modes, drift_rate, …).
- The verdict JSON records the bit-identical scipy version and numpy version.

---

## 8. Failure modes and pre-committed responses

| Failure | Verdict | Recovery |
|---|---|---|
| Any seed produces non-finite KL | run abort | requires post-mortem ADR-026.bis (clip-event diagnosis) |
| `n_dropped > 0` (zero δ_σ) | run continues, flag in JSON | manual review, no automatic reverdict |
| `n_post-drop < 20` | `H7_SIGMA_INCONCLUSIVE` | ADR-026.bis (sample-size diagnosis) |
| Verdicts disagree between corr and naive | `H7_SIGMA_INCONCLUSIVE` | no recovery — bias correction is decisive ⇒ result not robust |
| `d < 0` AND `p < 0.005` (greater test rejected the wrong way) | `H7_SIGMA_INVERTED` | mandatory ADR-026.ter — scientific error, methodological audit before any further H₇ work |
| `median(K_R − K_S) > 0` on main pool (sign flips vs pilot) | result remains the verdict computed above, but JSON `transparency.notes` records the flip | informs ADR-029 release decision (no automatic invalidation, but this would be a significant pilot-vs-main divergence to discuss) |

---

## 9. SHA-freeze obligation

This ADR file's SHA-256 is computed at the freeze of ADR-026 v2 and recorded in `H7_SIGMA_FREEZE_MANIFEST.json`. Any byte change to this file after that point invalidates the chain and requires the ADR-026.bis remediation path.
