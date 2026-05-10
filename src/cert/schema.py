"""ADR-036 §3 — strict validation of cae-cert.v01.json.

Stdlib only. Returns a list of error strings; empty == valid.
"""
from __future__ import annotations

import re
from typing import Any

# ADR-036 §3.1 — closed enums.
FORMAL_VERDICTS = frozenset({
    "KAPPA_TRANSFERS",
    "KAPPA_FAILS_TRANSFER",
    "KAPPA_INCONCLUSIVE",
    "KAPPA_INCONCLUSIVE_CONFIRMED",
    "KAPPA_BAND_LIMITED",
    "KAPPA_FRAGILE",
    "KAPPA_ROBUST_PORTABILITY",
})
OPERATIONAL_VERDICTS = FORMAL_VERDICTS | frozenset({
    "KAPPA_BAND_LIMITED_UPPER_OPEN",
    "KAPPA_BAND_LIMITED_LOWER_OPEN",
})
CLAUSE_STATUSES = frozenset({"PASS", "FIRE", "N/A"})

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_UUID_V4 = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_ISO_8601_Z = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$"
)
_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _err(errs: list[str], path: str, msg: str) -> None:
    errs.append(f"{path}: {msg}")


def _check_hex64(errs: list[str], path: str, val: Any) -> None:
    if not isinstance(val, str) or not _HEX64.match(val):
        _err(errs, path, "expected lowercase hex sha256 (64 chars)")


def _check_str(errs: list[str], path: str, val: Any, max_len: int | None = None) -> None:
    if not isinstance(val, str):
        _err(errs, path, "expected string")
    elif max_len is not None and len(val) > max_len:
        _err(errs, path, f"exceeds max length {max_len}")


def _check_required_keys(errs: list[str], path: str, obj: Any, keys: tuple[str, ...]) -> bool:
    if not isinstance(obj, dict):
        _err(errs, path, "expected object")
        return False
    missing = [k for k in keys if k not in obj]
    if missing:
        _err(errs, path, f"missing required keys: {missing}")
        return False
    return True


def validate_cert(cert: Any) -> list[str]:
    """Return list of validation errors. Empty list == valid CAE-Cert v0.1.

    Implements ADR-036 §3.1 (structure), §3.2 (constraints), §3.3 (canonicalisation
    is enforced at sign/verify time, not here).
    """
    errs: list[str] = []
    top = ("cert_version", "cert_id", "issued_at", "issuer", "subject",
           "claims", "evidence_chain", "audit_artefacts", "protocol_clauses",
           "defense_chain", "expiry", "revocation_url")
    if not _check_required_keys(errs, "$", cert, top):
        return errs

    if cert["cert_version"] != "0.1.0":
        _err(errs, "$.cert_version", "must be exactly '0.1.0' for v0.1 schema")
    if not isinstance(cert["cert_id"], str) or not _UUID_V4.match(cert["cert_id"]):
        _err(errs, "$.cert_id", "expected UUID v4")
    if not isinstance(cert["issued_at"], str) or not _ISO_8601_Z.match(cert["issued_at"]):
        _err(errs, "$.issued_at", "expected ISO 8601 UTC with Z suffix")

    if _check_required_keys(errs, "$.issuer", cert["issuer"],
                            ("name", "public_key_fingerprint_sha256")):
        _check_str(errs, "$.issuer.name", cert["issuer"]["name"], 256)
        _check_hex64(errs, "$.issuer.public_key_fingerprint_sha256",
                     cert["issuer"]["public_key_fingerprint_sha256"])

    if _check_required_keys(errs, "$.subject", cert["subject"],
                            ("release_tag", "doi", "manifest_path", "manifest_sha256")):
        _check_str(errs, "$.subject.release_tag", cert["subject"]["release_tag"], 256)
        _check_str(errs, "$.subject.doi", cert["subject"]["doi"], 256)
        _check_str(errs, "$.subject.manifest_path", cert["subject"]["manifest_path"], 1024)
        _check_hex64(errs, "$.subject.manifest_sha256", cert["subject"]["manifest_sha256"])

    _validate_claims(errs, cert["claims"])

    if not isinstance(cert["evidence_chain"], list) or len(cert["evidence_chain"]) < 1:
        _err(errs, "$.evidence_chain", "must be a non-empty list")
    else:
        for i, ev in enumerate(cert["evidence_chain"]):
            p = f"$.evidence_chain[{i}]"
            if _check_required_keys(errs, p, ev, ("adr_id", "path", "sha256")):
                _check_str(errs, f"{p}.adr_id", ev["adr_id"], 64)
                _check_str(errs, f"{p}.path", ev["path"], 1024)
                _check_hex64(errs, f"{p}.sha256", ev["sha256"])

    if not isinstance(cert["audit_artefacts"], list) or len(cert["audit_artefacts"]) < 1:
        _err(errs, "$.audit_artefacts", "must be a non-empty list")
    else:
        for i, art in enumerate(cert["audit_artefacts"]):
            p = f"$.audit_artefacts[{i}]"
            if _check_required_keys(errs, p, art, ("path", "sha256", "role")):
                _check_str(errs, f"{p}.path", art["path"], 1024)
                _check_hex64(errs, f"{p}.sha256", art["sha256"])
                _check_str(errs, f"{p}.role", art["role"], 64)

    if not isinstance(cert["protocol_clauses"], list):
        _err(errs, "$.protocol_clauses", "must be a list")
    else:
        for i, cl in enumerate(cert["protocol_clauses"]):
            p = f"$.protocol_clauses[{i}]"
            if _check_required_keys(errs, p, cl, ("id", "status", "note")):
                _check_str(errs, f"{p}.id", cl["id"], 128)
                if cl["status"] not in CLAUSE_STATUSES:
                    _err(errs, f"{p}.status", f"must be one of {sorted(CLAUSE_STATUSES)}")
                _check_str(errs, f"{p}.note", cl["note"], 280)
                # ADR-036 §3.2: FIRE clause requires non-trivial note
                if cl.get("status") == "FIRE" and isinstance(cl.get("note"), str) and not cl["note"].strip():
                    _err(errs, f"{p}.note", "FIRE clause requires non-empty note (ADR-036 §3.2)")

    if not isinstance(cert["defense_chain"], list):
        _err(errs, "$.defense_chain", "must be a list (possibly empty)")
    else:
        for i, df in enumerate(cert["defense_chain"]):
            p = f"$.defense_chain[{i}]"
            if _check_required_keys(errs, p, df, ("adr_id", "claim", "max_abs_delta")):
                _check_str(errs, f"{p}.adr_id", df["adr_id"], 64)
                _check_str(errs, f"{p}.claim", df["claim"], 280)
                if df["max_abs_delta"] is not None and not isinstance(df["max_abs_delta"], (int, float)):
                    _err(errs, f"{p}.max_abs_delta", "expected float or null")

    # ADR-036 §3.2: operational ≠ formal requires non-empty defense_chain
    claims = cert.get("claims", {})
    fv = claims.get("formal_verdict")
    ov = claims.get("operational_verdict")
    if ov is not None and ov != fv and isinstance(cert["defense_chain"], list) and len(cert["defense_chain"]) == 0:
        _err(errs, "$.defense_chain",
             "must be non-empty when operational_verdict differs from formal_verdict (ADR-036 §3.2)")

    if cert["expiry"] is not None:
        _err(errs, "$.expiry", "must be null in v0.1 (reserved for v0.2+)")

    _check_str(errs, "$.revocation_url", cert["revocation_url"], 1024)
    if "notes" in cert and cert["notes"] is not None:
        _check_str(errs, "$.notes", cert["notes"], 4096)

    return errs


def _validate_claims(errs: list[str], claims: Any) -> None:
    if not _check_required_keys(errs, "$.claims", claims,
                                ("formal_verdict", "operational_verdict",
                                 "operational_envelope", "primary_metrics")):
        return
    if claims["formal_verdict"] not in FORMAL_VERDICTS:
        _err(errs, "$.claims.formal_verdict",
             f"must be one of {sorted(FORMAL_VERDICTS)}")
    if claims["operational_verdict"] is not None and claims["operational_verdict"] not in OPERATIONAL_VERDICTS:
        _err(errs, "$.claims.operational_verdict",
             f"must be null or one of {sorted(OPERATIONAL_VERDICTS)}")

    env = claims["operational_envelope"]
    if _check_required_keys(errs, "$.claims.operational_envelope", env,
                            ("parameter", "min", "max", "rupture_above", "rupture_below")):
        _check_str(errs, "$.claims.operational_envelope.parameter", env["parameter"], 64)
        for k in ("min", "max", "rupture_above", "rupture_below"):
            v = env[k]
            if v is not None and not isinstance(v, (int, float)):
                _err(errs, f"$.claims.operational_envelope.{k}", "expected float or null")

    pm = claims["primary_metrics"]
    if _check_required_keys(errs, "$.claims.primary_metrics", pm,
                            ("cohen_d_median", "cohen_d_range", "p_value",
                             "n_seeds", "n_pos", "clip_total")):
        for k in ("cohen_d_median", "p_value"):
            v = pm[k]
            if v is not None and not isinstance(v, (int, float)):
                _err(errs, f"$.claims.primary_metrics.{k}", "expected float or null")
        for k in ("n_seeds", "n_pos", "clip_total"):
            v = pm[k]
            if v is not None and not isinstance(v, int):
                _err(errs, f"$.claims.primary_metrics.{k}", "expected int or null")
        rng = pm["cohen_d_range"]
        if rng is not None:
            if (not isinstance(rng, list) or len(rng) != 2
                    or not all(isinstance(x, (int, float)) for x in rng)):
                _err(errs, "$.claims.primary_metrics.cohen_d_range",
                     "expected [float, float] or null")
