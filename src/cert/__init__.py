"""ADR-036 — CAE-Cert v0.1 protocol implementation.

Modules:
    keygen  : Ed25519 keypair generation (RFC 8032)
    schema  : strict validation of cae-cert.v01.json
    issue   : build + sign a certificate from a release MANIFEST
    verify  : verify signature + schema + integrity of a certificate

All modules are stdlib + cryptography (RFC 8032 Ed25519) + jcs (RFC 8785 JCS).
No heavy deps. No network calls in default code paths.
"""
__all__ = ["keygen", "schema", "issue", "verify"]
CERT_VERSION = "0.1.0"
