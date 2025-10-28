"""FastAPI app for the Pterasim MCP service."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .core import simulate_pterasim
from .models import PterasimInput, PterasimOutput


def create_app() -> FastAPI:
    app = FastAPI(
        title="Pterasim MCP Service",
        version="0.1.0",
        description="Simulate flapping wing performance with Pterasim or analytic fallback.",
    )

    @app.post("/simulate", response_model=PterasimOutput)
    def simulate(request: PterasimInput) -> PterasimOutput:
        try:
            return simulate_pterasim(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return app


app = create_app()

__all__ = ["create_app", "app"]
