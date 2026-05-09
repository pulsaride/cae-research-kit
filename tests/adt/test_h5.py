"""ADT — H5 test destruction."""
from __future__ import annotations

import os

import numpy as np
import pytest

from src.config.determinism import apply_cae_determinism
from src.env.e0 import E0Config
from src.experiments import (
    H5Verdict,
    VERDICT_DETECTED,
    VERDICT_INCONCLUSIVE,
    VERDICT_REJECTED,
    adjudicate,
    persist,
    run_experiment,
)


@pytest.fixture(autouse=True)
def _bootstrap():
    apply_cae_determinism(strict=False)


# ADT-H1 — underpowered => INCONCLUSIVE, never DETECTED
def test_adt_h1_underpower_is_inconclusive():
    cfg = E0Config(horizon=64)
    seeds = list(range(2000, 2005))  # 5 seeds, below the minimum
    results = run_experiment(seeds, base_config=cfg)
    v = adjudicate(results, min_seeds=30)
    assert v.verdict == VERDICT_INCONCLUSIVE
    assert v.n_seeds == 5


# ADT-H3 — bit-exact verdict reproducibility
def test_adt_h3_verdict_reproducible():
    cfg = E0Config(horizon=64)
    seeds = list(range(3000, 3010))
    r1 = run_experiment(seeds, base_config=cfg)
    r2 = run_experiment(seeds, base_config=cfg)
    for a, b in zip(r1, r2):
        assert a == b, f"ADT-H3: divergence {a} vs {b}"


# ADT-H5 — verdicts are known constants
def test_adt_h5_verdict_enum_strict():
    assert VERDICT_DETECTED == "H5_SIGNATURE_DETECTED"
    assert VERDICT_REJECTED == "H5_REJECTED"
    assert VERDICT_INCONCLUSIVE == "H5_INCONCLUSIVE"


# ADT-H6 — persistence yields readable files
def test_adt_h6_persist_writes_files(tmp_path):
    cfg = E0Config(horizon=32)
    seeds = list(range(4000, 4003))
    results = run_experiment(seeds, base_config=cfg)
    v = adjudicate(results)
    paths = persist(results, v, str(tmp_path))
    assert os.path.exists(paths["csv"])
    assert os.path.exists(paths["json"])
    assert os.path.getsize(paths["csv"]) > 0


# ADT-H7 — adjudicate on trivial data (A=R) => REJECTED
def test_adt_h7_when_a_equals_r_is_rejected():
    from src.experiments import RunResult

    rng = np.random.default_rng(0)
    results = []
    for s in range(40):
        val = float(rng.random())
        for name in ("A", "R"):
            results.append(RunResult(
                agent=name, env_seed=s, horizon=10, grid_size=8,
                redistribution_mean=val,  # identical per seed
                redistribution_std=0.0,
                redistribution_sum=val,
            ))
        # B with distinct values to avoid NaN on Wilcoxon A vs B
        results.append(RunResult(
            agent="B", env_seed=s, horizon=10, grid_size=8,
            redistribution_mean=val + 0.1,
            redistribution_std=0.0, redistribution_sum=val + 0.1,
        ))
        # P with distinct values to avoid NaN on Wilcoxon A vs P
        results.append(RunResult(
            agent="P", env_seed=s, horizon=10, grid_size=8,
            redistribution_mean=val + 0.2,
            redistribution_std=0.0, redistribution_sum=val + 0.2,
        ))
    v = adjudicate(results, min_seeds=30)
    assert v.verdict == VERDICT_REJECTED, f"got {v.verdict}"
