# Exercise: Profile Before You Optimize

**Goal:** Build `vectorization_report.py`, a script that imports `time_sum` from the existing `measure.py`, profiles a plain Python loop sum against a NumPy vectorized sum on the same data, prints both timings and the speedup ratio, asserts the two results agree numerically, and exits 0.

**Why:** Every optimization decision in production starts with a measurement; this exercise makes that habit concrete by building the measurement artifact that Module 4 carries forward as its throughline.

## Before You Start

Read `src/module4/profile-before-you-optimize.md`. Then open `exercises/module1/the-cost-of-a-python-list/measure.py` and confirm `time_sum` is there. You are importing it off disk, not re-implementing it.

## Steps

1. Create `exercises/module4/vectorization_report.py` (the shared M4 artifact, at the module root so every M4 lesson extends the same file).

2. At the top of the file (module level, not inside any function), add the import:

   ```python
   import sys
   import pathlib
   import numpy as np

   # Resolve measure.py relative to this file, so the import works from any working directory
   _measure = pathlib.Path(__file__).resolve().parent.parent / "module1" / "the-cost-of-a-python-list"
   sys.path.insert(0, str(_measure))
   from measure import time_sum
   ```

3. Build the data. Use a fixed seed so results are deterministic:

   ```python
   import numpy as np

   rng = np.random.default_rng(42)
   data = rng.standard_normal(500_000).astype(np.float64)
   floats = data.tolist()
   ```

4. Time both implementations using `time_sum`:

   ```python
   RUNS = 5

   loop_time = time_sum(lambda: sum(floats), n=RUNS)
   vec_time  = time_sum(lambda: data.sum(),  n=RUNS)
   ```

5. Compute the reference results for correctness checking:

   ```python
   loop_result = sum(floats)
   vec_result  = data.sum()
   ```

6. Assert correctness and print the report:

   ```python
   assert np.isclose(loop_result, vec_result, rtol=1e-9), (
       f"Results must agree: loop={loop_result:.6f}, vec={vec_result:.6f}"
   )

   speedup = loop_time / vec_time

   print(f"loop sum:   {loop_result:.4f}  ({loop_time:.5f} s mean over {RUNS} runs)")
   print(f"vector sum: {vec_result:.4f}  ({vec_time:.5f} s mean over {RUNS} runs)")
   print(f"speedup:    {speedup:.1f}x")
   print("[PASS] results agree, speedup measured")
   ```

7. Wrap steps 3–6 in a module-level function `profile_loop_vs_vec()` so later M4 lessons can extend this file with their own module-level functions; call it from the main guard:

   ```python
   def profile_loop_vs_vec():
       # the data, timing, asserts, and prints from steps 3-6 live here
       ...

   if __name__ == "__main__":
       profile_loop_vs_vec()
   ```

## Done When

Run from the repo root:

```sh
python exercises/module4/vectorization_report.py
```

The script must:

- Print a `loop sum:` line, a `vector sum:` line, a `speedup:` line, and a `[PASS]` line.
- Exit with code 0.
- Assert that `np.isclose(loop_result, vec_result, rtol=1e-9)` passes (the machine-checkable gate).

No dependencies beyond NumPy and the existing `measure.py`.

## Stretch

Add a second experiment: time a Python loop that computes the element-wise square before summing (`sum(x**2 for x in floats)`) against the vectorized form (`(data**2).sum()`). Assert they agree to `rtol=1e-9`. Print a second speedup ratio. Does the gap grow or shrink compared to the plain sum? Print a line explaining which operation saw the larger speedup and why you think that is.
