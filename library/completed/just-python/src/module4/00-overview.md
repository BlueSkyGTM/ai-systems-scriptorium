# Module 4: Vectorization Discipline

## What This Module Covers

Module 1 built the cost model, Module 2 the NumPy operations, Module 3 the Pandas layer. Module 4 is the judgment that ties them together. You already know how to vectorize; this module teaches when to, when not to, and how to prove the call with numbers. The discipline is not "vectorize everything." It is profile first, measure the three costs (speed, memory, readability), then decide and justify.

This is the difference between an engineer who rewrites the wrong loop on a hunch and one who measures, changes one thing, and measures again. A take-home that hands you a slow pipeline is testing exactly this: can you find the real bottleneck, quantify the fix, and recognize the case where the clever one-liner is the wrong answer.

The work stays grounded in the AI-engineering call site: the batch job that times out, the `apply` that never scales, the broadcast that runs out of memory on a real corpus.

## Arc of Lessons

| Lesson | Title | What It Teaches |
|--------|-------|-----------------|
| 1 | Profile Before You Optimize | Measure before you rewrite; reach for `measure.py`'s `time_sum`, because the bottleneck is rarely where you guess |
| 2 | When the Array Wins | The loop-to-C-loop speedup, measured, and how it grows with N up to the cache limit; the crossover where a small loop can win |
| 3 | The Hidden Cost of apply | Put a number on the `apply(axis=1)` tax M3 named, watch it widen with scale, and map the few cases where `apply` is genuinely unavoidable |
| 4 | When Not to Vectorize | The broadcast that blows the memory budget, the one-liner that costs readability, and chunking as the third option; the decision rule that closes the module |

## Throughline Artifact

Module 4 is where the artifact chain pays off. Modules 1 through 3 each *added* one function to `measure.py`. Module 4 builds a new artifact, `vectorization_report.py` (at `exercises/module4/`), that **imports `measure.py` off disk and composes its functions**: it calls `time_sum` to profile a loop against a vectorized version, reuses `broadcast_allocates` to check whether the vectorized path blows the memory budget, and emits a "vectorize / keep the loop / chunk it" recommendation with the numbers behind it. The reuse is real composition, not a rewrite: the report imports the prior artifact and calls it. This is the same pattern the portfolio modules (M6, M7, M8) use, practiced here for the first time.

## Prerequisites

- Modules 1 through 3: the cost model, the NumPy operations, and the Pandas layer, including M3's finding that `apply(axis=1)` is a disguised per-row loop. Module 4 quantifies and decides; it does not re-teach the mechanics.
- The `measure.py` you have built across M1 through M3, at `exercises/module1/the-cost-of-a-python-list/measure.py`. Module 4 imports `time_sum` and `broadcast_allocates` from it.
- A Python 3.11+ environment with NumPy and pandas installed (`pip install numpy pandas`).
