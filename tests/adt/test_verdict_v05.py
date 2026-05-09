"""ADT — verdict_v05 (la guillotine ADR-032 §6).

Tests construits avec des CSVs synthétiques où le verdict attendu est
prouvable analytiquement. Couvre §6.1 (TRANSFERS), §6.2 (FAILS), §6.3
(BOUNDED), §6.5 (INCONCLUSIVE override sous tous ses angles).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from src.analysis.verdict_v05 import (
    D_FAILS_MAX,
    D_TRANSFERS_MIN,
    N_POSITIVE_FAILS_MAX,
    N_POSITIVE_TRANSFERS_MIN,
    N_SEEDS_EXPECTED,
    OOM_FACTOR,
    P_FAILS_MIN,
    P_TRANSFERS_MAX,
    REQUIRED_COLUMNS,
    compute_verdict,
)


# ----------------------------------------------------------------------
# Helpers : fabrication de CSV synthétiques
# ----------------------------------------------------------------------

def _write_csv(
    path: Path,
    deltas_corr: np.ndarray,
    deltas_naive: np.ndarray | None = None,
    clip_R: int = 0,
    clip_S: int = 0,
    clip_M: int = 0,
    clip_Mk: int = 0,
) -> None:
    """Écrit un CSV minimal au schéma v0.4.0 attendu par compute_verdict."""
    if deltas_naive is None:
        deltas_naive = deltas_corr.copy()
    n = deltas_corr.size
    assert deltas_naive.size == n

    rows = []
    for i in range(n):
        rows.append({
            "seed": 2000 + i,
            "Delta_kappa_corr": f"{deltas_corr[i]:.10f}",
            "Delta_kappa_naive": f"{deltas_naive[i]:.10f}",
            "clip_events_R": clip_R if i == 0 else 0,
            "clip_events_S": clip_S if i == 0 else 0,
            "clip_events_M": clip_M if i == 0 else 0,
            "clip_events_Mk": clip_Mk if i == 0 else 0,
        })

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(REQUIRED_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)


def _strong_positive_deltas(n: int = 30, seed: int = 0) -> np.ndarray:
    """Génère un set 'parfait' : effet large, p<<1e-4, tous positifs.
    Avec n=30, deltas tous ≈ 1.0 ± petit bruit → d >> 1, p infime."""
    rng = np.random.default_rng(seed)
    return 1.0 + rng.normal(0.0, 0.1, size=n)


def _weak_positive_deltas(n: int = 30, seed: int = 0) -> np.ndarray:
    """Effet modéré : d ∈ [0.3, 1.0), un peu de bruit qui pousse vers BOUNDED."""
    rng = np.random.default_rng(seed)
    return 0.5 + rng.normal(0.0, 1.0, size=n)


def _trivial_deltas(n: int = 30, seed: int = 0) -> np.ndarray:
    """Effet absent : centré sur 0, signe aléatoire → d ≈ 0, FAILS."""
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, 1.0, size=n)


# ----------------------------------------------------------------------
# §6.1 — KAPPA_TRANSFERS
# ----------------------------------------------------------------------

def test_perfect_set_yields_transfers(tmp_path: Path) -> None:
    deltas = _strong_positive_deltas(n=30, seed=42)
    csv_path = tmp_path / "perfect.csv"
    _write_csv(csv_path, deltas)

    report = compute_verdict(csv_path)

    assert report.label == "KAPPA_TRANSFERS"
    assert report.nominal_label == "KAPPA_TRANSFERS"
    assert report.branch_corrected.sub_label == "KAPPA_TRANSFERS"
    assert report.branch_naive.sub_label == "KAPPA_TRANSFERS"
    assert report.branch_corrected.cohen_d >= D_TRANSFERS_MIN
    assert report.branch_corrected.p_greater <= P_TRANSFERS_MAX
    assert report.branch_corrected.n_positive >= N_POSITIVE_TRANSFERS_MIN
    assert report.clip_events_total == 0
    assert report.inconclusive_reasons == []


# ----------------------------------------------------------------------
# §6.2 — KAPPA_FAILS_TRANSFER
# ----------------------------------------------------------------------

def test_trivial_set_yields_fails(tmp_path: Path) -> None:
    deltas = _trivial_deltas(n=30, seed=1)
    csv_path = tmp_path / "trivial.csv"
    _write_csv(csv_path, deltas)

    report = compute_verdict(csv_path)
    assert report.label == "KAPPA_FAILS_TRANSFER"
    assert report.branch_corrected.sub_label == "KAPPA_FAILS_TRANSFER"


def test_low_positive_count_yields_fails(tmp_path: Path) -> None:
    """< 18/30 positifs déclenche FAILS même avec un grand effet sur les positifs."""
    deltas = np.concatenate([
        np.full(15, 5.0),    # 15 très positifs
        np.full(15, -0.001),  # 15 négatifs petits
    ])
    csv_path = tmp_path / "few_positive.csv"
    _write_csv(csv_path, deltas)

    report = compute_verdict(csv_path)
    assert report.branch_corrected.n_positive == 15
    assert report.branch_corrected.n_positive < N_POSITIVE_FAILS_MAX
    assert report.label == "KAPPA_FAILS_TRANSFER"


# ----------------------------------------------------------------------
# §6.3 — KAPPA_BOUNDED
# ----------------------------------------------------------------------

def test_moderate_set_yields_bounded(tmp_path: Path) -> None:
    """Effet modéré construit déterministiquement :
    22 positifs (∈ [18, 25)), 8 négatifs, d ≈ 0.6 (∈ [0.3, 1.0)), p < 1e-2.
    Aucune des règles §6.1 ni §6.2 n'est satisfaite → §6.3 BOUNDED."""
    deltas = np.concatenate([
        np.linspace(0.05, 0.75, 22),  # 22 positifs distincts, moy ≈ 0.4
        np.linspace(-0.5, -0.1, 8),   # 8 négatifs distincts, moy ≈ -0.3
    ])
    csv_path = tmp_path / "moderate.csv"
    _write_csv(csv_path, deltas)

    report = compute_verdict(csv_path)
    n_pos = report.branch_corrected.n_positive
    d = report.branch_corrected.cohen_d
    assert n_pos == 22
    assert N_POSITIVE_FAILS_MAX <= n_pos < N_POSITIVE_TRANSFERS_MIN
    assert D_FAILS_MAX <= d < D_TRANSFERS_MIN, f"sanity: d={d}"
    assert report.label == "KAPPA_BOUNDED"


# ----------------------------------------------------------------------
# §6.5 — Override INCONCLUSIVE
# ----------------------------------------------------------------------

def test_clip_events_override_to_inconclusive(tmp_path: Path) -> None:
    """Un seul clip_event suffit à déclencher l'override §6.5."""
    deltas = _strong_positive_deltas(n=30, seed=42)
    csv_path = tmp_path / "with_clip.csv"
    _write_csv(csv_path, deltas, clip_R=1)

    report = compute_verdict(csv_path)

    # Verdict nominal aurait été TRANSFERS, mais override force INCONCLUSIVE.
    assert report.nominal_label == "KAPPA_TRANSFERS"
    assert report.label == "KAPPA_INCONCLUSIVE"
    assert any("clip_events_total=1" in r for r in report.inconclusive_reasons)


def test_branch_disagreement_override_to_inconclusive(tmp_path: Path) -> None:
    """Une branche TRANSFERS, l'autre BOUNDED → INCONCLUSIVE."""
    rng = np.random.default_rng(0)
    strong = 1.0 + rng.normal(0.0, 0.1, size=30)
    moderate = 0.4 + rng.normal(0.0, 1.0, size=30)
    csv_path = tmp_path / "disagree.csv"
    _write_csv(csv_path, deltas_corr=strong, deltas_naive=moderate)

    report = compute_verdict(csv_path)

    assert report.branch_corrected.sub_label == "KAPPA_TRANSFERS"
    assert report.branch_naive.sub_label != "KAPPA_TRANSFERS"
    assert report.label == "KAPPA_INCONCLUSIVE"
    assert report.nominal_label == "DISAGREEMENT"
    assert any("désaccord" in r for r in report.inconclusive_reasons)


def test_oom_divergence_override_to_inconclusive(tmp_path: Path) -> None:
    """d_corr et d_naive diffèrent de plus d'1 ordre de grandeur → INCONCLUSIVE,
    même si les sub-labels coïncident (les deux peuvent être TRANSFERS si
    p et n_positive passent, mais l'OOM sur d est un signal de divergence
    de mesure)."""
    # Construire deux séries où sub_label = TRANSFERS pour les deux mais
    # d diffère beaucoup. Cas extrême : corr fort (d≈10), naive juste au seuil (d≈1).
    rng = np.random.default_rng(0)
    strong = 5.0 + rng.normal(0.0, 0.1, size=30)   # d ≈ 50
    barely = 1.0 + rng.normal(0.0, 0.5, size=30)   # d ≈ 2
    csv_path = tmp_path / "oom.csv"
    _write_csv(csv_path, deltas_corr=strong, deltas_naive=barely)

    report = compute_verdict(csv_path)
    # Ratio d_corr / d_naive >> 10
    ratio = abs(report.branch_corrected.cohen_d) / abs(report.branch_naive.cohen_d)
    assert ratio > OOM_FACTOR, f"sanity: ratio={ratio}"
    assert report.label == "KAPPA_INCONCLUSIVE"
    assert any("OOM" in r or "ordre de grandeur" in r for r in report.inconclusive_reasons)


def test_sign_disagreement_override_to_inconclusive(tmp_path: Path) -> None:
    """Une branche dit +effet, l'autre -effet → divergence majeure."""
    rng = np.random.default_rng(0)
    pos = 1.0 + rng.normal(0.0, 0.3, size=30)
    neg = -1.0 + rng.normal(0.0, 0.3, size=30)
    csv_path = tmp_path / "sign.csv"
    _write_csv(csv_path, deltas_corr=pos, deltas_naive=neg)

    report = compute_verdict(csv_path)
    assert report.branch_corrected.cohen_d * report.branch_naive.cohen_d < 0
    assert report.label == "KAPPA_INCONCLUSIVE"


def test_wrong_n_rows_override_to_inconclusive(tmp_path: Path) -> None:
    """n_rows ≠ 30 (intégrité du tirage) déclenche INCONCLUSIVE."""
    deltas = _strong_positive_deltas(n=20, seed=42)  # ⚠ 20 ≠ 30
    csv_path = tmp_path / "short.csv"
    _write_csv(csv_path, deltas)

    report = compute_verdict(csv_path)
    assert report.n_rows == 20
    assert report.n_rows != N_SEEDS_EXPECTED
    assert report.label == "KAPPA_INCONCLUSIVE"
    assert any("n_rows=20" in r for r in report.inconclusive_reasons)


# ----------------------------------------------------------------------
# Robustesse de lecture
# ----------------------------------------------------------------------

def test_missing_required_column_raises(tmp_path: Path) -> None:
    csv_path = tmp_path / "broken.csv"
    csv_path.write_text("seed,Delta_kappa_corr\n2000,1.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="colonnes manquantes"):
        compute_verdict(csv_path)


def test_empty_csv_raises(tmp_path: Path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="vide"):
        compute_verdict(csv_path)


# ----------------------------------------------------------------------
# JSON report (traçabilité §7 du protocole)
# ----------------------------------------------------------------------

def test_json_report_written_and_parseable(tmp_path: Path) -> None:
    deltas = _strong_positive_deltas(n=30, seed=42)
    csv_path = tmp_path / "tirage.csv"
    json_path = tmp_path / "verdict.json"
    _write_csv(csv_path, deltas)

    report = compute_verdict(csv_path, json_report_path=json_path)
    assert json_path.exists()

    parsed = json.loads(json_path.read_text(encoding="utf-8"))
    assert parsed["label"] == "KAPPA_TRANSFERS"
    assert parsed["nominal_label"] == "KAPPA_TRANSFERS"
    assert parsed["clip_events_total"] == 0
    assert parsed["n_rows"] == 30
    assert parsed["branch_corrected"]["sub_label"] == "KAPPA_TRANSFERS"
    assert parsed["branch_naive"]["sub_label"] == "KAPPA_TRANSFERS"
    # Clés alphabétiques (sort_keys=True) pour traçabilité diff-friendly.
    assert list(parsed.keys()) == sorted(parsed.keys())


# ----------------------------------------------------------------------
# Encode-the-law : seuils sont bien hard-codés et alignés ADR-032
# ----------------------------------------------------------------------

def test_thresholds_match_adr_032() -> None:
    """Verrou doctrinal : si quelqu'un modifie ces constantes, le test casse
    et le commit doit être accompagné d'un ADR amendant §6."""
    assert D_TRANSFERS_MIN == 1.0
    assert P_TRANSFERS_MAX == 1e-4
    assert N_POSITIVE_TRANSFERS_MIN == 25
    assert D_FAILS_MAX == 0.3
    assert P_FAILS_MIN == 1e-2
    assert N_POSITIVE_FAILS_MAX == 18
    assert OOM_FACTOR == 10.0
    assert N_SEEDS_EXPECTED == 30
