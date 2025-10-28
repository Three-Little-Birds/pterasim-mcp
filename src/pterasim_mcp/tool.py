"""python-sdk tool registration for Pterasim."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .core import simulate_pterasim
from .models import PterasimInput, PterasimOutput


def build_tool(app: FastMCP) -> None:
    @app.tool()
    def simulate(request: PterasimInput) -> PterasimOutput:  # type: ignore[valid-type]
        return simulate_pterasim(request)


__all__ = ["build_tool"]
