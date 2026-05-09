"""ADT — bootstrap destruction tests.

Each test corresponds to a possible falsification of the structural lock.
Failure = invalid bootstrap, every later measurement is suspect.
"""
from __future__ import annotations

import os
import subprocess
import sys

import numpy as np
import pytest

from src.config.determinism import (
    CAE_SEED,
    apply_cae_determinism,
    assert_applied,
)
from src.metrics.base import ConstraintMetric


# ---------------------------------------------------------------------------
# ADT-B1 — bit-exact numpy/random reproducibility after reseed
# ---------------------------------------------------------------------------
def test_adt_b1_numpy_bitwise_reproducibility():
    apply_cae_determinism(strict=False)
    a = np.random.rand(1000).copy()
    apply_cae_determinism(strict=False)
    b = np.random.rand(1000).copy()
    assert np.array_equal(a, b), "ADT-B1: numpy draws diverge under same seed."


def test_adt_b1_fingerprint_stable():
    t1 = apply_cae_determinism(strict=False)
    t2 = apply_cae_determinism(strict=False)
    assert t1["fingerprint"] == t2["fingerprint"], "ADT-B1: unstable fingerprint."


# ---------------------------------------------------------------------------
# ADT-B2 — PYTHONHASHSEED actually effective when exported before the interpreter
# ---------------------------------------------------------------------------
def test_adt_b2_pythonhashseed_propagation():
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = str(CAE_SEED)
    code = (
        "from src.config.determinism import apply_cae_determinism;"
        "info = apply_cae_determinism(strict=True);"
        "print(info['hashseed_effective'])"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    )
    assert result.returncode == 0, f"ADT-B2 stderr: {result.stderr}"
    assert result.stdout.strip().endswith("True"), (
        f"ADT-B2: hashseed not propagated. stdout={result.stdout!r}"
    )


# ---------------------------------------------------------------------------
# ADT-B3 — pyproject.toml pins versions (==), no floating ranges
# ---------------------------------------------------------------------------
def test_adt_b3_pyproject_pins_exact_versions():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(root, "pyproject.toml")
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()

    forbidden_specifiers = (">=", "<=", "~=", ">", "<", "^")
    # Inspect only the dependencies block
    in_deps = False
    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith("dependencies"):
            in_deps = True
            continue
        if in_deps:
            if line.startswith("]"):
                break
            if not line or line.startswith("#"):
                continue
            assert "==" in line, f"ADT-B3: unpinned version -> {line!r}"
            for tok in forbidden_specifiers:
                assert tok not in line, f"ADT-B3: forbidden specifier {tok!r} in {line!r}"


# ---------------------------------------------------------------------------
# ADT-B4 — ConstraintMetric interface does not leak (non-instantiable / raises)
# ---------------------------------------------------------------------------
def test_adt_b4_constraint_metric_is_abstract():
    with pytest.raises(TypeError):
        ConstraintMetric()  # type: ignore[abstract]


def test_adt_b4_constraint_metric_concrete_must_override():
    class Leaky(ConstraintMetric):
        def compute(self, a, b):  # deliberately calls the base
            return super().compute(a, b)

    with pytest.raises(NotImplementedError):
        Leaky().compute(np.zeros(3), np.zeros(3))


# ---------------------------------------------------------------------------
# Safety net: assert_applied
# ---------------------------------------------------------------------------
def test_assert_applied_after_bootstrap():
    apply_cae_determinism(strict=False)
    assert_applied()
