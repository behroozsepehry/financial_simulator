"""
Retirement Enjoyment Simulator

This script contains the deterministic lifetime enjoyment simulator and a grid-based
"maximum feasible constant monthly spending" finder that uses Python's `bisect`
module to locate the highest spending in a discretized grid that preserves non-negative
final wealth, for a list of retirement ages.

How the code is organized:
- simulate_with_retirement(...) -> runs the deterministic monthly simulation and
  returns total_enjoyment, final_wealth and bankruptcy flag.
- max_feasible_spending_for_retire_age(...) -> constructs a discretized spending
  grid and uses bisect to find the highest grid point with final_wealth >= 0.
- main block runs the search for ages 34..45 and prints a table.

You can import the functions into an IDE and extend them (e.g., Monte Carlo, taxes,
utility changes) as discussed in the project's TODO file.
"""

import math
import bisect
import numpy as np
import pandas as pd
import json
from typing import Optional, Tuple, Dict


def simulate_with_retirement(
    current_age: float,
    D: float,
    W0: float,
    x0_monthly: float,
    alpha_annual: float,
    retire_age: float,
    x_post_monthly: float,
    beta_annual: float,
    y_monthly: float,
    gamma_pre: float = 0.0,  # 0 -> log utility; else power utility with exponent gamma_pre
    gamma_post: Optional[float] = None,
    L_pre: float = 1.0,
    L_post: float = 1.7,
    months_per_year: int = 12,
) -> Dict[str, float]:
    """
    Deterministic monthly simulation.

    Returns a dict with keys: total_enjoyment, final_wealth, bankrupt (bool).
    """
    months = int((D - current_age) * months_per_year)
    # monthly rate equivalents
    alpha_m = (1 + alpha_annual) ** (1 / months_per_year) - 1
    beta_m = (1 + beta_annual) ** (1 / months_per_year) - 1

    age = current_age
    W = W0
    x_month = x0_monthly
    total_enjoyment = 0.0

    for _ in range(months):
        if age >= retire_age:
            x_month_now = x_post_monthly
            L_now = L_post
            gamma_now = gamma_post if gamma_post is not None else gamma_pre
        else:
            x_month_now = x_month
            L_now = L_pre
            gamma_now = gamma_pre

        # linear age factor that declines to zero at D
        age_factor = max(0.0, 1.0 - (age - current_age) / (D - current_age))

        # utility from spending (monthly)
        if gamma_now == 0:
            monthly_utility = math.log(max(y_monthly, 1.0)) * age_factor * L_now
        else:
            monthly_utility = (y_monthly**gamma_now) * age_factor * L_now

        total_enjoyment += monthly_utility

        # wealth update
        W = W * (1 + beta_m) + (x_month_now - y_monthly)

        # step forward
        age += 1.0 / months_per_year
        if age < retire_age:
            x_month *= 1 + alpha_m

    bankrupt = W < 0
    return {"total_enjoyment": total_enjoyment, "final_wealth": W, "bankrupt": bankrupt}


def max_feasible_spending_for_retire_age(
    retire_age: float,
    spend_min: int = 0,
    spend_max: int = 30_000,
    step: int = 100,
    **sim_kwargs,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Find the largest spending on a discretized grid [spend_min, spend_max] with step
    `step` such that simulate_with_retirement(..., y_monthly=spend) yields final_wealth >= 0.

    Uses Python's bisect on the boolean feasibility vector.

    Returns (best_spend, total_enjoyment, final_wealth) or (None, None, None) if no
    feasible spend in the grid.
    """
    spends = list(np.arange(spend_min, spend_max + step, step))

    feas = []
    for s in spends:
        res = simulate_with_retirement(retire_age=retire_age, y_monthly=s, **sim_kwargs)
        feas.append(res["final_wealth"] >= 0)

    # Expect feas: [True, True, ..., True, False, False, ...]
    not_feas = [not f for f in feas]
    idx_first_infeas = bisect.bisect_left(not_feas, True)

    if idx_first_infeas == 0:
        # smallest spending already infeasible
        return None, None, None
    if idx_first_infeas >= len(spends):
        best_s = spends[-1]
    else:
        best_s = spends[idx_first_infeas - 1]

    best_res = simulate_with_retirement(
        retire_age=retire_age, y_monthly=best_s, **sim_kwargs
    )
    return best_s, best_res["total_enjoyment"], best_res["final_wealth"]


def run_grid_ages(
    ages: list,
    spend_min: int = 0,
    spend_max: int = 30_000,
    step: int = 100,
    sim_kwargs: dict = None,
) -> pd.DataFrame:
    """
    Run max_feasible_spending_for_retire_age for multiple ages and return a DataFrame.
    """
    if sim_kwargs is None:
        sim_kwargs = {}

    rows = []
    for age in ages:
        best_s, enjoy, final_w = max_feasible_spending_for_retire_age(
            retire_age=age,
            spend_min=spend_min,
            spend_max=spend_max,
            step=step,
            **sim_kwargs,
        )
        rows.append(
            {
                "retire_age": age,
                "best_monthly_spending": best_s,
                "total_enjoyment": enjoy,
                "final_wealth": final_w,
            }
        )

    df = pd.DataFrame(rows).sort_values("retire_age").reset_index(drop=True)
    return df


if __name__ == "__main__":
    # Load configuration from config.json
    with open("config.json", "r") as f:
        config = json.load(f)

    # Default run: ages 34..45, step = 100 CAD, beta=5%, alpha=1%, L_post=1.7
    ages = list(range(34, 46))
    sim_kwargs = {
        "current_age": config["current_age"],
        "D": config["D"],
        "W0": config["W0"],
        "x0_monthly": config["x0_monthly"],
        "alpha_annual": config["alpha_annual"],
        "x_post_monthly": config["x_post_monthly"],
        "beta_annual": config["beta_annual"],
        "gamma_pre": config["gamma_pre"],
        "gamma_post": config["gamma_post"],
        "L_pre": config["L_pre"],
        "L_post": config["L_post"],
        "months_per_year": config["months_per_year"],
    }

    df = run_grid_ages(
        ages=ages, spend_min=0, spend_max=30_000, step=100, sim_kwargs=sim_kwargs
    )

    # print nicely
    pd.set_option(
        "display.float_format", lambda x: f"{x:,.2f}" if pd.notnull(x) else "None"
    )
    print(df.to_string(index=False))

    # save csv for inspection
    df.to_csv("max_feasible_spending_by_age.csv", index=False)
    print("\nSaved results to max_feasible_spending_by_age.csv")
