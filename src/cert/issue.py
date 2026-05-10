"""ADR-036 §4.2 — issue a CAE-Cert v0.1 from a release MANIFEST.

Reads the YAML MANIFEST, resolves all referenced ADR + audit artefact paths
relative to the repo root, computes SHA-256 of each, builds the certificate
JSON per ADR-036 §3.1, canonicalises via JCS (RFC 8785), signs with Ed25519,
and writes both the JSON (indented, human-readable) and the .sig file.

Usage:
    python -m src.cert.issue \\
        --release-tag v0.6.0-h7-κ-boundary \\
        --manifest research/MANIFEST.v0.6.0.yaml \\
        --private-key ~/.cae-keys/cae-cert-issuer.ed25519 \\
        --output-cert research/cae-cert-v0.6.0.v01.json \\
        --output-sig  research/cae-cert-v0.6.0.v01.json.sig
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jcs
import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from src.cert import CERT_VERSION
from src.cert.keygen import public_key_fingerprint_sha256
from src.cert.schema import validate_cert
from src.cert.sigfile import SigFile
from src.cert.sigfile import write as write_sig

# ----------------------------------------------------------------------
# MANIFEST parsing — extract claims for the rétrofit.
# ----------------------------------------------------------------------
# v0.6.0 MANIFEST `release.operational_status` is a free-form string.
# ADR-036 §6.2 requires translation into the closed enum. The translation
# table is explicit and version-pinned here. Adding a new release with a
# different free-form string requires extending this table.
OPERATIONAL_STATUS_TRANSLATION: dict[str, str] = {
    "kappa_signature_robust_on_validated_envelope": "KAPPA_BAND_LIMITED_UPPER_OPEN",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve(repo_root: Path, p: str) -> Path:
    return (repo_root / p).resolve()


def _parse_d_envelope(env_str: str) -> tuple[float | None, float | None]:
    """Parse 'D ∈ [0.005, 0.320] (...)' → (0.005, 0.320). Best-effort."""
    import re
    m = re.search(r"\[\s*([0-9.eE+-]+)\s*,\s*([0-9.eE+-]+)\s*\]", env_str)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None, None


def _parse_rupture(rupture_str: str) -> float | None:
    import re
    m = re.search(r"D\s*[≈=]\s*([0-9.eE+-]+)", rupture_str)
    if m:
        return float(m.group(1))
    return None


def build_certificate(
    *,
    release_tag: str,
    manifest_path: Path,
    repo_root: Path,
    issuer_name: str,
    issuer_pub_fingerprint: str,
    revocation_url: str,
    notes: str | None,
    primary_metrics_override: dict[str, Any] | None = None,
    extra_evidence_adrs: list[str] | None = None,
    extra_audit_artefacts: list[tuple[str, str]] | None = None,  # (path, role)
    protocol_clauses: list[dict[str, str]] | None = None,
    defense_chain: list[dict[str, Any]] | None = None,
    issued_at: datetime | None = None,
    cert_id: str | None = None,
) -> dict[str, Any]:
    """Build the certificate dict (not yet signed). All paths repo-relative."""
    manifest_abs = _resolve(repo_root, str(manifest_path))
    with manifest_abs.open("r", encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)

    rel = manifest.get("release", {})
    formal_verdict = rel.get("scientific_status")
    if formal_verdict is None:
        raise ValueError(f"MANIFEST {manifest_path} missing release.scientific_status")
    raw_op = rel.get("operational_status")
    operational_verdict = OPERATIONAL_STATUS_TRANSLATION.get(raw_op, raw_op) if raw_op else None
    if operational_verdict == formal_verdict:
        operational_verdict = formal_verdict  # explicit equality

    env_str = rel.get("operational_envelope", "") or ""
    rupture_str = rel.get("rupture_boundary", "") or ""
    d_min, d_max = _parse_d_envelope(env_str)
    rupture_above = _parse_rupture(rupture_str)

    doi = rel.get("doi")
    if doi is not None:
        doi = str(doi)
    else:
        doi = ""

    # Evidence chain: parse ADR list from manifest header comments is brittle;
    # rely on caller-supplied list which is more explicit and audit-friendly.
    evidence: list[dict[str, str]] = []
    for adr_id in (extra_evidence_adrs or []):
        # Find the ADR file by id.
        adr_files = sorted((repo_root / "docs" / "adr").glob(f"{adr_id}-*.md"))
        if not adr_files:
            raise FileNotFoundError(f"ADR file for {adr_id} not found in docs/adr/")
        adr_path = adr_files[0]
        rel_path = adr_path.relative_to(repo_root).as_posix()
        evidence.append({
            "adr_id": adr_id,
            "path": rel_path,
            "sha256": sha256_file(adr_path),
        })

    # Audit artefacts.
    artefacts: list[dict[str, str]] = []
    for art_path, role in (extra_audit_artefacts or []):
        abs_art = _resolve(repo_root, art_path)
        if not abs_art.exists():
            raise FileNotFoundError(f"audit artefact not found: {art_path}")
        artefacts.append({
            "path": art_path,
            "sha256": sha256_file(abs_art),
            "role": role,
        })

    # Primary metrics: caller-supplied (manifest does not encode them in a
    # uniform schema across versions, and ADR-036 wants explicit values).
    pm = primary_metrics_override or {
        "cohen_d_median": None,
        "cohen_d_range": None,
        "p_value": None,
        "n_seeds": None,
        "n_pos": None,
        "clip_total": None,
    }

    cert = {
        "cert_version": CERT_VERSION,
        "cert_id": cert_id or str(uuid.uuid4()),
        "issued_at": (issued_at or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issuer": {
            "name": issuer_name,
            "public_key_fingerprint_sha256": issuer_pub_fingerprint,
        },
        "subject": {
            "release_tag": release_tag,
            "doi": doi,
            "manifest_path": str(manifest_path).replace("\\", "/"),
            "manifest_sha256": sha256_file(manifest_abs),
        },
        "claims": {
            "formal_verdict": formal_verdict,
            "operational_verdict": operational_verdict,
            "operational_envelope": {
                "parameter": "D",
                "min": d_min,
                "max": d_max,
                "rupture_above": rupture_above,
                "rupture_below": None,
            },
            "primary_metrics": pm,
        },
        "evidence_chain": evidence,
        "audit_artefacts": artefacts,
        "protocol_clauses": protocol_clauses or [],
        "defense_chain": defense_chain or [],
        "expiry": None,
        "revocation_url": revocation_url,
        "notes": notes,
    }
    return cert


def canonical_bytes(cert: dict[str, Any]) -> bytes:
    """RFC 8785 JCS canonicalisation."""
    return jcs.canonicalize(cert)


def sign_certificate(cert: dict[str, Any], private_key_path: Path) -> SigFile:
    pem = private_key_path.read_bytes()
    sk = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(sk, Ed25519PrivateKey):
        raise TypeError("private key must be Ed25519")
    pub_der = sk.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    fp = public_key_fingerprint_sha256(pub_der)
    msg = canonical_bytes(cert)
    sig = sk.sign(msg)
    return SigFile(algo="ed25519", pubkey_fingerprint=fp, signature=sig)


def issue(
    *,
    release_tag: str,
    manifest_path: Path,
    private_key_path: Path,
    output_cert_path: Path,
    output_sig_path: Path,
    repo_root: Path,
    issuer_name: str = "CAE Project (self-issued)",
    revocation_url: str,
    notes: str | None = None,
    primary_metrics_override: dict[str, Any] | None = None,
    extra_evidence_adrs: list[str] | None = None,
    extra_audit_artefacts: list[tuple[str, str]] | None = None,
    protocol_clauses: list[dict[str, str]] | None = None,
    defense_chain: list[dict[str, Any]] | None = None,
    issued_at: datetime | None = None,
    cert_id: str | None = None,
) -> tuple[Path, Path]:
    """End-to-end issuance. Returns (cert_path, sig_path)."""
    pem = private_key_path.read_bytes()
    sk = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(sk, Ed25519PrivateKey):
        raise TypeError("private key must be Ed25519")
    pub_der = sk.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    fp = public_key_fingerprint_sha256(pub_der)

    cert = build_certificate(
        release_tag=release_tag,
        manifest_path=manifest_path,
        repo_root=repo_root,
        issuer_name=issuer_name,
        issuer_pub_fingerprint=fp,
        revocation_url=revocation_url,
        notes=notes,
        primary_metrics_override=primary_metrics_override,
        extra_evidence_adrs=extra_evidence_adrs,
        extra_audit_artefacts=extra_audit_artefacts,
        protocol_clauses=protocol_clauses,
        defense_chain=defense_chain,
        issued_at=issued_at,
        cert_id=cert_id,
    )
    errs = validate_cert(cert)
    if errs:
        raise ValueError("certificate failed schema validation:\n  " + "\n  ".join(errs))

    sf = sign_certificate(cert, private_key_path)

    output_cert_path.parent.mkdir(parents=True, exist_ok=True)
    output_sig_path.parent.mkdir(parents=True, exist_ok=True)
    # Human-readable JSON; verifier re-canonicalises before signature check.
    output_cert_path.write_text(
        json.dumps(cert, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_sig(output_sig_path, sf)
    return output_cert_path, output_sig_path


def main() -> int:
    p = argparse.ArgumentParser(description="ADR-036 §4.2 — issue a CAE-Cert v0.1")
    p.add_argument("--release-tag", required=True)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--private-key", required=True, type=Path)
    p.add_argument("--output-cert", required=True, type=Path)
    p.add_argument("--output-sig", required=True, type=Path)
    p.add_argument("--revocation-url",
                   default="https://github.com/CAE-Project/CaePivot/releases/tag/cert-revocations")
    p.add_argument("--issuer-name", default="CAE Project (self-issued)")
    args = p.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cert_path, sig_path = issue(
        release_tag=args.release_tag,
        manifest_path=args.manifest,
        private_key_path=args.private_key.expanduser(),
        output_cert_path=args.output_cert,
        output_sig_path=args.output_sig,
        repo_root=repo_root,
        issuer_name=args.issuer_name,
        revocation_url=args.revocation_url,
    )
    print(f"cert_path={cert_path}")
    print(f"sig_path={sig_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
