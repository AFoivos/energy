# Aegean

Renewable energy trading and battery optimization for a hypothetical portfolio in the Greek electricity market.

## Status

Project scaffold and research design. Python source files and tests are intentionally empty. No data has been imported, no strategy has been evaluated, and no application is operational.

The portfolio is hypothetical and is not associated with METLEN or any other asset owner. This project does not place orders.

## Research question

Can forecast-driven scheduling and battery operation improve net portfolio value relative to simple market participation policies, under explicit physical, information and execution constraints?

The study will separate asset revenue from incremental strategy value. Conclusions will depend on data coverage, publication timestamps, market rules and execution assumptions.

## Scope

- Local Python workflow with XLSX source data.
- Data validation and point-in-time reconstruction.
- Forecast benchmarks and chronological evaluation.
- Battery scheduling with SciPy linear and mixed-integer optimization.
- Historical simulation, settlement and performance attribution.
- Excel reports and a Streamlit interface.

Continuous intraday execution will be studied only to the extent supported by the available data. Aggregate prices alone cannot establish executable fills.

## Tools

Python 3.11 or later; pandas, openpyxl, NumPy, SciPy, scikit-learn and statsmodels. Visualization, application and notebook dependencies are optional extras.

All project code will be written in Python. SciPy supplies the optimization interfaces; no separate optimization modelling language is planned.

## Repository

| Location | Purpose |
| --- | --- |
| `docs/` | Scope, contracts, mathematical model and implementation order |
| `src/aegean/` | Reusable Python package; currently empty modules |
| `tests/` | Reserved test files; currently empty |
| `data/raw/` | Original XLSX files, excluded from Git |
| `data/processed/` | Derived data, excluded from Git |
| `notebooks/` | Future exploratory analysis using package functions |
| `app/` | Future Streamlit application |
| `outputs/` | Generated reports, figures and logs, excluded from Git |

## Environment preparation

The following commands are intended for the repository root and have not been run as part of scaffold creation:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,visualization,app,notebooks]"
```

Dependency ranges are starting constraints, not a validated environment lock. Record exact resolved versions when the environment is first validated. No executable CLI entry point is registered yet.

Running pytest now would collect no implemented tests. There is no backtest or dashboard command to demonstrate yet.

## Development order

Start with [project scope](docs/project_scope.md), [data feasibility](docs/market_and_data.md) and [implementation order](docs/implementation_order.md).

Model assumptions belong in [the mathematical specification](docs/mathematical_model.md). Experiment decisions belong in [the research protocol](docs/research_protocol.md).

## Data and publication

Keep source spreadsheets unchanged. Do not commit raw data, credentials or generated results by default. Before publishing a dataset or report, check source rights and remove sensitive information.

No license has been selected. Public repository visibility, once enabled, will not by itself grant a reuse license.
