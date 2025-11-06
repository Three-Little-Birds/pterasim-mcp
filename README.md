# pterasim-mcp - UVLM + surrogate aerodynamics for MCP agents

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2B-3776AB.svg" alt="Python 3.10 or newer"></a>
  <a href="https://github.com/Three-Little-Birds/pterasim-mcp/actions/workflows/ci.yml"><img src="https://github.com/Three-Little-Birds/pterasim-mcp/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <img src="https://img.shields.io/badge/MCP-tooling-blueviolet.svg" alt="MCP tooling badge">
</p>

> **TL;DR**: Expose PteraSoftware's analytical/UVLM solvers through MCP so agents can request aerodynamic coefficients with provenance metadata.

## Table of contents

1. [What it provides](#what-it-provides)
2. [Quickstart](#quickstart)
3. [Run as a service](#run-as-a-service)
4. [Agent playbook](#agent-playbook)
5. [Stretch ideas](#stretch-ideas)
6. [Accessibility & upkeep](#accessibility--upkeep)
7. [Contributing](#contributing)

## What it provides

| Scenario | Value |
|----------|-------|
| Surrogate aerodynamics | Evaluate lightweight rigid-vortex-lattice models without a GUI, returning aerodynamic coefficients as structured data. |
| High-fidelity UVLM | When [PteraSoftware](https://github.com/pterasoftware/PteraSoftware) is installed, the service switches to its UVLM solver and records provenance metadata. |
| Controller integration | Provide consistent outputs that downstream MCP tools (e.g., `ctrltest-mcp`) can ingest for control and evidence pipelines. |

## Quickstart

### 1. Install

```bash
uv pip install "git+https://github.com/Three-Little-Birds/pterasim-mcp.git"
```

### 2. Run an analytic solve

```python
from pterasim_mcp import PterasimInput, simulate_pterasim

request = PterasimInput(
    span_m=0.8,
    mean_chord_m=0.12,
    stroke_frequency_hz=12.0,
    stroke_amplitude_rad=0.55,
    cruise_velocity_m_s=6.0,
    air_density_kg_m3=1.225,
    cl_alpha_per_rad=6.2,
    cd0=0.03,
    planform_area_m2=0.18,
)
response = simulate_pterasim(request)
print(response.metadata["solver"])            # "analytic" or "pterasoftware_uvlm"
print(response.thrust_N, response.lift_N, response.torque_Nm)

Typical metadata payload:

```json
{
  "solver": "pterasoftware_uvlm",
  "thrust_delta_pct_vs_analytic": -4.1,
  "lift_delta_pct_vs_analytic": -2.7
}
```
```

If a Python 3.13 environment with `PteraSoftware` (≥3.2) is available, the wrapper will prefer UVLM and note the solver in the metadata. Install it inside a dedicated environment:

```bash
uv python install 3.13
uv venv .venv-pterasim --python 3.13
source .venv-pterasim/bin/activate
pip install pterasoftware==3.2.0
uv pip install "git+https://github.com/Three-Little-Birds/pterasim-mcp.git"
```

If the UVLM solve fails for any reason (missing binaries, convergence issues, or the current `PteraSoftware` regression that removes `geometry.airfoil`), the wrapper logs a warning and falls back to the analytic surrogate—you will see `solver: "analytic"` in the metadata and no delta fields. UVLM runs with thousands of timesteps can take minutes; batch analytic sweeps first and promote only promising cases to the high-fidelity environment. Analytic-only mode works on Python 3.11 without `PteraSoftware`. Until the UVLM API stabilizes upstream, treat the analytic path as the supported/default mode.

## Run as a service

### CLI (STDIO / Streamable HTTP)

```bash
uvx pterasim-mcp  # runs the MCP over stdio
# or python -m pterasim_mcp
python -m pterasim_mcp --transport streamable-http --host 0.0.0.0 --port 8000 --path /mcp
```

Use `python -m pterasim_mcp --describe` to emit metadata without starting the server.

### FastAPI (REST)

```bash
uv run uvicorn pterasim_mcp.fastapi_app:create_app --factory --port 8003
```

### python-sdk tool (STDIO / MCP)

```python
from mcp.server.fastmcp import FastMCP
from pterasim_mcp.tool import build_tool

mcp = FastMCP("pterasim-mcp", "Wing UVLM & surrogate solver")
build_tool(mcp)

if __name__ == "__main__":
    mcp.run()
```

### ToolHive smoke test

```bash
uvx --with 'mcp==1.20.0' python scripts/integration/run_pterasim.py
# ToolHive 2025+ defaults to Streamable HTTP; match that transport when registering
# the workload manually so IDE clients avoid the SSE 502 bug.
```

## Agent playbook

- **Scenario sweeps** - vary span, frequency, or flapping amplitude and log derivatives for control studies.
- **Solver comparison** - leverage metadata to benchmark surrogate vs UVLM deltas and store the comparisons for regression dashboards.
- **Design flows** - combine with `openvsp-mcp` to generate geometry + aerodynamics pipelines.

## Stretch ideas

1. Generate JSONL experiment logs that feed directly into `ctrltest-mcp` or reinforcement-learning agents.
2. Use the metadata to route results into Grafana dashboards for solver provenance.
3. Auto-promote surrogate runs to UVLM once a high-fidelity environment is detected.

## Accessibility & upkeep

- Badges are limited and carry alt text for screen-readers, matching modern README style guidance.
- Tests simulate solver responses; run `uv run pytest` before pushing.
- Keep `.venv-pterasim` aligned with the PteraSoftware version you report in metadata.

## Contributing

1. `uv pip install --system -e .[dev]`
2. Run `uv run ruff check .` and `uv run pytest`
3. Include sample metadata/CSV artefacts in PRs so reviewers can confirm provenance handling.

MIT license - see [LICENSE](LICENSE).
