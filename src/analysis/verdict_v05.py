"""Verdict v0.5.0 — la guillotine portabilité κ (ADR-032 §6).

Fonction pure : CSV de tirage → label ∈ {KAPPA_TRANSFERS, KAPPA_FAILS_TRANSFER,
KAPPA_BOUNDED, KAPPA_INCONCLUSIVE}.

Spec verbatim (ADR-032 §6.1-§6.5, immuable après signature) :

§6.1 KAPPA_TRANSFERS — conditions CONJOINTES :
    - Cohen d ≥ 1.0 (effet large)
    - p_> (Wilcoxon greater) ≤ 1e-4 SUR LES DEUX BRANCHES
    - ≥ 25/30 seeds avec Δ_s > 0
    - 0 clip event (intégrité numérique)

§6.2 KAPPA_FAILS_TRANSFER — conditions DISJONCTIVES :
    - Cohen d < 0.3 OU p_> > 1e-2 sur une branche OU < 18/30 seeds Δ>0

§6.3 KAPPA_BOUNDED — tout l'intermédiaire.

§6.5 Override INCONCLUSIVE (PRIME sur §6.1-§6.4) :
    - clip_events > 0 sur n'importe quelle politique/seed
    - divergence MM ↔ plug-in > 1 ordre de grandeur sur Cohen d
    - branches en désaccord (e.g. corr=TRANSFERS, naive=BOUNDED)

Hard-codé. AUCUN seuil n'est paramétrable. Toute évolution exige un ADR.
"""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from src.analysis.sigma_chain import (
    cohen_d_paired,
    wilcoxon_paired_one_sided,
)


# ============================================================================
# Constantes immuables (ADR-032 §6, ne pas paramétrer)
# ============================================================================

D_TRANSFERS_MIN = 1.0          # §6.1 : d ≥ 1.0
P_TRANSFERS_MAX = 1e-4         # §6.1 : p_> ≤ 1e-4
N_POSITIVE_TRANSFERS_MIN = 25  # §6.1 : ≥ 25/30 seeds Δ > 0

D_FAILS_MAX = 0.3              # §6.2 : d < 0.3
P_FAILS_MIN = 1e-2             # §6.2 : p_> > 1e-2
N_POSITIVE_FAILS_MAX = 18      # §6.2 : < 18/30 seeds Δ > 0

OOM_FACTOR = 10.0              # §6.5 : > 1 ordre de grandeur entre branches

N_SEEDS_EXPECTED = 30          # §3 du protocole, taille fixe du tirage


VerdictLabel = Literal[
    "KAPPA_TRANSFERS",
    "KAPPA_FAILS_TRANSFER",
    "KAPPA_BOUNDED",
    "KAPPA_INCONCLUSIVE",
]
BranchLabel = Literal["KAPPA_TRANSFERS", "KAPPA_FAILS_TRANSFER", "KAPPA_BOUNDED"]


@dataclass(frozen=True)
class BranchEvaluation:
    """Résultat d'évaluation §6.1-§6.3 sur une branche d'entropie."""
    branch: str  # "corrected" | "naive"
    n_seeds: int
    n_positive: int
    n_post_drop: int
    n_dropped: int
    cohen_d: float
    p_greater: float
    sub_label: BranchLabel


@dataclass(frozen=True)
class VerdictReport:
    """Rapport de verdict — traçabilité complète."""
    label: VerdictLabel
    nominal_label: BranchLabel | Literal["DISAGREEMENT"]
    branch_corrected: BranchEvaluation
    branch_naive: BranchEvaluation
    clip_events_total: int
    inconclusive_reasons: list[str]
    csv_path: str
    n_rows: int


# ============================================================================
# Lecture CSV (schéma fixe v0.4.0)
# ============================================================================

REQUIRED_COLUMNS = (
    "seed",
    "Delta_kappa_corr",
    "Delta_kappa_naive",
    "clip_events_R",
    "clip_events_S",
    "clip_events_M",
    "clip_events_Mk",
)


def _read_csv(csv_path: Path) -> dict[str, np.ndarray]:
    """Lit un CSV de tirage (v0.4.0 schema). Retourne un dict de colonnes
    numpy. Lève ValueError si une colonne requise manque."""
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(row)
    if not rows:
        raise ValueError(f"CSV vide : {csv_path}")
    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        raise ValueError(f"colonnes manquantes dans {csv_path} : {missing}")
    cols: dict[str, np.ndarray] = {}
    for c in REQUIRED_COLUMNS:
        if c == "seed":
            cols[c] = np.array([int(r[c]) for r in rows], dtype=np.int64)
        elif c.startswith("clip_events_"):
            cols[c] = np.array([int(r[c]) for r in rows], dtype=np.int64)
        else:
            cols[c] = np.array([float(r[c]) for r in rows], dtype=np.float64)
    return cols


# ============================================================================
# Évaluation par branche (§6.1-§6.3)
# ============================================================================

def _classify_branch(
    branch_name: str,
    deltas: np.ndarray,
) -> BranchEvaluation:
    """Applique §6.1-§6.3 à une branche d'entropie."""
    n_seeds = int(deltas.size)
    n_positive = int(np.sum(deltas > 0))

    w = wilcoxon_paired_one_sided(deltas, alternative="greater")
    d = cohen_d_paired(deltas)

    cohen_d_val = float(d) if not np.isnan(d) else 0.0
    p_val = float(w.p_value)

    # §6.2 — disjonction (échec si l'une au moins est vraie)
    if (
        cohen_d_val < D_FAILS_MAX
        or p_val > P_FAILS_MIN
        or n_positive < N_POSITIVE_FAILS_MAX
    ):
        sub: BranchLabel = "KAPPA_FAILS_TRANSFER"
    # §6.1 — conjonction (succès si toutes vraies)
    elif (
        cohen_d_val >= D_TRANSFERS_MIN
        and p_val <= P_TRANSFERS_MAX
        and n_positive >= N_POSITIVE_TRANSFERS_MIN
    ):
        sub = "KAPPA_TRANSFERS"
    # §6.3 — par construction, ce qui reste
    else:
        sub = "KAPPA_BOUNDED"

    return BranchEvaluation(
        branch=branch_name,
        n_seeds=n_seeds,
        n_positive=n_positive,
        n_post_drop=int(w.n_post_drop),
        n_dropped=int(w.n_dropped),
        cohen_d=cohen_d_val,
        p_greater=p_val,
        sub_label=sub,
    )


def _check_oom_divergence(d_corr: float, d_naive: float) -> bool:
    """True ssi |d_corr| et |d_naive| diffèrent de plus de 1 OOM (§6.5)
    OU si leurs signes diffèrent (cas pathologique : une branche dit
    "effet positif", l'autre "effet négatif")."""
    a = abs(d_corr)
    b = abs(d_naive)
    # Sign disagreement : si d_corr et d_naive non-nuls et de signes opposés
    if d_corr * d_naive < 0:
        return True
    # Magnitudes very small : ignore (effet trivial des deux côtés)
    eps = 1e-12
    if a < eps and b < eps:
        return False
    if a < eps or b < eps:
        # Une branche annonce un effet, l'autre rien : divergence majeure
        return True
    return (max(a, b) / min(a, b)) > OOM_FACTOR


# ============================================================================
# Verdict global
# ============================================================================

def compute_verdict(
    csv_path: str | Path,
    json_report_path: str | Path | None = None,
) -> VerdictReport:
    """Calcule le verdict v0.5.0 ADR-032 §6 sur un CSV de tirage.

    Args
    ----
    csv_path : chemin vers research/h7_kappa_e1_run_results.csv (ou audit).
    json_report_path : si fourni, écrit un rapport JSON complet pour
        traçabilité.

    Returns
    -------
    VerdictReport (frozen dataclass).
    """
    csv_path = Path(csv_path)
    cols = _read_csv(csv_path)

    n_rows = int(cols["seed"].size)
    eval_corr = _classify_branch("corrected", cols["Delta_kappa_corr"])
    eval_naive = _classify_branch("naive", cols["Delta_kappa_naive"])

    clip_total = int(
        cols["clip_events_R"].sum()
        + cols["clip_events_S"].sum()
        + cols["clip_events_M"].sum()
        + cols["clip_events_Mk"].sum()
    )

    # §6.5 override : recense toutes les raisons indépendamment.
    reasons: list[str] = []
    if clip_total > 0:
        reasons.append(f"clip_events_total={clip_total} > 0 (§6.5)")
    if _check_oom_divergence(eval_corr.cohen_d, eval_naive.cohen_d):
        reasons.append(
            "divergence Cohen d > 1 OOM ou signes opposés entre branches "
            f"(corr={eval_corr.cohen_d:.4f}, naive={eval_naive.cohen_d:.4f}) (§6.5)"
        )
    if eval_corr.sub_label != eval_naive.sub_label:
        reasons.append(
            f"branches en désaccord : corr={eval_corr.sub_label}, "
            f"naive={eval_naive.sub_label} (§6.5)"
        )
    if n_rows != N_SEEDS_EXPECTED:
        reasons.append(
            f"n_rows={n_rows} ≠ {N_SEEDS_EXPECTED} attendus (intégrité du tirage)"
        )

    if eval_corr.sub_label == eval_naive.sub_label:
        nominal: BranchLabel | Literal["DISAGREEMENT"] = eval_corr.sub_label
    else:
        nominal = "DISAGREEMENT"

    if reasons:
        label: VerdictLabel = "KAPPA_INCONCLUSIVE"
    else:
        # §6.5 ne se déclenche pas → nominal = label (les branches concordent ici).
        assert nominal != "DISAGREEMENT"
        label = nominal  # type: ignore[assignment]

    report = VerdictReport(
        label=label,
        nominal_label=nominal,
        branch_corrected=eval_corr,
        branch_naive=eval_naive,
        clip_events_total=clip_total,
        inconclusive_reasons=reasons,
        csv_path=str(csv_path),
        n_rows=n_rows,
    )

    if json_report_path is not None:
        Path(json_report_path).write_text(
            json.dumps(_report_to_dict(report), indent=2, sort_keys=True),
            encoding="utf-8",
        )

    return report


def _report_to_dict(report: VerdictReport) -> dict:
    """Sérialisation traçable (clés stables, ordre alphabétique)."""
    d = asdict(report)
    # Ensure floats are JSON-safe (no inf, no NaN slipping through).
    def _safe(x):
        if isinstance(x, float):
            if not np.isfinite(x):
                return None
            return x
        if isinstance(x, dict):
            return {k: _safe(v) for k, v in x.items()}
        if isinstance(x, list):
            return [_safe(v) for v in x]
        return x
    return _safe(d)
