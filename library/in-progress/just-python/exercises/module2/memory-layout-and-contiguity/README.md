# Exercise: Memory Layout and Contiguity

**Goal:** Extend `measure.py` with `time_contiguous_vs_strided`, a function that times a column reduction on a C-contiguous array and on its transposed view, prints both timings in milliseconds, and asserts the layout gap.

**Why:** A vectorized reduction over a strided view silently pays a cache-locality tax that compounds across every batch in an embedding pipeline; measuring it once makes the cost concrete before Module 4 formalizes where to apply the fix.

## Steps

1. Open `exercises/module1/the-cost-of-a-python-list/measure.py`. Read its current state: it exports `list_bytes`, `array_bytes`, and `time_sum`. You are continuing the build, not starting a new file.

2. Add the following function to `measure.py`:

   ```python
   def time_contiguous_vs_strided(
       size: int = 2000,
       runs: int = 50,
       dtype: np.dtype = np.float64,
   ) -> tuple[float, float]:
       """
       Time a column reduction over a C-contiguous array vs its transposed view.

       Parameters
       ----------
       size : int
           Side length of the square array (default 2000 -> 2000x2000, ~32 MB float64).
       runs : int
           Number of timed repetitions to average over.
       dtype : np.dtype
           Element dtype (default np.float64).

       Returns
       -------
       (c_ms, strided_ms) : tuple[float, float]
           Mean per-reduction time in milliseconds for the C-contiguous and strided cases.

       Side effects
       ------------
       Prints two ms lines and a ratio line:
           C-contiguous reduction:  X.XXX ms
           transposed (strided):    X.XXX ms
           ratio: X.XXx slower
       Asserts:
           - both reductions produce the same result (correctness)
           - strided_ms <= c_ms * SLACK  (layout never makes contiguous worse by more than SLACK)

       Reuses time_sum from this module for single-call timing checks.
       """
   ```

3. Implement the body. Use `time_sum` (already in `measure.py`) to verify a single-call result is correct, then use `time.perf_counter` for the multi-run average that produces `c_ms` and `strided_ms`. The function must:

   - Allocate `arr = rng.random((size, size), dtype=dtype)` with `rng = np.random.default_rng(42)` for reproducibility.
   - Time `arr.sum(axis=0)` for `runs` iterations and compute the mean milliseconds: `c_ms`.
   - Build `t = arr.T` (a view, no copy). Time `t.sum(axis=1)` for `runs` iterations: `strided_ms`.
   - Print:
     ```
     C-contiguous reduction:  X.XXX ms
     transposed (strided):    X.XXX ms
     ratio: X.XXx slower
     ```
   - Assert correctness: `np.allclose(arr.sum(axis=0), t.sum(axis=1))`.
   - Assert timing robustness: `strided_ms <= c_ms * SLACK` where `SLACK = 4.0`. This generous margin ensures the gate passes on fast machines and under load; the printed ratio is the real diagnostic.
   - Return `(c_ms, strided_ms)`.

4. Add `time_contiguous_vs_strided` to `measure.py`'s `main()` block (after the existing assertions):

   ```python
   print("\n--- layout timing ---")
   c_ms, s_ms = time_contiguous_vs_strided()
   ```

5. Run `python measure.py` from the exercise folder. All existing assertions must still pass. The new timing block must print and the new assertions must pass.

## Done When

`python measure.py` exits 0 and the output includes:

```
--- layout timing ---
C-contiguous reduction:  X.XXX ms
transposed (strided):    X.XXX ms
ratio: X.XXx slower
```

The two machine-checkable gates are:

```python
assert np.allclose(arr.sum(axis=0), t.sum(axis=1))          # correctness
assert strided_ms <= c_ms * 4.0, (                           # timing robustness
    f"strided {strided_ms:.3f} ms is >4x slower than "
    f"contiguous {c_ms:.3f} ms -- unexpected"
)
```

NumPy only, no external dependencies, deterministic (seeded RNG).

## Stretch

Add a third timing block inside `time_contiguous_vs_strided`: call `np.ascontiguousarray(t)` once, then time the `sum` over the copy. Assert that the copy-then-reduce time is within 20% of `c_ms`. Print:

```
ascontiguousarray + reduce: X.XXX ms
```

This proves the one-time copy restores performance and gives you a concrete cost-benefit threshold: copy once if you reduce more than roughly `copy_ms / (strided_ms - c_ms)` times.
