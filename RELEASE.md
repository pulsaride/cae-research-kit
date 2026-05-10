# Release v0.6.0-h7-κ-boundary

**Title:** *H₇-κ Boundary of Validity: A Six-Octave Robust Envelope Around D=0.080, a Sharp Rupture at D=0.640 Attributable to E₁ Saturation, and a Pre-Registered Override That Fires on Sampling Noise*
**Date:** 2026-05-10
**Scientific status (formal):** `KAPPA_INCONCLUSIVE` — the pre-registered ADR-034 §5.4 override fires on a single criterion: concordance of Cohen $d$ at the reference grid-point $D=0.080$ between the v0.6.0 sweep pool $[4000, 4029]$ and the v0.5.0 reference pool $[2000, 2029]$ measured at $3.85\%$, above the $1\%$ threshold pre-registered in ADR-034 §3.4 (line 130). The verdict is published as written, without retroactive revision of the protocol.
**Operational status:** the κ pipeline is certified robust on a six-octave diffusion envelope $D \in [0.005, 0.320]$ (six grid-points pass with $n_\text{pos} \geq 29/30$, $p < 1.9 \times 10^{-9}$, Cohen $d \geq 2.76$, $0$ clip events). A sharp rupture is observed at $D = 0.640$ ($n_\text{pos} = 14/30$, $d = 0.52$); post-hoc forensics attribute it to thermodynamic saturation of environment $E_1$ (full $P \in \{0, 1\}$ collapse, $K_R = 2$ for half the seeds), not to a failure of the H₇-κ instrument.
**Predecessor:** [v0.5.0-h7-κ-transfers](#release-v050-h7-κ-transfers) (κ on E₁ at $D=0.080$; v0.6.0 maps the validity envelope around that single point).
**DOI (v0.6.0):** [10.5281/zenodo.20112259](https://doi.org/10.5281/zenodo.20112259) — concept: [10.5281/zenodo.20091625](https://doi.org/10.5281/zenodo.20091625).
**Authority chain:** ADR-026 v2.1 → ADR-027 → ADR-030 → ADR-031 / ADR-031.bis → ADR-032 → ADR-033 (audit gate, ACCEPTED 2026-05-09) → ADR-034 (boundary sweep, ACCEPTED 2026-05-10) → ADR-035 (seed-paired replication, ACCEPTED 2026-05-10) → this release.

> **Note sur le Verdict v0.6.0 :** Bien que le verdict formel soit `INCONCLUSIVE` suite à l'application stricte de l'override §5.4 de l'ADR-034, la réplication seed-paired (ADR-035) confirme une identité bit-à-bit du moteur avec la v0.5.0.
>
> **Garantie Opérationnelle :** Le système est certifié **Robuste** pour tout environnement de diffusion $D \in [0.005, 0.320]$. La limite de rupture est identifiée à $D=0.640$ par saturation thermodynamique de l'environnement $E_1$.

---

## 1. Abstract (no marketing)

v0.5.0 published a single point of κ portability on E₁: at the calibrated diffusion coefficient $D = 0.080$ (ADR-032), the one-tick-memory signature reverses the H₇-σ inverted coupling with Cohen $d = +3.09$ at $p = 9.3 \times 10^{-10}$ on the fresh, pre-registered pool $[2000, 2029]$. v0.5.0 did *not* claim that this result generalised to any other E₁ regime. ADR-034 (ACCEPTED 2026-05-10) pre-registered a 7-point geometric diffusion grid $\{0.005, 0.020, 0.040, 0.080, 0.160, 0.320, 0.640\}$ on a fresh pool $[4000, 4029]$ — 210 runs total — to map the validity envelope around v0.5.0's single calibration point.

The sweep was executed under Option β (ADR-034 §4.2): a new entry point `src/experiments/diffusion_sweep.py` re-uses the v0.5.0 runner `src/experiments/portability_draw.py` *unchanged* (SHA-256 = `3c4a7df4…716aa79d`, identical to the `audit-passed-v1` tag artefact). Before the sweep, the audit gate of ADR-033 was re-run on the E₀ reference pool $[1500, 1529]$ to confirm the HEAD engine still reproduces v0.4.0 byte-for-byte; the candidate CSV is byte-identical to the `audit-passed-v1` artefact (max $|\Delta| \leq 4.5 \times 10^{-11}$, 0 strict integer mismatches).

| $D$ | $n_\text{pos}/n$ | $p_\text{greater (corr)}$ | Cohen $d_\text{corr}$ | clip | grid-point pass |
|---|---:|---:|---:|---:|:---:|
| 0.005 | 30/30 | $9.3 \times 10^{-10}$ | $+2.876$ | 0 | ✅ |
| 0.020 | 30/30 | $9.3 \times 10^{-10}$ | $+2.772$ | 0 | ✅ |
| 0.040 | 29/30 | $1.9 \times 10^{-9}$  | $+2.764$ | 0 | ✅ |
| 0.080 | 30/30 | $9.3 \times 10^{-10}$ | $+2.972$ | 0 | ✅ |
| 0.160 | 30/30 | $9.3 \times 10^{-10}$ | $+3.014$ | 0 | ✅ |
| 0.320 | 30/30 | $9.3 \times 10^{-10}$ | $+2.924$ | 0 | ✅ |
| 0.640 | 14/30 | $3.18 \times 10^{-3}$ | $+0.520$ | 0 | ❌ |

Six contiguous grid-points pass; the seventh (the upper-most octave $D=0.640$) fails the n-positive criterion ($14/30 < 25/30$). On the surface this is a textbook `KAPPA_BAND_LIMITED (upper_open)` envelope, defended by the pre-registered ROBUST/BAND_LIMITED ladder of ADR-034 §3.4. **However**, ADR-034 §5.4 also pre-registered an unconditional override: any disagreement between the v0.6.0 sweep and the v0.5.0 reference at $D=0.080$ greater than $1\%$ on Cohen $d$ forces the verdict to `KAPPA_INCONCLUSIVE`, regardless of how clean the rest of the sweep looks. The measured concordance is

$$\frac{|d_\text{v0.6.0}^{D=0.080} - d_\text{v0.5.0}|}{d_\text{v0.5.0}} = \frac{|2.9718 - 3.0906|}{3.0906} = 3.85\% > 1\%,$$

so the override fires. The release publishes `KAPPA_INCONCLUSIVE` as written.

ADR-035 (ACCEPTED 2026-05-10) pre-registered a single diagnostic test before the verdict was finalised: re-run the v0.5.0 portability draw on the v0.5.0 pool $[2000, 2029]$ at $D=0.080$ with the HEAD engine, and compare byte-for-byte against `research/h7_kappa_portability.csv` under ADR-033 §4 tolerances (atol $= 10^{-9}$, rtol $= 0$, `==` strict on integer columns). Result: **PASS, with `max |Δ| = 0.0` across all float columns** — the candidate CSV (`research/h7_kappa_replication_v060.csv`) is byte-for-byte identical to the v0.5.0 reference (SHA-256 match `b532d938…c02829ee`). The HEAD engine is therefore proven *bit-identical* to the v0.5.0 runner on the reference grid-point. The $3.85\%$ inter-pool gap that fired the override is sampling noise between two disjoint $n=30$ pools — approximately $0.46\sigma$ — not engine drift.

In the vocabulary of ADR-035 §5.1, the formal verdict `KAPPA_INCONCLUSIVE` remains the official scientific status of v0.6.0 (the protocol is honored verbatim; no retroactive revision of ADR-034 is performed). In parallel, the operational reading `KAPPA_BAND_LIMITED (upper_open)` on $D \in [0.005, 0.320]$ is published as a defended secondary statement, with full traceability to the pre-registered override that prevented it from becoming the formal verdict. The fracture at $D=0.640$ is documented as a property of the test bed (E₁ saturates), not of the instrument.

This is what scientific honesty looks like when a pre-registered override fires on a sampling-noise gap: you publish the verdict the protocol produced, you publish the diagnostic that explains why, and you let the reader see both.

## 2. What this release ships

| Path | Description | SHA-256 |
|---|---|---|
| `research/MANIFEST.v0.6.0.yaml` | full release manifest (audit re-confirmation + sweep + replication + envelope) | `61188671…44470` |
| `research/h7_kappa_audit_HEAD_pre_v060.csv` | audit re-confirmation candidate on $[1500,1529]$ (byte-identical to `audit-passed-v1`) | `4a6815c2…61bd231b0` |
| `research/h7_kappa_audit_HEAD_pre_v060.report.txt` | audit verdict (PASS, max $\|\Delta\| \leq 4.5 \times 10^{-11}$) | `386d993e…44fed65a` |
| `research/h7_kappa_boundary_sweep.csv` | per-(D,seed) sweep table (210 rows × 30 cols) | `997b8e85…cfc677` |
| `research/h7_kappa_boundary_verdict.json` | adjudicator output — `KAPPA_INCONCLUSIVE` | `95512b36…6290c0` |
| `research/h7_kappa_replication_v060.csv` | ADR-035 replication on $[2000,2029]$ at $D=0.080$ (byte-for-byte identical to v0.5.0 portability CSV) | `b532d938…c02829ee` |
| `research/h7_kappa_replication_v060.report.txt` | ADR-035 audit verdict (PASS, $\max \|\Delta\| = 0.0$) | `bf5e8a46…f64e7` |
| `src/experiments/diffusion_sweep.py` | new sweep entry point (Option β: imports `portability_draw` by reference, no fork) | `3d3f1b7f…6908` |
| `src/analysis/verdict_v06.py` | v0.6.0 adjudicator (frozen before sweep) | `f99de4ff…879` |
| `tests/adt/test_diffusion_sweep.py` | 7 ADT (sweep entry point) | `c0ecd819…d5e1` |
| `docs/adr/ADR-034-h7-kappa-boundary-of-validity-diffusion-sweep.md` | sweep pre-registration, ACCEPTED 2026-05-10 | `fbc4f673…b0a2` |
| `docs/adr/ADR-035-h7-kappa-replication-v050-seed-paired.md` | replication pre-registration, ACCEPTED 2026-05-10 | `84ba0176…3f3` |

All other artefacts (`portability_draw.py`, `audit_compare.py`, `sigma_chain.py`, the four agents, the v0.5.0 ADT suite, ADRs 026–033) are inherited bit-identical from v0.5.0; their SHA-256s are reproduced for completeness in `research/MANIFEST.v0.6.0.yaml`.

## 3. Reproducibility

Same dev environment as v0.5.0: Python 3.12.3, numpy 1.26.4, scipy 1.12.0, pytest 8.1.1.

```bash
# 1. Audit re-confirmation on E₀ reference pool [1500-1529]
python -m src.experiments.portability_draw --pool audit \
  --i-have-read-adr-033 \
  --output research/h7_kappa_audit_HEAD_pre_v060.csv
python -m src.analysis.audit_compare \
  --reference research/h7_kappa_run_results.csv \
  --candidate research/h7_kappa_audit_HEAD_pre_v060.csv \
  --report-output research/h7_kappa_audit_HEAD_pre_v060.report.txt

# 2. Boundary sweep on pool [4000-4029] across the 7-point geometric diffusion grid
python -m src.experiments.diffusion_sweep \
  --i-have-read-adr-034 \
  --output research/h7_kappa_boundary_sweep.csv

# 3. Verdict v0.6.0
python -m src.analysis.verdict_v06 \
  --sweep research/h7_kappa_boundary_sweep.csv \
  --reference-cohen-d-corr  3.090641237972993 \
  --reference-cohen-d-naive 3.090653026205383 \
  --output research/h7_kappa_boundary_verdict.json

# 4. ADR-035 seed-paired replication on v0.5.0 pool [2000-2029] at D=0.080
python -m src.experiments.portability_draw --pool portability \
  --i-have-read-adr-033 \
  --output research/h7_kappa_replication_v060.csv
python -m src.analysis.audit_compare \
  --reference research/h7_kappa_portability.csv \
  --candidate research/h7_kappa_replication_v060.csv \
  --report-output research/h7_kappa_replication_v060.report.txt
```

Sweep total runtime on the H7 dev environment: $\approx 41\,\text{min}\,33\,\text{s}$ (single process, 210 runs). Replication runtime: $\approx 9\,\text{min}\,52\,\text{s}$ (30 runs).

## 4. What v0.6.0 does NOT claim

- v0.6.0 does **not** rescue the formal verdict to `KAPPA_BAND_LIMITED`. The ADR-034 §5.4 override fired and is honored. The official scientific status of this release is `KAPPA_INCONCLUSIVE`.
- v0.6.0 does **not** claim the κ signature transfers to *any* diffusion regime. The defended operational envelope is $D \in [0.005, 0.320]$. Behaviour at $D \geq 0.640$ is documented as a fracture of the test bed under hyper-diffusion, not a generalisation of κ.
- v0.6.0 does **not** open new H₈ territory. ADR-031.bis remains in force: B-first remains the doctrine, no architectural pivot is warranted by these data.
- v0.6.0 does **not** revise any earlier verdict. v0.5.0's `KAPPA_TRANSFERS` at $D=0.080$ stands; v0.4.0's `KAPPA_REVERSES` on E₀ stands; the H₆ falsification stands.

---

# Release v0.5.0-h7-κ-transfers

**Title:** *H₇-κ Transfers: The One-Tick-Memory Signature Survives a Calibrated Change of Environment, Under a Publicly Audited Runner*
**Date:** 2026-05-10
**Scientific status:** `KAPPA_TRANSFERS` — the κ signature published in v0.4.0 (one tick of local-pressure memory breaks the σ inversion on E₀) survives an out-of-distribution change to a calibrated diffusive environment E₁ on a fresh, pre-registered seed pool [2000-2029]. Both branches of the pre-registered double reporting (Miller-Madow corrected primary, plug-in transparency) agree at the same p-value with `verdicts_agree = true`.
**Operational status:** the κ pipeline is now end-to-end publicly executable. The runner is a public reimplementation gated by a bit-level audit against the v0.4.0 reference seeds [1500-1529] under fixed tolerances (atol = 1e-9, rtol = 0, `==` strict on integer columns). ADR-033 ACCEPTED on 2026-05-09; tag `audit-passed-v1` placed before the portability tirage.
**Predecessor:** [v0.4.0-h7-κ-reverses](#release-v040-h7-κ-reverses) (κ on E₀; v0.5.0 tests whether the same signature transfers to a calibrated E₁).
**DOI (v0.5.0):** [10.5281/zenodo.20107855](https://doi.org/10.5281/zenodo.20107855) — concept: [10.5281/zenodo.20091625](https://doi.org/10.5281/zenodo.20091625).

---

## 1. Abstract (no marketing)

H₇-κ (v0.4.0) published a paradox resolution on E₀: a single tick of
memory on the previous local-pressure observation (M_κ, zero parameters,
zero learning) reversed the H₇-σ inverted-coupling signature with
$d = +2.66$ at $p = 9.3 \times 10^{-10}$ on n = 30 seeds [1500-1529].
The closing section of v0.4.0 explicitly listed *cross-environment
portability* as out of scope and requiring its own pre-registration.

ADR-031 (post-κ trilemma) ranked branch B (portability E₁) first among
the three legitimate continuations. ADR-031.bis clarified the binding
conditions. ADR-032 pre-registered H₇-κ portability on E₁ under the same
statistical chain as ADR-027 (paired Wilcoxon, both alternatives,
$\alpha = 0.005$, $d \geq 0.5$, Miller-Madow + plug-in double reporting),
on a fresh seed pool [2000-2029] never used in any prior tirage, with
M_κ inherited *bit-identical* from ADR-030.

Two independent guarantees were required *before* the portability tirage
was admissible:

1. **Audit gate (ADR-033).** The public reimplementation of the κ
   runner (`src/experiments/portability_draw.py`) had to reproduce the
   v0.4.0 per-seed CSV `research/h7_kappa_run_results.csv` on the
   reference pool [1500-1529] under fixed tolerances. Iter1 failed
   strictly on the obs-shuffled witness branch S; R, M_κ and M were
   already bit-identical. The investigation prescribed in ADR-033 §6.2
   #5 (BLAKE2b convention) was executed by exhaustive S-only brute
   force on witness seed 1500 (90 combinations: key format ×
   digest_size × byteorder). A unique solution reproduced
   `KL_S_M_corr` to $3.0 \times 10^{-11}$:
   `key = "obs_shuffle::{seed}"`, `digest_size = 8`, `byteorder = "big"`.
   Single-bit fix in `src/agents/obs_shuffled_agent.py` (commit
   `c15f313`). Iter2 PASS: max $|\Delta|$ across all 14 float columns
   $\leq 4.5 \times 10^{-11}$; 0 strict mismatches across all 15
   integer columns. Tag `audit-passed-v1` placed.
2. **Pool freshness.** The portability pool [2000-2029] was reserved
   in ADR-032 and remained frozen until ADR-033 reached `ACCEPTED`. No
   pre-tirage observation of E₁ pressure on these seeds was permitted.

The portability tirage was then run on E₁ under
`--pool portability --i-have-read-adr-033`. Result:

| Metric | Corrected (primary) | Naive (transparency) |
|---|---|---|
| Wilcoxon $p_\text{greater}$ | $9.31 \times 10^{-10}$ | $9.31 \times 10^{-10}$ |
| Cohen $d$ | $+3.0906$ | $+3.0907$ |
| $n_\text{post-drop}$ | 30 / 30 | 30 / 30 |
| seeds with $\Delta_s > 0$ | 30 / 30 | 30 / 30 |
| total clip events | 0 | 0 |

`verdicts_agree = true`. `inconclusive_reasons = []`. Verdict:
**`KAPPA_TRANSFERS`**.

The diagnostic numbers replicate the qualitative pattern of v0.4.0
under the new medium: median $\delta_\sigma^R_\text{corr} = -0.18$
(R remains on the σ-inverted side under E₁) versus median
$\delta_\sigma^{M_\kappa}_\text{corr} = +0.40$ (M_κ still crosses to the
structural side); the action-repertoire diagnostic shifts from median
$K_R = 35$ to $K_{M_\kappa} = 57$, a +22-cell recovery — of the same
order as the +23 reported on E₀ in v0.4.0. The κ mechanism — local
temporal differentiation — is therefore not an artefact of E₀'s
specific pressure dynamics: it transfers across a calibrated change of
medium with no loss of effect size.

## 2. What this release ships

| Path | Description | SHA-256 |
|---|---|---|
| `research/MANIFEST.v0.5.0.yaml` | full release manifest (audit gate + portability) | `2232e037…ca13b6ee` |
| `research/h7_kappa_portability.csv` | per-seed E₁ tirage (30 rows × 29 cols) | `b532d938…c02829ee` |
| `research/h7_kappa_portability_verdict.json` | adjudicator output | `1b7f4ee0…58218dc3d8` |
| `research/h7_kappa_audit_v04_iter2.csv` | iter2 audit candidate (30 rows × 29 cols) | `4a6815c2…61bd231b0` |
| `research/h7_kappa_audit_v04_iter2.report.txt` | audit verdict (PASS, max $\|\Delta\| = 4.5 \times 10^{-11}$) | `386d993e…4fed65a` |
| `src/experiments/portability_draw.py` | public κ runner (E₀ audit + E₁ portability) | `3c4a7df4…716aa79d` |
| `src/agents/obs_shuffled_agent.py` | obs-shuffled witness (BLAKE2b byteorder=big per §11.2) | `c5e77295…34f37007` |
| `src/agents/adaptive_agent.py` | R policy | `19042669…07176d3` |
| `src/agents/memory1_agent.py` | M_κ (bit-identical to v0.4.0) | `2684b171…e727c7870` |
| `src/analysis/sigma_chain.py` | KL chain, histograms, Markov fit, Wilcoxon | `414e1463…05d49084` |
| `src/analysis/audit_compare.py` | bit-level audit comparator (CLI + dataclass) | `a55e3df1…17fac681` |
| `src/analysis/verdict_v05.py` | v0.5.0 adjudicator (frozen before tirage) | `389528eb…34a36be` |
| `tests/adt/test_portability_draw.py` | 12 ADT (runner) | `f25c1c07…342e8500abc59b4` |
| `tests/adt/test_audit_compare.py` | 12 ADT (audit gate) | `a27cb107…182b6cdca2f644` |
| `tests/adt/test_sigma_chain.py` | 21 ADT (KL / Markov / histograms) | `5a599fad…ccefa943570353b` |
| `tests/adt/test_obs_shuffled_agent.py` | 15 ADT (witness; assertion updated to byteorder=big) | `91653b03…0c8fc50ce` |
| `tests/adt/test_verdict_v05.py` | 13 ADT (adjudicator) | `5523cd4d…3a3189c89e5` |
| `docs/adr/ADR-031-post-kappa-trilemma-b-first.md` | branch B selection | `fb1a52ea…57648e841` |
| `docs/adr/ADR-031.bis-supersede-section-5-3.md` | ADR-031 §5.3 supersession | `f4628531…fc920f3f9` |
| `docs/adr/ADR-032-h7-kappa-portability-e1.md` | portability E₁ pre-registration | `4e87aa4e…7567f4e749` |
| `docs/adr/ADR-033-audit-gate-public-runner.md` | audit gate, ACCEPTED 2026-05-09 | `938aa792…994d3f2f` |

**Now public (no longer behind the private freeze chain):** the entire
κ pipeline. Unlike v0.4.0, v0.5.0 ships a runner that an auditor can
execute end-to-end against the v0.4.0 CSV with a single command and
verify the bit-level reproduction (max $|\Delta| \leq 4.5 \times 10^{-11}$
on the worst float column, 0 mismatches on all integer columns) before
the portability claim is even considered. The private v0.4.0 runner
(`.forge_private/h7_dev/src/h7/kappa_runner.py`) is no longer required
to reproduce the κ statistical claim.

## 3. Where the value is

This release ships three independent guarantees stacked on top of each
other:

- **Portability of the signature.** The v0.4.0 κ effect is not an
  E₀-specific artefact. Under a calibrated diffusive E₁, on a fresh
  pool [2000-2029] never observed before the tirage, the same paired
  Wilcoxon test returns $p_\text{greater} = 9.3 \times 10^{-10}$ with
  $d = +3.09$ on both reporting branches simultaneously. Thirty
  positive seeds out of thirty. The mechanism — local temporal
  differentiation — survives the change of medium with the effect size
  *increasing* slightly rather than decaying.
- **A public bit-level audit.** The runner that produced
  `h7_kappa_portability.csv` is the same runner that, on the v0.4.0
  reference pool, reproduces `h7_kappa_run_results.csv` to
  $4.5 \times 10^{-11}$ on the worst float column and exactly on all
  fifteen integer columns. The audit was a precondition for the
  portability tirage being admissible, not a post-hoc justification.
  Tolerances were frozen in ADR-033 §4 *before* iter1 was executed and
  were not relaxed when iter1 failed.
- **A reproducible failure-then-fix trail.** Iter1 failed strictly on
  the obs-shuffled witness branch. The diagnostic was published
  (commit `2719191`), the investigation was bounded by ADR-033 §6.2
  with the candidate hypotheses ordered by prior probability, and the
  fix was a single-bit byteorder change in
  `src/agents/obs_shuffled_agent.py` (commit `c15f313`) — *not* a
  tolerance relaxation. The v0.4.0 reference CSV was not modified at
  any point. This is what an audit gate is for.

For an operational reader interested in detection-of-anomaly use cases,
the practical reading is narrow and intentional: the κ test is a
*portability stress test* of a structural-coupling probe, not a
detection product. What v0.5.0 demonstrates is that the probe's
positive answer on E₀ does not collapse when the environment is
replaced by a calibrated diffusive variant; the signal-to-noise on
$\Delta_\kappa$ (Cohen $d \approx 3$) survives the swap. Whether that
property is useful for a downstream anomaly-detection pipeline is a
separate engineering question that is *not* answered here.

## 4. What this release is NOT

- Not a claim about cognition, agency, intent, intelligence, emergence,
  thought, or any cousin term. ADR-020 §3 vocabulary remains binding;
  permitted vocabulary remains operational only.
- Not a claim that v0.5.0's $d = +3.09$ is *larger than* v0.4.0's
  $d = +2.66$ in any meaningful sense. The two effect sizes were
  measured under different environments, on different seed pools, and
  the comparison is not pre-registered as a test.
- Not a claim that the κ mechanism is *the only* mechanism that would
  transfer to E₁, nor that it is the *minimal* transferring mechanism.
  Alternative agents are not tested here. ADR-032 only pre-registered
  M_κ.
- Not a claim about portability to environments *other than* the
  calibrated E₁ specified in `research/calibration_e1.json`. Generic
  "robustness" or "out-of-distribution generalisation" beyond the
  pre-registered E₁ is *not* claimed.
- Not a detection product, not a security product, not a compliance
  product. The runner is a research instrument; using it as a
  decision-making component requires its own qualification process,
  which is out of scope of v0.5.0.
- Not preliminary. Per ADR-032 the portability pool [2000-2029] is now
  spent. No further runs of the κ pipeline on E₁ under the present
  probe are authorised on this pool.

## 5. Reproducibility note

The H₅ Docker image (`cae-research-kit:0.1.0`, fingerprint
`406ce26e…008e7e5f`) is unchanged. The development environment is
unchanged from v0.3.0 / v0.4.0 (Python 3.12.3, `numpy==1.26.4`,
`scipy==1.12.0`, `pytest==8.1.1`). All v0.4.0 private-chain SHAs are
copied into `research/MANIFEST.v0.5.0.yaml` for cross-reference.

To reproduce the audit gate (cold):

```
python -m src.experiments.portability_draw \
  --pool audit \
  --output research/h7_kappa_audit_v04_iter2.csv

python -m src.analysis.audit_compare \
  --reference research/h7_kappa_run_results.csv \
  --candidate research/h7_kappa_audit_v04_iter2.csv \
  --report-output research/h7_kappa_audit_v04_iter2.report.txt
# exit code 0 on PASS, 1 on FAIL.
```

To reproduce the portability verdict on E₁ (cold; only after audit
PASS):

```
python -m src.experiments.portability_draw \
  --pool portability --i-have-read-adr-033 \
  --output research/h7_kappa_portability.csv

python -c "from src.analysis.verdict_v05 import compute_verdict; \
  compute_verdict('research/h7_kappa_portability.csv', \
                  'research/h7_kappa_portability_verdict.json')"
```

Wall-clock on the H₇ development environment: ≈ 3 min 35 s (audit
[1500-1529], E₀) + ≈ 9 min 50 s (portability [2000-2029], E₁) on a
single CPU. The portability runner enforces a hard refusal on
`--pool portability` without `--i-have-read-adr-033`.

The 30-row per-seed CSVs (29 columns each: header verified by
`audit_compare.EXPECTED_HEADER`) are sufficient to reproduce both
verdict computations independently of the runner. The 73 new ADTs
introduced between v0.4.0 and v0.5.0 (`test_sigma_chain` 21,
`test_obs_shuffled_agent` 15, `test_portability_draw` 12,
`test_audit_compare` 12, `test_verdict_v05` 13) all pass against the
shipped sources.

## 6. Next steps

This release closes the portability question raised in v0.4.0 §6
(bullet *Cross-environment portability*). It does not pre-empt the
other two follow-on questions of v0.4.0 §6:

- **κ-stability sweep.** Whether the same effect size holds for
  variants of M_κ (longer windows, EMA, leaky integrator, multi-tick
  lookback). Not pre-registered; pool not reserved.
- **H8 deferral confirmation.** Whether the H8 architectural pivot
  remains permanently unnecessary. ADR-028's Option A vindication —
  now extended to E₁ by v0.5.0 — does not pre-empt H8 on its own
  merits; a separate ADR is required.

A new question opens with v0.5.0:

- **Portability beyond E₁.** Whether the κ-transfers signature
  replicates under environments other than the specific calibrated E₁
  used here (e.g. recalibrated diffusion coefficients, alternative
  topologies, perturbed observation maps). Out of scope; would require
  a new pre-registration, a new pool, and a new audit gate against
  v0.5.0.

The portability pool tail [2030-2099] remains reserved and **frozen**
pending any of the above ADRs. No further H₇ runs are authorised on it
until then.

---

# Release v0.4.0-h7-κ-reverses

**Title:** *H₇-κ Reverses: A Single Tick of Memory Breaks the σ Inversion*
**Date:** 2026-05-09
**Scientific status:** `KAPPA_REVERSES` — the H7-σ inverted-coupling signature is fully reversed by adding a single tick of local-pressure memory. Both branches of the pre-registered double reporting (Miller-Madow corrected primary, plug-in transparency) agree at the same p-value.
**Operational status:** paradox-resolution published with full data, ADR chain, public agent + ADT, per-seed CSV, verdict file, and SHA-pinned freeze manifest (κ v1).
**Predecessor:** [v0.3.0-h7-σ-inverted](#release-v030-h7-σ-inverted) (σ-inversion is the regime κ now decomposes).
**DOI (v0.4.0):** [10.5281/zenodo.20097880](https://doi.org/10.5281/zenodo.20097880) — concept: [10.5281/zenodo.20091626](https://doi.org/10.5281/zenodo.20091626).

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
