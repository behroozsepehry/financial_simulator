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

MONTHS_PER_YEAR = 12


def simulate_with_retirement(
    initial_age: float,
    final_age: float,
    initial_wealth: float,
    initial_monthly_income: float,
    income_annual_growth: float,
    retire_age: float,
    retired_monthly_income: float,
    investment_annual_growth: float,
    monthly_spending: float,
    utility_exponent_pre_retire: float = 0.0,  # 0 -> log utility; else power utility with exponent utility_exponent_pre_retire
    utility_exponent_post_retire: Optional[float] = None,
    utility_multiplier_pre_retire: float = 1.0,
    utility_multiplier_post_retire: float = 1.7,
) -> Dict[str, float]:
    """
    Deterministic monthly simulation.

    Returns a dict with keys: total_enjoyment, final_wealth, bankrupt (bool).
    """
    months = int((final_age - initial_age) * MONTHS_PER_YEAR)
    # monthly rate equivalents
    alpha_m = (1 + income_annual_growth) ** (1 / MONTHS_PER_YEAR) - 1
    beta_m = (1 + investment_annual_growth) ** (1 / MONTHS_PER_YEAR) - 1

    age = initial_age
    W = initial_wealth
    x_month = initial_monthly_income
    total_enjoyment = 0.0

    for _ in range(months):
        if age >= retire_age:
            x_month_now = retired_monthly_income
            L_now = utility_multiplier_post_retire
            gamma_now = utility_exponent_post_retire if utility_exponent_post_retire is not None else utility_exponent_pre_retire
        else:
            x_month_now = x_month
            L_now = utility_multiplier_pre_retire
            gamma_now = utility_exponent_pre_retire

        # linear age factor that declines to zero at final_age
        age_factor = max(0.0, 1.0 - (age - initial_age) / (final_age - initial_age))

        # utility from spending (monthly)
        if gamma_now == 0:
            monthly_utility = math.log(max(monthly_spending, 1.0)) * age_factor * L_now
        else:
            monthly_utility = (monthly_spending**gamma_now) * age_factor * L_now

        total_enjoyment += monthly_utility

        # wealth update
        W = W * (1 + beta_m) + (x_month_now - monthly_spending)

        # step forward
        age += 1.0 / MONTHS_PER_YEAR
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
    `step` such that simulate_with_retirement(..., monthly_spending=spend) yields final_wealth >= 0.

    Uses Python's bisect on the boolean feasibility vector.

    Returns (best_spend, total_enjoyment, final_wealth) or (None, None, None) if no
    feasible spend in the grid.
    """
    spend_range = range(spend_min, spend_max + step, step)

    def is_not_feasible(y: int) -> bool:
        res = simulate_with_retirement(retire_age=retire_age, monthly_spending=y, **sim_kwargs)
        return res["final_wealth"] < 0

    idx_first_infeas = bisect.bisect_left(spend_range, True, key=is_not_feasible)

    if idx_first_infeas == 0:
        # smallest spending already infeasible
        return None, None, None
    if idx_first_infeas >= len(spend_range):
        best_s_index = len(spend_range) - 1
    else:
        best_s_index = idx_first_infeas - 1

    best_s = spend_range.start + best_s_index * spend_range.step

    best_res = simulate_with_retirement(
        retire_age=retire_age, monthly_spending=best_s, **sim_kwargs
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

    # Default run: ages 34..45, step = 100 CAD, investment_annual_growth=5%, income_annual_growth=1%, utility_multiplier_post_retire=1.7
    ages = list(range(34, 46))
    sim_kwargs = {
        "initial_age": config["initial_age"],
        "final_age": config["final_age"],
        "initial_wealth": config["initial_wealth"],
        "initial_monthly_income": config["initial_monthly_income"],
        "income_annual_growth": config["income_annual_growth"],
        "retired_monthly_income": config["retired_monthly_income"],
        "investment_annual_growth": config["investment_annual_growth"],
        "utility_exponent_pre_retire": config["utility_exponent_pre_retire"],
        "utility_exponent_post_retire": config["utility_exponent_post_retire"],
        "utility_multiplier_pre_retire": config["utility_multiplier_pre_retire"],
        "utility_multiplier_post_retire": config["utility_multiplier_post_retire"],
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
