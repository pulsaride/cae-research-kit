"""ADT — diffusion_sweep (ADR-034 §4.4, 6 tests obligatoires).

Ces tests sont des VERROUS : ils s'assurent que le script de sweep ne dévie
pas d'un iota de la pré-registration ADR-034. Échec d'un seul test = blocage
du tirage v0.6.0.

  1. test_grid_frozen        — DIFFUSION_GRID figée verbatim §3.1
  2. test_pool_frozen        — SEED_POOL figé verbatim §3.2 (no overlap)
  3. test_no_runner_modification — SHA-256 portability_draw.py inchangé
  4. test_csv_header         — header v0.5.0 + diffusion_coeff en col 1
  5. test_guard_flag         — refus tirage sans --i-have-read-adr-034
  6. test_smoke_seed_2000    — reproduit seed 2000 v0.5.0 sous ADR-033 §4

Le test (6) est lent (~minute, exécute le pipeline complet sur 1 seed). Il est
marqué `slow` pour pouvoir être désactivé en CI rapide via `-m "not slow"`.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from src.experiments import diffusion_sweep as ds
from src.experiments.diffusion_sweep import (
    CSV_FIELDNAMES,
    DIFFUSION_GRID,
    REFERENCE_DIFFUSION,
    REFERENCE_PORTABILITY_CSV,
    SEED_POOL,
    SMOKE_SEED,
    main,
    run_smoke_test,
)
from src.experiments.portability_draw import (
    CSV_FIELDNAMES as BASE_FIELDNAMES,
    POOL_AUDIT,
    POOL_PORTABILITY,
)


# ============================================================================
# (1) Grille figée verbatim ADR-034 §3.1
# ============================================================================

def test_grid_frozen() -> None:
    """ADR-034 §3.1 : grille géométrique 7 points, immuable."""
    assert DIFFUSION_GRID == (
        0.005, 0.020, 0.040, 0.080, 0.160, 0.320, 0.640
    )
    assert len(DIFFUSION_GRID) == 7
    # Le point de calibration v0.5.0 doit être présent comme contrôle.
    assert REFERENCE_DIFFUSION == 0.080
    assert REFERENCE_DIFFUSION in DIFFUSION_GRID
    # Géométrie : ratio constant ×2 entre points consécutifs.
    for i in range(1, len(DIFFUSION_GRID)):
        ratio = DIFFUSION_GRID[i] / DIFFUSION_GRID[i - 1]
        # 0.020/0.005 = 4 (saut intentionnel sous-bande), reste = 2.
        assert ratio in (2.0, 4.0), (
            f"DIFFUSION_GRID[{i}]/DIFFUSION_GRID[{i-1}]={ratio} "
            f"hors {{2, 4}} — grille modifiée vs ADR-034 §3.1"
        )


# ============================================================================
# (2) Pool figé + non-recouvrement avec pools antérieurs
# ============================================================================

def test_pool_frozen_and_disjoint() -> None:
    """ADR-034 §3.2 : pool [4000-4029], 30 seeds, AUCUN chevauchement avec
    pools κ existants ou tail réservée E1."""
    assert SEED_POOL == tuple(range(4000, 4030))
    assert len(SEED_POOL) == 30

    pool_set = set(SEED_POOL)
    audit_set = set(range(POOL_AUDIT[0], POOL_AUDIT[1] + 1))
    portability_set = set(range(POOL_PORTABILITY[0], POOL_PORTABILITY[1] + 1))
    # Tail [2030-2099] réservée E1 (ADR-031), pool [2100-2129] réservé E2 (ADR-032 §4)
    e1_tail_set = set(range(2030, 2100))
    e2_reserve_set = set(range(2100, 2130))

    assert pool_set.isdisjoint(audit_set)
    assert pool_set.isdisjoint(portability_set)
    assert pool_set.isdisjoint(e1_tail_set)
    assert pool_set.isdisjoint(e2_reserve_set)

    # SMOKE_SEED appartient au pool v0.5.0, JAMAIS au pool sweep.
    assert SMOKE_SEED == 2000
    assert SMOKE_SEED in portability_set
    assert SMOKE_SEED not in pool_set


# ============================================================================
# (3) Le runner v0.5.0 ne doit pas avoir bougé d'un octet
# ============================================================================

# SHA-256 mesuré le 2026-05-10 sur HEAD post-v0.5.0 (commits c0a61c5 / 56c2cc4).
# Cf. ADR-034 §4.2 + audit secondaire §4.3.
PORTABILITY_DRAW_SHA256_V050: str = (
    "3c4a7df4c67e162174466e2488ebc8d35676558e870e02c2bbb5cfc2716aa79d"
)


def test_no_runner_modification() -> None:
    """ADR-034 §4.4 : portability_draw.py figé par ADR-033 audit-gate.
    Toute modification de ce fichier invalide le tag audit-passed-v1
    et bloque le sweep v0.6.0."""
    runner_path = Path("src/experiments/portability_draw.py")
    assert runner_path.exists(), f"runner introuvable : {runner_path}"
    actual = hashlib.sha256(runner_path.read_bytes()).hexdigest()
    assert actual == PORTABILITY_DRAW_SHA256_V050, (
        f"portability_draw.py a été modifié.\n"
        f"  attendu : {PORTABILITY_DRAW_SHA256_V050}\n"
        f"  obtenu  : {actual}\n"
        f"=> audit-passed-v1 (ADR-033) invalidé. Sweep ADR-034 BLOQUÉ."
    )


# ============================================================================
# (4) Header CSV : diffusion_coeff en première position, schéma v0.5.0 ensuite
# ============================================================================

def test_csv_header() -> None:
    """ADR-034 §4.4 : header CSV étendu = ('diffusion_coeff',) + header v0.5.0."""
    assert CSV_FIELDNAMES[0] == "diffusion_coeff"
    assert CSV_FIELDNAMES[1:] == tuple(BASE_FIELDNAMES)
    # Toutes les colonnes v0.5.0 préservées dans le même ordre.
    assert len(CSV_FIELDNAMES) == 1 + len(BASE_FIELDNAMES)


def test_csv_header_written_correctly(tmp_path: Path) -> None:
    """Sanité : write_csv produit un header conforme."""
    out = tmp_path / "empty.csv"
    ds.write_csv([], out)
    written_header = out.read_text(encoding="utf-8").splitlines()[0].split(",")
    assert tuple(written_header) == CSV_FIELDNAMES


# ============================================================================
# (5) Garde --i-have-read-adr-034 sur le tirage complet
# ============================================================================

def test_guard_flag_required(tmp_path: Path) -> None:
    """ADR-034 §4.4 : refus du tirage sans drapeau de lecture explicite."""
    out = tmp_path / "ne_doit_pas_apparaitre.csv"
    with pytest.raises(SystemExit) as exc:
        main(["--output", str(out)])
    msg = str(exc.value)
    assert "ADR-034" in msg
    assert "--i-have-read-adr-034" in msg
    assert not out.exists()


def test_guard_flag_not_required_for_smoke_test() -> None:
    """Le smoke-test §4.3 doit être exécutable sans le drapeau de tirage
    (c'est précisément un PRÉ-requis du tirage)."""
    parser = ds._build_arg_parser()
    args = parser.parse_args(["--smoke-test"])
    assert args.smoke_test is True
    assert args.i_have_read_adr_034 is False


# ============================================================================
# (6) Smoke-test : seed 2000 à D=0.080 reproduit v0.5.0 sous ADR-033 §4
# ============================================================================

@pytest.mark.slow
def test_smoke_seed_2000_reproduces_v050() -> None:
    """ADR-034 §4.3 : audit secondaire bloquant. Le pipeline complet sur
    seed 2000 à D=0.080 doit retourner les mêmes chiffres que la ligne
    correspondante de research/h7_kappa_portability.csv, à atol=1e-9 sur
    les floats et == strict sur les entiers (ADR-033 §4).

    Test marqué `slow` : ~1 minute sur un seul seed (T_TOTAL=55000)."""
    if not REFERENCE_PORTABILITY_CSV.exists():
        pytest.skip(
            f"référence v0.5.0 absente ({REFERENCE_PORTABILITY_CSV}) — "
            f"impossible d'exécuter l'audit secondaire §4.3"
        )
    exit_code = run_smoke_test()
    assert exit_code == 0, (
        "L'audit secondaire ADR-034 §4.3 a échoué : la branche main HEAD "
        "ne reproduit plus bit-à-bit le résultat v0.5.0 sur seed 2000. "
        "Le tirage v0.6.0 est BLOQUÉ jusqu'à investigation forensique."
    )
