# Exercise: The Hidden Cost of apply

**Goal:** Extend `vectorization_report.py` (the M4 throughline artifact) with `apply_tax_report()`: a function that imports `time_sum` from `measure.py`, times `df.apply(axis=1)` against the vectorized column expression on a generated frame at multiple scales, prints the measured tax, asserts the results agree and the vectorized path wins, and exits 0.

**Why:** Knowing that `apply(axis=1)` is slow is the M3 fact. Knowing *how slow* at real scale, with a number, is what lets you push back in a code review or justify a rewrite to a teammate. This exercise makes that number yours.

## Before You Touch Code

1. Read the lesson at `library/in-progress/just-python/src/module4/the-hidden-cost-of-apply.md`.
2. Find `exercises/module4/vectorization_report.py` and read its current state. You are adding to a file that already has a speedup benchmark from earlier M4 exercises. Do not reset or remove what is already there.
3. Find `exercises/module1/the-cost-of-a-python-list/measure.py` and read it. You need `time_sum`; import it, do not copy it.

## Steps

1. Open `exercises/module4/vectorization_report.py`. Read what is already there.

2. Add this import block near the top (adjust the relative path if your layout differs):

   ```python
   import sys
   import pathlib
   sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "module1" / "the-cost-of-a-python-list"))
   from measure import time_sum
   ```

   Do not re-add this block if it already exists from a prior M4 exercise.

3. Add a function `apply_tax_report` to `vectorization_report.py`:

   ```python
   def apply_tax_report(
       sizes: list[int] | None = None,
       runs: int = 5,
       seed: int = 42,
   ) -> list[tuple[int, float, float, float]]:
       """
       Time df.apply(axis=1) vs the vectorized column multiply at each frame size.

       Returns
       -------
       rows : list of (N, apply_ms, vec_ms, tax) tuples

       Side effects
       ------------
       Prints a formatted table:
           N       apply ms    vec ms      tax
           10,000    XX.XX      X.XX      XXx
           ...
       Asserts:
           - Results agree (allclose) at every size
           - Vectorized path is faster at the largest size (generous slack: tax >= 1)
       """
   ```

4. Implement the body. Use `np.random.default_rng(seed)` for reproducibility.

   For each size N:

   - Build a DataFrame with two float columns:

     ```python
     rng = np.random.default_rng(seed)
     df = pd.DataFrame({
         "score":  rng.standard_normal(N),
         "weight": rng.uniform(0.5, 1.5, N),
     })
     ```

   - Time the apply path using `time_sum`:

     ```python
     apply_s = time_sum(
         lambda: df.apply(lambda row: row["score"] * row["weight"], axis=1),
         n=runs,
     )
     apply_ms = apply_s * 1000
     ```

   - Time the vectorized path using `time_sum`:

     ```python
     vec_s = time_sum(lambda: df["score"] * df["weight"], n=runs)
     vec_ms = vec_s * 1000
     ```

   - Compute correctness and the tax:

     ```python
     result_apply = df.apply(lambda row: row["score"] * row["weight"], axis=1)
     result_vec   = df["score"] * df["weight"]
     assert (result_apply - result_vec).abs().max() < 1e-10, (
         f"apply and vectorized disagree at N={N}"
     )
     tax = apply_ms / vec_ms
     ```

   - Print one row of the table.

5. After the loop, capture the last (largest) entry and assert the vectorized path won:

   ```python
   last_tax = rows[-1][3]
   assert last_tax >= 1, (
       f"apply was not slower than vectorized at N={sizes[-1]:,}: tax={last_tax:.2f}x"
   )
   print(f"\nApply tax at N={sizes[-1]:,}: {last_tax:.0f}x slower than vectorized")
   ```

6. In the `if __name__ == "__main__":` block, call `apply_tax_report()` after the existing speedup benchmark:

   ```python
   print("\n--- apply tax (pandas apply vs vectorized column) ---")
   apply_tax_report(sizes=[10_000, 100_000, 500_000])
   ```

7. Run from the `exercises/module4/` directory:

   ```
   python vectorization_report.py
   ```

   All assertions must pass, the apply tax table must print, and the script must exit 0.

## Done When

`python vectorization_report.py` exits 0 and the output includes a table like:

```
--- apply tax (pandas apply vs vectorized column) ---
N          apply ms    vec ms    tax
10,000       XX.XX      X.XX    XXx
100,000     XXX.XX      X.XX   XXXx
500,000    XXXX.XX      X.XX  XXXXx

Apply tax at N=500,000: XXXXx slower than vectorized
```

The two machine-checkable gates are:

```python
# Correctness: apply and vectorized produce the same result at every size
assert (result_apply - result_vec).abs().max() < 1e-10

# Scale: apply is at least as slow as vectorized at the largest size
assert last_tax >= 1
```

pandas and numpy only (plus the `measure.py` import). Deterministic via seeded RNG. One command to run. Exit code must be 0.

## Stretch

Add a legitimate-apply case. When a function needs an external scorer that only accepts a scalar, apply is correct, not lazy. Show the pattern:

```python
def external_scorer(score: float, weight: float) -> float:
    """Simulates a scalar-only external predictor (no batch path)."""
    # pure Python: cannot be vectorized because the caller sets the interface
    return float(score * weight + 0.01 * score ** 2)

result_external = df.apply(
    lambda row: external_scorer(row["score"], row["weight"]),
    axis=1,
)
print(f"\nLegitimate apply: external_scorer called {len(df):,} times (no batch path available)")
print(f"First 3 results: {result_external.head(3).tolist()}")
```

This is not the case where you should rewrite it. The library's interface sets the constraint. Document it with a comment so the next reviewer knows the apply is intentional.
