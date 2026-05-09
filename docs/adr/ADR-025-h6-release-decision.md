# ADR-025 — Release decision for H₆ (β + γ): falsified by control

**Status:** Decided
**Date:** 2026-05-09
**Sibling of:** ADR-021 (H₅ release decision)
**Authority chain:** ADR-022 → ADR-023 → ADR-023.bis → ADR-023.ter → ADR-024 → this ADR.

---

## 1. Verdicts

| Phase | Verdict (frozen) | Cohen d | p-value | n |
|-------|------------------|---------|---------|---|
| H6-β  | `H6_SIGNATURE_DETECTED` (paired Wilcoxon, ADR-023.ter) | +2.5068 | 1.86 × 10⁻⁹ | 30 |
| H6-γ.1 (RS > RM) | **fail to reject H₀** | −0.5027 | 0.998 | 30 |
| H6-γ.2 (SM > 0)  | reject H₀ | (statistic recorded) | 9.31 × 10⁻¹⁰ | 30 |

Combined verdict per ADR-024 §3.5: **`H6_GAMMA_FEEDBACK_ONLY`**.

## 2. Interpretation

The β verdict was correct *as a statistical test against a Markov-null
baseline*. The γ control proves it was the wrong test for the claim it was
asked to support. The mechanism producing the β signal is the **fact** of
agent-environment feedback, not any non-trivial coupling between the
agent's policy and the field's structure. An obs-shuffled agent — one that
acts on permuted, information-free observations — produces a trajectory
just as far from the Markov-null as the real agent does, and on average
*farther from the real agent than the Markov-null is*.

The H₆ hypothesis as stated in ADR-022 §3 is therefore **not supported**
by the H6-β + H6-γ run pair. We treat this as a falsification of the
phase-space topological-signature claim, *not* a refutation of the broader
research question, which now requires a different probe (see §5).

## 3. Release decision

Per ADR-024 §9 (FEEDBACK_ONLY → downgraded scope) **and** consistent with
the precedent set by ADR-021 (publish null results with full data):

- **Publish** as `v0.2.0-h6-rejected`.
- **Title:** *H₆ Falsified: Topological Signatures Reclassified as Feedback Artefacts.*
- **Scope:** the public release distributes (a) the full pre-registration
  chain (ADR-022 → ADR-024), (b) both verdict files (β and γ), (c) both
  per-seed CSVs, (d) the MANIFEST, (e) the abstract reformulated honestly.
- **No code release** for H6-α/β/γ in this version. The H6 development tree
  remains in `.forge_private/` until either (i) ADR-026+H₇ designs a
  successor experiment that consumes it, or (ii) we decide to publish the
  H6 code as a separately-tagged null-result artefact under
  `v0.2.1-h6-code-archive`. Decision deferred — does not gate this release.
- **DOI:** request a new DOI version on Zenodo concept `10.5281/zenodo.20091626`.

## 4. What this release is and is not

**This release is** a documented falsification with full pre-registration,
two distinct experiments (β and γ), reproducible verdicts, and explicit
self-criticism that downgraded a positive-looking d=2.5 result via a
controlled experiment we wrote and froze before running.

**This release is not** a claim about emergence, structure, signature,
intelligence, cognition, agency, or any cousin term. The only positive
claim it makes is methodological: *a feedback-naïve null is insufficient
to support a "structural" claim about a feedback-coupled agent's trajectory.*

## 5. What changes for H₇ / H_δ

- Trajectory-coupling probes on E₀ (in their current form) cannot
  discriminate "feedback effect" from "structural coupling". Future work
  must either (a) measure something orthogonal to feedback (e.g. agent
  state, internal representations if any, or response to controlled
  perturbations of the field), or (b) compare two policies that differ
  only in a quantity we want to attribute the signal to, with all other
  feedback channels held equal — going beyond what `ObsShuffledAgent`
  provides.
- Any future probe must be pre-registered under a new ADR before any code
  is run.

## 6. Anti-patterns (binding for any future H₆ work)

1. Do not re-run H6-β or H6-γ on a different seed pool to "see if it
   replicates". The pre-registration is spent.
2. Do not introduce new tweaks to `phase_delta` to "rescue" β. The metric
   is frozen by ADR-023.bis and locked by the release SHA below.
3. Do not refer to the v0.2.0 release as preliminary. It is final for H₆
   under the present probe.

## 7. Frozen artefacts referenced by this ADR

| Artefact | SHA-256 (in `.forge_private/`) |
|----------|--------------------------------|
| ADR-022  | `86b49ac1e4eba24c18c5c393b86d1992bcdb3cc8a6651ea7a914f59ee69cd068` |
| ADR-023  | `93a63b49492d184889a476a2b608c83434d8d9891cdce6fca1ad91a9c5205649` |
| ADR-023.bis | `df5e7f68e8b18c068cad7be7356e08b95ca264e37ee8ef2aa14835f3f8bcd757` |
| ADR-023.ter | `5fe12025637e97706bc6719487a7aeeaadd13bf652a30324974810a9db9856c9` |
| ADR-024  | `20098aef28b24ea9c74aa532cae3e42adc95dc944ded6d513b4b1d1a05819b75` |
| H6-β code bundle | see `.forge_private/h6_beta_code.sha256` |
| H6-γ code bundle | see `.forge_private/h6_gamma_code.sha256` |
| `h6_beta_verdict.json` | recorded in MANIFEST.v0.2.0.yaml |
| `h6_gamma_verdict.json` | recorded in MANIFEST.v0.2.0.yaml |

The public copies under `docs/adr/` and `research/` are byte-identical to
the private originals at the SHAs above.

---
End of ADR-025.
