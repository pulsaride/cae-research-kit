# External case studies of CAE-Cert v0.1 issuance

This directory archives **independent issuances** of CAE-Cert certificates by projects other than `cae-research-kit`. Its existence is a deliberate signal: the CAE-Cert protocol is only useful to the extent that a second issuer can adopt it without our help and without our key.

## Why this directory exists

The protocol's first worked example (the v0.6.0 retrofit certificate of the CAE research repository, archived at [10.5281/zenodo.20112693](https://doi.org/10.5281/zenodo.20112693)) is, by construction, a self-issuance: same project, same key, same author. That self-issuance is sufficient to demonstrate that the toolchain works; it is **not sufficient** to demonstrate that the protocol is portable across maintainers, key custodians, or scientific cultures.

Each entry in this directory documents a certificate issued by an external project, with an external key, under that project's own governance. We are neither the issuer nor the verifier of authority for those certificates — we are only the maintainers of the schema and the verifier code.

## Status

**Currently empty — actively seeking external adopters.**

## How to be listed here

If you maintain a research software project with pre-registered acceptance criteria (or are willing to introduce some), and you would like to issue your first CAE-Cert certificate, please open a [GitHub Issue](https://github.com/pulsaride/cae-research-kit/issues/new) titled `Case study request: <your project>` with:

- a one-paragraph description of the release you want to certify;
- a link to the pre-registered acceptance criteria (ADR, OSF registration, or equivalent);
- the public key fingerprint you intend to use (or a request for guidance on key generation);
- whether you want a synchronous pair-programming session (~2 h) to issue the first certificate together.

We will pair-program your first issuance for free, document the case study here as `docs/case-studies/<your-project>.md`, and link to your independently archived certificate (your repository, your Zenodo DOI). The CAE project does **not** retain any signing authority over your certificates.

## Required entry format

Each case study, once published, should follow this minimal template:

```markdown
# Case study: <project name>

- **Issuer:** <organisation / individual> (independent of CAE project)
- **Issuer key fingerprint (SHA-256 of DER SubjectPublicKeyInfo):** `<hex64>`
- **Certified release:** <tag> of <repo URL>
- **Certificate:** <URL to JSON> (archived at <Zenodo DOI>)
- **Pre-registered acceptance criteria:** <ADR or OSF link>
- **Verdict published:**
  - `formal_verdict   : ...`
  - `operational_verdict : ...`
  - `defense_chain present: yes/no`
- **Independent verification command:**
  ```bash
  python -m src.cert.verify --cert <path> --sig <path> --public-key <path> --repo-root <path>
  ```
- **Issuance date:** YYYY-MM-DD
- **Notes from the external issuer (optional):** ...
```

## Non-goals

- We do not run a registry, a CA, or a transparency log. This directory is documentation, not infrastructure.
- We do not endorse the scientific content of any certificate listed here. We only attest that the certificate was issued by the named external party using the v0.1 protocol.
- We do not maintain a leaderboard, a citation count, or any other competitive metric.
