# The Hidden Cost of apply

M3 established the fact: `df.apply(func, axis=1)` is a disguised per-row Python loop. This lesson puts a number on it.

## What You Build

You extend `vectorization_report.py` with `apply_tax_report()`: a function that times `df.apply(axis=1)` against the vectorized column expression on a generated frame, prints the measured tax at each scale, and adds the apply profile to the running report.

## The Apply Tax, Measured

When pandas executes `df.apply(func, axis=1)`, it constructs a `Series` for each row, passes it to your function, collects the return value, and repeats. The overhead is not just the Python interpreter round-trip per element; it is the `Series` object construction per row on top of that. Each call allocates, each call type-checks, and pandas cannot batch these into a single typed C loop the way a column expression can.

Time the contrast directly:

```python
import pandas as pd
import numpy as np
import time

rng = np.random.default_rng(42)
N = 500_000
df = pd.DataFrame({
    "score":  rng.standard_normal(N),
    "weight": rng.uniform(0.5, 1.5, N),
})

# apply path: one Python call per row
start = time.perf_counter()
result_apply = df.apply(lambda row: row["score"] * row["weight"], axis=1)
apply_ms = (time.perf_counter() - start) * 1000

# vectorized path: one C-level column multiply
start = time.perf_counter()
result_vec = df["score"] * df["weight"]
vec_ms = (time.perf_counter() - start) * 1000

print(f"N={N:,}: apply {apply_ms:.1f} ms | vectorized {vec_ms:.2f} ms | tax {apply_ms/vec_ms:.0f}x")
```

At 500,000 rows, the output looks like this:

```
N=500,000: apply 4820.3 ms | vectorized 1.84 ms | tax 2619x
```

The exact ratio varies by machine. The pattern is stable: the gap widens with row count, because the apply overhead scales linearly while the vectorized path benefits from SIMD and cache. The pandas documentation confirms this directly: vectorized operations leverage optimized C functions via NumPy to process entire arrays at once, avoiding per-row Python function calls. The "Explore and Analyze Data with Python" module on Microsoft Learn grounds the same principle: typed NumPy array operations outperform the equivalent work over Python sequences by a wide margin ([learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas)).

## Why the Gap Widens with Scale

At 100 rows, the apply overhead is invisible. Both paths finish in microseconds and the difference is lost in measurement noise. At 100,000 rows, apply's linear overhead starts showing. At one million rows, the tax is a hard production fact: batch scoring jobs that take twenty minutes instead of two almost always have an apply call that nobody profiled.

The apply overhead is not flat; it compounds. `Series` construction takes roughly constant time per row, so the total cost is O(N). The vectorized column multiply pays interpreter overhead once, then hands the whole buffer to a compiled loop. At scale, the ratio does not plateau; it stays wide.

## The Decision Checklist

Before you reach for `apply(axis=1)`, run this check:

1. Does the function touch only values in the same row? If so, the vectorized column expression handles it. Column arithmetic, `.str` accessor methods, `np.where`, and `np.select` all operate on whole columns without a Python call per row.
2. Does the logic branch on a condition across columns? `np.where` and `np.select` replace most row-wise conditionals without apply.
3. Does the function need to call an external library that accepts scalars only, not arrays? That is a legitimate apply case.
4. Does the function need data from other rows in the same group (e.g., subtract each row from its group mean)? Use `groupby().transform()` instead of apply.

If you reach step 3 and can confirm the library truly has no vectorized path, apply is acceptable. Document it.

## When apply Is Genuinely the Right Tool

Two cases survive the checklist:

**An external library that takes scalars.** A model library with a `predict(x: float) -> float` signature has no batch path. You cannot vectorize what the library won't accept. Use apply, and note it: `# apply: sklearn_custom_predictor takes scalar, no batch path`.

**Group-wise logic that requires the full group.** When the function for a row depends on the group's aggregate (fitting a per-group model, running a sliding window), `groupby().apply()` is the right shape. This is not the `axis=1` row-loop case; it is a different API for a different problem.

The rest is a vectorized column expression waiting to be written.

## The Cheaper Escape Hatches

When you cannot avoid row-wise dispatch but the function is simple, two tools cut the tax:

`np.where(condition, x, y)` replaces the most common apply pattern: a conditional that reads two columns and picks one. No `apply`, no `Series` construction.

`Series.map(dict)` replaces element-wise lookup with a hash-table join. When the "function" is a mapping from one set of values to another, `.map` is faster than `apply` because it delegates to a C-level loop over scalars, not a Python callable per row.

For string columns, the `.str` accessor exposes vectorized string operations: `.str.upper()`, `.str.contains()`, `.str.replace()`. An apply that wraps a string operation is always replaceable by `.str`.

The batch scoring job that times out in production is almost always an `apply` that ran unnoticed at 200 rows during development and surfaced its true cost at two million.

## Core Concepts

- `df.apply(func, axis=1)` pays interpreter overhead plus `Series` construction per row; the total cost scales linearly with N, making the tax grow wider as the frame grows.
- The vectorized column expression pays interpreter overhead once, then hands the buffer to a compiled C loop; at 500,000 rows the gap is routinely three to four orders of magnitude.
- `np.where`, `np.select`, `Series.map`, and the `.str` accessor replace the most common `apply(axis=1)` patterns without leaving Python per row.
- apply earns its place in two cases: a scalar-only external library with no batch path, or group-wise logic via `groupby().apply()` where the function genuinely requires the full group.

<div class="claude-handoff" data-exercise="exercises/module4/the-hidden-cost-of-apply/">

**Build It in Claude Code:** Extend `vectorization_report.py` with `apply_tax_report()`: import `time_sum` from `measure.py`, time `df.apply(axis=1)` against the vectorized column multiply on a generated frame, print the measured tax, assert the results agree and the vectorized path is faster, and exit 0.

</div>
