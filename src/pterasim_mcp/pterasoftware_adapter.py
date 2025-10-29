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
            rho=inputs.air_density_kg_m3,
            vCg__E=max(inputs.cruise_velocity_m_s, 0.1),
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

        forces = solver.airplanes[0].forces_W  # type: ignore[attr-defined]
        metadata = {
            "solver": "pterasoftware",
            "solver_version": getattr(ps, "__version__", "unknown"),
            "panel_count": int(solver.num_panels),
        }

        velocity = max(inputs.cruise_velocity_m_s, 0.1)
        rho = inputs.air_density_kg_m3
        ref_area = inputs.planform_area_m2
        omega = 2.0 * math.pi * inputs.stroke_frequency_hz

        aerodynamic_lift = float(-forces[2])
        dynamic_pressure = 0.5 * rho * (velocity**2)
        aspect_ratio = inputs.span_m**2 / ref_area if ref_area > 0 else 0.0
        target_cl = inputs.cl_alpha_per_rad * inputs.stroke_amplitude_rad
        induced_drag = float(-forces[0])
        if aspect_ratio > 0 and dynamic_pressure > 0:
            induced_drag = max(
                dynamic_pressure
                * ref_area
                * (target_cl**2)
                / (math.pi * aspect_ratio * 0.9),
                0.0,
            )
        else:
            induced_drag = max(induced_drag, 0.0)
        parasitic_drag = 0.5 * rho * (velocity**2) * ref_area * inputs.cd0
        thrust = induced_drag + parasitic_drag
        heave_lift = 0.5 * rho * ref_area * (omega * inputs.stroke_amplitude_rad) ** 2
        lift = aerodynamic_lift + heave_lift

        moment_arm = (
            inputs.tail_moment_arm_m if inputs.tail_moment_arm_m is not None else inputs.span_m / 4.0
        )
        torque = lift * moment_arm

        metadata.update(
            {
                "induced_drag_N": induced_drag,
                "parasitic_drag_N": parasitic_drag,
                "heave_lift_N": heave_lift,
                "aero_lift_N": aerodynamic_lift,
            }
        )

        return PterasimOutput(
            thrust_N=thrust,
            lift_N=lift,
            torque_Nm=torque,
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

    airfoil = ps.geometry.airfoil.Airfoil(name="naca0012")  # type: ignore[attr-defined]
    root_section = ps.geometry.wing.WingCrossSection(  # type: ignore[attr-defined]
        airfoil=airfoil,
        num_spanwise_panels=6,
        chord=chord,
        control_surface_symmetry_type="symmetric",
    )
    tip_section = ps.geometry.wing.WingCrossSection(  # type: ignore[attr-defined]
        airfoil=airfoil,
        num_spanwise_panels=None,
        chord=chord,
        Lp_Wcsp_Lpp=(0.0, half_span, 0.0),
        control_surface_symmetry_type="symmetric",
    )
    wing = ps.geometry.wing.Wing(  # type: ignore[attr-defined]
        wing_cross_sections=[root_section, tip_section],
        name="Main Wing",
        symmetric=True,
        symmetryNormal_G=(0.0, 1.0, 0.0),
        symmetryPoint_G_Cg=(0.0, 0.0, 0.0),
        num_chordwise_panels=6,
        chordwise_spacing="cosine",
    )

    return ps.geometry.airplane.Airplane(  # type: ignore[attr-defined]
        name="pterasim-mcp",
        wings=[wing],
        s_ref=inputs.planform_area_m2,
        b_ref=inputs.span_m,
        c_ref=inputs.mean_chord_m,
    )


__all__ = ["is_available", "run_high_fidelity"]
