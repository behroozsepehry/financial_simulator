# Retirement Enjoyment Simulator

This project models lifetime utility ("enjoyment") as a function of constant monthly spending, investment returns, salary growth, and retirement timing. It helps explore the trade-off between retiring early (more time to enjoy money) and preserving wealth for longer horizons.

## Project structure
- `retirement_enjoyment_simulator.py` — the main Python script (deterministic simulator + grid-based feasible spending finder using `bisect`).
- `README.md` — this file.
- `TODO.md` — prioritized list of improvements and experiments.

Default parameters are configured in config.json. See the file for current values and modify as needed.

## Running the script
1. Create a virtual environment and install dependencies (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
.venv\Scripts\activate     # Windows
pip install numpy pandas
```

2. Run the script:

```bash
python retirement_enjoyment_simulator.py
```

The script runs a grid search for retirement ages as defined in config.json using a spending grid as defined in config.json and prints a table of the maximum feasible constant monthly spending for each age along with total modeled lifetime enjoyment and final wealth.

## Extending the project
This project is intentionally compact. The `retirement_enjoyment_simulator.py` script is designed so you can:

- plug in Monte Carlo returns to evaluate ruin probability
- add a utility component for working years
- model multi-component spending (experience vs goods)
- add taxes, pensions, and account-specific withdrawal rules for Canada
- incorporate dynamic asset allocation or glidepaths

See `TODO.md` for a prioritized list of next steps.

## Notes and limitations
This is a **deterministic** simulator and does not model sequence-of-returns risk, taxes, pensions, or stochastic shocks. The results are sensitive to input choices (especially investment return, L_post and the utility function). Use the tool for exploration and sensitivity analysis rather than as single-source financial advice.
