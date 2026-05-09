"""Tirage portabilité κ — runner public (ADR-032 + audit gate ADR-033).

Pour un seed s donné, le pipeline est :

  1. Instancier un env neuf, faire tourner R = AdaptiveAgent T_total ticks ;
     collecter (i) la pression cellule par cellule à chaque tick et (ii) la
     séquence d'actions de R.
  2. Instancier un env neuf au même seed, faire tourner S =
     ObsShuffledAgent(AdaptiveAgent, env_seed=s) T_total ticks ; collecter
     la pression.
  3. Instancier un env neuf, faire tourner M_κ = Memory1Agent T_total ticks ;
     collecter la pression.
  4. Ajuster une matrice de transition Markov sur la séquence complète
     d'actions de R (Laplace α=1.0). Échantillonner T_total actions de M
     baseline (init_state = R_actions[0], seed = s). Rejouer ces actions
     sur un env neuf, collecter la pression.
  5. Pour X ∈ {R, S, M, M_κ}, garder la fenêtre stat [T_warmup,
     T_warmup + T_stat), aplatir (cellule × tick), calculer histogramme
     B=64 sur [0, 1].
  6. Calculer KL(X ‖ M) pour X ∈ {R, S, M_κ}. Définir
     δ_σ^X = KL(X ‖ M) − KL(S ‖ M)  pour X ∈ {R, M_κ}
     Δ_κ = δ_σ^{M_κ} − δ_σ^R

Branche corrigée (Miller-Madow) ET branche naïve (plug-in) en parallèle.

CLI :

  python -m src.experiments.portability_draw --pool audit \
      --output research/h7_kappa_audit_v04.csv

  python -m src.experiments.portability_draw --pool portability \
      --output research/h7_kappa_e1_run_results.csv \
      --i-have-read-adr-033

POOL audit  → E0, seeds [1500-1529]  (rejeu du tirage v0.4.0).
POOL portability → E1, seeds [2000-2029] (le tirage qui rend le verdict v0.5.0).

Le pool 'portability' est INACCESSIBLE sans le drapeau explicite
--i-have-read-adr-033 et tant que le verrou V3 n'a pas été levé par
acceptation publique d'ADR-033.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

import numpy as np

from src.agents.adaptive_agent import AdaptiveAgent
from src.agents.base import Agent
from src.agents.memory1_agent import Memory1Agent
from src.agents.obs_shuffled_agent import ObsShuffledAgent
from src.analysis.sigma_chain import (
    B_DEFAULT,
    P_MAX_DEFAULT,
    P_MIN_DEFAULT,
    fit_markov_transition,
    histogram_pressure,
    kl_corrected_and_naive,
    sample_markov,
)


# ============================================================================
# Constantes du tirage (figées par ADR-026 §3 + CSV v0.4.0)
# ============================================================================

T_WARMUP = 5000
T_STAT = 50000
T_TOTAL = T_WARMUP + T_STAT  # 55000
GRID_SIZE = 64

POOL_AUDIT = (1500, 1529)        # 30 seeds, E0, AUDIT (v0.4.0 reproduction)
POOL_PORTABILITY = (2000, 2029)  # 30 seeds, E1, V3 — gel jusqu'à ADR-033 ACCEPT


# ============================================================================
# Interfaces : env factory abstraite
# ============================================================================

class _EnvLike(Protocol):
    """Forme minimale attendue d'un environnement (cf. PROTOCOL §3)."""

    def observe(self) -> np.ndarray: ...
    def act(self, position: int) -> None: ...
    def step(self) -> dict: ...
    @property
    def is_done(self) -> bool: ...


EnvFactory = Callable[[int], _EnvLike]
"""Construit un env neuf pour un seed donné, avec horizon = T_TOTAL."""


# ============================================================================
# Run bas-niveau : un agent sur un env, retour pression + actions
# ============================================================================

@dataclass(frozen=True)
class _PolicyTrace:
    """Trace d'une politique sur un env (T_TOTAL ticks)."""
    pressure: np.ndarray  # shape (T_TOTAL, GRID_SIZE), float64
    actions: np.ndarray   # shape (T_TOTAL,), int64


def _run_policy(env: _EnvLike, agent: Agent) -> _PolicyTrace:
    """Boucle standard PROTOCOL §3 : observe → select_action → act → step.
    Collecte pression à chaque tick AVANT action (cf. ADR-026 §3.2)."""
    pressure = np.empty((T_TOTAL, GRID_SIZE), dtype=np.float64)
    actions = np.empty(T_TOTAL, dtype=np.int64)
    for t in range(T_TOTAL):
        obs = env.observe()
        a = agent.select_action(obs)
        pressure[t] = obs
        actions[t] = a
        env.act(a)
        env.step()
    return _PolicyTrace(pressure=pressure, actions=actions)


def _run_action_sequence(env: _EnvLike, actions: np.ndarray) -> np.ndarray:
    """Rejoue une séquence d'actions sur un env neuf, retourne pression
    (T_TOTAL, GRID_SIZE)."""
    if actions.shape != (T_TOTAL,):
        raise ValueError(
            f"actions doit avoir shape ({T_TOTAL},), reçu {actions.shape}"
        )
    pressure = np.empty((T_TOTAL, GRID_SIZE), dtype=np.float64)
    for t in range(T_TOTAL):
        pressure[t] = env.observe()
        env.act(int(actions[t]))
        env.step()
    return pressure


def _stat_window(pressure: np.ndarray) -> np.ndarray:
    """Aplatit la fenêtre stat [T_WARMUP, T_TOTAL) → vecteur 1D
    (T_STAT * GRID_SIZE,)."""
    return pressure[T_WARMUP:T_TOTAL].reshape(-1)


# ============================================================================
# Run d'un seed : produit la ligne CSV complète
# ============================================================================

@dataclass(frozen=True)
class SeedRow:
    """Une ligne CSV (schéma v0.4.0 verbatim)."""
    seed: int
    T_warmup: int
    T_stat: int
    B: int
    P_min: float
    P_max: float
    KL_R_M_corr: float
    KL_S_M_corr: float
    KL_Mk_M_corr: float
    KL_R_M_naive: float
    KL_S_M_naive: float
    KL_Mk_M_naive: float
    delta_sigma_R_corr: float
    delta_sigma_Mk_corr: float
    delta_sigma_R_naive: float
    delta_sigma_Mk_naive: float
    Delta_kappa_corr: float
    Delta_kappa_naive: float
    K_R_nonempty: int
    K_S_nonempty: int
    K_M_nonempty: int
    K_Mk_nonempty: int
    laplace_bins_R: int
    laplace_bins_S: int
    laplace_bins_Mk: int
    clip_events_R: int
    clip_events_S: int
    clip_events_M: int
    clip_events_Mk: int


CSV_FIELDNAMES = (
    "seed", "T_warmup", "T_stat", "B", "P_min", "P_max",
    "KL_R_M_corr", "KL_S_M_corr", "KL_Mk_M_corr",
    "KL_R_M_naive", "KL_S_M_naive", "KL_Mk_M_naive",
    "delta_sigma_R_corr", "delta_sigma_Mk_corr",
    "delta_sigma_R_naive", "delta_sigma_Mk_naive",
    "Delta_kappa_corr", "Delta_kappa_naive",
    "K_R_nonempty", "K_S_nonempty", "K_M_nonempty", "K_Mk_nonempty",
    "laplace_bins_R", "laplace_bins_S", "laplace_bins_Mk",
    "clip_events_R", "clip_events_S", "clip_events_M", "clip_events_Mk",
)


def run_seed(seed: int, env_factory: EnvFactory) -> SeedRow:
    """Exécute le tirage complet pour un seed et retourne la ligne CSV."""
    # -- Run R (AdaptiveAgent) -------------------------------------------
    env_R = env_factory(seed)
    agent_R = AdaptiveAgent(GRID_SIZE)
    trace_R = _run_policy(env_R, agent_R)

    # -- Run S (ObsShuffledAgent wrapping AdaptiveAgent) -----------------
    env_S = env_factory(seed)
    agent_S = ObsShuffledAgent(AdaptiveAgent(GRID_SIZE), GRID_SIZE, env_seed=seed)
    trace_S = _run_policy(env_S, agent_S)

    # -- Run M_κ (Memory1Agent) ------------------------------------------
    env_Mk = env_factory(seed)
    agent_Mk = Memory1Agent(GRID_SIZE)
    trace_Mk = _run_policy(env_Mk, agent_Mk)

    # -- Markov baseline M : fit sur actions de R, replay -----------------
    # ADR-026 §3.1 : init_state = actions_R[0], seed = s, default_rng.
    P = fit_markov_transition(trace_R.actions, n_states=GRID_SIZE, alpha=1.0)
    actions_M = sample_markov(P, length=T_TOTAL, seed=seed,
                              init_state=int(trace_R.actions[0]))
    env_M = env_factory(seed)
    pressure_M = _run_action_sequence(env_M, actions_M)

    # -- Histogrammes sur la fenêtre stat ---------------------------------
    samples_R = _stat_window(trace_R.pressure)
    samples_S = _stat_window(trace_S.pressure)
    samples_Mk = _stat_window(trace_Mk.pressure)
    samples_M = _stat_window(pressure_M)

    h_R = histogram_pressure(samples_R, B=B_DEFAULT,
                             P_min=P_MIN_DEFAULT, P_max=P_MAX_DEFAULT)
    h_S = histogram_pressure(samples_S, B=B_DEFAULT,
                             P_min=P_MIN_DEFAULT, P_max=P_MAX_DEFAULT)
    h_Mk = histogram_pressure(samples_Mk, B=B_DEFAULT,
                              P_min=P_MIN_DEFAULT, P_max=P_MAX_DEFAULT)
    h_M = histogram_pressure(samples_M, B=B_DEFAULT,
                             P_min=P_MIN_DEFAULT, P_max=P_MAX_DEFAULT)

    # -- KL(X ‖ M) pour X ∈ {R, S, M_κ} -----------------------------------
    kl_R = kl_corrected_and_naive(h_R.counts, h_M.counts)
    kl_S = kl_corrected_and_naive(h_S.counts, h_M.counts)
    kl_Mk = kl_corrected_and_naive(h_Mk.counts, h_M.counts)

    # -- δ_σ et Δ_κ -------------------------------------------------------
    delta_R_corr = kl_R.kl_corrected - kl_S.kl_corrected
    delta_Mk_corr = kl_Mk.kl_corrected - kl_S.kl_corrected
    delta_R_naive = kl_R.kl_naive - kl_S.kl_naive
    delta_Mk_naive = kl_Mk.kl_naive - kl_S.kl_naive
    Delta_kappa_corr = delta_Mk_corr - delta_R_corr
    Delta_kappa_naive = delta_Mk_naive - delta_R_naive

    return SeedRow(
        seed=seed,
        T_warmup=T_WARMUP, T_stat=T_STAT,
        B=B_DEFAULT, P_min=P_MIN_DEFAULT, P_max=P_MAX_DEFAULT,
        KL_R_M_corr=kl_R.kl_corrected,
        KL_S_M_corr=kl_S.kl_corrected,
        KL_Mk_M_corr=kl_Mk.kl_corrected,
        KL_R_M_naive=kl_R.kl_naive,
        KL_S_M_naive=kl_S.kl_naive,
        KL_Mk_M_naive=kl_Mk.kl_naive,
        delta_sigma_R_corr=delta_R_corr,
        delta_sigma_Mk_corr=delta_Mk_corr,
        delta_sigma_R_naive=delta_R_naive,
        delta_sigma_Mk_naive=delta_Mk_naive,
        Delta_kappa_corr=Delta_kappa_corr,
        Delta_kappa_naive=Delta_kappa_naive,
        K_R_nonempty=kl_R.K_X_nonempty,
        K_S_nonempty=kl_S.K_X_nonempty,
        K_M_nonempty=int((h_M.counts > 0).sum()),
        K_Mk_nonempty=kl_Mk.K_X_nonempty,
        laplace_bins_R=kl_R.laplace_bins,
        laplace_bins_S=kl_S.laplace_bins,
        laplace_bins_Mk=kl_Mk.laplace_bins,
        clip_events_R=h_R.clip_events,
        clip_events_S=h_S.clip_events,
        clip_events_M=h_M.clip_events,
        clip_events_Mk=h_Mk.clip_events,
    )


# ============================================================================
# Sérialisation CSV
# ============================================================================

def _format_value(value, fieldname: str) -> str:
    """Formate une valeur pour CSV avec précision figée (12 décimales sur les
    floats de chaîne, pas de notation scientifique inutile)."""
    if isinstance(value, float):
        # 12 décimales : suffisant pour audit atol=1e-9 sans bruit d'arrondi.
        return f"{value:.12f}"
    return str(value)


def write_csv(rows: list[SeedRow], output_path: Path) -> None:
    """Écrit les lignes au format v0.4.0 (en-têtes + ordre fixe)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(CSV_FIELDNAMES))
        writer.writeheader()
        for row in rows:
            d = {f: _format_value(getattr(row, f), f) for f in CSV_FIELDNAMES}
            writer.writerow(d)


# ============================================================================
# Env factories (E0 audit / E1 portabilité)
# ============================================================================

def _e0_factory(seed: int) -> _EnvLike:
    """Importé localement pour ne pas créer de dépendance forte au module
    src.env (qui peut échouer à l'import si POT manque dans certains env)."""
    from src.env.e0 import E0, E0Config
    cfg = E0Config(grid_size=GRID_SIZE, horizon=T_TOTAL, seed=seed)
    return E0(cfg)


def _e1_factory(seed: int) -> _EnvLike:
    from src.env.e1 import E1, E1Config
    cfg = E1Config(grid_size=GRID_SIZE, horizon=T_TOTAL, seed=seed)
    return E1(cfg)


# ============================================================================
# CLI
# ============================================================================

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="portability_draw",
        description=(
            "Tirage portabilité κ — runner public ADR-032 + ADR-033 audit gate."
        ),
    )
    p.add_argument(
        "--pool",
        choices=("audit", "portability"),
        required=True,
        help=(
            "audit: E0 seeds [1500-1529] (re-jeu v0.4.0). "
            "portability: E1 seeds [2000-2029] (verdict v0.5.0). "
            "Le pool 'portability' exige --i-have-read-adr-033 et que V3 "
            "soit levé par acceptation publique d'ADR-033."
        ),
    )
    p.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Chemin du CSV de sortie.",
    )
    p.add_argument(
        "--i-have-read-adr-033",
        action="store_true",
        help="Drapeau requis pour --pool portability (verrou V3).",
    )
    p.add_argument(
        "--seeds",
        nargs="*",
        type=int,
        default=None,
        help=(
            "Optionnel : liste explicite de seeds à exécuter. "
            "Par défaut, utilise le pool standard du --pool choisi."
        ),
    )
    return p


def _resolve_pool(args: argparse.Namespace) -> tuple[list[int], EnvFactory]:
    if args.pool == "audit":
        seeds = (
            list(range(POOL_AUDIT[0], POOL_AUDIT[1] + 1))
            if args.seeds is None else list(args.seeds)
        )
        return seeds, _e0_factory
    if args.pool == "portability":
        if not args.i_have_read_adr_033:
            raise SystemExit(
                "REFUS : --pool portability exige --i-have-read-adr-033 "
                "(verrou V3, ADR-032 §7.1). Le pool [2000-2029] est gelé "
                "tant qu'ADR-033 n'est pas formellement ACCEPTÉ et que "
                "le tag 'audit-passed-v1' n'a pas été posé sur main."
            )
        seeds = (
            list(range(POOL_PORTABILITY[0], POOL_PORTABILITY[1] + 1))
            if args.seeds is None else list(args.seeds)
        )
        return seeds, _e1_factory
    raise SystemExit(f"Pool inconnu : {args.pool}")


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    seeds, factory = _resolve_pool(args)

    print(f"[portability_draw] pool={args.pool} n_seeds={len(seeds)} "
          f"output={args.output}", flush=True)

    rows: list[SeedRow] = []
    t0 = time.time()
    for i, seed in enumerate(seeds, start=1):
        ts = time.time()
        row = run_seed(seed, factory)
        rows.append(row)
        elapsed = time.time() - ts
        print(
            f"[portability_draw] [{i:>2d}/{len(seeds)}] seed={seed} "
            f"Δκ_corr={row.Delta_kappa_corr:+.6f} "
            f"Δκ_naive={row.Delta_kappa_naive:+.6f} "
            f"clip={row.clip_events_R+row.clip_events_S+row.clip_events_M+row.clip_events_Mk} "
            f"({elapsed:.1f}s)",
            flush=True,
        )

    write_csv(rows, args.output)
    print(f"[portability_draw] DONE total={time.time()-t0:.1f}s "
          f"→ {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
