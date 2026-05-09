"""Calibration de `diffusion_coeff` pour E1 (ADR-032 §3.4).

Procédure (ADR-032 §3.4 amendée 2026-05-09) :
  1. σ̄_E0 = écart-type spatial moyen sur régime stationnaire, sur 10 seeds [3000-3009]
  2. σ̄_E1(D) = idem sur E1 pour chaque D ∈ {0.005, 0.010, 0.020, 0.040, 0.080}
  3. Choisir D tel que σ̄_E1(D) ∈ [0.5, 0.8] × σ̄_E0
  4. Audit JSON dans research/calibration_e1.json

Verrou V1 (ADR-032 §7.1) : ce script NE FAIT PAS TOURNER M_κ. Il mesure des
propriétés du champ uniquement (variance spatiale). Conforme.

Usage :
    python -m src.experiments.calibrate_e1
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from src.env.e0 import E0, E0Config
from src.env.e1 import E1, E1Config


CALIBRATION_SEEDS: list[int] = list(range(3000, 3010))     # pool calibration disjoint
DIFFUSION_GRID: list[float] = [0.005, 0.010, 0.020, 0.040, 0.080]
T_WARMUP: int = 64
T_STAT: int = 256
TARGET_RATIO_LOW: float = 0.5
TARGET_RATIO_HIGH: float = 0.8


def _stationary_sigma(env_factory, horizon: int) -> float:
    """Mean over t∈[T_warmup, T_warmup+T_stat] of std_x(f_t), single env."""
    env = env_factory()
    sigmas = []
    for t in range(horizon):
        env.step()
        if t >= T_WARMUP and t < T_WARMUP + T_STAT:
            sigmas.append(float(env.observe().std()))
    return float(np.mean(sigmas))


def _mean_sigma_e0(seeds: list[int]) -> float:
    horizon = T_WARMUP + T_STAT
    vals = [_stationary_sigma(lambda s=s: E0(E0Config(seed=s)), horizon) for s in seeds]
    return float(np.mean(vals))


def _mean_sigma_e1(seeds: list[int], D: float) -> float:
    horizon = T_WARMUP + T_STAT
    vals = [
        _stationary_sigma(
            lambda s=s, d=D: E1(E1Config(seed=s, diffusion_coeff=d)),
            horizon,
        )
        for s in seeds
    ]
    return float(np.mean(vals))


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    print(f"=== Calibration E1 — ADR-032 §3.4 ===")
    print(f"Pool seeds   : {CALIBRATION_SEEDS}")
    print(f"D grid       : {DIFFUSION_GRID}")
    print(f"Window       : t ∈ [{T_WARMUP}, {T_WARMUP + T_STAT})")
    print(f"Target ratio : [{TARGET_RATIO_LOW}, {TARGET_RATIO_HIGH}] × σ̄_E0")
    print()

    sigma_e0 = _mean_sigma_e0(CALIBRATION_SEEDS)
    print(f"σ̄_E0 (10 seeds) = {sigma_e0:.6f}")
    print()

    target_low = TARGET_RATIO_LOW * sigma_e0
    target_high = TARGET_RATIO_HIGH * sigma_e0
    print(f"Target σ̄_E1 ∈ [{target_low:.6f}, {target_high:.6f}]")
    print()

    results: list[dict] = []
    in_band: list[float] = []
    for D in DIFFUSION_GRID:
        s = _mean_sigma_e1(CALIBRATION_SEEDS, D)
        ratio = s / sigma_e0
        ok = target_low <= s <= target_high
        results.append({
            "diffusion_coeff": D,
            "sigma_bar_e1": s,
            "ratio_to_e0": ratio,
            "in_target_band": ok,
        })
        marker = "✓" if ok else " "
        print(f"  D={D:7.4f}  σ̄_E1={s:.6f}  ratio={ratio:.4f}  {marker}")
        if ok:
            in_band.append(D)
    print()

    if not in_band:
        verdict = "NO_VALID_D"
        chosen: float | None = None
        message = (
            f"No D in {DIFFUSION_GRID} produces σ̄_E1 in target band. "
            f"Per ADR-032 §3.4, this triggers an ADR-032.bis (grid extension)."
        )
    else:
        # Among valid D, pick the median to maximize robustness (no spec rule for ties;
        # this choice is logged in the audit).
        chosen = sorted(in_band)[len(in_band) // 2]
        verdict = "OK"
        message = f"D={chosen} retained (median of in-band candidates {in_band})."

    print(f"Verdict: {verdict}")
    print(f"Message: {message}")

    # Audit
    out_dir = Path("research")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "calibration_e1.json"
    audit = {
        "adr": "ADR-032 §3.4 (amended 2026-05-09)",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "seeds_pool": CALIBRATION_SEEDS,
        "diffusion_grid": DIFFUSION_GRID,
        "window": {"t_warmup": T_WARMUP, "t_stat": T_STAT},
        "target_band": [TARGET_RATIO_LOW, TARGET_RATIO_HIGH],
        "sigma_bar_e0": sigma_e0,
        "target_sigma_e1": [target_low, target_high],
        "results": results,
        "verdict": verdict,
        "chosen_diffusion_coeff": chosen,
        "message": message,
        "code_files": {
            "src/env/e0.py": _file_sha256(Path("src/env/e0.py")),
            "src/env/e1.py": _file_sha256(Path("src/env/e1.py")),
        },
    }
    out_path.write_text(json.dumps(audit, indent=2))
    print(f"\nAudit écrit : {out_path}")
    print(f"SHA256 e1.py : {audit['code_files']['src/env/e1.py']}")
    return 0 if verdict == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
