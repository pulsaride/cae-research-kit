"""ADR-036 §4.3 — verify a CAE-Cert v0.1.

Steps (per ADR-036 §4.3):
  1. Parse .sig, extract algo + fingerprint + signature.
  2. Verify fingerprint matches the supplied public key.
  3. Re-canonicalise the JSON via JCS.
  4. Verify Ed25519 signature on canonical bytes.
  5. Re-compute SHA-256 of MANIFEST + ADRs + artefacts (if accessible);
     compare to encoded values. Missing files are reported but do not
     fail signature verification (per ADR-036 §4.4 self-containment).
  6. Cross-field consistency (defense_chain ↔ verdict mismatch, FIRE clause
     notes).
  7. Strict schema validation.
  8. Exit 0 / 1 + report on stderr.

Usage:
    python -m src.cert.verify \\
        --cert research/cae-cert-v0.6.0.v01.json \\
        --sig  research/cae-cert-v0.6.0.v01.json.sig \\
        --public-key keys/cae-cert-issuer.pub
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from src.cert.issue import canonical_bytes, sha256_file
from src.cert.keygen import public_key_fingerprint_sha256
from src.cert.schema import validate_cert
from src.cert.sigfile import read as read_sig


@dataclass
class VerifyReport:
    cert_path: Path
    sig_path: Path
    pub_path: Path
    fingerprint_match: bool = False
    signature_valid: bool = False
    schema_errors: list[str] = field(default_factory=list)
    integrity_errors: list[str] = field(default_factory=list)
    integrity_warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            self.fingerprint_match
            and self.signature_valid
            and not self.schema_errors
            and not self.integrity_errors
        )

    def render(self) -> str:
        lines = [
            f"# CAE-Cert verification report",
            f"cert      : {self.cert_path}",
            f"signature : {self.sig_path}",
            f"public_key: {self.pub_path}",
            f"",
            f"fingerprint_match : {'PASS' if self.fingerprint_match else 'FAIL'}",
            f"signature_valid   : {'PASS' if self.signature_valid else 'FAIL'}",
            f"schema_errors     : {len(self.schema_errors)}",
            f"integrity_errors  : {len(self.integrity_errors)}",
            f"integrity_warnings: {len(self.integrity_warnings)}",
        ]
        for e in self.schema_errors:
            lines.append(f"  [schema]    {e}")
        for e in self.integrity_errors:
            lines.append(f"  [integrity] {e}")
        for w in self.integrity_warnings:
            lines.append(f"  [warn]      {w}")
        lines.append("")
        lines.append(f"OVERALL: {'PASS' if self.passed else 'FAIL'}")
        return "\n".join(lines)


def _load_public_key(path: Path) -> tuple[Ed25519PublicKey, str]:
    pem = path.read_bytes()
    pk = serialization.load_pem_public_key(pem)
    if not isinstance(pk, Ed25519PublicKey):
        raise TypeError("public key must be Ed25519")
    der = pk.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pk, public_key_fingerprint_sha256(der)


def verify(
    *,
    cert_path: Path,
    sig_path: Path,
    public_key_path: Path,
    repo_root: Path | None = None,
) -> VerifyReport:
    """Verify a certificate. Re-checks artefact SHAs only if repo_root provided."""
    report = VerifyReport(cert_path=cert_path, sig_path=sig_path, pub_path=public_key_path)

    pk, fp = _load_public_key(public_key_path)
    sf = read_sig(sig_path)
    report.fingerprint_match = (sf.pubkey_fingerprint == fp)
    if not report.fingerprint_match:
        report.integrity_errors.append(
            f"sig pubkey_fp={sf.pubkey_fingerprint} != provided pub key fp={fp}"
        )

    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    msg = canonical_bytes(cert)

    try:
        pk.verify(sf.signature, msg)
        report.signature_valid = True
    except InvalidSignature:
        report.signature_valid = False
        report.integrity_errors.append("Ed25519 signature verification failed")

    report.schema_errors = validate_cert(cert)

    # Cross-field consistency already partially in schema, double-check here.
    claims = cert.get("claims", {})
    fv = claims.get("formal_verdict")
    ov = claims.get("operational_verdict")
    if ov is not None and ov != fv and not cert.get("defense_chain"):
        report.integrity_errors.append(
            "operational_verdict differs from formal_verdict but defense_chain is empty"
        )

    issuer_fp = cert.get("issuer", {}).get("public_key_fingerprint_sha256")
    if issuer_fp != fp:
        report.integrity_errors.append(
            f"issuer.public_key_fingerprint_sha256={issuer_fp} != actual key fp={fp}"
        )

    # Optional: re-check artefact SHAs if repo accessible.
    if repo_root is not None:
        for ev in cert.get("evidence_chain", []):
            p = (repo_root / ev["path"]).resolve()
            if not p.exists():
                report.integrity_warnings.append(f"evidence file not found: {ev['path']}")
                continue
            actual = sha256_file(p)
            if actual != ev["sha256"]:
                report.integrity_errors.append(
                    f"evidence {ev['adr_id']} sha mismatch: file={actual} cert={ev['sha256']}"
                )
        manifest_path = cert.get("subject", {}).get("manifest_path", "")
        if manifest_path:
            p = (repo_root / manifest_path).resolve()
            if p.exists():
                actual = sha256_file(p)
                if actual != cert["subject"]["manifest_sha256"]:
                    report.integrity_errors.append(
                        f"manifest sha mismatch: file={actual} cert={cert['subject']['manifest_sha256']}"
                    )
            else:
                report.integrity_warnings.append(f"manifest not found: {manifest_path}")
        for art in cert.get("audit_artefacts", []):
            p = (repo_root / art["path"]).resolve()
            if not p.exists():
                report.integrity_warnings.append(f"artefact not found: {art['path']}")
                continue
            actual = sha256_file(p)
            if actual != art["sha256"]:
                report.integrity_errors.append(
                    f"artefact {art['path']} sha mismatch: file={actual} cert={art['sha256']}"
                )

    return report


def main() -> int:
    p = argparse.ArgumentParser(description="ADR-036 §4.3 — verify a CAE-Cert v0.1")
    p.add_argument("--cert", required=True, type=Path)
    p.add_argument("--sig", required=True, type=Path)
    p.add_argument("--public-key", required=True, type=Path)
    p.add_argument("--repo-root", type=Path,
                   help="if set, re-verify SHA-256 of referenced artefacts")
    args = p.parse_args()
    report = verify(
        cert_path=args.cert,
        sig_path=args.sig,
        public_key_path=args.public_key.expanduser(),
        repo_root=args.repo_root.resolve() if args.repo_root else None,
    )
    print(report.render(), file=sys.stderr)
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
