"""Typed models for Pterasim MCP interactions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PterasimInput(BaseModel):
    span_m: float = Field(..., gt=0.0)
    mean_chord_m: float = Field(..., gt=0.0)
    stroke_frequency_hz: float = Field(..., ge=0.0)
    stroke_amplitude_rad: float = Field(..., ge=0.0)
    cruise_velocity_m_s: float = Field(..., ge=0.0)
    air_density_kg_m3: float = Field(..., gt=0.0)
    cl_alpha_per_rad: float = Field(...)
    cd0: float = Field(..., ge=0.0)
    planform_area_m2: float = Field(..., gt=0.0)
    tail_moment_arm_m: float | None = Field(default=None, ge=0.0)
    prefer_high_fidelity: bool = Field(
        default=True,
        description="Attempt to use PteraSoftware when available before falling back to the analytic surrogate.",
    )


class PterasimOutput(BaseModel):
    thrust_N: float
    lift_N: float
    torque_Nm: float
    metadata: dict[str, object] | None = Field(default=None, description="Solver details and diagnostics")
