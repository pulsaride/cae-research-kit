"""Verdict v0.6.0 — boundary-of-validity sweep (ADR-034 §5).

Fonction pure : CSV de sweep diffusion → label global ∈ {
    KAPPA_ROBUST_PORTABILITY, KAPPA_BAND_LIMITED, KAPPA_FRAGILE,
    KAPPA_INCONCLUSIVE
}.

Spec verbatim (ADR-034 §5, immuable après ACCEPTED 2026-05-10) :

§5 grille-point passant — CONJONCTION :
    - Cohen d(D) ≥ 0.5 sur les DEUX branches (corr + naive)
    - p_>(D) < 0.005          sur les DEUX branches
    - ≥ 25/30 seeds Δ_s(D) > 0
    - 0 clip event sur les 30 runs M_κ à D
       (extension ADR-033 §4 : on agrège aussi R, S, M, M_κ → 0 sur tout
        le sous-ensemble de seeds appariés à ce D)

§5.1 KAPPA_ROBUST_PORTABILITY — CONJONCTION :
    - 7/7 grille-points passent
    - profil non-trivial : ≥ 2 valeurs avec Cohen d ≥ 1.0 sur la grille
      intérieure {0.04, 0.08, 0.16}
    - concordance v0.5.0 au point de référence D=0.080 :
        |d(D=0.080)_v0.6.0 − d_v0.5.0| / d_v0.5.0 ≤ 0.01

§5.2 KAPPA_BAND_LIMITED — sous-ensemble CONTIGU passant, contenant 0.080,
     mais < 7. Variantes reportées : band_lower_open / band_upper_open /
     band_both_open.

§5.3 KAPPA_FRAGILE — < 3 grille-points passent OU 0.080 ne passe pas
     (ce dernier cas déclenche §5.4 en priorité) OU passants non contigus.

§5.4 Override KAPPA_INCONCLUSIVE (PRIME §5.1-§5.3) :
    - clip_events_total > 0 sur l'ensemble du sweep (210×4=840 runs)
    - divergence MM ↔ plug-in > 1 OOM sur Cohen d pour ≥ 1 grille-point
    - discordance > 1% au point de référence vs v0.5.0
    - (échec ADT et smoke sont gérés AVANT exécution, hors de ce module)

Hard-codé. AUCUN seuil n'est paramétrable. Toute évolution exige une ADR.
"""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np

from src.analysis.sigma_chain import (
    cohen_d_paired,
    wilcoxon_paired_one_sided,
)
from src.experiments.diffusion_sweep import (
    DIFFUSION_GRID,
    REFERENCE_DIFFUSION,
    SEED_POOL,
)


# ============================================================================
# Constantes IMMUABLES (ADR-034 §5, ne pas paramétrer)
# ============================================================================

# §5 grille-point passant
D_PASS_MIN: float = 0.5            # Cohen d ≥ 0.5 sur DEUX branches
P_PASS_MAX: float = 0.005          # p_> < 0.005 sur DEUX branches (α ADR-027)
N_POSITIVE_PASS_MIN: int = 25      # ≥ 25/30 seeds Δ_s > 0
CLIP_TOLERANCE: int = 0            # 0 clip event toléré

# §5.1 KAPPA_ROBUST_PORTABILITY
N_GRID_POINTS_EXPECTED: int = 7
INNER_TRIPLET: tuple[float, ...] = (0.040, 0.080, 0.160)
INNER_D_LARGE_MIN: float = 1.0
INNER_LARGE_COUNT_MIN: int = 2
CONCORDANCE_TOLERANCE: float = 0.01  # 1 %

# Référence v0.5.0 (immuable, lue de research/h7_kappa_portability_verdict.json
# et figée ici pour bloquer toute dérive silencieuse).
COHEN_D_V050_CORRECTED: float = 3.090641237972993
COHEN_D_V050_NAIVE: float = 3.090653026205383

# §5.3 KAPPA_FRAGILE
N_PASS_FRAGILE_MAX: int = 3   # strict : pass < 3 → FRAGILE

# §5.4 INCONCLUSIVE
OOM_FACTOR: float = 10.0       # > 1 ordre de grandeur entre branches

# Tirage attendu
N_SEEDS_EXPECTED: int = len(SEED_POOL)  # 30


VerdictLabel = Literal[
    "KAPPA_ROBUST_PORTABILITY",
    "KAPPA_BAND_LIMITED",
    "KAPPA_FRAGILE",
    "KAPPA_INCONCLUSIVE",
]
BandVariant = Literal[
    "band_lower_open",   # 0.080 inclus, plus petit passant ≥ 0.040
    "band_upper_open",   # 0.080 inclus, plus grand passant ≤ 0.160
    "band_both_open",    # sous-ensemble fermé strictement à l'intérieur
    "n_a",
]


# ============================================================================
# Évaluation par grille-point
# ============================================================================

@dataclass(frozen=True)
class GridPointEvaluation:
    """Verdict §5 sur une valeur de D."""
    diffusion_coeff: float
    n_seeds: int
    n_positive_corr: int
    n_positive_naive: int
    cohen_d_corr: float
    cohen_d_naive: float
    p_greater_corr: float
    p_greater_naive: float
    clip_events_total_at_D: int
    passed: bool
    reasons_failed: tuple[str, ...] = ()


def _evaluate_grid_point(
    D: float,
    delta_corr: np.ndarray,
    delta_naive: np.ndarray,
    clip_total_at_D: int,
) -> GridPointEvaluation:
    """Applique §5 (grille-point passant) à un D donné."""
    n = int(delta_corr.size)
    n_pos_corr = int((delta_corr > 0).sum())
    n_pos_naive = int((delta_naive > 0).sum())

    w_corr = wilcoxon_paired_one_sided(delta_corr, alternative="greater")
    w_naive = wilcoxon_paired_one_sided(delta_naive, alternative="greater")
    d_corr = cohen_d_paired(delta_corr)
    d_naive = cohen_d_paired(delta_naive)
    d_corr = float(d_corr) if not np.isnan(d_corr) else 0.0
    d_naive = float(d_naive) if not np.isnan(d_naive) else 0.0

    reasons: list[str] = []
    if d_corr < D_PASS_MIN:
        reasons.append(f"d_corr={d_corr:.4f} < {D_PASS_MIN}")
    if d_naive < D_PASS_MIN:
        reasons.append(f"d_naive={d_naive:.4f} < {D_PASS_MIN}")
    if w_corr.p_value >= P_PASS_MAX:
        reasons.append(f"p_corr={w_corr.p_value:.3e} ≥ {P_PASS_MAX}")
    if w_naive.p_value >= P_PASS_MAX:
        reasons.append(f"p_naive={w_naive.p_value:.3e} ≥ {P_PASS_MAX}")
    if n_pos_corr < N_POSITIVE_PASS_MIN:
        reasons.append(
            f"n_pos_corr={n_pos_corr}/{n} < {N_POSITIVE_PASS_MIN}"
        )
    if n_pos_naive < N_POSITIVE_PASS_MIN:
        reasons.append(
            f"n_pos_naive={n_pos_naive}/{n} < {N_POSITIVE_PASS_MIN}"
        )
    if clip_total_at_D > CLIP_TOLERANCE:
        reasons.append(
            f"clip_events={clip_total_at_D} > {CLIP_TOLERANCE} (§5)"
        )

    return GridPointEvaluation(
        diffusion_coeff=D,
        n_seeds=n,
        n_positive_corr=n_pos_corr,
        n_positive_naive=n_pos_naive,
        cohen_d_corr=d_corr,
        cohen_d_naive=d_naive,
        p_greater_corr=float(w_corr.p_value),
        p_greater_naive=float(w_naive.p_value),
        clip_events_total_at_D=clip_total_at_D,
        passed=(len(reasons) == 0),
        reasons_failed=tuple(reasons),
    )


# ============================================================================
# Verdict global (conjonctions §5.1-§5.3 + override §5.4)
# ============================================================================

@dataclass(frozen=True)
class VerdictReportV06:
    label: VerdictLabel
    band_variant: BandVariant
    per_point: tuple[GridPointEvaluation, ...]
    passing_diffusions: tuple[float, ...]
    n_passing: int
    inner_d_large_count: int
    concordance_corr: float
    concordance_naive: float
    clip_events_total_sweep: int
    inconclusive_reasons: tuple[str, ...]
    csv_path: str
    n_rows: int


def _is_contiguous_subset(
    passing_diffusions: tuple[float, ...],
    grid: tuple[float, ...] = DIFFUSION_GRID,
) -> bool:
    """True ssi passing_diffusions est un préfixe / suffixe / segment
    contigu dans `grid` (ordre numérique)."""
    if not passing_diffusions:
        return False
    indices = sorted(grid.index(D) for D in passing_diffusions)
    expected = list(range(indices[0], indices[0] + len(indices)))
    return indices == expected


def _classify_band_variant(
    passing: tuple[float, ...],
    grid: tuple[float, ...] = DIFFUSION_GRID,
) -> BandVariant:
    """Caractérise la position du sous-ensemble passant vs la grille."""
    if not passing:
        return "n_a"
    sorted_pass = tuple(sorted(passing))
    if sorted_pass[0] == grid[0] and sorted_pass[-1] != grid[-1]:
        # commence au minimum, ne va pas jusqu'au max → coupé en haut
        return "band_upper_open"
    if sorted_pass[0] != grid[0] and sorted_pass[-1] == grid[-1]:
        return "band_lower_open"
    if sorted_pass[0] != grid[0] and sorted_pass[-1] != grid[-1]:
        return "band_both_open"
    # commence à grid[0] ET finit à grid[-1] → c'est 7/7, pas BAND_LIMITED.
    return "n_a"


def _check_oom_divergence(d_corr: float, d_naive: float) -> bool:
    """True ssi divergence > 1 OOM ou signes opposés (§5.4)."""
    if d_corr * d_naive < 0:
        return True
    a, b = abs(d_corr), abs(d_naive)
    eps = 1e-12
    if a < eps and b < eps:
        return False
    if a < eps or b < eps:
        return True
    return (max(a, b) / min(a, b)) > OOM_FACTOR


# ============================================================================
# Lecture CSV
# ============================================================================

REQUIRED_COLUMNS = (
    "diffusion_coeff", "seed",
    "Delta_kappa_corr", "Delta_kappa_naive",
    "clip_events_R", "clip_events_S", "clip_events_M", "clip_events_Mk",
)


def _read_csv(csv_path: Path) -> dict[str, np.ndarray]:
    """Lit le CSV sweep et retourne un dict de colonnes numpy.
    Lève ValueError si une colonne requise manque ou si la grille / le pool
    ne correspondent pas à la pré-registration."""
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    if not rows:
        raise ValueError(f"CSV vide : {csv_path}")
    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        raise ValueError(f"colonnes manquantes dans {csv_path} : {missing}")

    cols: dict[str, np.ndarray] = {}
    cols["diffusion_coeff"] = np.array(
        [float(r["diffusion_coeff"]) for r in rows], dtype=np.float64
    )
    cols["seed"] = np.array([int(r["seed"]) for r in rows], dtype=np.int64)
    for c in ("Delta_kappa_corr", "Delta_kappa_naive"):
        cols[c] = np.array([float(r[c]) for r in rows], dtype=np.float64)
    for c in ("clip_events_R", "clip_events_S",
              "clip_events_M", "clip_events_Mk"):
        cols[c] = np.array([int(r[c]) for r in rows], dtype=np.int64)
    return cols


def _validate_sweep_structure(cols: dict[str, np.ndarray]) -> list[str]:
    """Vérifie que le CSV contient exactement DIFFUSION_GRID × SEED_POOL."""
    issues: list[str] = []
    n_expected = len(DIFFUSION_GRID) * len(SEED_POOL)
    if cols["seed"].size != n_expected:
        issues.append(
            f"n_rows={cols['seed'].size} ≠ {n_expected} attendus "
            f"({len(DIFFUSION_GRID)} D × {len(SEED_POOL)} seeds)"
        )
    # Grille : compare l'ensemble des D rencontrés à DIFFUSION_GRID (à 1e-12).
    unique_D = sorted(set(round(float(x), 12) for x in cols["diffusion_coeff"]))
    expected_D = sorted(round(float(x), 12) for x in DIFFUSION_GRID)
    if unique_D != expected_D:
        issues.append(
            f"D rencontrés {unique_D} ≠ DIFFUSION_GRID {expected_D}"
        )
    # Pool : pour chaque D, on doit retrouver SEED_POOL exactement.
    for D in DIFFUSION_GRID:
        mask = np.isclose(cols["diffusion_coeff"], D, atol=1e-12)
        seeds_at_D = sorted(int(s) for s in cols["seed"][mask])
        if seeds_at_D != list(SEED_POOL):
            issues.append(
                f"seeds @ D={D}: {len(seeds_at_D)} trouvés, "
                f"{len(SEED_POOL)} attendus"
            )
    return issues


# ============================================================================
# API publique
# ============================================================================

def compute_verdict(
    csv_path: str | Path,
    json_report_path: str | Path | None = None,
) -> VerdictReportV06:
    """Calcule le verdict v0.6.0 ADR-034 §5 sur le CSV de sweep.

    Args
    ----
    csv_path : research/h7_kappa_boundary_sweep.csv
    json_report_path : si fourni, écrit un rapport JSON complet.

    Returns
    -------
    VerdictReportV06 (frozen dataclass).
    """
    csv_path = Path(csv_path)
    cols = _read_csv(csv_path)
    structure_issues = _validate_sweep_structure(cols)

    per_point: list[GridPointEvaluation] = []
    for D in DIFFUSION_GRID:
        mask = np.isclose(cols["diffusion_coeff"], D, atol=1e-12)
        clip_at_D = int(
            cols["clip_events_R"][mask].sum()
            + cols["clip_events_S"][mask].sum()
            + cols["clip_events_M"][mask].sum()
            + cols["clip_events_Mk"][mask].sum()
        )
        ev = _evaluate_grid_point(
            D=D,
            delta_corr=cols["Delta_kappa_corr"][mask],
            delta_naive=cols["Delta_kappa_naive"][mask],
            clip_total_at_D=clip_at_D,
        )
        per_point.append(ev)

    passing = tuple(p.diffusion_coeff for p in per_point if p.passed)
    n_passing = len(passing)

    # Concordance v0.5.0 au point de référence
    ref_eval = next(
        p for p in per_point if p.diffusion_coeff == REFERENCE_DIFFUSION
    )
    concordance_corr = abs(
        ref_eval.cohen_d_corr - COHEN_D_V050_CORRECTED
    ) / COHEN_D_V050_CORRECTED
    concordance_naive = abs(
        ref_eval.cohen_d_naive - COHEN_D_V050_NAIVE
    ) / COHEN_D_V050_NAIVE

    # Triplet intérieur : compte les D avec d ≥ 1.0 sur DEUX branches
    inner_d_large_count = sum(
        1 for p in per_point
        if p.diffusion_coeff in INNER_TRIPLET
        and p.cohen_d_corr >= INNER_D_LARGE_MIN
        and p.cohen_d_naive >= INNER_D_LARGE_MIN
    )

    clip_total_sweep = int(
        cols["clip_events_R"].sum()
        + cols["clip_events_S"].sum()
        + cols["clip_events_M"].sum()
        + cols["clip_events_Mk"].sum()
    )

    # ----- §5.4 override INCONCLUSIVE -----------------------------------
    reasons: list[str] = list(structure_issues)
    if clip_total_sweep > 0:
        reasons.append(
            f"clip_events_total={clip_total_sweep} > 0 sur le sweep (§5.4)"
        )
    for p in per_point:
        if _check_oom_divergence(p.cohen_d_corr, p.cohen_d_naive):
            reasons.append(
                f"D={p.diffusion_coeff}: divergence MM↔naive > 1 OOM "
                f"(d_corr={p.cohen_d_corr:.4f}, d_naive={p.cohen_d_naive:.4f}) (§5.4)"
            )
    if max(concordance_corr, concordance_naive) > CONCORDANCE_TOLERANCE:
        reasons.append(
            f"discordance v0.5.0 @ D={REFERENCE_DIFFUSION}: "
            f"corr={concordance_corr:.4f}, naive={concordance_naive:.4f} "
            f"> {CONCORDANCE_TOLERANCE} (§5.4)"
        )

    # ----- §5.1-§5.3 (si pas d'override) --------------------------------
    if reasons:
        label: VerdictLabel = "KAPPA_INCONCLUSIVE"
        band_variant: BandVariant = "n_a"
    elif n_passing == N_GRID_POINTS_EXPECTED \
            and inner_d_large_count >= INNER_LARGE_COUNT_MIN \
            and max(concordance_corr, concordance_naive) <= CONCORDANCE_TOLERANCE:
        label = "KAPPA_ROBUST_PORTABILITY"
        band_variant = "n_a"
    elif n_passing < N_PASS_FRAGILE_MAX:
        label = "KAPPA_FRAGILE"
        band_variant = "n_a"
    elif REFERENCE_DIFFUSION not in passing:
        # 0.080 ne passe pas mais §5.4 ne s'est pas déclenché : FRAGILE.
        label = "KAPPA_FRAGILE"
        band_variant = "n_a"
    elif not _is_contiguous_subset(passing):
        # Sous-ensemble non contigu = FRAGILE par §5.3 (pas de bande définie).
        label = "KAPPA_FRAGILE"
        band_variant = "n_a"
    else:
        # Sous-ensemble contigu, contient 0.080, < 7 : BAND_LIMITED.
        label = "KAPPA_BAND_LIMITED"
        band_variant = _classify_band_variant(passing)

    report = VerdictReportV06(
        label=label,
        band_variant=band_variant,
        per_point=tuple(per_point),
        passing_diffusions=tuple(sorted(passing)),
        n_passing=n_passing,
        inner_d_large_count=inner_d_large_count,
        concordance_corr=float(concordance_corr),
        concordance_naive=float(concordance_naive),
        clip_events_total_sweep=clip_total_sweep,
        inconclusive_reasons=tuple(reasons),
        csv_path=str(csv_path),
        n_rows=int(cols["seed"].size),
    )

    if json_report_path is not None:
        Path(json_report_path).write_text(
            json.dumps(_report_to_dict(report), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return report


def _report_to_dict(report: VerdictReportV06) -> dict:
    d = asdict(report)
    # asdict transforme déjà les sub-dataclasses ; convertir les tuples en
    # listes JSON-friendly explicitement.
    d["per_point"] = [asdict(p) for p in report.per_point]
    d["passing_diffusions"] = list(report.passing_diffusions)
    d["inconclusive_reasons"] = list(report.inconclusive_reasons)
    return d


__all__ = [
    "GridPointEvaluation",
    "VerdictReportV06",
    "compute_verdict",
    "DIFFUSION_GRID",
    "SEED_POOL",
    "REFERENCE_DIFFUSION",
    "COHEN_D_V050_CORRECTED",
    "COHEN_D_V050_NAIVE",
]
