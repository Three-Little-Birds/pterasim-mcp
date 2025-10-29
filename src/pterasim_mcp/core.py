"""Core simulation helper for Pterasim MCP."""

from __future__ import annotations

import logging
import math

from .models import PterasimInput, PterasimOutput
from .pterasoftware_adapter import is_available, run_high_fidelity

LOGGER = logging.getLogger(__name__)


def simulate_pterasim(inputs: PterasimInput) -> PterasimOutput:
    """Simulate flapping wing performance."""

    if inputs.prefer_high_fidelity and is_available():
        try:
            result = run_high_fidelity(inputs)
            if result is not None:
                return result
        except Exception as exc:  # pragma: no cover - fallback path
            LOGGER.warning("High-fidelity PteraSoftware run failed, falling back to surrogate: %s", exc)

    return _analytic_surrogate(inputs)


def _analytic_surrogate(inputs: PterasimInput) -> PterasimOutput:
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
    metadata = {
        "solver": "analytic",
    }
    return PterasimOutput(thrust_N=thrust, lift_N=lift, torque_Nm=torque, metadata=metadata)


__all__ = ["simulate_pterasim"]
