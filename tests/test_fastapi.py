from __future__ import annotations

from fastapi.testclient import TestClient

from pterasim_mcp.fastapi_app import create_app


def test_simulate_endpoint() -> None:
    app = create_app()
    client = TestClient(app)
    payload = {
        "span_m": 0.8,
        "mean_chord_m": 0.12,
        "stroke_frequency_hz": 5.0,
        "stroke_amplitude_rad": 0.25,
        "cruise_velocity_m_s": 8.0,
        "air_density_kg_m3": 1.2,
        "cl_alpha_per_rad": 5.7,
        "cd0": 0.02,
        "planform_area_m2": 0.18,
        "tail_moment_arm_m": 0.3,
    }
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["lift_N"] > 0
