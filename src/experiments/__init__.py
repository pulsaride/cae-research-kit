"""CAE — H5 experimental harness.

Runs A, B, R, P over K environment seeds, measures the W1 redistribution
trajectory, aggregates, and persists CSV/JSON in /research.

No "soft" decisions: the verdict is a strict enum.
"""
from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, asdict
from typing import Callable, Iterable

import numpy as np
from scipy.stats import wilcoxon

from src.agents.adaptive_agent import AdaptiveAgent
from src.agents.base import Agent
from src.agents.pretrained_agent import PretrainedAgent
from src.agents.random_agent import RandomAgent
from src.agents.scripted_agent import ScriptedAgent
from src.config.determinism import apply_cae_determinism
from src.env.e0 import E0, E0Config

# NB : src.metrics.pressure dépend de POT (`ot`), absent de certains
# environnements de dev (.venv-h6 sans POT). On reporte l'import au
# call-site pour permettre à src.experiments.portability_draw d'être
# chargé indépendamment (ADR-033 audit gate, runner public chaîne σ).
if False:  # type-checker hint only
    from src.metrics.pressure import Wasserstein1, trajectory_redistribution  # noqa: F401

OFFLINE_SEED: int = 99  # disjoint from evaluation seeds (>= 1000)


VERDICT_DETECTED = "H5_SIGNATURE_DETECTED"
VERDICT_REJECTED = "H5_REJECTED"
VERDICT_INCONCLUSIVE = "H5_INCONCLUSIVE"


@dataclass(frozen=True)
class RunResult:
    agent: str
    env_seed: int
    horizon: int
    grid_size: int
    redistribution_mean: float
    redistribution_std: float
    redistribution_sum: float


@dataclass(frozen=True)
class H5Verdict:
    verdict: str
    n_seeds: int
    mean_A: float
    mean_B: float
    mean_R: float
    mean_P: float
    delta_AR: float
    delta_AB: float
    delta_AP: float
    sigma_pooled_AR: float
    cohen_d_AR: float
    cohen_d_AB: float
    cohen_d_AP: float
    wilcoxon_AR_pvalue: float
    wilcoxon_AB_pvalue: float
    wilcoxon_AP_pvalue: float
    threshold_sigma: float
    min_seeds_required: int


def _agent_factories(
    grid_size: int,
    pretrained_policy: np.ndarray,
) -> dict[str, Callable[[int], Agent]]:
    """Per-agent factories. P receives the offline-frozen policy."""
    return {
        "A": lambda _seed: AdaptiveAgent(grid_size),
        "B": lambda _seed: ScriptedAgent(grid_size),
        "R": lambda seed: RandomAgent(grid_size, seed=seed),
        "P": lambda _seed: PretrainedAgent(grid_size, policy_table=pretrained_policy),
    }


def run_single(agent: Agent, env: E0, metric: "Wasserstein1") -> RunResult:  # type: ignore[name-defined]
    """Run a full trajectory; return redistribution aggregates."""
    from src.metrics.pressure import trajectory_redistribution
    fields = [env.observe()]
    while not env.is_done:
        a = agent.select_action(fields[-1])
        env.act(a)
        env.step()
        fields.append(env.observe())
    F = np.stack(fields)  # (T+1, grid_size)
    R = trajectory_redistribution(F, metric=metric)
    return RunResult(
        agent=agent.name,
        env_seed=env.config.seed,
        horizon=env.config.horizon,
        grid_size=env.config.grid_size,
        redistribution_mean=float(R.mean()),
        redistribution_std=float(R.std(ddof=1)) if R.size > 1 else 0.0,
        redistribution_sum=float(R.sum()),
    )


def _train_pretrained_policy(base_config: E0Config) -> np.ndarray:
    """Offline training of P, on a disjoint seed."""
    if OFFLINE_SEED in range(1000, 100000):
        raise RuntimeError("OFFLINE_SEED collides with evaluation seeds.")

    def factory(seed: int) -> E0:
        return E0(E0Config(
            grid_size=base_config.grid_size,
            horizon=base_config.horizon,
            n_modes=base_config.n_modes,
            seed=seed,
            drift_rate=base_config.drift_rate,
            action_kernel_width=base_config.action_kernel_width,
            action_amplitude=base_config.action_amplitude,
            relaxation=base_config.relaxation,
        ))
    return PretrainedAgent.train(factory, offline_seed=OFFLINE_SEED)


def run_experiment(
    seeds: Iterable[int],
    base_config: E0Config | None = None,
    metric: "Wasserstein1 | None" = None,  # type: ignore[name-defined]
) -> list[RunResult]:
    """Paired loop: for each E0 seed, run A, B, R, P."""
    from src.metrics.pressure import Wasserstein1
    base_config = base_config or E0Config()
    metric = metric or Wasserstein1()
    pretrained_policy = _train_pretrained_policy(base_config)
    factories = _agent_factories(base_config.grid_size, pretrained_policy)
    results: list[RunResult] = []
    for s in seeds:
        cfg = E0Config(
            grid_size=base_config.grid_size,
            horizon=base_config.horizon,
            n_modes=base_config.n_modes,
            seed=int(s),
            drift_rate=base_config.drift_rate,
            action_kernel_width=base_config.action_kernel_width,
            action_amplitude=base_config.action_amplitude,
            relaxation=base_config.relaxation,
        )
        for name, factory in factories.items():
            agent = factory(int(s))
            agent.reset()
            env = E0(cfg)
            results.append(run_single(agent, env, metric))
    return results


def adjudicate(
    results: list[RunResult],
    threshold_sigma: float = 3.0,
    min_seeds: int = 30,
    alpha: float = 0.01,
) -> H5Verdict:
    """Strict verdict. Without sufficient power -> INCONCLUSIVE."""
    by_agent: dict[str, list[RunResult]] = {"A": [], "B": [], "R": [], "P": []}
    for r in results:
        if r.agent in by_agent:
            by_agent[r.agent].append(r)

    seeds_sorted = sorted({r.env_seed for r in results})

    def _vec(name: str) -> np.ndarray:
        return np.array([
            next(r.redistribution_mean for r in by_agent[name] if r.env_seed == s)
            for s in seeds_sorted
        ])

    has_P = len(by_agent["P"]) > 0
    A = _vec("A"); B = _vec("B"); R = _vec("R")
    P = _vec("P") if has_P else np.full_like(A, np.nan)

    n = len(seeds_sorted)
    mean_A, mean_B, mean_R = float(A.mean()), float(B.mean()), float(R.mean())
    mean_P = float(P.mean()) if has_P else float("nan")
    delta_AR = mean_A - mean_R
    delta_AB = mean_A - mean_B
    delta_AP = (mean_A - mean_P) if has_P else float("nan")

    def _cohen(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
        s = float(np.sqrt(0.5 * (x.var(ddof=1) + y.var(ddof=1))))
        d = float((x.mean() - y.mean()) / s) if s > 0 else 0.0
        return d, s

    cohen_d_AR, sigma_pooled_AR = _cohen(A, R)
    cohen_d_AB, _ = _cohen(A, B)
    cohen_d_AP, _ = _cohen(A, P) if has_P else (float("nan"), float("nan"))

    def _wil(x: np.ndarray, y: np.ndarray) -> float:
        if n >= 6 and not np.allclose(x, y):
            _, p = wilcoxon(x, y)
            return float(p)
        return float("nan")

    p_AR = _wil(A, R)
    p_AB = _wil(A, B)
    p_AP = _wil(A, P) if has_P else float("nan")

    # Decision: H5 DETECTED requires simultaneous distinction vs R, B, and P.
    if n < min_seeds:
        verdict = VERDICT_INCONCLUSIVE
    elif (
        abs(cohen_d_AR) >= threshold_sigma
        and p_AR < alpha and p_AB < alpha and (not has_P or p_AP < alpha)
        and abs(delta_AR) > abs(delta_AB) * 0.5
        and (not has_P or abs(delta_AR) > abs(delta_AP) * 0.5)
    ):
        verdict = VERDICT_DETECTED
    elif p_AR >= alpha or abs(cohen_d_AR) < 1.0:
        verdict = VERDICT_REJECTED
    else:
        verdict = VERDICT_INCONCLUSIVE

    return H5Verdict(
        verdict=verdict,
        n_seeds=n,
        mean_A=mean_A, mean_B=mean_B, mean_R=mean_R, mean_P=mean_P,
        delta_AR=delta_AR, delta_AB=delta_AB, delta_AP=delta_AP,
        sigma_pooled_AR=sigma_pooled_AR,
        cohen_d_AR=cohen_d_AR, cohen_d_AB=cohen_d_AB, cohen_d_AP=cohen_d_AP,
        wilcoxon_AR_pvalue=p_AR,
        wilcoxon_AB_pvalue=p_AB,
        wilcoxon_AP_pvalue=p_AP,
        threshold_sigma=threshold_sigma,
        min_seeds_required=min_seeds,
    )


def persist(results: list[RunResult], verdict: H5Verdict, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "h5_run_results.csv")
    json_path = os.path.join(out_dir, "h5_verdict.json")

    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(asdict(results[0]).keys()))
        w.writeheader()
        for r in results:
            w.writerow(asdict(r))

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(asdict(verdict), fh, indent=2)

    return {"csv": csv_path, "json": json_path}


def main(n_seeds: int = 30, out_dir: str = "research") -> H5Verdict:
    apply_cae_determinism(strict=False)
    seeds = list(range(1000, 1000 + n_seeds))  # deterministic range
    results = run_experiment(seeds)
    verdict = adjudicate(results)
    paths = persist(results, verdict, out_dir)
    print(f"[CAE_H5] verdict={verdict.verdict}")
    print(f"[CAE_H5] n_seeds={verdict.n_seeds}")
    print(f"[CAE_H5] mean A={verdict.mean_A:.6e} B={verdict.mean_B:.6e} "
          f"R={verdict.mean_R:.6e} P={verdict.mean_P:.6e}")
    print(f"[CAE_H5] delta AR={verdict.delta_AR:.3e} AB={verdict.delta_AB:.3e} "
          f"AP={verdict.delta_AP:.3e}")
    print(f"[CAE_H5] cohen_d AR={verdict.cohen_d_AR:.3f} AB={verdict.cohen_d_AB:.3f} "
          f"AP={verdict.cohen_d_AP:.3f}")
    print(f"[CAE_H5] wilcoxon p(A,R)={verdict.wilcoxon_AR_pvalue:.3e} "
          f"p(A,B)={verdict.wilcoxon_AB_pvalue:.3e} "
          f"p(A,P)={verdict.wilcoxon_AP_pvalue:.3e}")
    print(f"[CAE_H5] csv={paths['csv']} json={paths['json']}")
    return verdict


if __name__ == "__main__":
    main()
