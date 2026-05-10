"""Brute-force éphémère ADR-033 §6.2 #5 — version S-only optimisée.

R, Mκ, M sont déjà bit-identiques au runner privé (audit FAIL sur S seul).
Donc h_M ne dépend pas de la convention BLAKE2b cherchée. Stratégie :
1. Compute h_M ONCE et cache.
2. Pour chaque candidat (key_fmt × digest_size × byteorder), simule UNIQUEMENT
   la branche S (≈ 4s au lieu de 12s) et calcule KL_S_M_corr contre h_M.
"""
from __future__ import annotations

import csv
import hashlib
import time
from itertools import product

import numpy as np

import src.agents.obs_shuffled_agent as osa_mod
from src.agents.adaptive_agent import AdaptiveAgent
from src.agents.obs_shuffled_agent import ObsShuffledAgent
from src.analysis.sigma_chain import (
    B_DEFAULT,
    fit_markov_transition,
    histogram_pressure,
    kl_corrected_and_naive,
    sample_markov,
)
from src.experiments.portability_draw import (
    GRID_SIZE,
    T_TOTAL,
    _e0_factory,
    _run_action_sequence,
    _run_policy,
    _stat_window,
)

REF_CSV = "research/h7_kappa_run_results.csv"
TARGET_SEED = 1500


def _load_ref(seed: int) -> dict[str, str]:
    with open(REF_CSV) as f:
        for row in csv.DictReader(f):
            if int(row["seed"]) == seed:
                return row
    raise RuntimeError(f"seed {seed} not found in {REF_CSV}")


def make_seed_fn(key_format: str, digest_size: int, byteorder: str):
    def fn(env_seed: int) -> int:
        digest = hashlib.blake2b(
            key_format.format(s=env_seed).encode("ascii"),
            digest_size=digest_size,
        ).digest()
        return int.from_bytes(digest, byteorder=byteorder, signed=False)
    return fn


KEY_FORMATS = [
    "obs_shuffle::{s}",
    "obs_shuffle:{s}",
    "obs_shuffle_{s}",
    "obs_shuffle{s}",
    "S::{s}",
    "{s}",
    "obs::{s}",
    "shuffle::{s}",
    "ObsShuffled::{s}",
    "obs_shuffle::seed::{s}",
    "obs_shuffle/{s}",
    "obs_shuffle.{s}",
    "obs-shuffle::{s}",
    "obs_shuffle::{s}::v1",
    "{s}::obs_shuffle",
]
DIGEST_SIZES = [4, 8, 16]
BYTEORDERS = ["little", "big"]


def compute_kl_s(seed: int, h_M_counts: np.ndarray) -> float:
    env = _e0_factory(seed)
    inner = AdaptiveAgent(GRID_SIZE)
    s_agent = ObsShuffledAgent(inner, GRID_SIZE, env_seed=seed)
    trace_S = _run_policy(env, s_agent)
    pressure_S = _stat_window(trace_S.pressure)
    h_S = histogram_pressure(pressure_S, B_DEFAULT, 0.0, 1.0)
    res = kl_corrected_and_naive(h_S.counts, h_M_counts)
    return res.kl_corrected


def main():
    ref = _load_ref(TARGET_SEED)
    target_kl_s = float(ref["KL_S_M_corr"])
    print(f"[brute] target KL_S_M_corr (seed={TARGET_SEED}) = {target_kl_s:.12f}")

    # Build h_M (cache across candidates).
    print("[brute] building h_M (one-shot)...")
    t0 = time.time()
    env_R = _e0_factory(TARGET_SEED)
    trace_R = _run_policy(env_R, AdaptiveAgent(GRID_SIZE))
    P = fit_markov_transition(trace_R.actions, n_states=GRID_SIZE, alpha=1.0)
    actions_M = sample_markov(
        P, length=T_TOTAL, seed=TARGET_SEED, init_state=int(trace_R.actions[0])
    )
    pressure_M_full = _run_action_sequence(_e0_factory(TARGET_SEED), actions_M)
    pressure_M = _stat_window(pressure_M_full)
    h_M = histogram_pressure(pressure_M, B_DEFAULT, 0.0, 1.0)
    print(f"[brute] h_M ready ({time.time()-t0:.1f}s)")

    original_fn = osa_mod._obs_shuffle_seed

    # Sanity: current convention should reproduce candidate audit value.
    osa_mod._obs_shuffle_seed = original_fn
    cur = compute_kl_s(TARGET_SEED, h_M.counts)
    print(f"[brute] current convention KL_S = {cur:.12f}, diff = {abs(cur-target_kl_s):.3e}")

    n_total = len(KEY_FORMATS) * len(DIGEST_SIZES) * len(BYTEORDERS)
    print(f"[brute] {n_total} combinations to test (S-only)")
    print()

    matches, near = [], []
    for i, (kf, ds, bo) in enumerate(product(KEY_FORMATS, DIGEST_SIZES, BYTEORDERS), 1):
        osa_mod._obs_shuffle_seed = make_seed_fn(kf, ds, bo)
        t0 = time.time()
        kl_s = compute_kl_s(TARGET_SEED, h_M.counts)
        dt = time.time() - t0
        diff = abs(kl_s - target_kl_s)
        tag = ""
        if diff < 1e-9:
            tag = "  *** MATCH ***"
            matches.append((kf, ds, bo, kl_s))
        elif diff < 1e-4:
            tag = "  (near)"
            near.append((kf, ds, bo, kl_s, diff))
        print(
            f"[{i:3d}/{n_total}] "
            f"key={kf!r:<28s} ds={ds:2d} bo={bo:<6s} "
            f"KL_S={kl_s:.12f} diff={diff:.3e} ({dt:.1f}s){tag}"
        )

    osa_mod._obs_shuffle_seed = original_fn
    print()
    print(f"[brute] DONE. matches={len(matches)} near={len(near)}")
    if matches:
        print("[brute] WINNING COMBINATIONS:")
        for kf, ds, bo, kl in matches:
            print(f"  key={kf!r:<28s} ds={ds:2d} bo={bo:<6s} KL_S={kl:.12f}")
    elif near:
        print("[brute] nearest:")
        for kf, ds, bo, kl, diff in sorted(near, key=lambda x: x[4])[:8]:
            print(f"  key={kf!r:<28s} ds={ds:2d} bo={bo:<6s} diff={diff:.3e}")


if __name__ == "__main__":
    main()
