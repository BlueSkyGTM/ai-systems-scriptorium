# Exercise: When the Array Wins

**Goal:** Extend `vectorization_report.py` (the M4 throughline artifact) with a speedup benchmark function that imports from `measure.py`, times a Python loop against a vectorized reduction across a range of array sizes, and prints a formatted speedup table. Exit 0 only when all assertions pass.

**Why:** Measuring the crossover between loop and vectorized paths turns a general principle into a calibrated decision rule you can apply to any batch function you write or review at work.

## Before You Touch Code

1. Read the lesson at `library/completed/just-python/src/module4/when-the-array-wins.md` for the full reasoning behind the benchmark.
2. Find `vectorization_report.py` in `exercises/module4/` and read its current state. You are extending a build already in progress, not starting a new file.
3. Find `exercises/module1/the-cost-of-a-python-list/measure.py` and read its current state. It exports `time_sum` (and possibly `time_contiguous_vs_strided`). You will import from it; do not rewrite it.

If `vectorization_report.py` does not exist yet (this is the first M4 exercise you are completing), create it. If it does exist, add to it.

## Steps

1. Open `exercises/module4/vectorization_report.py`. Read its current state before touching it.

2. At the top of the file, add the import:

   ```python
   import sys
   import pathlib
   sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "module1" / "the-cost-of-a-python-list"))
   from measure import time_sum
   ```

   Adjust the relative path if your file layout differs. The point is to import `time_sum` off disk; do not copy its implementation.

3. Add a function `speedup_table` to `vectorization_report.py` with this signature:

   ```python
   def speedup_table(
       sizes: list[int] | None = None,
       runs: int = 20,
       seed: int = 42,
   ) -> list[tuple[int, float, float, float]]:
       """
       Time a Python loop sum-of-squares vs a vectorized reduction at each size.

       Parameters
       ----------
       sizes : list[int]
           Array lengths to benchmark. Defaults to [10, 100, 1_000, 10_000, 100_000, 1_000_000].
       runs : int
           Timed repetitions per size (averaged).
       seed : int
           RNG seed for reproducibility.

       Returns
       -------
       rows : list of (N, loop_ms, vec_ms, speedup) tuples
           One row per size.

       Side effects
       ------------
       Prints a formatted table:
           N      loop ms    vec ms   speedup
           10       X.XXX    X.XXXX      X.Xx
           ...
       Asserts:
           - np.allclose(loop_result, vec_result) for each size (correctness)
           - At the largest size, vec_ms <= loop_ms (vectorized wins at scale)
       """
   ```

4. Implement the body:

   - Use `np.random.default_rng(seed)` for reproducibility.
   - For each size N:
     - Build `arr = rng.standard_normal(N).astype(np.float64)`.
     - **Loop path:** time `runs` iterations of a Python `for x in arr: total += x * x` loop and compute the mean milliseconds as `loop_ms`.
     - **Vectorized path:** time `runs` iterations of `(arr ** 2).sum()` and compute the mean milliseconds as `vec_ms`.
     - Assert `np.allclose(loop_result, vec_result)` (correctness gate).
     - Compute `speedup = loop_ms / vec_ms`.
   - Print a formatted table with one row per size.
   - After the loop, assert `vec_ms_at_largest <= loop_ms_at_largest` (the vectorized path wins at the largest size). Use a generous check: `speedup_at_largest >= 1` is sufficient; the printed numbers are the real diagnostic.
   - Return `rows` as a list of `(N, loop_ms, vec_ms, speedup)` tuples.

5. In the `if __name__ == "__main__":` block of `vectorization_report.py`, call `speedup_table()` and print a summary line:

   ```python
   rows = speedup_table()
   max_speedup = max(r[3] for r in rows)
   print(f"\nPeak speedup: {max_speedup:.0f}x at N={max(r[0] for r in rows):,}")
   ```

6. Run the script from the `exercises/module4/` directory:

   ```
   python vectorization_report.py
   ```

   All assertions must pass and the table must print. Exit code must be 0.

## Done When

`python vectorization_report.py` exits 0 and the output includes:

```
N          loop ms    vec ms   speedup
10           X.XXX    X.XXXX      X.Xx
100          X.XXX    X.XXXX      X.Xx
1,000        X.XXX    X.XXXX      X.Xx
10,000       X.XXX    X.XXXX      X.Xx
100,000      X.XXX    X.XXXX      X.Xx
1,000,000    X.XXX    X.XXXX      X.Xx

Peak speedup: XXx at N=1,000,000
```

The two machine-checkable gates are:

```python
# Correctness: loop and vectorized produce the same result at every size
assert np.allclose(loop_result, vec_result), (
    f"loop {loop_result:.6f} != vec {vec_result:.6f} at N={N}"
)

# Scale: vectorized is at least as fast as the loop at the largest size
assert speedup_at_largest >= 1, (
    f"vectorized was slower than loop at N={sizes[-1]:,}: "
    f"speedup={speedup_at_largest:.2f}x"
)
```

NumPy only (plus the `measure.py` import). Deterministic via seeded RNG. One command to run.

## Stretch

After the speedup table, add a second block that calls `time_contiguous_vs_strided()` from `measure.py` (if it exists on the imported module) and prints the layout ratio alongside the vectorization ratio. This pairs the two lessons: vectorization replaces per-element overhead; contiguity removes the memory-latency tax on top of that. The combined picture is the M4 payoff.

```python
if hasattr(sys.modules.get("measure"), "time_contiguous_vs_strided"):
    from measure import time_contiguous_vs_strided
    print("\n--- layout timing (from measure.py) ---")
    time_contiguous_vs_strided()
```
