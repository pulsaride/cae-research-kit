"""CAE — environment E1 (κ portability target, ADR-032).

E1 differs from E0 on **a single structural axis**: a non-local spatial coupling
introduced by a discrete 1D Laplacian on a ring (periodic boundary).

All other terms (drifting reference field, action kernel, relaxation) are
**bit-identical** to E0 — see test_e1.py::test_blackbox_isolation and
test_structural_difference_from_e0.

Spec: ADR-032 §3.1, §3.2, §3.3 (frozen). Modification of those sections after
E1 instantiation requires PROPOSED rollback per V2 (ADR-032 §7.1).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class E1Config:
    """Frozen E1 configuration. Any modification = new experiment.

    Fields shared with E0Config keep identical defaults to guarantee that the
    only structural difference is `diffusion_coeff` (cf. ADR-032 §3.1).
    """
    grid_size: int = 64
    horizon: int = 512
    n_modes: int = 4
    seed: int = 42
    drift_rate: float = 0.015
    action_kernel_width: int = 5
    action_amplitude: float = 0.10
    relaxation: float = 0.05
    # --- E1-specific (NEW per ADR-032 §3.2) ---
    diffusion_coeff: float = 0.080  # Calibrated 2026-05-09 per ADR-032 §3.4 step 4.
                                    # See research/calibration_e1.json (audit).
    laplacian_boundary: str = "periodic"  # applies ONLY to the Laplacian operator


class E1:
    """1D non-stationary constraint field with non-local spatial coupling.

    Public API (identical to E0 for measurability — ADR-032 C4):
        - observe() -> np.ndarray
        - act(position: int) -> None
        - step() -> dict
        - t (read-only)
        - is_done: bool
        - config: E1Config (frozen)
    """

    def __init__(self, config: E1Config | None = None) -> None:
        self._config: E1Config = config if config is not None else E1Config()

        if self._config.laplacian_boundary != "periodic":
            raise NotImplementedError(
                "Only laplacian_boundary='periodic' is specified by ADR-032 §3.2."
            )

        rng = np.random.default_rng(self._config.seed)
        # Bit-identical reference-field generators (ADR-032 §3.3).
        self.__freqs = rng.integers(1, 8, size=self._config.n_modes)
        self.__phases = rng.uniform(0.0, 2 * np.pi, size=self._config.n_modes)
        self.__omegas = (np.arange(1, self._config.n_modes + 1)
                         * np.pi * self._config.drift_rate)
        self.__amplitudes = rng.uniform(0.3, 0.7, size=self._config.n_modes)
        self.__amplitudes /= self.__amplitudes.sum()

        x = np.linspace(0.0, 1.0, self._config.grid_size, endpoint=False)
        self.__basis = np.stack(
            [np.cos(2 * np.pi * f * x + p)
             for f, p in zip(self.__freqs, self.__phases)],
            axis=0,
        )

        self._t: int = 0
        self._field: np.ndarray = self._reference_field(0)
        self._last_action_pos: int | None = None

    # ---- Public API --------------------------------------------------------

    @property
    def config(self) -> E1Config:
        return self._config

    @property
    def t(self) -> int:
        return self._t

    @property
    def is_done(self) -> bool:
        return self._t >= self._config.horizon

    def observe(self) -> np.ndarray:
        return self._field.copy()

    def act(self, position: int) -> None:
        if not (0 <= position < self._config.grid_size):
            raise ValueError(
                f"position {position} out of grid [0, {self._config.grid_size})"
            )
        kernel = self._action_kernel(position)
        # Action kernel is bit-identical to E0: euclidean distance, NOT modular
        # (ADR-032 §3.3 amendment §12 / 2026-05-09).
        self._field = np.clip(self._field - kernel, 0.0, 1.0)
        self._last_action_pos = position

    def step(self) -> dict[str, Any]:
        if self.is_done:
            raise RuntimeError("E1 horizon reached. Re-instantiate for a new run.")

        # 1. Linear relaxation toward the drifting reference (bit-identical to E0).
        ref = self._reference_field(self._t + 1)
        self._field = (1.0 - self._config.relaxation) * self._field \
            + self._config.relaxation * ref

        # 2. ADR-032 §3.3: f_{t+1} <- f_{t+1} + D * Δ_ring f_{t+1}
        #    Discrete 1D Laplacian on a ring (periodic boundary).
        self._field = self._field + self._config.diffusion_coeff * self._laplacian_ring(
            self._field
        )

        # 3. Final clip (after both linear relaxation and diffusion).
        self._field = np.clip(self._field, 0.0, 1.0)

        self._t += 1
        return {
            "t": self._t,
            "pressure_integral": float(self._field.sum()),
            "pressure_max": float(self._field.max()),
            "pressure_min": float(self._field.min()),
            "last_action_pos": self._last_action_pos,
        }

    # ---- Internals (NON-API) ---------------------------------------------

    def _reference_field(self, t: int) -> np.ndarray:
        """Identical formula to E0._reference_field. Bit-equality is asserted in tests."""
        time_phases = self.__omegas * t
        weights = self.__amplitudes * (0.5 + 0.5 * np.cos(time_phases))
        raw = weights @ self.__basis
        normed = (raw - raw.min()) / (raw.max() - raw.min() + 1e-12)
        return normed

    def _action_kernel(self, position: int) -> np.ndarray:
        """Identical formula to E0._action_kernel. Bit-equality is asserted in tests."""
        x = np.arange(self._config.grid_size)
        sigma = max(1.0, self._config.action_kernel_width / 2.0)
        kern = np.exp(-0.5 * ((x - position) / sigma) ** 2)
        kern *= self._config.action_amplitude / kern.max()
        return kern

    @staticmethod
    def _laplacian_ring(f: np.ndarray) -> np.ndarray:
        """Discrete 1D Laplacian with periodic boundary (ADR-032 §3.3).

        (Δ_ring f)_i = f_{i-1 mod G} - 2 f_i + f_{i+1 mod G}
        """
        return np.roll(f, -1) - 2.0 * f + np.roll(f, 1)
