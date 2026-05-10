# Contributing to `cae-research-kit`

Thank you for considering a contribution. This repository ships a *falsification-disciplined* research kit and a signed certification protocol (`CAE-Cert v0.1`); contributions are welcome but the bar is **reproducibility, not novelty**.

## Scope

We accept contributions in three categories:

1. **Bug reports and reproducibility failures** — anything where `python -m src.cert.verify --repo-root .` or `pytest tests/cert -q` fails in a clean environment.
2. **Documentation improvements** — typos, clarifications, ports of the `paper.md` to other formats, translations of the user-facing README.
3. **Protocol extensions** — strictly via a new ADR under `docs/adr/`; see [ADR-036 §11](docs/adr/ADR-036-cae-cert-v01-protocol.md) for the governance procedure. **No silent schema changes**: the `cert_version` field is frozen at `"0.1.0"`; any new feature requires a version bump and a new ADR.

## How to report a bug

Open a GitHub issue with:

- the exact command you ran,
- the expected output,
- the actual output (full stderr),
- your platform (`uname -a`, `python --version`),
- the commit SHA you tested (`git rev-parse HEAD`).

If the bug is a verification failure on a published certificate, **please attach the failing `verify` report verbatim** — do not paraphrase.

## How to submit a pull request

1. Fork the repository.
2. Create a topic branch off `main`.
3. Make your change. Keep PRs **small and single-purpose**.
4. Run the test suite: `PYTHONPATH=. pytest tests/cert -q`. All 8 tests must pass.
5. If your change touches the certificate schema, the signing flow, or the verifier, **add a regression test** in `tests/cert/`.
6. Run the lexicon check (no marketing words): `grep -rEi 'révolutionnaire|breakthrough|cognition|conscience|intelligence' src/ docs/ paper/ || echo OK`.
7. Open a PR with a clear title and a description of *why* the change is necessary.

## Code style

- Python: standard library + the three pinned dependencies (`cryptography`, `jcs`, `PyYAML`). **No new dependencies in v0.x without an ADR.**
- Type hints encouraged but not enforced.
- Docstrings: short, factual, no marketing.

## Governance

All non-trivial decisions (new public API, schema change, key rotation, threat-model change) require an Architecture Decision Record (ADR) under `docs/adr/`. The format is documented in [ADR-020](docs/adr/) ("lexique froid") and [ADR-036](docs/adr/ADR-036-cae-cert-v01-protocol.md). The project lead retains final acceptance authority on ADRs.

## Reporting security issues

For vulnerabilities affecting the certification protocol (signature forgery, schema bypass, key compromise, etc.), **do not open a public issue**. Open a [GitHub Security Advisory](https://github.com/pulsaride/cae-research-kit/security/advisories/new) instead.

## Code of conduct

Be civil, be technical, be precise. Disagreements are resolved on technical merit and reproducibility, not on rhetoric.

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE) (code) and [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) (text/data), the dual-licensing scheme of this repository.
