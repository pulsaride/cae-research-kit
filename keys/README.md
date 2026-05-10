# CAE-Cert v0.1 — Public keys

This directory contains **only public keys** used to verify CAE-Cert
certificates. Private keys are never stored here (see `.gitignore`).

## Trust anchor

| File                       | Algorithm | Fingerprint (SHA-256 of DER SubjectPublicKeyInfo)              |
|----------------------------|-----------|----------------------------------------------------------------|
| `cae-cert-issuer.pub`      | Ed25519   | `6c153dc3dddb9738347c587e107399e3ed714f715f0e7716761436b748dcbb65` |

The fingerprint is the trust anchor (ADR-036 §4.4). It is reproduced
inside every issued certificate (`issuer.public_key_fingerprint_sha256`)
and inside the binary `.sig` file (`pubkey_fp=…`). A verifier MUST
refuse any certificate whose three fingerprint copies do not all match
each other and the public key file fetched from this directory.

## Verification

```bash
python -m src.cert.verify \
  --cert research/cae-cert-v0.6.0.v01.json \
  --sig  research/cae-cert-v0.6.0.v01.json.sig \
  --public-key keys/cae-cert-issuer.pub \
  --repo-root .
```

Exit code 0 = PASS, 1 = FAIL. Detailed report on stderr.

## Key rotation

Per ADR-036 §5.3, key rotation requires a dedicated ADR (≥ ADR-037).
Until then, this fingerprint is immutable.

## Governance v0.1

- v0.1: solo signer (CEO). Single keypair, single fingerprint.
- v0.2 (planned): co-signature (CEO + technical reviewer), separate ADR.
- v1.0 (planned): external CA / public timestamping, separate ADR.
