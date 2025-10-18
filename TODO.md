# TODO — Improvements & Experiments (prioritized)

This TODO aggregates the model refinements and experiments discussed during the conversation. Items are grouped by priority and include short notes on approach and rationale.

---

## High priority (most impactful)

1. **Monte Carlo returns + ruin probability analysis**
   - Replace deterministic `investment_annual_growth` with stochastic returns (e.g., annual lognormal shocks) and run many simulations (e.g., 5k–50k).
   - Compute `P(ruin)` = probability wealth hits zero before death, and the distribution of terminal wealth.
   - For each (retire_age, spending) policy, estimate ruin probability and choose policies with `P(ruin) ≤ p*` (user-specified, e.g., 1% or 5%).
   - Rationale: sequence-of-returns risk is critical for early retirement scenarios.

2. **Add "utility from working" term**
   - Include a positive utility stream during working years; allow parameter for intensity (per-month utility) and age-dependence.
   - Allow `part-time`/meaningful work in retirement (non-zero income + utility).
   - Rationale: many people derive happiness from work; omitting it biases model toward retirement.

3. **Dynamic spending / time-sensitive consumption**
   - Split spending into `experience` vs `goods`. Model `experience` utility to be amplified by `utility_multiplier_post_retire` and possibly front-loaded.
   - Allow time-varying spending policies (e.g., higher early-retirement spending for travel).
   - Rationale: concentrating experience spending when young/healthy increases utility without necessarily increasing ruin risk as much as constant high spending.

---

## Medium priority

4. **Asset allocation & glidepath**
   - Model equity fraction that decreases with age; use different expected returns & volatility pre/post retirement.
   - Rationale: realistic retirement portfolios reduce expected return but also volatility.

5. **Tax / account modeling (Canadian context)**
   - Model TFSA, RRSP/RRIF, taxable accounts; include tax drag on withdrawals and pension timing (CPP/OAS).
   - Rationale: taxes materially affect sustainable withdrawals and retirement timing.

6. **Bequest motive & charitable giving**
   - Add a bequest utility term or constraints on final wealth.
   - Rationale: if user cares about legacy, optimal spending will change.

7. **Health shocks & long-term care risk**
   - Add stochastic big-cost events (e.g., 1-in-20 chance of large expense) and/or rising baseline healthcare consumption with age.

---

## Lower priority / niceties

8. **Sensitivity & robustness analysis**
   - Sweep income_annual_growth, investment_annual_growth, utility_multiplier_post_retire, utility_exponent_pre_retire, final_age, and show contours of feasible spending and ruin probability.
   - Compute regret-minimizing policies under parameter uncertainty.

9. **Refine leisure mapping**
   - Replace scalar `utility_multiplier_post_retire` with a calibrated function `L(t)` of discretionary hours (concave / capped). Calibrate using literature heuristics.

10. **Add discounting and time preference**
    - Allow discount factor or time preference in utility aggregation.

11. **Front-end & visualization**
    - Produce interactive plots (Bokeh/Plotly streamlit) for exploring the policy surface.

12. **Unit tests / reproducibility**
    - Add tests for deterministic functions and reproducible Monte Carlo seeds.

13. **Refine utility function**
    - Compare log vs CRRA (power) utility and possibly piecewise utility (different γ pre/post-retirement).

14. **CLI and config file**
    - Add argument parsing and a YAML/JSON config loader for running scenarios reproducibly.

---

## Implementation notes & data sources
- For Monte Carlo returns: consider historical rolling annual returns for a chosen index (e.g., US total market or a VGT-like tech ETF) to set mean & volatility, or use a lognormal model with mean `mu` and sd `sigma`. Use realistic sd (e.g., 12-18% annual for equities depending on the index).
- For taxes & pensions: use Canadian sources for CPP/OAS timing and contribution rules, and approximations for marginal tax rates when withdrawing from RRSP/RRIF vs taxable accounts.
- For leisure mapping: consult psychophysics and time-use literature. Use concave functions (log or power with exponent 0.4–0.7).

---

## Next actionable steps (recommended)
1. Implement Monte Carlo returns + ruin probability and produce a table of max spending by age for a chosen acceptable ruin probability (e.g., 5%).
2. Add a simple `work_utility` parameter and re-run the deterministic sweep to inspect how retirement recommendations change.
3. Implement dynamic spending (split experience vs goods) and test front-loading experience spending early in retirement.
