"""ADR-033 §10 — comparateur d'audit pour la chaîne σ_κ publique.

Compare un CSV produit par src.experiments.portability_draw (--pool audit)
au CSV de référence research/h7_kappa_run_results.csv (verdict v0.4.0).

Tolérances figées par ADR-033 §4 :
- Colonnes entières : égalité stricte (`==`).
- Colonnes flottantes : np.isclose(atol=1e-9, rtol=0).

Sortie binaire (PASS/FAIL). Toute divergence d'un seul élément d'une
colonne entière, ou une divergence flottante > atol, est éliminatoire.
"""
from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# Conforme ADR-033 §4.1.
INT_COLUMNS: tuple[str, ...] = (
    "seed",
    "T_warmup",
    "T_stat",
    "B",
    "K_R_nonempty",
    "K_S_nonempty",
    "K_M_nonempty",
    "K_Mk_nonempty",
    "laplace_bins_R",
    "laplace_bins_S",
    "laplace_bins_Mk",
    "clip_events_R",
    "clip_events_S",
    "clip_events_M",
    "clip_events_Mk",
)

# Conforme ADR-033 §4.2.
FLOAT_COLUMNS: tuple[str, ...] = (
    "P_min",
    "P_max",
    "KL_R_M_corr",
    "KL_S_M_corr",
    "KL_Mk_M_corr",
    "KL_R_M_naive",
    "KL_S_M_naive",
    "KL_Mk_M_naive",
    "delta_sigma_R_corr",
    "delta_sigma_Mk_corr",
    "delta_sigma_R_naive",
    "delta_sigma_Mk_naive",
    "Delta_kappa_corr",
    "Delta_kappa_naive",
)

EXPECTED_HEADER: tuple[str, ...] = (
    "seed",
    "T_warmup",
    "T_stat",
    "B",
    "P_min",
    "P_max",
    "KL_R_M_corr",
    "KL_S_M_corr",
    "KL_Mk_M_corr",
    "KL_R_M_naive",
    "KL_S_M_naive",
    "KL_Mk_M_naive",
    "delta_sigma_R_corr",
    "delta_sigma_Mk_corr",
    "delta_sigma_R_naive",
    "delta_sigma_Mk_naive",
    "Delta_kappa_corr",
    "Delta_kappa_naive",
    "K_R_nonempty",
    "K_S_nonempty",
    "K_M_nonempty",
    "K_Mk_nonempty",
    "laplace_bins_R",
    "laplace_bins_S",
    "laplace_bins_Mk",
    "clip_events_R",
    "clip_events_S",
    "clip_events_M",
    "clip_events_Mk",
)

DEFAULT_FLOAT_ATOL: float = 1e-9


@dataclass(frozen=True)
class AuditReport:
    passed: bool
    header_match: bool
    n_rows_reference: int
    n_rows_candidate: int
    seeds_match: bool
    max_abs_diff_per_column: dict[str, float] = field(default_factory=dict)
    strict_mismatches_per_column: dict[str, int] = field(default_factory=dict)
    failure_reasons: tuple[str, ...] = ()


def _load_csv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV introuvable : {path}")
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"En-tête CSV vide : {path}")
        header = tuple(reader.fieldnames)
        rows = list(reader)
    return header, rows


def compare_audit_csv(
    reference_path: str | Path,
    candidate_path: str | Path,
    *,
    int_columns: tuple[str, ...] = INT_COLUMNS,
    float_columns: tuple[str, ...] = FLOAT_COLUMNS,
    float_atol: float = DEFAULT_FLOAT_ATOL,
) -> AuditReport:
    """Compare candidate au reference selon ADR-033 §4. Lance FileNotFoundError si absent."""
    reference_path = Path(reference_path)
    candidate_path = Path(candidate_path)

    ref_header, ref_rows = _load_csv(reference_path)
    can_header, can_rows = _load_csv(candidate_path)

    failures: list[str] = []
    header_match = ref_header == can_header
    if not header_match:
        failures.append(
            f"En-tête divergent : ref={ref_header} vs candidate={can_header}"
        )

    n_ref = len(ref_rows)
    n_can = len(can_rows)
    if n_ref != n_can:
        failures.append(f"Nombre de lignes divergent : ref={n_ref} vs candidate={n_can}")

    seeds_match = False
    if header_match and n_ref == n_can:
        ref_seeds = [int(r["seed"]) for r in ref_rows]
        can_seeds = [int(r["seed"]) for r in can_rows]
        seeds_match = ref_seeds == can_seeds
        if not seeds_match:
            failures.append(
                "Colonne 'seed' divergente (ordre ou contenu) — comparaison ligne-à-ligne refusée."
            )

    max_abs_diff: dict[str, float] = {}
    strict_mismatches: dict[str, int] = {}

    if header_match and n_ref == n_can and seeds_match:
        for col in int_columns:
            mismatches = 0
            for r_row, c_row in zip(ref_rows, can_rows):
                if int(r_row[col]) != int(c_row[col]):
                    mismatches += 1
            strict_mismatches[col] = mismatches
            if mismatches > 0:
                failures.append(
                    f"Colonne entière '{col}' : {mismatches} divergence(s) stricte(s)."
                )

        for col in float_columns:
            ref_vals = np.array([float(r[col]) for r in ref_rows], dtype=np.float64)
            can_vals = np.array([float(r[col]) for r in can_rows], dtype=np.float64)
            diff = np.abs(ref_vals - can_vals)
            max_diff = float(diff.max()) if diff.size > 0 else 0.0
            max_abs_diff[col] = max_diff
            if max_diff > float_atol:
                failures.append(
                    f"Colonne flottante '{col}' : max |Δ| = {max_diff:.3e} > atol = {float_atol:.0e}."
                )

    passed = (
        header_match
        and n_ref == n_can
        and seeds_match
        and len(failures) == 0
    )

    return AuditReport(
        passed=passed,
        header_match=header_match,
        n_rows_reference=n_ref,
        n_rows_candidate=n_can,
        seeds_match=seeds_match,
        max_abs_diff_per_column=max_abs_diff,
        strict_mismatches_per_column=strict_mismatches,
        failure_reasons=tuple(failures),
    )


def format_report(report: AuditReport, float_atol: float = DEFAULT_FLOAT_ATOL) -> str:
    """Format texte stable (diff-friendly) du rapport."""
    lines: list[str] = []
    verdict = "PASS" if report.passed else "FAIL"
    lines.append(f"ADR-033 audit gate verdict: {verdict}")
    lines.append(f"  header_match           : {report.header_match}")
    lines.append(f"  n_rows_reference       : {report.n_rows_reference}")
    lines.append(f"  n_rows_candidate       : {report.n_rows_candidate}")
    lines.append(f"  seeds_match            : {report.seeds_match}")
    lines.append(f"  float_atol             : {float_atol:.0e}")
    lines.append("")
    lines.append("Strict mismatches per integer column:")
    for col in sorted(report.strict_mismatches_per_column):
        lines.append(
            f"  {col:24s} : {report.strict_mismatches_per_column[col]}"
        )
    lines.append("")
    lines.append("Max |Δ| per float column:")
    for col in sorted(report.max_abs_diff_per_column):
        lines.append(
            f"  {col:24s} : {report.max_abs_diff_per_column[col]:.3e}"
        )
    if report.failure_reasons:
        lines.append("")
        lines.append("Failure reasons:")
        for reason in report.failure_reasons:
            lines.append(f"  - {reason}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="ADR-033 audit gate : comparateur CSV chaîne σ_κ.",
    )
    parser.add_argument("--reference", required=True, help="CSV de référence (v0.4.0).")
    parser.add_argument("--candidate", required=True, help="CSV produit par le runner public.")
    parser.add_argument(
        "--report-output",
        default=None,
        help="Chemin optionnel pour persister le rapport texte.",
    )
    parser.add_argument(
        "--atol",
        type=float,
        default=DEFAULT_FLOAT_ATOL,
        help="Tolérance absolue flottante (défaut : 1e-9, ADR-033 §4.2).",
    )
    args = parser.parse_args(argv)

    report = compare_audit_csv(
        args.reference,
        args.candidate,
        float_atol=args.atol,
    )
    text = format_report(report, float_atol=args.atol)
    sys.stdout.write(text)
    if args.report_output is not None:
        Path(args.report_output).write_text(text, encoding="utf-8")
    return 0 if report.passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
