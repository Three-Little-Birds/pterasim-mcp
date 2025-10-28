"""Core simulation helper for Pterasim MCP."""

from __future__ import annotations

import math
from importlib import import_module
from typing import Any

from .models import PterasimInput, PterasimOutput

try:  # pragma: no cover
    PTR = import_module("pterasim")
except ModuleNotFoundError:  # pragma: no cover
    PTR = None


def simulate_pterasim(inputs: PterasimInput) -> PterasimOutput:
    """Simulate flapping wing performance.

    Uses the native `pterasim` module when available; otherwise performs a simplified analytic
    estimate mirroring the legacy Orthodrone fallback.
    """

    if PTR is not None:  # pragma: no cover
        try:
            result: Any = PTR.simulate_wing(
                span=inputs.span_m,
                chord=inputs.mean_chord_m,
                frequency=inputs.stroke_frequency_hz,
                amplitude=inputs.stroke_amplitude_rad,
                velocity=inputs.cruise_velocity_m_s,
            )
            return PterasimOutput(
                thrust_N=float(result.thrust),
                lift_N=float(result.lift),
                torque_Nm=float(result.torque),
            )
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(str(exc)) from exc

    # Analytic fallback
    rho = inputs.air_density_kg_m3
    omega = 2.0 * math.pi * inputs.stroke_frequency_hz
    aspect_ratio = inputs.span_m**2 / inputs.planform_area_m2
    cl = inputs.cl_alpha_per_rad * inputs.stroke_amplitude_rad
    dynamic_pressure = 0.5 * rho * max(inputs.cruise_velocity_m_s, 0.1) ** 2
    heave_q = 0.5 * rho * inputs.planform_area_m2 * (omega * inputs.stroke_amplitude_rad) ** 2
    lift = dynamic_pressure * inputs.planform_area_m2 * cl + heave_q
    induced = 0.0
    if aspect_ratio > 0:
        induced = (cl**2) / (math.pi * aspect_ratio * 0.9)
    cd = inputs.cd0 + induced
    drag = dynamic_pressure * inputs.planform_area_m2 * cd
    thrust = drag
    moment_arm = (
        inputs.tail_moment_arm_m if inputs.tail_moment_arm_m is not None else inputs.span_m / 4.0
    )
    torque = lift * moment_arm
    return PterasimOutput(thrust_N=thrust, lift_N=lift, torque_Nm=torque)


__all__ = ["simulate_pterasim"]
