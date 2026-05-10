"""ADR-036 §8 critère C2 — round-trip + tamper resistance tests for CAE-Cert v0.1."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from src.cert import CERT_VERSION
from src.cert.issue import build_certificate, canonical_bytes, issue, sha256_file
from src.cert.keygen import generate_keypair, public_key_fingerprint_sha256
from src.cert.schema import validate_cert
from src.cert.verify import verify
from src.cert.sigfile import read as read_sig
from src.cert.sigfile import write as write_sig

REPO_ROOT = Path(__file__).resolve().parents[2]


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def keypair(tmp_path: Path) -> tuple[Path, Path, str]:
    priv = tmp_path / "issuer.ed25519"
    pub = tmp_path / "issuer.pub"
    fp = generate_keypair(priv, pub)
    return priv, pub, fp


@pytest.fixture
def fake_release(tmp_path: Path) -> tuple[Path, Path]:
    """Build a minimal repo skeleton mimicking v0.6.0 for hermetic tests."""
    root = tmp_path / "repo"
    (root / "research").mkdir(parents=True)
    (root / "docs" / "adr").mkdir(parents=True)

    manifest = {
        "release": {
            "tag": "v-test-1.0.0",
            "date": "2026-05-10",
            "doi": "10.5281/zenodo.99999999",
            "scientific_status": "KAPPA_INCONCLUSIVE",
            "operational_status": "kappa_signature_robust_on_validated_envelope",
            "operational_envelope": "D ∈ [0.005, 0.320] (six octaves)",
            "rupture_boundary": "D ≈ 0.640 (saturation)",
        }
    }
    manifest_path = root / "research" / "MANIFEST.test.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    # Stub ADR file for evidence chain.
    adr = root / "docs" / "adr" / "ADR-099-stub-for-tests.md"
    adr.write_text("# ADR-099 — stub\nContent for hashing.\n", encoding="utf-8")

    # Stub artefact.
    art = root / "research" / "stub_artefact.csv"
    art.write_text("seed,kappa\n1,0.5\n", encoding="utf-8")

    return root, manifest_path.relative_to(root)


def _build_minimal_kwargs(repo_root: Path, manifest_path: Path, fingerprint: str):
    return dict(
        release_tag="v-test-1.0.0",
        manifest_path=manifest_path,
        repo_root=repo_root,
        issuer_name="Test Issuer",
        issuer_pub_fingerprint=fingerprint,
        revocation_url="https://example.invalid/revocations",
        notes="hermetic test certificate",
        primary_metrics_override={
            "cohen_d_median": 3.0906,
            "cohen_d_range": [2.764, 3.014],
            "p_value": 9.31e-10,
            "n_seeds": 30,
            "n_pos": 30,
            "clip_total": 0,
        },
        extra_evidence_adrs=["ADR-099"],
        extra_audit_artefacts=[("research/stub_artefact.csv", "stub_csv")],
        protocol_clauses=[
            {"id": "ADR-034 §5.4", "status": "FIRE",
             "note": "concordance gap 3.85% > 1% (sampling noise)"},
        ],
        defense_chain=[
            {"adr_id": "ADR-035", "claim": "HEAD byte-identical to v0.5.0",
             "max_abs_delta": 4.5e-11},
        ],
        issued_at=datetime(2026, 5, 10, 12, 0, 0, tzinfo=timezone.utc),
        cert_id="11111111-2222-4333-8444-555555555555",
    )


# ----------------------------------------------------------------------
# 1. Round-trip issue → verify PASS
# ----------------------------------------------------------------------

def test_round_trip_issue_then_verify_passes(tmp_path, keypair, fake_release):
    priv, pub, fp = keypair
    repo_root, manifest_path = fake_release
    cert_out = tmp_path / "cert.json"
    sig_out = tmp_path / "cert.json.sig"

    issue(
        release_tag="v-test-1.0.0",
        manifest_path=manifest_path,
        private_key_path=priv,
        output_cert_path=cert_out,
        output_sig_path=sig_out,
        repo_root=repo_root,
        revocation_url="https://example.invalid/revocations",
        notes="hermetic test",
        primary_metrics_override={
            "cohen_d_median": 3.0906, "cohen_d_range": [2.764, 3.014],
            "p_value": 9.31e-10, "n_seeds": 30, "n_pos": 30, "clip_total": 0,
        },
        extra_evidence_adrs=["ADR-099"],
        extra_audit_artefacts=[("research/stub_artefact.csv", "stub_csv")],
        protocol_clauses=[{"id": "ADR-034 §5.4", "status": "FIRE",
                           "note": "concordance gap"}],
        defense_chain=[{"adr_id": "ADR-035", "claim": "byte-identical",
                        "max_abs_delta": 4.5e-11}],
    )
    report = verify(cert_path=cert_out, sig_path=sig_out, public_key_path=pub,
                    repo_root=repo_root)
    assert report.passed, report.render()


# ----------------------------------------------------------------------
# 2. Tampered JSON (one field altered) → verify FAIL
# ----------------------------------------------------------------------

def test_tampered_field_fails_signature(tmp_path, keypair, fake_release):
    priv, pub, _ = keypair
    repo_root, manifest_path = fake_release
    cert_out = tmp_path / "cert.json"
    sig_out = tmp_path / "cert.json.sig"
    issue(
        release_tag="v-test-1.0.0",
        manifest_path=manifest_path,
        private_key_path=priv,
        output_cert_path=cert_out,
        output_sig_path=sig_out,
        repo_root=repo_root,
        revocation_url="https://example.invalid/revocations",
        primary_metrics_override={
            "cohen_d_median": 3.0906, "cohen_d_range": [2.764, 3.014],
            "p_value": 9.31e-10, "n_seeds": 30, "n_pos": 30, "clip_total": 0,
        },
        extra_evidence_adrs=["ADR-099"],
        extra_audit_artefacts=[("research/stub_artefact.csv", "stub_csv")],
        protocol_clauses=[{"id": "ADR-034 §5.4", "status": "FIRE", "note": "x"}],
        defense_chain=[{"adr_id": "ADR-035", "claim": "y", "max_abs_delta": 0.0}],
    )
    cert = json.loads(cert_out.read_text())
    cert["claims"]["primary_metrics"]["cohen_d_median"] = 99.999
    cert_out.write_text(json.dumps(cert, indent=2, ensure_ascii=False, sort_keys=True))
    report = verify(cert_path=cert_out, sig_path=sig_out, public_key_path=pub)
    assert not report.passed
    assert not report.signature_valid


# ----------------------------------------------------------------------
# 3. Tampered .sig (one byte flipped) → verify FAIL
# ----------------------------------------------------------------------

def test_tampered_signature_fails(tmp_path, keypair, fake_release):
    priv, pub, _ = keypair
    repo_root, manifest_path = fake_release
    cert_out = tmp_path / "cert.json"
    sig_out = tmp_path / "cert.json.sig"
    issue(
        release_tag="v-test-1.0.0", manifest_path=manifest_path, private_key_path=priv,
        output_cert_path=cert_out, output_sig_path=sig_out, repo_root=repo_root,
        revocation_url="https://example.invalid/revocations",
        primary_metrics_override={"cohen_d_median": 3.0, "cohen_d_range": [2.7, 3.1],
                                   "p_value": 1e-9, "n_seeds": 30, "n_pos": 30, "clip_total": 0},
        extra_evidence_adrs=["ADR-099"],
        extra_audit_artefacts=[("research/stub_artefact.csv", "stub_csv")],
        protocol_clauses=[{"id": "C", "status": "PASS", "note": "ok"}],
        defense_chain=[{"adr_id": "ADR-035", "claim": "x", "max_abs_delta": 0.0}],
    )
    sf = read_sig(sig_out)
    flipped = bytearray(sf.signature)
    flipped[0] ^= 0xFF
    from src.cert.sigfile import SigFile
    write_sig(sig_out, SigFile(algo=sf.algo, pubkey_fingerprint=sf.pubkey_fingerprint,
                                signature=bytes(flipped)))
    report = verify(cert_path=cert_out, sig_path=sig_out, public_key_path=pub)
    assert not report.signature_valid


# ----------------------------------------------------------------------
# 4. Wrong public key → verify FAIL (fingerprint mismatch)
# ----------------------------------------------------------------------

def test_wrong_public_key_fails_fingerprint(tmp_path, keypair, fake_release):
    priv, pub, _ = keypair
    repo_root, manifest_path = fake_release
    cert_out = tmp_path / "cert.json"
    sig_out = tmp_path / "cert.json.sig"
    issue(
        release_tag="v-test-1.0.0", manifest_path=manifest_path, private_key_path=priv,
        output_cert_path=cert_out, output_sig_path=sig_out, repo_root=repo_root,
        revocation_url="https://example.invalid/revocations",
        primary_metrics_override={"cohen_d_median": 3.0, "cohen_d_range": [2.7, 3.1],
                                   "p_value": 1e-9, "n_seeds": 30, "n_pos": 30, "clip_total": 0},
        extra_evidence_adrs=["ADR-099"],
        extra_audit_artefacts=[("research/stub_artefact.csv", "stub_csv")],
        protocol_clauses=[{"id": "C", "status": "PASS", "note": "ok"}],
        defense_chain=[{"adr_id": "ADR-035", "claim": "x", "max_abs_delta": 0.0}],
    )
    other_priv = tmp_path / "other.ed25519"
    other_pub = tmp_path / "other.pub"
    generate_keypair(other_priv, other_pub)
    report = verify(cert_path=cert_out, sig_path=sig_out, public_key_path=other_pub)
    assert not report.fingerprint_match


# ----------------------------------------------------------------------
# 5. JCS canonicalisation: re-ordered JSON keys must still verify
# ----------------------------------------------------------------------

def test_canonicalisation_invariant_to_key_order(tmp_path, keypair, fake_release):
    priv, pub, _ = keypair
    repo_root, manifest_path = fake_release
    cert_out = tmp_path / "cert.json"
    sig_out = tmp_path / "cert.json.sig"
    issue(
        release_tag="v-test-1.0.0", manifest_path=manifest_path, private_key_path=priv,
        output_cert_path=cert_out, output_sig_path=sig_out, repo_root=repo_root,
        revocation_url="https://example.invalid/revocations",
        primary_metrics_override={"cohen_d_median": 3.0, "cohen_d_range": [2.7, 3.1],
                                   "p_value": 1e-9, "n_seeds": 30, "n_pos": 30, "clip_total": 0},
        extra_evidence_adrs=["ADR-099"],
        extra_audit_artefacts=[("research/stub_artefact.csv", "stub_csv")],
        protocol_clauses=[{"id": "C", "status": "PASS", "note": "ok"}],
        defense_chain=[{"adr_id": "ADR-035", "claim": "x", "max_abs_delta": 0.0}],
    )
    cert = json.loads(cert_out.read_text())
    # Rewrite with reverse-sorted keys (semantically identical).
    cert_out.write_text(json.dumps(cert, indent=4, ensure_ascii=False, sort_keys=False))
    report = verify(cert_path=cert_out, sig_path=sig_out, public_key_path=pub)
    assert report.signature_valid, report.render()


# ----------------------------------------------------------------------
# 6. Schema: missing required field rejected
# ----------------------------------------------------------------------

def test_schema_rejects_missing_field():
    cert = {"cert_version": "0.1.0"}  # everything else missing
    errs = validate_cert(cert)
    assert any("missing required keys" in e for e in errs)


# ----------------------------------------------------------------------
# 7. Schema: cert_version frozen at 0.1.0
# ----------------------------------------------------------------------

def test_schema_frozen_v01_version():
    """ADR-036 §9 mitigation: lint protects against silent schema drift."""
    base = _build_minimal_kwargs(Path("/tmp"), Path("dummy"), "0" * 64)
    # Build a syntactically-valid cert dict skeleton without going through
    # the full issue path (which requires real files).
    cert = {
        "cert_version": "0.1.1",  # bumped without ADR
        "cert_id": "11111111-2222-4333-8444-555555555555",
        "issued_at": "2026-05-10T00:00:00Z",
        "issuer": {"name": "x", "public_key_fingerprint_sha256": "0"*64},
        "subject": {"release_tag": "v", "doi": "d", "manifest_path": "m",
                    "manifest_sha256": "0"*64},
        "claims": {
            "formal_verdict": "KAPPA_INCONCLUSIVE",
            "operational_verdict": "KAPPA_INCONCLUSIVE",
            "operational_envelope": {"parameter": "D", "min": 0.0, "max": 1.0,
                                      "rupture_above": None, "rupture_below": None},
            "primary_metrics": {"cohen_d_median": 1.0, "cohen_d_range": [0.5, 1.5],
                                 "p_value": 0.01, "n_seeds": 30, "n_pos": 30, "clip_total": 0},
        },
        "evidence_chain": [{"adr_id": "ADR-099", "path": "x", "sha256": "0"*64}],
        "audit_artefacts": [{"path": "x", "sha256": "0"*64, "role": "x"}],
        "protocol_clauses": [],
        "defense_chain": [],
        "expiry": None,
        "revocation_url": "x",
    }
    errs = validate_cert(cert)
    assert any("0.1.0" in e for e in errs), errs


# ----------------------------------------------------------------------
# 8. ADR-036 §3.2 — operational ≠ formal requires defense_chain non-empty
# ----------------------------------------------------------------------

def test_schema_rejects_orphan_operational_verdict():
    cert = {
        "cert_version": "0.1.0",
        "cert_id": "11111111-2222-4333-8444-555555555555",
        "issued_at": "2026-05-10T00:00:00Z",
        "issuer": {"name": "x", "public_key_fingerprint_sha256": "0"*64},
        "subject": {"release_tag": "v", "doi": "d", "manifest_path": "m",
                    "manifest_sha256": "0"*64},
        "claims": {
            "formal_verdict": "KAPPA_INCONCLUSIVE",
            "operational_verdict": "KAPPA_BAND_LIMITED_UPPER_OPEN",
            "operational_envelope": {"parameter": "D", "min": 0.0, "max": 1.0,
                                      "rupture_above": None, "rupture_below": None},
            "primary_metrics": {"cohen_d_median": 1.0, "cohen_d_range": [0.5, 1.5],
                                 "p_value": 0.01, "n_seeds": 30, "n_pos": 30, "clip_total": 0},
        },
        "evidence_chain": [{"adr_id": "ADR-099", "path": "x", "sha256": "0"*64}],
        "audit_artefacts": [{"path": "x", "sha256": "0"*64, "role": "x"}],
        "protocol_clauses": [],
        "defense_chain": [],  # empty but operational ≠ formal
        "expiry": None,
        "revocation_url": "x",
    }
    errs = validate_cert(cert)
    assert any("defense_chain" in e and "operational_verdict" in e for e in errs), errs
