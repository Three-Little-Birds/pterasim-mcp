from __future__ import annotations

from unittest import mock

import pytest

from pterasim_mcp.core import simulate_pterasim
from pterasim_mcp.models import PterasimInput, PterasimOutput


@pytest.fixture()
def sample_input() -> PterasimInput:
    return PterasimInput(
        span_m=0.8,
        mean_chord_m=0.12,
        stroke_frequency_hz=5.0,
        stroke_amplitude_rad=0.25,
        cruise_velocity_m_s=8.0,
        air_density_kg_m3=1.2,
        cl_alpha_per_rad=5.7,
        cd0=0.02,
        planform_area_m2=0.18,
        tail_moment_arm_m=0.3,
    )


def test_simulate_fallback(sample_input: PterasimInput) -> None:
    """Even without Pterasim installed we should estimate forces."""
    output = simulate_pterasim(sample_input)
    assert output.thrust_N > 0.0
    assert output.lift_N > 0.0
    assert output.torque_Nm > 0.0
    assert output.metadata == {"solver": "analytic"}


def test_simulate_with_pterasoftware(sample_input: PterasimInput) -> None:
    """When PteraSoftware is available we use its results."""
    sample_input.prefer_high_fidelity = True
    high_fidelity_output = PterasimOutput(
        thrust_N=12.3,
        lift_N=45.6,
        torque_Nm=7.8,
        metadata={"solver": "pterasoftware"},
    )

    with mock.patch("pterasim_mcp.core.is_available", return_value=True), mock.patch(
        "pterasim_mcp.core.run_high_fidelity", return_value=high_fidelity_output
    ):
        output = simulate_pterasim(sample_input)

    assert output.thrust_N == pytest.approx(12.3)
    assert output.lift_N == pytest.approx(45.6)
    assert output.torque_Nm == pytest.approx(7.8)
    assert output.metadata == {"solver": "pterasoftware"}
