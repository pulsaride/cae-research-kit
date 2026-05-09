"""CAE — global determinism lock (ADR-020).

Imported at the top of every executable module of the kit. Any uncontrolled
source of entropy invalidates the constraint-pressure redistribution
measurement required by H5.
"""
from __future__ import annotations

import hashlib
import os
import random
import sys
import warnings

import numpy as np

CAE_SEED: int = 42
_APPLIED: bool = False


def apply_cae_determinism(seed: int = CAE_SEED, *, strict: bool = True) -> dict:
    """Force determinism on the current process.

    Returns an external telemetry dict (no internal black-box state).
    If ``strict`` is true, raises when ``PYTHONHASHSEED`` was not set before
    the interpreter started (intrinsic CPython limitation).
    """
    global _APPLIED

    random.seed(seed)
    np.random.seed(seed)

    declared_hashseed = os.environ.get("PYTHONHASHSEED")
    hashseed_effective = declared_hashseed == str(seed)

    if not hashseed_effective:
        msg = (
            f"PYTHONHASHSEED='{declared_hashseed}' != '{seed}'. "
            "Must be set BEFORE the interpreter starts "
            f"(e.g. PYTHONHASHSEED={seed} python -m ...)."
        )
        if strict:
            raise RuntimeError(f"[CAE_SYSTEM] {msg}")
        warnings.warn(f"[CAE_SYSTEM] {msg}", RuntimeWarning, stacklevel=2)

    _APPLIED = True

    telemetry = {
        "seed": seed,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "hashseed_effective": hashseed_effective,
        "fingerprint": _fingerprint(seed),
    }
    return telemetry


def _fingerprint(seed: int) -> str:
    """Reproducible fingerprint: SHA256 of a numpy draw after reseed."""
    rng = np.random.default_rng(seed)
    sample = rng.standard_normal(1024).tobytes()
    return hashlib.sha256(sample).hexdigest()


def assert_applied() -> None:
    if not _APPLIED:
        raise RuntimeError(
            "[CAE_SYSTEM] Determinism not applied. "
            "Call apply_cae_determinism() before any measurement."
        )


if __name__ == "__main__":
    info = apply_cae_determinism(strict=False)
    for k, v in info.items():
        print(f"[CAE_SYSTEM] {k}={v}")
