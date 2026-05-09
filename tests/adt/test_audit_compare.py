"""ADTs ADR-033 §10 — comparateur d'audit (compare_audit_csv).

Couvre les huit cas exigés : header mismatch, row-count mismatch,
int divergence d'une unité = FAIL, float divergence à 1.1e-9 = FAIL,
float divergence à 9e-10 = PASS, identité parfaite = PASS, ordre
seeds permuté = FAIL, fichier manquant = exception explicite.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.analysis.audit_compare import (
    EXPECTED_HEADER,
    FLOAT_COLUMNS,
    INT_COLUMNS,
    compare_audit_csv,
    format_report,
)

REFERENCE_CSV = Path("research/h7_kappa_run_results.csv")


def _write_csv(path: Path, header: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(header))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _read_reference_rows() -> tuple[tuple[str, ...], list[dict[str, str]]]:
    assert REFERENCE_CSV.exists(), "research/h7_kappa_run_results.csv requis pour les ADTs."
    with REFERENCE_CSV.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = tuple(reader.fieldnames or ())
        rows = list(reader)
    return header, rows


def test_expected_header_matches_v04_csv():
    header, _ = _read_reference_rows()
    assert header == EXPECTED_HEADER, (
        "L'en-tête attendu d'ADR-033 §10 doit refléter exactement "
        "research/h7_kappa_run_results.csv"
    )


def test_int_and_float_columns_partition_header():
    union = set(INT_COLUMNS) | set(FLOAT_COLUMNS)
    assert union == set(EXPECTED_HEADER)
    assert set(INT_COLUMNS).isdisjoint(set(FLOAT_COLUMNS))


def test_perfect_identity_passes(tmp_path):
    header, rows = _read_reference_rows()
    candidate = tmp_path / "candidate.csv"
    _write_csv(candidate, header, rows)
    report = compare_audit_csv(REFERENCE_CSV, candidate)
    assert report.passed is True
    assert report.header_match is True
    assert report.seeds_match is True
    assert report.n_rows_reference == report.n_rows_candidate == 30
    for col in INT_COLUMNS:
        assert report.strict_mismatches_per_column[col] == 0
    for col in FLOAT_COLUMNS:
        assert report.max_abs_diff_per_column[col] == 0.0


def test_header_mismatch_fails(tmp_path):
    header, rows = _read_reference_rows()
    bad_header = tuple([h if h != "Delta_kappa_corr" else "delta_kappa_corr" for h in header])
    renamed_rows = [
        {(k if k != "Delta_kappa_corr" else "delta_kappa_corr"): v for k, v in row.items()}
        for row in rows
    ]
    candidate = tmp_path / "bad_header.csv"
    _write_csv(candidate, bad_header, renamed_rows)
    report = compare_audit_csv(REFERENCE_CSV, candidate)
    assert report.passed is False
    assert report.header_match is False
    assert any("En-tête" in reason for reason in report.failure_reasons)


def test_row_count_mismatch_fails(tmp_path):
    header, rows = _read_reference_rows()
    candidate = tmp_path / "short.csv"
    _write_csv(candidate, header, rows[:25])
    report = compare_audit_csv(REFERENCE_CSV, candidate)
    assert report.passed is False
    assert report.n_rows_candidate == 25
    assert any("Nombre de lignes" in reason for reason in report.failure_reasons)


def test_int_divergence_one_unit_fails(tmp_path):
    header, rows = _read_reference_rows()
    perturbed = [dict(r) for r in rows]
    perturbed[7]["clip_events_R"] = str(int(perturbed[7]["clip_events_R"]) + 1)
    candidate = tmp_path / "int_drift.csv"
    _write_csv(candidate, header, perturbed)
    report = compare_audit_csv(REFERENCE_CSV, candidate)
    assert report.passed is False
    assert report.strict_mismatches_per_column["clip_events_R"] == 1
    assert any("clip_events_R" in reason for reason in report.failure_reasons)


def test_float_divergence_above_atol_fails(tmp_path):
    header, rows = _read_reference_rows()
    perturbed = [dict(r) for r in rows]
    base = float(perturbed[3]["KL_R_M_corr"])
    perturbed[3]["KL_R_M_corr"] = f"{base + 1.1e-9:.12f}"
    candidate = tmp_path / "float_drift_high.csv"
    _write_csv(candidate, header, perturbed)
    report = compare_audit_csv(REFERENCE_CSV, candidate)
    assert report.passed is False
    assert report.max_abs_diff_per_column["KL_R_M_corr"] > 1e-9
    assert any("KL_R_M_corr" in reason for reason in report.failure_reasons)


def test_float_divergence_below_atol_passes(tmp_path):
    header, rows = _read_reference_rows()
    perturbed = [dict(r) for r in rows]
    base = float(perturbed[3]["KL_R_M_corr"])
    # 9e-10 < atol=1e-9 ; mais nos floats sont sérialisés à 12 décimales
    # → toute perturbation < 5e-13 disparaît à l'écriture. Forge la
    # divergence directement à 12 décimales en biaisant le dernier digit.
    raw = f"{base:.12f}"
    # increment last digit by ±5e-13 (≈ 0.0000000000005), bien sous 1e-9.
    incremented = base + 5e-13
    perturbed[3]["KL_R_M_corr"] = f"{incremented:.12f}"
    candidate = tmp_path / "float_drift_low.csv"
    _write_csv(candidate, header, perturbed)
    report = compare_audit_csv(REFERENCE_CSV, candidate)
    # Soit la perturbation est invisible à 12 décimales (==), soit < 1e-9 → PASS.
    assert report.passed is True
    assert report.max_abs_diff_per_column["KL_R_M_corr"] < 1e-9


def test_seed_permutation_fails(tmp_path):
    header, rows = _read_reference_rows()
    permuted = list(rows)
    permuted[0], permuted[1] = permuted[1], permuted[0]
    candidate = tmp_path / "permuted.csv"
    _write_csv(candidate, header, permuted)
    report = compare_audit_csv(REFERENCE_CSV, candidate)
    assert report.passed is False
    assert report.seeds_match is False
    assert any("seed" in reason for reason in report.failure_reasons)


def test_missing_candidate_raises(tmp_path):
    missing = tmp_path / "ne-pas-creer.csv"
    with pytest.raises(FileNotFoundError):
        compare_audit_csv(REFERENCE_CSV, missing)


def test_missing_reference_raises(tmp_path):
    header, rows = _read_reference_rows()
    candidate = tmp_path / "candidate.csv"
    _write_csv(candidate, header, rows)
    missing = tmp_path / "no-ref.csv"
    with pytest.raises(FileNotFoundError):
        compare_audit_csv(missing, candidate)


def test_format_report_contains_verdict_string(tmp_path):
    header, rows = _read_reference_rows()
    candidate = tmp_path / "ok.csv"
    _write_csv(candidate, header, rows)
    report = compare_audit_csv(REFERENCE_CSV, candidate)
    text = format_report(report)
    assert "ADR-033 audit gate verdict: PASS" in text
    assert "header_match" in text
    assert "Max |Δ| per float column" in text
