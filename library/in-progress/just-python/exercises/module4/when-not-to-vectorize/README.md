# Exercise: When Not to Vectorize

**Goal:** Extend `vectorization_report.py` with a memory check that imports `broadcast_allocates` and `time_sum` from the M1 `measure.py`, runs two fixtures (one where vectorizing wins cleanly, one where the broadcast blows the memory budget), and emits a final "vectorize / keep the loop / chunk it" recommendation with the measured numbers. This is the M4 capstone: the report calls the prior artifact's functions, it does not reimplement them.

**Why:** A production AI engineer does not ask "can I vectorize this?" She asks "what is the cheapest path to a correct result inside the memory budget?" This exercise wires up the decision tool that answers that question with numbers, not instinct.

## Before You Touch Code

Read the lesson at `src/module4/when-not-to-vectorize.md`. Then open `exercises/module1/the-cost-of-a-python-list/measure.py` and read its current state. It already exports `broadcast_allocates` and `time_sum`. You are importing those functions, not rewriting them.

L1, L2, and L3 of M4 built up `vectorization_report.py` with timing results. You are adding the memory check and the recommendation function on top of what is already there. Read the file before adding anything.

## Steps

1. Open `exercises/module4/vectorization_report.py`. Read what L1-L3 put there. Do not delete or rename anything already in the file.

2. Add these imports at the top of `vectorization_report.py` if they are not already present:

   ```python
   import sys
   import pathlib
   import numpy as np
   _measure = pathlib.Path(__file__).resolve().parent.parent / "module1" / "the-cost-of-a-python-list"
   sys.path.insert(0, str(_measure))
   from measure import broadcast_allocates, time_sum
   ```

   The path is resolved relative to this file, so it works from any working directory.

3. Implement `check_memory_budget(source, target_shape, budget_bytes)` at module level:

   ```python
   def check_memory_budget(
       source: np.ndarray,
       target_shape: tuple[int, ...],
       budget_bytes: int,
   ) -> dict:
       """
       Use broadcast_allocates to measure whether materializing a broadcast
       into target_shape fits inside budget_bytes.

       Returns a dict with keys:
         'source_bytes'  -- backing memory of source
         'result_bytes'  -- materialized output buffer size
         'budget_bytes'  -- the supplied budget
         'fits'          -- bool: result_bytes <= budget_bytes
       """
   ```

   Call `broadcast_allocates(source, target_shape)` inside the function and return the dict above. Do not re-implement `broadcast_allocates`.

4. Implement `recommend(speed_ratio, memory_check, readable)` at module level:

   ```python
   def recommend(
       speed_ratio: float,       # loop_time / vec_time; >1 means vectorized is faster
       memory_check: dict,       # from check_memory_budget
       readable: bool,           # caller's judgment: can a reader verify this in 30 s?
   ) -> str:
       """
       Return one of: 'vectorize', 'keep-the-loop', 'chunk-it'.

       Decision rule:
         - If vec is faster (speed_ratio > 1.0), fits in memory, and is readable: 'vectorize'
         - If vec does not fit in memory but would be faster: 'chunk-it'
         - Otherwise: 'keep-the-loop'
       """
   ```

5. Add a `run_decision_report()` driver that runs two fixtures and prints the report:

   ```python
   def run_decision_report() -> None:
       print("\n=== Vectorization Decision Report ===\n")

       # --- Fixture 1: small batch, vectorized wins ---
       N_small, D = 512, 1_536
       data_small = np.random.default_rng(0).random((N_small, D)).astype(np.float32)
       mean_small  = np.zeros((1, D), dtype=np.float32)
       budget_small = 64 * 1024 * 1024   # 64 MB is plentiful for 512 rows

       loop_time_s = time_sum(lambda: _center_loop(data_small))
       vec_time_s  = time_sum(lambda: _center_vec(data_small))
       speed_ratio_small = loop_time_s / vec_time_s

       mem_small = check_memory_budget(mean_small, (N_small, D), budget_small)
       rec_small = recommend(speed_ratio_small, mem_small, readable=True)

       print(f"Fixture 1 -- {N_small} x {D} float32")
       print(f"  loop time:          {loop_time_s * 1000:.3f} ms")
       print(f"  vectorized time:    {vec_time_s * 1000:.3f} ms")
       print(f"  speed ratio:        {speed_ratio_small:.2f}x  (vec faster if > 1)")
       print(f"  materialized size:  {mem_small['result_bytes']:,} bytes")
       print(f"  budget:             {mem_small['budget_bytes']:,} bytes")
       print(f"  fits in budget:     {mem_small['fits']}")
       print(f"  RECOMMENDATION:     {rec_small}\n")

       assert rec_small == "vectorize", f"Fixture 1 must recommend vectorize, got {rec_small!r}"

       # --- Fixture 2: large batch, broadcast blows the budget ---
       N_large, D = 50_000, 1_536
       mean_large  = np.zeros((1, D), dtype=np.float32)
       budget_large = 32 * 1024 * 1024   # 32 MB -- 50k rows needs ~300 MB, won't fit

       # We only need the memory check for the large batch (timing a 50k loop is slow)
       mem_large   = check_memory_budget(mean_large, (N_large, D), budget_large)
       rec_large   = recommend(2.0, mem_large, readable=True)   # assume vec would be faster

       print(f"Fixture 2 -- {N_large:,} x {D} float32")
       print(f"  materialized size:  {mem_large['result_bytes']:,} bytes")
       print(f"  budget:             {mem_large['budget_bytes']:,} bytes")
       print(f"  fits in budget:     {mem_large['fits']}")
       print(f"  RECOMMENDATION:     {rec_large}\n")

       assert rec_large == "chunk-it", f"Fixture 2 must recommend chunk-it, got {rec_large!r}"

       print("All assertions passed. Report complete.")
   ```

   You will need two small helpers for fixture 1; add them above `run_decision_report`:

   ```python
   def _center_loop(embeddings: np.ndarray) -> np.ndarray:
       mean = embeddings.mean(axis=0)
       result = np.empty_like(embeddings)
       for i in range(len(embeddings)):
           result[i] = embeddings[i] - mean
       return result

   def _center_vec(embeddings: np.ndarray) -> np.ndarray:
       return embeddings - embeddings.mean(axis=0)
   ```

6. Call `run_decision_report()` inside the existing `if __name__ == "__main__":` block, after the L1-L3 output already there.

7. Run:

   ```
   python vectorization_report.py
   ```

   from the repo root. Confirm it exits 0 and the decision report lines appear at the end.

## Done When

`python vectorization_report.py` exits 0, prints the fixture 1 and fixture 2 blocks with real measured numbers, and reaches `All assertions passed. Report complete.` Two assertions are the machine-checkable gate:

- `rec_small == "vectorize"` (512-row batch fits budget and is faster)
- `rec_large == "chunk-it"` (50 000-row broadcast would need ~307 MB; 32 MB budget says chunk)

No external dependencies beyond NumPy and the standard library. The random seed is fixed (`default_rng(0)`) so measurements are reproducible.

## Expected Output Shape

Exact timing numbers vary by machine. The structure should look like:

```
=== Vectorization Decision Report ===

Fixture 1 -- 512 x 1536 float32
  loop time:           3.241 ms
  vectorized time:     0.187 ms
  speed ratio:        17.33x  (vec faster if > 1)
  materialized size:  3,145,728 bytes
  budget:            67,108,864 bytes
  fits in budget:     True
  RECOMMENDATION:     vectorize

Fixture 2 -- 50,000 x 1536 float32
  materialized size:  307,200,000 bytes
  budget:              33,554,432 bytes
  fits in budget:     False
  RECOMMENDATION:     chunk-it

All assertions passed. Report complete.
```

## Stretch

Implement `center_chunked(embeddings, chunk_size)` from the lesson and add a Fixture 3 that runs it on the 50 000-row batch with `chunk_size=5_000`. Verify the output matches `_center_vec` on a small sample. Print peak memory per chunk and the total wall time. The recommendation for this fixture should come back `vectorize` because inside each chunk the budget is satisfied.
