#!/usr/bin/env python3
"""ADR-036 Phase 4 — issue the rétrofit certificate for v0.6.0-h7-κ-boundary.

Wraps src.cert.issue.issue() with the explicit per-release inputs that
ADR-036 §6.3 requires: primary metrics, evidence ADR list, audit
artefacts, protocol clauses, and defense chain.

Output:
  research/cae-cert-v0.6.0.v01.json
  research/cae-cert-v0.6.0.v01.json.sig

After issuance, verify with:
  python -m src.cert.verify \\
    --cert research/cae-cert-v0.6.0.v01.json \\
    --sig  research/cae-cert-v0.6.0.v01.json.sig \\
    --public-key keys/cae-cert-issuer.pub \\
    --repo-root .
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from src.cert.issue import issue

REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_KEY = Path("~/.cae-keys/cae-cert-issuer.ed25519").expanduser()


def main() -> int:
    cert_path, sig_path = issue(
        release_tag="v0.6.0-h7-κ-boundary",
        manifest_path=Path("research/MANIFEST.v0.6.0.yaml"),
        private_key_path=PRIVATE_KEY,
        output_cert_path=REPO_ROOT / "research" / "cae-cert-v0.6.0.v01.json",
        output_sig_path=REPO_ROOT / "research" / "cae-cert-v0.6.0.v01.json.sig",
        repo_root=REPO_ROOT,
        issuer_name="CAE Project (self-issued, v0.1 governance)",
        revocation_url="https://github.com/CAE-Project/CaePivot/releases/tag/cert-revocations",
        notes=(
            "Rétrofit certificate for the published v0.6.0 release. "
            "Operational verdict KAPPA_BAND_LIMITED_UPPER_OPEN is defended "
            "by ADR-035 byte-identity on pool [2000-2029] @ D=0.080. "
            "Formal verdict KAPPA_INCONCLUSIVE remains the published "
            "scientific status per ADR-034 §5.4 (concordance v0.5.0 = "
            "3.85% > 1% override)."
        ),
        # ADR-036 §3.1.5 — primary metrics. Cohen d median = v0.5.0 reference
        # at D=0.080 (calibrated headline); range = v0.6.0 sweep envelope min/max.
        primary_metrics_override={
            "cohen_d_median": 3.090641237972993,        # v0.5.0 ref @ D=0.080
            "cohen_d_range": [2.763514822944643,        # v0.6.0 D=0.040
                              3.013621930330641],        # v0.6.0 D=0.160
            "p_value": 1.862645149230957e-09,            # max p across envelope
            "n_seeds": 30,
            "n_pos": 30,                                  # at reference D=0.080
            "clip_total": 0,
        },
        extra_evidence_adrs=[
            "ADR-030",  # H7-κ pre-registration
            "ADR-032",  # H7-κ portability E₁
            "ADR-033",  # audit gate doctrine
            "ADR-034",  # boundary of validity (the v0.6.0 pre-reg)
            "ADR-035",  # seed-paired replication v0.5.0 (the defense)
            "ADR-036",  # CAE-Cert protocol (this protocol itself)
        ],
        extra_audit_artefacts=[
            ("research/h7_kappa_boundary_sweep.csv", "primary_sweep_csv"),
            ("research/h7_kappa_boundary_verdict.json", "verdict_json"),
            ("research/h7_kappa_audit_HEAD_pre_v060.csv", "audit_gate_csv"),
            ("research/h7_kappa_audit_HEAD_pre_v060.report.txt", "audit_gate_report"),
            ("research/h7_kappa_replication_v060.csv", "adr035_replication_csv"),
            ("research/h7_kappa_replication_v060.report.txt", "adr035_replication_report"),
            ("research/h7_kappa_portability.csv", "v050_reference_csv"),
        ],
        # ADR-036 §3.1.7 — protocol clauses status snapshot.
        # Six AND criteria of ADR-034 §3.4 + the §5.4 override + the §5.1 path.
        protocol_clauses=[
            {"id": "ADR-034 §3.4 alpha=0.005",      "status": "PASS",
             "note": "all 6 envelope grid-points p < 1.86e-9"},
            {"id": "ADR-034 §3.4 cohen_d_min=0.5",  "status": "PASS",
             "note": "envelope min d = 2.764 > 0.5"},
            {"id": "ADR-034 §3.4 n_positive_min=25", "status": "PASS",
             "note": "envelope min n_pos = 29/30 > 25"},
            {"id": "ADR-034 §3.4 clip_events_max=0", "status": "PASS",
             "note": "0 clip events across full sweep (210 runs)"},
            {"id": "ADR-034 §3.4 both_branches_must_agree", "status": "PASS",
             "note": "intra-sample corr/naive max disagreement = 4.1e-06"},
            {"id": "ADR-034 §3.4 D_080_must_pass",   "status": "PASS",
             "note": "n_pos=30, d=2.972, p=9.31e-10 at D=0.080"},
            {"id": "ADR-034 §5.4 concordance_v050 ≤ 1%", "status": "FIRE",
             "note": ("observed concordance = 3.85% > 1% threshold; "
                      "this single criterion override forces formal "
                      "scientific_status = KAPPA_INCONCLUSIVE per "
                      "pre-registration verbatim")},
            {"id": "ADR-035 §5.1 byte-identity path", "status": "PASS",
             "note": ("HEAD CSV byte-for-byte identical to v0.5.0 reference "
                      "on pool [2000-2029] @ D=0.080; max|Δ_float|=0.0; "
                      "defends operational envelope as sampling noise")},
        ],
        # ADR-036 §3.1.8 — defense_chain: only required when
        # operational_verdict ≠ formal_verdict (which is the case here).
        defense_chain=[
            {"adr_id": "ADR-035",
             "claim": ("HEAD CSV byte-identical to v0.5.0 ref on pool "
                       "[2000-2029] @ D=0.080 (max|Δ|=0.0); the 3.85% "
                       "inter-pool concordance gap triggering ADR-034 §5.4 "
                       "is sampling noise (~0.46σ, disjoint n=30), not "
                       "engine drift; defends envelope D∈[0.005,0.320]"),
             "max_abs_delta": 0.0},
            {"adr_id": "ADR-033",
             "claim": ("HEAD audit gate on E₀ pool [1500-1529] reproduces "
                       "audit-passed-v1 reference under atol=1e-9 rtol=0; "
                       "max|Δ_float|=4.5e-11; no drift in src/env, "
                       "src/agents, src/metrics, src/analysis/sigma_chain.py"),
             "max_abs_delta": 4.5e-11},
        ],
        issued_at=datetime(2026, 5, 10, 18, 0, 0, tzinfo=timezone.utc),
    )
    print(f"cert: {cert_path}")
    print(f"sig : {sig_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
