from __future__ import annotations

from unittest import mock

import pytest

from pterasim_mcp.core import simulate_pterasim
from pterasim_mcp.models import PterasimInput


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


def test_simulate_with_native_module(sample_input: PterasimInput) -> None:
    """When the real module is present we proxy straight through."""
    fake_module = mock.Mock()
    fake_module.simulate_wing.return_value = mock.Mock(
        thrust=12.3,
        lift=45.6,
        torque=7.8,
    )

    with mock.patch("pterasim_mcp.core.PTR", fake_module):
        output = simulate_pterasim(sample_input)

    assert output.thrust_N == pytest.approx(12.3)
    assert output.lift_N == pytest.approx(45.6)
    assert output.torque_Nm == pytest.approx(7.8)
