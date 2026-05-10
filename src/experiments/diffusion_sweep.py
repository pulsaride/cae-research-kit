"""Sweep diffusion E1 — runner pré-enregistré (ADR-034 ACCEPTED 2026-05-10).

Pour chaque valeur D ∈ DIFFUSION_GRID et chaque seed s ∈ SEED_POOL :
  - construit un E1 avec E1Config(diffusion_coeff=D, ...) ;
  - exécute le pipeline `run_seed` IMPORTÉ par référence depuis
    `src.experiments.portability_draw` (pas de copie de code, ADR-034 §4.2) ;
  - sérialise une ligne CSV étendue avec `diffusion_coeff` en première colonne.

Architecture **Option β** (ADR-034 §4.2) :
  Aucune modification de `portability_draw.py` (figé par ADR-033 audit-gate,
  tag `audit-passed-v1`). Seules les briques internes (`run_seed`, constantes
  T_*, SeedRow, etc.) sont importées. Toute dérive bit-level entre v0.5.0 et
  v0.6.0 sur ces briques sera détectée par l'audit secondaire §4.3 et par les
  ADTs de `tests/adt/test_portability_draw.py` qui restent verts.

CLI :

  # Audit secondaire §4.3 — compare le seed 2000 à D=0.080 contre
  # research/h7_kappa_portability.csv sous tolérances ADR-033 §4.
  python -m src.experiments.diffusion_sweep --smoke-test

  # Tirage complet (210 runs ≈ 70 min wall-clock).
  python -m src.experiments.diffusion_sweep --i-have-read-adr-034 \
      --output research/h7_kappa_boundary_sweep.csv

GRILLE et POOL sont FIGÉS par ADR-034 §3.1-§3.2. Aucun flag ne permet
de les surcharger. Toute modification exige une nouvelle ADR.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Callable

# IMPORT PAR RÉFÉRENCE — pas de copie de code (ADR-034 §4.2).
# Toute dérive bit-level sur ces symboles serait détectée par les ADTs
# de tests/adt/test_portability_draw.py et par l'audit secondaire §4.3.
from src.experiments import portability_draw as _runner
from src.experiments.portability_draw import (
    CSV_FIELDNAMES as _BASE_FIELDNAMES,
    GRID_SIZE,
    SeedRow,
    T_TOTAL,
    _format_value,
    run_seed,
)


# ============================================================================
# Constantes pré-enregistrées (ADR-034 §3.1-§3.2, IMMUABLES)
# ============================================================================

DIFFUSION_GRID: tuple[float, ...] = (
    0.005, 0.020, 0.040, 0.080, 0.160, 0.320, 0.640
)
"""Grille géométrique 7 points, ancrée sur la calibration v0.5.0 (D=0.080).
ADR-034 §3.1 : aucun ajout, aucune suppression, aucune ré-échelle."""

SEED_POOL: tuple[int, ...] = tuple(range(4000, 4030))
"""Pool unique partagé sur les 7 D — 30 seeds appariés. ADR-034 §3.2."""

REFERENCE_DIFFUSION: float = 0.080
"""Point de cohérence v0.5.0 (ADR-032 §3.4). Présent dans la grille comme
contrôle, NON comme test. ADR-034 §3.1, §5.4."""

REFERENCE_PORTABILITY_CSV: Path = Path("research/h7_kappa_portability.csv")
"""CSV v0.5.0 de référence pour l'audit secondaire §4.3 (smoke-test)."""

SMOKE_SEED: int = 2000
"""Seed unique du smoke-test §4.3 — appartient à POOL_PORTABILITY (v0.5.0),
PAS à SEED_POOL (4000-4029). N'est jamais compté dans le tirage v0.6.0."""

# Header CSV étendu : `diffusion_coeff` en première colonne, puis schéma v0.5.0
# verbatim (pour réutilisabilité par audit_compare et symétrie de format).
CSV_FIELDNAMES: tuple[str, ...] = ("diffusion_coeff",) + tuple(_BASE_FIELDNAMES)


EnvFactory = Callable[[int], object]


# ============================================================================
# Env factory paramétrée par D (la SEULE chose qui change vs v0.5.0)
# ============================================================================

def _e1_factory_at_D(diffusion_coeff: float) -> EnvFactory:
    """Retourne une factory E1 dont le diffusion_coeff est FIXÉ à `D`.
    Toute autre dimension (grid_size, horizon, laplacian_boundary='periodic')
    est BIT-IDENTIQUE à _e1_factory du runner v0.5.0."""
    def _factory(seed: int) -> object:
        # Import local pour rester aligné sur le pattern de portability_draw
        # (évite couplage fort à src.env si POT manque dans certains env).
        from src.env.e1 import E1, E1Config
        cfg = E1Config(
            grid_size=GRID_SIZE,
            horizon=T_TOTAL,
            seed=seed,
            diffusion_coeff=diffusion_coeff,
            # laplacian_boundary='periodic' par défaut — figé par ADR-032 §3.2.
        )
        return E1(cfg)
    return _factory


# ============================================================================
# Sérialisation CSV
# ============================================================================

def _row_to_dict(diffusion_coeff: float, row: SeedRow) -> dict[str, str]:
    """Sérialise SeedRow + diffusion_coeff au format CSV (12 décimales sur D
    pour homogénéité avec les autres floats)."""
    d: dict[str, str] = {"diffusion_coeff": f"{diffusion_coeff:.12f}"}
    for f in _BASE_FIELDNAMES:
        d[f] = _format_value(getattr(row, f), f)
    return d


def write_csv(
    rows: list[tuple[float, SeedRow]],
    output_path: Path,
) -> None:
    """Écrit le CSV sweep avec colonne `diffusion_coeff` en première position."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(CSV_FIELDNAMES))
        writer.writeheader()
        for D, row in rows:
            writer.writerow(_row_to_dict(D, row))


# ============================================================================
# Audit secondaire §4.3 — smoke test
# ============================================================================

def _read_reference_seed_2000() -> dict[str, str]:
    """Lit la ligne seed=SMOKE_SEED du CSV v0.5.0 de référence."""
    if not REFERENCE_PORTABILITY_CSV.exists():
        raise SystemExit(
            f"REFUS smoke-test : référence v0.5.0 introuvable "
            f"({REFERENCE_PORTABILITY_CSV}). Audit secondaire §4.3 impossible."
        )
    with REFERENCE_PORTABILITY_CSV.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            if int(r["seed"]) == SMOKE_SEED:
                return r
    raise SystemExit(
        f"REFUS smoke-test : seed {SMOKE_SEED} absent de "
        f"{REFERENCE_PORTABILITY_CSV}."
    )


def _compare_to_reference(
    candidate: SeedRow,
    reference: dict[str, str],
    *,
    atol: float = 1e-9,
) -> tuple[bool, list[str]]:
    """Compare BIT-level (==) sur les colonnes entières, atol sur les floats.
    Tolérances figées par ADR-033 §4 (rtol=0, atol=1e-9, == strict sur int)."""
    int_cols = (
        "seed", "T_warmup", "T_stat", "B",
        "K_R_nonempty", "K_S_nonempty", "K_M_nonempty", "K_Mk_nonempty",
        "laplace_bins_R", "laplace_bins_S", "laplace_bins_Mk",
        "clip_events_R", "clip_events_S", "clip_events_M", "clip_events_Mk",
    )
    diffs: list[str] = []
    for f in _BASE_FIELDNAMES:
        ref_str = reference[f]
        cand_val = getattr(candidate, f)
        if f in int_cols:
            ref_val = int(ref_str)
            if int(cand_val) != ref_val:
                diffs.append(
                    f"  [{f}] int ≠ : ref={ref_val} cand={int(cand_val)}"
                )
        else:
            ref_val = float(ref_str)
            if abs(float(cand_val) - ref_val) > atol:
                diffs.append(
                    f"  [{f}] |Δ|={abs(float(cand_val)-ref_val):.3e} > atol={atol:.0e} "
                    f"(ref={ref_val:.12f} cand={float(cand_val):.12f})"
                )
    return (len(diffs) == 0, diffs)


def run_smoke_test() -> int:
    """Exécute le seed SMOKE_SEED à D=REFERENCE_DIFFUSION et compare au
    CSV v0.5.0 sous tolérances ADR-033 §4. EXIT 0 si PASS, 1 sinon."""
    print(
        f"[diffusion_sweep] SMOKE-TEST §4.3 : seed={SMOKE_SEED} "
        f"D={REFERENCE_DIFFUSION} vs {REFERENCE_PORTABILITY_CSV}",
        flush=True,
    )
    reference = _read_reference_seed_2000()

    t0 = time.time()
    factory = _e1_factory_at_D(REFERENCE_DIFFUSION)
    candidate = run_seed(SMOKE_SEED, factory)
    elapsed = time.time() - t0

    passed, diffs = _compare_to_reference(candidate, reference)
    if passed:
        print(
            f"[diffusion_sweep] SMOKE-TEST PASS — "
            f"Δκ_corr={candidate.Delta_kappa_corr:+.6f} "
            f"({elapsed:.1f}s, atol=1e-9 strict).",
            flush=True,
        )
        return 0
    print(
        f"[diffusion_sweep] SMOKE-TEST FAIL ({elapsed:.1f}s) — divergences :",
        flush=True,
    )
    for line in diffs:
        print(line, flush=True)
    print(
        "[diffusion_sweep] L'audit secondaire §4.3 BLOQUE le tirage v0.6.0.",
        flush=True,
    )
    return 1


# ============================================================================
# Tirage complet (210 runs)
# ============================================================================

def run_full_sweep(output_path: Path) -> int:
    """Exécute DIFFUSION_GRID × SEED_POOL et écrit le CSV de sortie."""
    n_total = len(DIFFUSION_GRID) * len(SEED_POOL)
    print(
        f"[diffusion_sweep] FULL SWEEP : "
        f"{len(DIFFUSION_GRID)} D × {len(SEED_POOL)} seeds = {n_total} runs "
        f"→ {output_path}",
        flush=True,
    )
    rows: list[tuple[float, SeedRow]] = []
    t_global = time.time()
    i = 0
    for D in DIFFUSION_GRID:
        factory = _e1_factory_at_D(D)
        t_D = time.time()
        for seed in SEED_POOL:
            i += 1
            t_s = time.time()
            row = run_seed(seed, factory)
            rows.append((D, row))
            print(
                f"[diffusion_sweep] [{i:>3d}/{n_total}] D={D:.3f} seed={seed} "
                f"Δκ_corr={row.Delta_kappa_corr:+.6f} "
                f"clip={row.clip_events_R+row.clip_events_S+row.clip_events_M+row.clip_events_Mk} "
                f"({time.time()-t_s:.1f}s)",
                flush=True,
            )
        print(
            f"[diffusion_sweep] === D={D:.3f} done in {time.time()-t_D:.1f}s ===",
            flush=True,
        )

    write_csv(rows, output_path)
    print(
        f"[diffusion_sweep] DONE total={time.time()-t_global:.1f}s "
        f"→ {output_path} ({len(rows)} rows)",
        flush=True,
    )
    return 0


# ============================================================================
# CLI
# ============================================================================

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="diffusion_sweep",
        description=(
            "Sweep diffusion E1 — pré-enregistré ADR-034 ACCEPTED 2026-05-10. "
            "Architecture Option β : runner v0.5.0 figé, briques importées."
        ),
    )
    p.add_argument(
        "--smoke-test",
        action="store_true",
        help=(
            "Audit secondaire §4.3 : seed 2000 à D=0.080 vs "
            "research/h7_kappa_portability.csv (ADR-033 §4 tolérances). "
            "EXIT 0 si PASS, 1 sinon."
        ),
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("research/h7_kappa_boundary_sweep.csv"),
        help="Chemin du CSV de sortie (mode tirage complet uniquement).",
    )
    p.add_argument(
        "--i-have-read-adr-034",
        action="store_true",
        help=(
            "Drapeau requis pour le tirage complet. Symétrique de "
            "--i-have-read-adr-033 sur portability_draw.py. Refus sinon."
        ),
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    if args.smoke_test:
        return run_smoke_test()

    if not args.i_have_read_adr_034:
        raise SystemExit(
            "REFUS : le tirage complet exige --i-have-read-adr-034 "
            "(garde ADR-034 §4.4). Pour l'audit secondaire §4.3, "
            "utilisez --smoke-test."
        )

    return run_full_sweep(args.output)


if __name__ == "__main__":
    sys.exit(main())
