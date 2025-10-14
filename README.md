# Retirement Enjoyment Simulator

This project models lifetime utility ("enjoyment") as a function of constant monthly spending, investment returns, salary growth, and retirement timing. It helps explore the trade-off between retiring early (more time to enjoy money) and preserving wealth for longer horizons.

## Project structure
- `retirement_enjoyment_simulator.py` — the main Python script (deterministic simulator + grid-based feasible spending finder using `bisect`).
- `max_feasible_spending_by_age.csv` — output produced when running the main script (saved automatically).
- `README.md` — this file.
- `TODO.md` — prioritized list of improvements and experiments.

## Key assumptions (defaults)
- Current age: **30**
- Planning horizon (death age D): **90**
- Starting investible wealth W0: **500,000 CAD**
- Monthly after-tax salary: **8,000 CAD** (starting)
- Salary growth (real): **1%/yr**
- Investment return (real): **5%/yr**
- Utility from spending: **log(y)** (monthly), multiplied by an age factor that declines linearly to zero at D
- Leisure multiplier after retirement: **L_post = 1.7** (per-dollar enjoyment is 70% higher in retirement)

These defaults can be modified by editing the script or importing functions into your own code.

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

The script runs a grid search for retirement ages 34..45 using a spending grid (0..30,000 by default, step=100) and prints a table of the maximum feasible constant monthly spending for each age along with total modeled lifetime enjoyment and final wealth, saving results to a CSV file.

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
