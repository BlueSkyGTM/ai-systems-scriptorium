# Exercise: Broadcasting

**Goal:** Extend your existing `measure.py` with `broadcast_allocates`, a function that proves a broadcast view costs near-zero bytes until an arithmetic operation forces the full output buffer.

**Why:** Knowing when NumPy allocates memory (and when it does not) is what lets you keep a 512x1536 batch-normalization step inside your memory budget instead of blowing past it silently.

## Steps

1. Open `exercises/module1/the-cost-of-a-python-list/measure.py`. Read its current state. You are extending this file, not starting a new one. Do not re-implement `list_bytes`, `array_bytes`, or `time_sum`.

2. Add the following import at the top of `measure.py` if it is not already there:

   ```python
   import numpy as np
   ```

3. Implement `broadcast_allocates` at module level, after the existing functions:

   ```python
   def broadcast_allocates(
       source: np.ndarray,
       target_shape: tuple[int, ...],
   ) -> dict[str, int]:
       """
       Probe whether broadcasting a source array to target_shape allocates memory.

       Returns a dict with keys:
         'source_bytes'  -- source.nbytes (the real backing memory)
         'view_bytes'    -- np.broadcast_to(source, target_shape).nbytes (reported size, no copy)
         'result_bytes'  -- (np.broadcast_to(source, target_shape) + 0.0).nbytes (materialized)
         'view_shares'   -- int(np.shares_memory(view, source))  (1 if still lazy, 0 if copied)
         'result_shares' -- int(np.shares_memory(result, source)) (0 after materialization)
       """
   ```

   The function must:
   - Create `view = np.broadcast_to(source, target_shape)`.
   - Force materialization with `result = view + 0.0` (a no-op arithmetic op writes a new buffer).
   - Use `np.shares_memory` to confirm the view shares the source buffer and the result does not.
   - Return the dict described above.

4. Add a `run_broadcast_allocates()` driver that calls `broadcast_allocates` with a concrete case and prints the results:

   ```python
   def run_broadcast_allocates() -> None:
       mean = np.zeros((1536,), dtype=np.float32)          # shape (1536,)
       source = mean[np.newaxis, :]                        # shape (1, 1536)
       target = (512, 1536)

       stats = broadcast_allocates(source, target)

       print(f"source bytes:        {stats['source_bytes']:>12,}")
       print(f"view bytes (lazy):   {stats['view_bytes']:>12,}")
       print(f"result bytes (full): {stats['result_bytes']:>12,}")
       print(f"view shares source:  {bool(stats['view_shares'])}")
       print(f"result shares source:{bool(stats['result_shares'])}")

       assert stats['view_shares'] == 1, "broadcast_to view must share memory with source"
       assert stats['result_shares'] == 0, "materialized result must not share memory with source"
       assert stats['result_bytes'] > stats['source_bytes'], \
           "materialized buffer must be larger than the source"

       print("assertion passed: broadcast stays lazy until arithmetic forces allocation")
   ```

5. Call `run_broadcast_allocates()` inside the existing `if __name__ == "__main__":` block, after the existing M1 assertions.

6. Run `python measure.py` from `exercises/module1/the-cost-of-a-python-list/`. Confirm it still exits 0 and the new lines appear after the M1 output.

## Done When

`python measure.py` exits 0, prints the five broadcast lines, reaches `assertion passed: broadcast stays lazy until arithmetic forces allocation`, and the three assertions all pass. No external dependencies beyond NumPy and the standard library. Deterministic: the arrays are fixed-shape zeros, no random seed needed.

Expected output shape (exact numbers are platform-stable for `float32`):

```
source bytes:                6,144
view bytes (lazy):       3,145,728
result bytes (full):     3,145,728
view shares source:  True
result shares source:False
assertion passed: broadcast stays lazy until arithmetic forces allocation
```

Note: `view.nbytes` reports the *logical* size of the broadcast shape (512 * 1536 * 4 = 3,145,728), but no allocation of that size occurs. `np.shares_memory(view, source)` returning `True` is the proof it is a zero-copy view. The result, at the same size, does own its buffer.

## Stretch

Repeat the experiment with a `(512, 1536)` source and a `(512, 1)` mean (row-wise broadcasting). Add a second block to `run_broadcast_allocates` that measures this direction and asserts the same lazy/materialized relationship. Print which axis the broadcast expanded across.
