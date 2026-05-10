---
title: "CAE-Cert v0.1: a signed, machine-verifiable certification protocol for falsification-disciplined scientific software releases"
authors:
  - name: "CAE Project"
    affiliation: "Self-issued"
date: 2026-05-10
keywords:
  - reproducibility
  - signed releases
  - Ed25519
  - JCS
  - pre-registration
  - falsification
target: "JOSS / SoftwareX (≤ 8 pages)"
license: "Apache-2.0 (code), CC-BY-4.0 (text)"
doi: "10.5281/zenodo.20112693"
repository: "https://github.com/pulsaride/cae-research-kit"
archive_doi: "https://doi.org/10.5281/zenodo.20112693"
bibliography: paper.bib
---

## Summary

`CAE-Cert v0.1` is a minimal, dependency-light protocol for issuing
**signed, schema-validated certificates** that bind, at a single
fingerprint and signature, the formal scientific verdict of a software
release to (i) the closed enumeration of pre-registered acceptance
clauses that fired or passed for that release, (ii) the SHA-256 audit
trail of every Architecture Decision Record (ADR) and audit artefact
listed by the release manifest, and (iii) any *defense chain* that
justifies the publication of a parallel **operational reading** when
that operational reading differs from the formal verdict. The protocol
is implemented as a ~1 kLOC Python package (`src/cert/`) using only
`cryptography` (Ed25519 — RFC 8032), `jcs` (JSON canonicalisation —
RFC 8785), and `PyYAML`. Certificates are emitted as human-readable
JSON plus a binary `.sig` companion file. Verification is offline,
deterministic, and exits 0 / 1 with a single command. The protocol
explicitly forbids any verdict outside of two closed enumerations and
refuses, by schema construction, the silent renaming of a verdict
between formal scientific status and operational status. It is
released alongside a worked retrofit certificate for the
`v0.6.0-h7-κ-boundary` release of the CAE research repository, in
which the formal verdict `KAPPA_INCONCLUSIVE` (triggered by a single
pre-registered override clause) is published in parallel with the
operational reading `KAPPA_BAND_LIMITED_UPPER_OPEN`, defended by a
signed two-link chain of byte-level identity proofs against the
reference release `v0.5.0-h7-κ-transfers`.

## Statement of need

Software releases that publish empirical scientific claims face a
governance problem that no general-purpose package metadata format
addresses. A `CITATION.cff` file or a Zenodo DOI pin a release to its
authors and source tree but say nothing about which pre-registered
clauses were satisfied at release time, which ones fired, what was
defended after the fact, and which artefacts a downstream verifier must
re-hash to re-derive the published claim. Conversely, attestation
frameworks designed for software supply-chain provenance (e.g.,
Sigstore, in-toto) can sign arbitrary attestations but do not encode
the structural distinction, central to falsification-disciplined
methodologies, between *the verdict the protocol was forced to write
verbatim* and *the empirical reading the data also support*. When
those two readings disagree — which happens routinely in
pre-registered work whose acceptance criteria are stated *before* data
collection — readers, downstream consumers, and future replicators
need a machine-checkable record of (a) which clause forced the
divergence, (b) which prior ADR is being invoked to defend the
parallel reading, and (c) the maximum residual error tolerated by
that ADR. `CAE-Cert v0.1` was designed to solve exactly that narrow
problem at the smallest possible surface area.

## Protocol description

A certificate is a JSON object whose schema is fully defined by ADR-036
§3 and enforced by `src/cert/schema.py`. Top-level fields include
`cert_version` (frozen at `"0.1.0"`), `cert_id` (UUID v4),
`issued_at` (ISO 8601 UTC with `Z` suffix), `issuer` (name and
SHA-256 fingerprint of the DER-encoded SubjectPublicKeyInfo of the
Ed25519 public key), `subject` (release tag, optional DOI,
manifest path and SHA-256), `claims` (a `formal_verdict` from a
seven-value closed enumeration, an `operational_verdict` from a
nine-value closed enumeration, an `operational_envelope` with
parameter and bounds, and primary metrics), an `evidence_chain`
listing every cited ADR with its SHA-256, an `audit_artefacts` list
binding each result file to its hash and role, a
`protocol_clauses` list each labelled `PASS`, `FIRE`, or `N/A` with
mandatory note when fired, and a `defense_chain` that **must** be
non-empty whenever `operational_verdict` differs from
`formal_verdict`. The schema enforces that constraint; the verifier
re-checks it independently.

Signing uses **Ed25519 over the JCS canonical bytes** of the JSON
object, eliminating dependence on whitespace or key ordering. The
signature, the algorithm tag, and the issuer fingerprint are written
to a four-line ASCII `.sig` file (`CAESIGv01` header,
`algo=ed25519`, `pubkey_fp=<hex64>`, `sig=<base64>`). Verification
re-canonicalises the JSON, checks the fingerprint matches the
fetched public key, verifies the Ed25519 signature, re-runs the
schema validator, optionally re-hashes every referenced artefact
when a `--repo-root` is supplied, and produces a single PASS/FAIL
report on stderr.

Key generation, issuance, and verification are exposed both as
importable functions and as `python -m` CLIs. The full toolchain is
exercised by eight tests in `tests/cert/test_issue_verify.py`
covering: round-trip success, single-byte JSON tampering detection,
single-byte signature tampering detection, wrong-key detection,
canonicalisation invariance under JSON re-serialisation with
different key order, missing-required-field rejection, frozen
`cert_version` rejection of unauthorised bumps, and rejection of an
operational verdict that differs from the formal verdict without a
non-empty defense chain.

## Worked example: retrofit certificate for `v0.6.0-h7-κ-boundary`

The `v0.6.0` release of the CAE repository pre-registered, in
ADR-034, a seven-criterion AND test for accepting the KAPPA
signature on a six-octave diffusion sweep. Six of the seven criteria
passed cleanly across all six envelope grid points
($D \in [0.005, 0.320]$, $n_{\mathrm{pos}} \geq 29/30$,
Cohen $d \geq 2.76$, $p < 1.86 \times 10^{-9}$, zero clip events,
intra-sample disagreement of $4.1 \times 10^{-6}$); the seventh
(`concordance vs v0.5.0 ≤ 1%`, ADR-034 §5.4) fired with an observed
gap of $3.85\%$. Per pre-registration, this single FIRE forced
$\mathrm{formal\_verdict} = \texttt{KAPPA\_INCONCLUSIVE}$, even
though all six other criteria of `KAPPA_BAND_LIMITED` were met. A
follow-up pre-registration (ADR-035) ran a seed-paired byte-identity
test of the HEAD engine against the `v0.5.0` reference CSV on the
calibration pool; the two CSVs were byte-for-byte identical
($\max \lvert \Delta \rvert = 0.0$), proving that the $3.85\%$ gap
was sampling noise between two disjoint $n=30$ pools (~$0.46 \sigma$
under the Wilcoxon framework), not engine drift.

The retrofit certificate `research/cae-cert-v0.6.0.v01.json` encodes
this situation literally: $\texttt{formal\_verdict} =
\texttt{KAPPA\_INCONCLUSIVE}$, $\texttt{operational\_verdict} =
\texttt{KAPPA\_BAND\_LIMITED\_UPPER\_OPEN}$, with the §5.4 clause
labelled `FIRE` and a non-empty defense chain pointing to ADR-035
($\max \lvert \Delta \rvert = 0.0$) and ADR-033
($\max \lvert \Delta \rvert = 4.5 \times 10^{-11}$). The certificate
re-hashes seven external audit artefacts and seven ADR documents.
Verification with `python -m src.cert.verify --repo-root .` exits 0
and reports `OVERALL: PASS`. Any byte-level alteration of the JSON
or of a referenced artefact flips the verdict to FAIL with a
specific error.

## Limitations and explicit non-goals

`v0.1` ships **deliberately** with a single signer (the project's
self-issued key), no expiry mechanism, no certificate transparency
log, and no external timestamp authority. These are not oversights:
each is documented as a known threat model gap in ADR-036 §9 and
mapped to a future minor version (`v0.2` co-signature, `v1.0`
external CA / public timestamping). The protocol does not certify
that a finding is *true*; it certifies that the published triplet
(formal verdict, operational verdict, defense chain) is the one the
issuer actually emitted, that every cited artefact is intact, and
that the schema constraints (closed enumerations, mandatory notes
on FIRE clauses, mandatory defense chain on verdict divergence) are
all satisfied. It is, by design, a *minimum viable instrument of
governance discipline*, not an oracle.

## Acknowledgements

The protocol design absorbed lessons from seven consecutive
pre-registered, frozen, falsification-disciplined experiments
(H₅ → H₇-κ boundary) released under the CAE research repository
between 2026-04-15 and 2026-05-10, and especially from the
governance pressure created by the operational/formal split that
ADR-035 forced into the `v0.6.0` release.

## References

<!-- Pandoc reads bibliography: paper.bib (see frontmatter) and renders entries below. -->

- `CAE-Cert v0.1` archived release [@cae_cert_zenodo_v070].
- ADR-030 [@adr030], ADR-032 [@adr032], ADR-033 [@adr033], ADR-034 [@adr034], ADR-035 [@adr035], ADR-036 [@adr036].
- Edwards-curve Digital Signature Algorithm (EdDSA) [@rfc8032].
- JSON Canonicalization Scheme (JCS) [@rfc8785].
- Sigstore [@sigstore]; in-toto [@intoto] (compared in Statement of need).
