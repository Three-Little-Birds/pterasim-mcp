# pterasim-mcp · Guided Flight for Flapping-Wing Learners

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](pyproject.toml)
[![CI](https://github.com/yevheniikravchuk/pterasim-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/yevheniikravchuk/pterasim-mcp/actions/workflows/ci.yml)

`pterasim-mcp` wraps [PteraSoftware](https://github.com/camUrban/PteraSoftware) when it is available—and falls back to a lightweight analytic surrogate otherwise—so you can teach an MCP agent how flapping wings generate thrust, lift, and torque. The goal is to make aerodynamic experimentation approachable even if you are new to UVLM solvers.

## Learning objectives

- Understand the input parameters that govern flapping-wing performance.
- Run the simulator (or the deterministic fallback) from Python and interpret the results.
- Expose the capability through an MCP tool so assistants can compare wing designs in real time.

## Requirements

| Component | Why it matters |
|-----------|----------------|
| `PteraSoftware` Python package (optional) | Installs the full UVLM solver. If missing, the analytic fallback still provides useful estimates. |
| Python 3.10+ & `uv` | For installation and examples. |
| NumPy/Matplotlib (optional) | Handy for plotting thrust or lift traces. |

Install PteraSoftware if you want the high-fidelity solver:

```bash
pip install PteraSoftware
```

## Step 1 – Install the MCP helper

```bash
uv pip install "git+https://github.com/yevheniikravchuk/pterasim-mcp.git"
```

## Step 2 – Simulate a baseline wing

```python
from pterasim_mcp import PterasimInput, simulate_pterasim

inputs = PterasimInput(
    span_m=0.7,
    mean_chord_m=0.12,
    stroke_frequency_hz=6.0,
    stroke_amplitude_rad=0.35,
    cruise_velocity_m_s=8.0,
    air_density_kg_m3=1.2,
    cl_alpha_per_rad=5.5,
    cd0=0.02,
    planform_area_m2=0.18,
)

outputs = simulate_pterasim(inputs)
print(outputs)
```

If `pterasim` is available the solver returns UVLM-based thrust, lift, and torque. Otherwise the wrapper computes a physics-informed approximation useful for prototyping and unit tests.

Every response also includes a `metadata` field. When the UVLM solver runs you will see entries such as `{"solver": "pterasoftware", "solver_version": "0.10.1", "panel_count": 72}`; the fallback reports `{"solver": "analytic"}` so pipelines (or the CEE) know which fidelity produced the numbers.

## Step 3 – Compare design tweaks

```python
for freq in [5.0, 6.0, 7.0]:
    trial = inputs.model_copy(update={"stroke_frequency_hz": freq})
    perf = simulate_pterasim(trial)
    print(f"{freq} Hz -> thrust {perf.thrust_N:.2f} N, lift {perf.lift_N:.2f} N")
```

Use the loop above to build an intuition for how frequency or stroke amplitude affect performance.

## Step 4 – Share the simulator via MCP

### FastAPI service

```python
from pterasim_mcp.fastapi_app import create_app

app = create_app()
```

Run locally:

```bash
uv run uvicorn pterasim_mcp.fastapi_app:create_app --factory --port 8003
```

### python-sdk tool

```python
from mcp.server.fastmcp import FastMCP
from pterasim_mcp.tool import build_tool

mcp = FastMCP("pterasim-mcp", "Flapping wing simulation")
build_tool(mcp)

if __name__ == "__main__":
    mcp.run()
```

Now your MCP-aware agent can evaluate alternative wing plans on demand.

## Experiment ideas

- **Mission profiling:** sweep cruise velocities to identify lift margins throughout a flight segment.
- **Material study:** combine outputs with ctrltest-mcp to see how actuator limits interact with aerodynamic loads.
- **Curriculum project:** ask students to hit a target thrust while minimising torque using the MCP tool.

## Contributing & tests

```bash
uv pip install --system -e .[dev]
uv run ruff check .
uv run pytest
```

Tests cover both the UVLM path (when the module is present) and the fallback to keep behaviour predictable.

## License

MIT — see [LICENSE](LICENSE).
