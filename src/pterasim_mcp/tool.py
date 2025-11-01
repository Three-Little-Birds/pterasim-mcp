"""python-sdk tool registration for Pterasim."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .core import simulate_pterasim
from .models import PterasimInput, PterasimOutput


def build_tool(app: FastMCP) -> None:
    """Attach the pterasim aerodynamic solver tools to an MCP server."""

    @app.tool(
        name="pterasim.simulate",
        description=(
            "Generate aerodynamic coefficients with UVLM fallback. "
            "Supply wing geometry, flapping schedule, and timestep count. "
            "Returns forces, torques, and solver metadata. "
            "Example: {\"span_m\":0.8,\"chord_m\":0.12,\"num_timesteps\":180}"
        ),
        meta={"version": "0.1.0", "categories": ["aero", "simulation"]},
    )
    def simulate(request: PterasimInput) -> PterasimOutput:
        return simulate_pterasim(request)


__all__ = ["build_tool"]
