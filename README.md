# Meal Optimization

A mixed-integer meal planner that minimizes food cost while meeting daily nutrition targets. It chooses three dishes per day, adjusts serving sizes, and limits repetition across the week.

Uses the included recipe prices and nutrition data collected from Budget Bytes. The optimization is implemented in CVXPY with the Gurobi solver.

## Run

Install pandas, CVXPY, and a working Gurobi installation, then run:

```bash
python analysis.py
```

Set nutrition bounds and planning duration at the bottom of `analysis.py`. The selected dishes and servings are saved to `opt.csv`. `analysis.ipynb` contains exploratory analysis; `scrape.py` is the original data-collection script.
