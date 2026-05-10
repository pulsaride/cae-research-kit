"""ADR-036 §4.1 — Ed25519 keypair generation.

Writes private key in PEM PKCS#8 (chmod 600), public key in PEM
SubjectPublicKeyInfo (chmod 644). The fingerprint of the public key DER
bytes (SHA-256, hex, lowercase) is the trust anchor.

Usage:
    python -m src.cert.keygen \\
        --output-private ~/.cae-keys/cae-cert-issuer.ed25519 \\
        --output-public  ~/.cae-keys/cae-cert-issuer.pub
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def public_key_fingerprint_sha256(pub_der: bytes) -> str:
    """Trust anchor: SHA-256 hex of public key DER (SubjectPublicKeyInfo)."""
    return hashlib.sha256(pub_der).hexdigest()


def generate_keypair(out_priv: Path, out_pub: Path, force: bool = False) -> str:
    """Generate Ed25519 keypair, write to disk, return public-key fingerprint."""
    if out_priv.exists() and not force:
        raise FileExistsError(f"{out_priv} exists; pass force=True to overwrite")
    if out_pub.exists() and not force:
        raise FileExistsError(f"{out_pub} exists; pass force=True to overwrite")

    out_priv.parent.mkdir(parents=True, exist_ok=True)
    out_pub.parent.mkdir(parents=True, exist_ok=True)

    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key()

    priv_pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_pem = pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    pub_der = pk.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    out_priv.write_bytes(priv_pem)
    out_pub.write_bytes(pub_pem)
    os.chmod(out_priv, 0o600)
    os.chmod(out_pub, 0o644)

    return public_key_fingerprint_sha256(pub_der)


def main() -> int:
    p = argparse.ArgumentParser(description="ADR-036 §4.1 — generate Ed25519 keypair")
    p.add_argument("--output-private", required=True, type=Path)
    p.add_argument("--output-public", required=True, type=Path)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    fp = generate_keypair(
        args.output_private.expanduser(),
        args.output_public.expanduser(),
        force=args.force,
    )
    print(f"public_key_fingerprint_sha256={fp}")
    print(f"private_key_path={args.output_private}")
    print(f"public_key_path={args.output_public}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
