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
from pterasim_mcp import PterasimRequest, run_simulation

request = PterasimRequest(num_timesteps=200, span_m=0.8, chord_m=0.12)
response = run_simulation(request)
print(response.metadata["solver"])
```

If a Python 3.13 environment with `PteraSoftware` is available, the wrapper will prefer UVLM and note the solver in the metadata.

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
- **Solver comparison** - leverage metadata to benchmark surrogate vs UVLM deltas, feeding results into the CEE.
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
