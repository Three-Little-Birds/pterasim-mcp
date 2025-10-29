"""Optional bridge to the PteraSoftware UVLM solver."""

from __future__ import annotations

import math
from typing import Optional

from .models import PterasimInput, PterasimOutput

try:  # pragma: no cover - optional dependency
    import pterasoftware as ps  # type: ignore
except Exception:  # pragma: no cover
    ps = None  # type: ignore


def is_available() -> bool:
    """Return True when PteraSoftware can be imported."""

    return ps is not None  # type: ignore[return-value]


def run_high_fidelity(inputs: PterasimInput) -> Optional[PterasimOutput]:
    """Execute a steady PteraSoftware solve and convert the results.

    Returns ``None`` if PteraSoftware is not installed.
    """

    if ps is None:  # pragma: no cover - guarded import
        return None

    try:
        airplane = _build_airplane(inputs)
        operating_point = ps.operating_point.OperatingPoint(  # type: ignore[attr-defined]
            density=inputs.air_density_kg_m3,
            velocity=max(inputs.cruise_velocity_m_s, 0.1),
            alpha=math.degrees(inputs.stroke_amplitude_rad),
            beta=0.0,
        )

        problem = ps.problems.SteadyProblem(  # type: ignore[attr-defined]
            airplanes=[airplane],
            operating_point=operating_point,
        )

        solver = ps.steady_ring_vortex_lattice_method.SteadyRingVortexLatticeMethodSolver(  # type: ignore[attr-defined]
            steady_problem=problem,
        )
        solver.run(logging_level="Error")

        forces = solver.airplanes[0].total_near_field_force_wind_axes
        moments = solver.airplanes[0].total_near_field_moment_wind_axes
        metadata = {
            "solver": "pterasoftware",
            "solver_version": getattr(ps, "__version__", "unknown"),
            "panel_count": int(solver.num_panels),
        }
        return PterasimOutput(
            thrust_N=float(-forces[0]),
            lift_N=float(forces[2]),
            torque_Nm=float(moments[1]),
            metadata=metadata,
        )
    except Exception as exc:  # pragma: no cover - runtime safety
        raise RuntimeError(f"PteraSoftware solve failed: {exc}") from exc


def _build_airplane(inputs: PterasimInput):  # pragma: no cover - exercised at runtime
    """Create a basic wing geometry matching the input parameters."""

    if ps is None:
        raise RuntimeError("PteraSoftware is not available")

    half_span = max(inputs.span_m / 2.0, 1e-3)
    chord_guess = inputs.planform_area_m2 / max(inputs.span_m, 1e-3)
    chord = max(chord_guess, inputs.mean_chord_m, 1e-3)

    airfoil = ps.geometry.Airfoil(name="naca0012")  # type: ignore[attr-defined]

    wing = ps.geometry.Wing(  # type: ignore[attr-defined]
        name="Main Wing",
        symmetric=True,
        chordwise_spacing="cosine",
        num_chordwise_panels=6,
        wing_cross_sections=[
            ps.geometry.WingCrossSection(  # type: ignore[attr-defined]
                x_le=0.0,
                y_le=0.0,
                chord=chord,
                twist=0.0,
                num_spanwise_panels=6,
                spanwise_spacing="cosine",
                airfoil=airfoil,
            ),
            ps.geometry.WingCrossSection(  # type: ignore[attr-defined]
                x_le=0.0,
                y_le=half_span,
                chord=chord,
                twist=0.0,
                num_spanwise_panels=6,
                spanwise_spacing="cosine",
                airfoil=airfoil,
            ),
        ],
    )

    airplane = ps.geometry.Airplane(  # type: ignore[attr-defined]
        name="pterasim-mcp",
        wings=[wing],
        s_ref=inputs.planform_area_m2,
        b_ref=inputs.span_m,
        c_ref=inputs.mean_chord_m,
    )
    return airplane


__all__ = ["is_available", "run_high_fidelity"]
