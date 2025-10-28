# pterasim-mcp

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](pyproject.toml)
[![CI](https://github.com/yevheniikravchuk/pterasim-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/yevheniikravchuk/pterasim-mcp/actions/workflows/ci.yml)

Model Context Protocol integration for the [Pterasim](https://github.com/wnordmann/pterasim) flapping-wing solver. It exposes typed request/response models, a FastAPI surface, and an analytic fallback when the native `pterasim` module is unavailable.

## Why you might want this

- **Automate flapping-wing studies** – call `pterasim.simulate_wing` from agents without crafting bespoke glue code.
- **Keep pipelines running without CUDA** – the analytic fallback estimates thrust/lift so CI or laptops can still produce meaningful numbers.
- **Archive context** – request/response models make it easy to log every assumption that went into a simulation run.

## Features

- `simulate` helper that calls `pterasim.simulate_wing` when installed, otherwise returns a lift/drag/thrust estimate.
- FastAPI app factory (`create_app`) for HTTP deployments.
- python-sdk tool registration helper for STDIO-based agents.

## Installation

```bash
pip install "git+https://github.com/yevheniikravchuk/pterasim-mcp.git"
```

## Usage

```python
from pterasim_mcp import PterasimInput, simulate_pterasim

inputs = PterasimInput(
    span_m=0.8,
    mean_chord_m=0.12,
    stroke_frequency_hz=6.0,
    stroke_amplitude_rad=0.35,
    cruise_velocity_m_s=8.0,
    air_density_kg_m3=1.2,
    cl_alpha_per_rad=5.7,
    cd0=0.02,
    planform_area_m2=0.18,
    tail_moment_arm_m=0.25,
)
output = simulate_pterasim(inputs)
print(output.thrust_N)
```

## Development

```bash
uv pip install --system -e .[dev]
uv run ruff check .
uv run pytest
```

## License

MIT — see [LICENSE](LICENSE).
