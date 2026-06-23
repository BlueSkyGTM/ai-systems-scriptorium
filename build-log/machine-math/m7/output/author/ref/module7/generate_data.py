"""generate_data.py -- produce data.csv for the M7 capstone.

Provenance: seeded synthetic benchmark designed to exercise the full methodology.
All randomness is fixed to numpy seed 42; the output is byte-reproducible.

Schema
------
tenure_months   int     [1, 60]
monthly_charge  float   [20.0, 120.0]
num_products    int     [1, 5]
plan_type       str     {basic, plus, premium}
region          str     {north, south, east, west}
churned         int     {0, 1}   ~30 pct positive, learnable signal

Run: python generate_data.py   (creates data.csv alongside this file)
"""
from __future__ import annotations

import os
import csv
import numpy as np

SEED = 42
N_ROWS = 1_000

PLAN_TYPES = ["basic", "plus", "premium"]
REGIONS = ["north", "south", "east", "west"]

HEADER = [
    "tenure_months",
    "monthly_charge",
    "num_products",
    "plan_type",
    "region",
    "churned",
]


def generate(n: int = N_ROWS, seed: int = SEED) -> list[dict]:
    rng = np.random.default_rng(seed)

    tenure = rng.integers(1, 61, size=n)                        # 1-60 months
    charge = rng.uniform(20.0, 120.0, size=n).round(2)         # $20-$120/mo
    num_products = rng.integers(1, 6, size=n)                   # 1-5 products
    plan_idx = rng.integers(0, 3, size=n)                       # 0=basic 1=plus 2=premium
    region_idx = rng.integers(0, 4, size=n)                     # 0-3

    # Learnable logistic signal:
    #   short tenure, high charge, basic plan, south region -> higher churn risk
    log_odds = (
        -0.5                                  # intercept (pulls baseline toward ~25-35%)
        - 0.08 * tenure                       # longer tenure => lower churn (stronger signal)
        + 0.035 * charge                      # higher charge => higher churn (stronger signal)
        - 0.5 * num_products                  # more products => lower churn (stronger stickiness)
        + np.where(plan_idx == 0, 1.2, 0.0)  # basic plan => higher churn (stronger)
        + np.where(region_idx == 3, 0.7, 0.0)  # south => higher churn
    )
    prob_churn = 1.0 / (1.0 + np.exp(-log_odds))
    churned = rng.binomial(1, prob_churn).astype(int)

    rows = []
    for i in range(n):
        rows.append({
            "tenure_months": int(tenure[i]),
            "monthly_charge": float(charge[i]),
            "num_products": int(num_products[i]),
            "plan_type": PLAN_TYPES[int(plan_idx[i])],
            "region": REGIONS[int(region_idx[i])],
            "churned": int(churned[i]),
        })
    return rows


def write_csv(rows: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "data.csv")
    rows = generate()
    write_csv(rows, out_path)
    churned = sum(r["churned"] for r in rows)
    print(f"Class balance: {churned}/{len(rows)} positive ({churned/len(rows):.1%})")
