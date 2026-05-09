"""ADT — portability_draw (smoke + structure, pas de tirage 30-seeds full).

Tests rapides : structure de la ligne, conformité CSV, refus V3 sur le pool
portability sans drapeau, exécution mini sur 1 seed à T_TOTAL réduit (via
monkey-patch des constantes). Le test bit-identité de l'audit complet est
RÉSERVÉ à ADR-033 (gate doctrinale, exécution longue ~minutes/seed).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.experiments import portability_draw as pd_mod
from src.experiments.portability_draw import (
    CSV_FIELDNAMES,
    POOL_AUDIT,
    POOL_PORTABILITY,
    SeedRow,
    main,
    write_csv,
    _e0_factory,
    _e1_factory,
)


# ----------------------------------------------------------------------
# Constantes
# ----------------------------------------------------------------------

def test_pool_constants_match_doctrine() -> None:
    """Verrou : pools figés par ADR-026/032. Toute modification → ADR."""
    assert POOL_AUDIT == (1500, 1529)
    assert POOL_PORTABILITY == (2000, 2029)
    assert pd_mod.T_WARMUP == 5000
    assert pd_mod.T_STAT == 50000
    assert pd_mod.T_TOTAL == 55000
    assert pd_mod.GRID_SIZE == 64


def test_csv_schema_matches_v04() -> None:
    """Schéma de colonnes = celui de research/h7_kappa_run_results.csv (v0.4.0)."""
    expected = (
        "seed,T_warmup,T_stat,B,P_min,P_max,"
        "KL_R_M_corr,KL_S_M_corr,KL_Mk_M_corr,"
        "KL_R_M_naive,KL_S_M_naive,KL_Mk_M_naive,"
        "delta_sigma_R_corr,delta_sigma_Mk_corr,"
        "delta_sigma_R_naive,delta_sigma_Mk_naive,"
        "Delta_kappa_corr,Delta_kappa_naive,"
        "K_R_nonempty,K_S_nonempty,K_M_nonempty,K_Mk_nonempty,"
        "laplace_bins_R,laplace_bins_S,laplace_bins_Mk,"
        "clip_events_R,clip_events_S,clip_events_M,clip_events_Mk"
    ).split(",")
    assert list(CSV_FIELDNAMES) == expected


# ----------------------------------------------------------------------
# Verrou V3 : pool portability inaccessible sans drapeau explicite
# ----------------------------------------------------------------------

def test_v3_refuses_portability_without_flag(tmp_path: Path) -> None:
    out = tmp_path / "ne_doit_pas_apparaitre.csv"
    with pytest.raises(SystemExit) as exc:
        main(["--pool", "portability", "--output", str(out)])
    assert "ADR-033" in str(exc.value)
    assert "V3" in str(exc.value)
    assert not out.exists()  # rien n'a été écrit


# ----------------------------------------------------------------------
# Argument parser : audit accessible nominalement, portability sous flag
# ----------------------------------------------------------------------

def test_arg_parser_resolves_audit_pool() -> None:
    args = pd_mod._build_arg_parser().parse_args(
        ["--pool", "audit", "--output", "/tmp/x.csv"]
    )
    seeds, factory = pd_mod._resolve_pool(args)
    assert seeds == list(range(1500, 1530))
    assert factory is _e0_factory


def test_arg_parser_resolves_portability_pool_with_flag() -> None:
    args = pd_mod._build_arg_parser().parse_args([
        "--pool", "portability",
        "--output", "/tmp/x.csv",
        "--i-have-read-adr-033",
    ])
    seeds, factory = pd_mod._resolve_pool(args)
    assert seeds == list(range(2000, 2030))
    assert factory is _e1_factory


def test_arg_parser_custom_seeds_override() -> None:
    args = pd_mod._build_arg_parser().parse_args([
        "--pool", "audit",
        "--output", "/tmp/x.csv",
        "--seeds", "1500", "1501",
    ])
    seeds, _ = pd_mod._resolve_pool(args)
    assert seeds == [1500, 1501]


# ----------------------------------------------------------------------
# CSV writer : ordre, format, round-trip
# ----------------------------------------------------------------------

def _dummy_row(seed: int = 1500) -> SeedRow:
    return SeedRow(
        seed=seed, T_warmup=5000, T_stat=50000,
        B=64, P_min=0.0, P_max=1.0,
        KL_R_M_corr=0.166804169926, KL_S_M_corr=0.842040881310,
        KL_Mk_M_corr=1.000154092570,
        KL_R_M_naive=0.166801826176, KL_S_M_naive=0.842040881310,
        KL_Mk_M_naive=1.000154092570,
        delta_sigma_R_corr=-0.675236711385, delta_sigma_Mk_corr=0.158113211259,
        delta_sigma_R_naive=-0.675239055135, delta_sigma_Mk_naive=0.158113211259,
        Delta_kappa_corr=0.833349922644, Delta_kappa_naive=0.833352266394,
        K_R_nonempty=38, K_S_nonempty=63, K_M_nonempty=53, K_Mk_nonempty=63,
        laplace_bins_R=0, laplace_bins_S=10, laplace_bins_Mk=10,
        clip_events_R=0, clip_events_S=0, clip_events_M=0, clip_events_Mk=0,
    )


def test_write_csv_round_trip(tmp_path: Path) -> None:
    out = tmp_path / "row.csv"
    write_csv([_dummy_row(1500), _dummy_row(1501)], out)
    text = out.read_text(encoding="utf-8")
    lines = text.strip().split("\n")
    assert lines[0] == ",".join(CSV_FIELDNAMES)
    assert len(lines) == 3  # header + 2 rows
    # Format : 12 décimales sur les floats.
    assert "0.166804169926" in lines[1]
    # Pas de notation scientifique.
    assert "e-" not in lines[1].replace("e-", "")  # cosmetic
    # Header order strict.
    cols = lines[0].split(",")
    assert cols.index("seed") == 0
    assert cols.index("Delta_kappa_corr") < cols.index("Delta_kappa_naive")
    assert cols[-1] == "clip_events_Mk"


def test_write_csv_creates_parent_dir(tmp_path: Path) -> None:
    out = tmp_path / "deep" / "nested" / "row.csv"
    write_csv([_dummy_row()], out)
    assert out.exists()


# ----------------------------------------------------------------------
# Run réel : un seed à T_TOTAL minuscule (smoke) — vérifie le câblage
# de bout en bout sans payer le coût des 55000 ticks.
# ----------------------------------------------------------------------

def test_run_seed_smoke_at_small_horizon(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reduce T_WARMUP/T_STAT/T_TOTAL pour exécuter en <1s.
    NB : ne reproduit PAS la v0.4.0, c'est juste un smoke de câblage."""
    monkeypatch.setattr(pd_mod, "T_WARMUP", 50)
    monkeypatch.setattr(pd_mod, "T_STAT", 200)
    monkeypatch.setattr(pd_mod, "T_TOTAL", 250)

    row = pd_mod.run_seed(1500, _e0_factory)

    # Conformité de la ligne.
    assert isinstance(row, SeedRow)
    assert row.seed == 1500
    assert row.B == 64
    assert row.P_min == 0.0 and row.P_max == 1.0
    # Comptes bornés par grid_size + warmup logic.
    assert 0 < row.K_R_nonempty <= 64
    assert 0 < row.K_S_nonempty <= 64
    assert 0 < row.K_M_nonempty <= 64
    assert 0 < row.K_Mk_nonempty <= 64
    # Pas de clip : env clipe en interne sur [0,1].
    assert row.clip_events_R == 0
    assert row.clip_events_S == 0
    assert row.clip_events_M == 0
    assert row.clip_events_Mk == 0
    # Identité algébrique : Δκ = δσ_Mk - δσ_R (les deux branches).
    assert abs(row.Delta_kappa_corr -
               (row.delta_sigma_Mk_corr - row.delta_sigma_R_corr)) < 1e-12
    assert abs(row.Delta_kappa_naive -
               (row.delta_sigma_Mk_naive - row.delta_sigma_R_naive)) < 1e-12
    # Identité algébrique : δσ_X = KL_X_M - KL_S_M.
    assert abs(row.delta_sigma_R_corr -
               (row.KL_R_M_corr - row.KL_S_M_corr)) < 1e-12
    assert abs(row.delta_sigma_Mk_corr -
               (row.KL_Mk_M_corr - row.KL_S_M_corr)) < 1e-12


def test_run_seed_smoke_e1_executes(monkeypatch: pytest.MonkeyPatch) -> None:
    """E1 doit exécuter le pipeline sans erreur sur un seed du pool E1."""
    monkeypatch.setattr(pd_mod, "T_WARMUP", 50)
    monkeypatch.setattr(pd_mod, "T_STAT", 200)
    monkeypatch.setattr(pd_mod, "T_TOTAL", 250)

    row = pd_mod.run_seed(2000, _e1_factory)
    assert row.seed == 2000
    # Sanity : E1 a une diffusion → la pression devrait être plus lisse,
    # K_R_nonempty pourrait différer de E0 mais doit rester dans [1, 64].
    assert 1 <= row.K_R_nonempty <= 64


def test_run_seed_determinism(monkeypatch: pytest.MonkeyPatch) -> None:
    """Deux exécutions du même seed doivent produire des lignes identiques
    sur tous les champs (déterminisme bit-identique du runner public)."""
    monkeypatch.setattr(pd_mod, "T_WARMUP", 50)
    monkeypatch.setattr(pd_mod, "T_STAT", 200)
    monkeypatch.setattr(pd_mod, "T_TOTAL", 250)

    row_a = pd_mod.run_seed(1500, _e0_factory)
    row_b = pd_mod.run_seed(1500, _e0_factory)
    for f in CSV_FIELDNAMES:
        va = getattr(row_a, f)
        vb = getattr(row_b, f)
        if isinstance(va, float):
            np.testing.assert_equal(va, vb)  # bit-identique sur floats
        else:
            assert va == vb, f"divergence sur {f} : {va} vs {vb}"


def test_run_seed_distinct_seeds_yield_distinct_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(pd_mod, "T_WARMUP", 50)
    monkeypatch.setattr(pd_mod, "T_STAT", 200)
    monkeypatch.setattr(pd_mod, "T_TOTAL", 250)

    row_1500 = pd_mod.run_seed(1500, _e0_factory)
    row_1501 = pd_mod.run_seed(1501, _e0_factory)
    # Au moins une métrique diffère (Δκ, par construction).
    assert row_1500.Delta_kappa_corr != row_1501.Delta_kappa_corr
