"""CAE — environment E0.

1D non-stationary, deterministic, bounded [0,1] constraint field.

Principles (PROTOCOL §3, §6):
- Black-box isolation: only the public methods `observe`, `act`, `step` and
  the frozen configuration attributes are exposed. Internal stochastic state
  is protected by an underscore and is NOT documented as API.
- Determinism: at a given seed, the trajectory is bit-identical.
- External telemetry: `observe()` returns a pressure vector, `step()`
  returns a dict of measurements (integrated pressure, simulated latency,
  success).

The field is built as a superposition of spatial modes whose amplitudes
drift over time according to a deterministic regime (sum of incommensurable
sinusoids). No hidden dynamics beyond that.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class E0Config:
    """Frozen E0 configuration. Any modification = new experiment."""
    grid_size: int = 64
    horizon: int = 512
    n_modes: int = 4
    seed: int = 42
    drift_rate: float = 0.015        # non-stationary drift speed
    action_kernel_width: int = 5     # spatial support of an action
    action_amplitude: float = 0.10   # unit impact of an action
    relaxation: float = 0.05         # passive return to the reference field


class E0:
    """1D non-stationary constraint field.

    Public API (the only one A/B/R/P agents must see):
        - observe() -> np.ndarray  (local pressure, shape=(grid_size,))
        - act(position: int) -> None  (locally deforms the field)
        - step() -> dict  (advances time, returns external telemetry)
        - t (read-only): current time step
        - is_done: bool
        - config: E0Config (frozen)
    """

    def __init__(self, config: E0Config | None = None) -> None:
        self._config: E0Config = config if config is not None else E0Config()

        rng = np.random.default_rng(self._config.seed)
        # Spatial modes: integer frequencies, seed-derived phases.
        self.__freqs = rng.integers(1, 8, size=self._config.n_modes)
        self.__phases = rng.uniform(0.0, 2 * np.pi, size=self._config.n_modes)
        # Incommensurable (irrational) temporal speeds
        self.__omegas = (np.arange(1, self._config.n_modes + 1)
                         * np.pi * self._config.drift_rate)
        self.__amplitudes = rng.uniform(0.3, 0.7, size=self._config.n_modes)
        self.__amplitudes /= self.__amplitudes.sum()  # sum = 1

        x = np.linspace(0.0, 1.0, self._config.grid_size, endpoint=False)
        # Frozen spatial basis
        self.__basis = np.stack(
            [np.cos(2 * np.pi * f * x + p)
             for f, p in zip(self.__freqs, self.__phases)],
            axis=0,
        )  # shape: (n_modes, grid_size)

        self._t: int = 0
        self._field: np.ndarray = self._reference_field(0)
        self._last_action_pos: int | None = None

    # ---- Public API --------------------------------------------------------

    @property
    def config(self) -> E0Config:
        return self._config

    @property
    def t(self) -> int:
        return self._t

    @property
    def is_done(self) -> bool:
        return self._t >= self._config.horizon

    def observe(self) -> np.ndarray:
        """Return a COPY of the pressure field. No external aliasing."""
        return self._field.copy()

    def act(self, position: int) -> None:
        """Locally deform the field around `position` (bounded Gaussian kernel)."""
        if not (0 <= position < self._config.grid_size):
            raise ValueError(f"position {position} out of grid [0, {self._config.grid_size})")
        kernel = self._action_kernel(position)
        self._field = np.clip(self._field - kernel, 0.0, 1.0)
        self._last_action_pos = position

    def step(self) -> dict[str, Any]:
        """Advance time by one step. Returns external telemetry."""
        if self.is_done:
            raise RuntimeError("E0 horizon reached. Re-instantiate for a new run.")

        # Passive relaxation toward the reference field + non-stationary drift
        ref = self._reference_field(self._t + 1)
        self._field = (1.0 - self._config.relaxation) * self._field \
            + self._config.relaxation * ref
        self._field = np.clip(self._field, 0.0, 1.0)

        self._t += 1
        telemetry = {
            "t": self._t,
            "pressure_integral": float(self._field.sum()),
            "pressure_max": float(self._field.max()),
            "pressure_min": float(self._field.min()),
            "last_action_pos": self._last_action_pos,
        }
        return telemetry

    # ---- Internals (NON-API, do not call from an agent) -------------------

    def _reference_field(self, t: int) -> np.ndarray:
        """Reference field at time t: superposition of drifting modes."""
        time_phases = self.__omegas * t
        weights = self.__amplitudes * (
            0.5 + 0.5 * np.cos(time_phases)  # temporal modulation
        )
        # Combination + normalization into [0,1]
        raw = weights @ self.__basis           # shape: (grid_size,)
        # Min-max normalization bounded by theoretical extremes
        normed = (raw - raw.min()) / (raw.max() - raw.min() + 1e-12)
        return normed

    def _action_kernel(self, position: int) -> np.ndarray:
        """Action kernel: truncated Gaussian, controlled mass."""
        x = np.arange(self._config.grid_size)
        sigma = max(1.0, self._config.action_kernel_width / 2.0)
        kern = np.exp(-0.5 * ((x - position) / sigma) ** 2)
        kern *= self._config.action_amplitude / kern.max()
        return kern
