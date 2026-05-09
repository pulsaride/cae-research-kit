# ADR-023 — Pre-registration of H₆-β (phase-space trajectory pivot)

**Status:** PROPOSED — frozen at SHA-256 record time
**Date:** 2026-05-09
**Relation to ADR-022:** does NOT modify ADR-022 (which is frozen). ADR-023
selects the operational definition of the constraint field for H6-β.
**Confidentiality:** PRIVATE — `.forge_private/` only.

---

## 1. Context

ADR-022 §4.4 specifies "constraint field (U, F, R, P)" but does not bind whether
these are spatial fields on the E₀ grid or scalar global aggregates over time.

H₅ (frozen v0.1.0) defines U, F, R, P as **scalar global aggregates** computed
once per tick over the whole environment. There is no spatial field U(x, y, t)
in the H₅ instrument; only the time series U(t), F(t), R(t), P(t).

H6-α was implemented on **synthetic spatial fields** (a Gaussian bump on a
16×16 grid) as a stand-in. The 8/8 ADT-H6 tests passed (ripser==0.6.10 +
persim==0.3.5), but the metric was never connected to the real H₅ instrument.

Two options were available for H6-β:

- **A. ADR-022.bis** — extend ADR-022 to define U, F, R, P as spatial fields
  on the E₀ grid. Requires modifying `src/env/e0.py` (forbidden by ADR-022 §4.1)
  or duplicating it. Adds a new component (spatial sampling) to the constraint
  field. Forbidden by ADR-022 §8.
- **B. ADR-023 (this document)** — reuse the H₅ scalar instrument as-is and
  redefine the H₆ object of measurement as the **4-D trajectory in phase space
  (U, F, R, P)** over time. No modification to E₀. No new constraint
  components. Strictly inside ADR-022 §8 anti-patterns.

Option B is selected. This is a refinement of ADR-022 §4.4 within its existing
scope, not an extension.

## 2. The redefinition

| ADR-022 §4.4 (abstract) | ADR-023 (concrete) |
|---|---|
| "constraint field (U, F, R, P)" | the 4-D trajectory $\mathbf{x}(t) = (U_t, F_t, R_t, P_t) \in \mathbb{R}^4$, $t \in [0, T)$ |
| "sublevel-set persistence diagram on each component" | Vietoris–Rips persistence diagram on the 4-D point cloud $\{\mathbf{x}(t)\}_{t=0}^{T-1}$ |
| "bottleneck distance per component → average" | bottleneck distance per homology dimension → average |

Composite metric:
$$\delta = \frac{1}{D+1} \sum_{k=0}^{D} d_B\big(\mathrm{PD}_k(\Omega), \mathrm{PD}_k(M_0)\big)$$
with $D = 1$ (homology dim 0 and 1, per ADR-022 §4.4).

## 3. What is preserved from ADR-022

All of §3 (formal H₆ statement), §4.2 (Ω = Agent A from v0.1.0), §4.3 (Markov
null with α=1 Laplace smoothing), §4.6 (determinism), §6 (success criteria),
§7 (failure → publication), §8 (forbidden anti-patterns), §10 (freeze clause).

## 4. What ADR-023 binds

### 4.1 Phase-space construction

For each seed $s$:
1. Run Agent A on E₀ for $T = 256$ ticks (ADR-022 §4.2 + harness default).
2. Record per-tick scalars $U_t, F_t, R_t, P_t$ as already exposed by the H₅
   `RunResult` API in `src/experiments/__init__.py`.
3. Stack into matrix $\mathbf{X}_\Omega \in \mathbb{R}^{T \times 4}$.
4. Z-score normalize **each component independently** using the mean/std of
   the run itself: $\tilde{x}_{t,k} = (x_{t,k} - \mu_k) / \sigma_k$.
   Justification: removes scale heterogeneity between U/F/R/P (P is much larger
   than U,F,R per the H₅ verdict), while preserving topology by Φ₂-equivariance
   (ADR-022 §5 ADT-H6-05).
5. The action sequence $\{a_t\}$ used to fit the Markov null is the per-tick
   discrete action emitted by Agent A, recorded alongside the scalars.

### 4.2 Null trajectory

For the same seed:
1. Fit $\hat{M}$ on $\{a_t\}$ (Laplace α=1, ADR-022 §4.3).
2. Sample $\{a^0_t\}$ from $\hat{M}$.
3. Replay $\{a^0_t\}$ on a fresh E₀ with **the same seed** as step 1 of §4.1.
4. Record null scalars → $\mathbf{X}_{M_0} \in \mathbb{R}^{T \times 4}$.
5. Z-score normalize using the **same** $\mu_k, \sigma_k$ as the real run
   (so that the Markov null is compared on the same axis basis).

### 4.3 Persistence diagram

- `ripser(X, maxdim=1)` on the (T, 4) point cloud.
- No subsampling. No distance threshold (let ripser default).
- `persim.bottleneck` on finite portion of each dimension's PD; mean across
  dim 0 and dim 1.

### 4.4 Library binding

- `ripser==0.6.10` (binding from H6-α, retained).
- `persim==0.3.5` (binding from H6-α, retained).
- No `gudhi`. The choice is final.

### 4.5 Seed range

- $n = 30$ disjoint seeds, range `[1200, 1229]`.
- Disjoint from H₅ `[1000, 1029]` ∪ {99}, H6-α synthetic `[1100, 1129]`.
- Disjoint-seed guard mandatory in `src/experiments/h6/__init__.py` (public)
  AND in any private staging code (`.forge_private/h6_dev/src/h6/harness.py`).

### 4.6 Decision rule (unchanged from ADR-022 §3)

- $d \geq 0.5$ AND Wilcoxon $p < 0.01$ ⇒ `H6_SIGNATURE_DETECTED`.
- $d < 0.2$ ⇒ `H6_REJECTED`.
- otherwise ⇒ `H6_INCONCLUSIVE`.

## 5. ADT-H6-β (phase-space adaptation, mandatory before harness)

ADT-H6-α (synthetic) remain GREEN as the regression suite for the metric
itself. The phase-space pipeline gets its own RED→GREEN tier:

| ADT | What it tries to break | Pass condition |
|---|---|---|
| ADT-H6β-01 | Self-replay of the phase trajectory | $\delta(\mathbf{X}, \mathbf{X}) < 0.05$ |
| ADT-H6β-02 | Permuting tick indices destroys $\delta$ | post-shuffle $\delta < 0.2$ |
| ADT-H6β-03 | Z-score invariance: scaling each column by $k>0$ does not change $\delta$ by more than 0.05 | required |
| ADT-H6β-04 | Synthetic constant-velocity trajectory $\mathbf{x}(t) = t \cdot \mathbf{v}$ has $\delta < 0.2$ vs its Markov null on a synthetic action sequence | required |
| ADT-H6β-05 | Synthetic chaotic trajectory (e.g. Lorenz subsampled) has $\delta > 0$ vs uniform iid null (positive control: a known non-Markov system MUST be detected) | required |

**If any ADT-H6β fails, H₆ verdict is `H6_INCONCLUSIVE` regardless of the
main test outcome.** Aligned with ADR-022 §5.

## 6. Implementation plan (informational, not pre-registered)

| Step | Deliverable | Gate |
|---|---|---|
| H6-β.1 | `.forge_private/h6_dev/src/h6/phase.py` with `phase_trajectory`, `phase_delta` | RED tests first |
| H6-β.2 | 5 ADT-H6β tests RED → GREEN | mandatory before harness |
| H6-β.3 | `.forge_private/h6_dev/src/h6/harness.py` running A on E₀ | one optimizer only |
| H6-β.4 | n=30 main run, `h6_verdict.json` | one shot |
| H6-β.5 | Public release (if DETECTED) or null release (if REJECTED) | ADR-022 §10 |

## 7. Anti-patterns (in addition to ADR-022 §8)

- Tweaking the z-score normalization per-component to "bring components into
  the same regime" (e.g. log-scale on P only). The normalization is fixed at
  per-run mean/std as defined in §4.1.4.
- Changing $T$ from 256 mid-experiment.
- Re-running with a different seed range "to compare". H6-β is one shot.
- Adding a second optimizer Ω' before H6-β.4 verdict is recorded (deferred to
  ADR-024 per ADR-022 §6.3).

## 8. Decision

This pre-registration is **frozen** at the moment its SHA-256 is recorded in
`.forge_private/ADR-023.sha256`. Any change requires ADR-023.bis with explicit
justification and reset of seed plans.

```
sha256(this file) → record before first H6-β commit
```

---

*Private pre-registration. Do not publish until experiment is executed.*
*Authority: doctrine §10 (CAE_Vision_Position.md), pivot rationale in
ADR-022 §1–§3, library binding from H6-α (ADT-H6-01..07 GREEN, 8/8).*
