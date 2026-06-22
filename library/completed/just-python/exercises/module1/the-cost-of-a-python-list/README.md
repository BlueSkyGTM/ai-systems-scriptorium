# Exercise: The Cost of a Python List

**Goal:** Build `measure.py`, a reusable benchmark helper that measures the true memory cost of a Python list versus a NumPy array and times the difference, then run it on one million floats and confirm the ratio exceeds 2.

**Why:** Every numerical pipeline in production AI carries a memory budget; knowing the real cost of a list before committing to one is how engineers avoid the 4x penalty at scale.

## Steps

1. Create `exercises/module1/the-cost-of-a-python-list/measure.py`.

2. Implement `list_bytes(values)`: returns the true memory cost of a Python list by summing `sys.getsizeof` on the container and on every element.

   ```python
   import sys

   def list_bytes(values: list) -> int:
       """Return true memory cost of a Python list: header + all pointed-to objects."""
       return sys.getsizeof(values) + sum(sys.getsizeof(v) for v in values)
   ```

3. Implement `array_bytes(arr)`: returns `arr.nbytes`, the contiguous buffer size.

   ```python
   def array_bytes(arr) -> int:
       """Return the contiguous buffer size of a NumPy ndarray."""
       return arr.nbytes
   ```

4. Implement `time_sum(fn, n: int = 3) -> float`: runs `fn()` `n` times via `timeit.timeit` and returns the mean elapsed seconds. Expose it so later lessons can import it.

   ```python
   import timeit

   def time_sum(fn, n: int = 3) -> float:
       """Return mean wall-clock seconds for fn() over n runs."""
       total = timeit.timeit(fn, number=n)
       return total / n
   ```

5. Add a `main()` block that:
   - Allocates `floats = [1.0] * 1_000_000` and `arr = np.ones(1_000_000, dtype=np.float64)`.
   - Calls `list_bytes` and `array_bytes` and prints both.
   - Computes `ratio = list_bytes(floats) / array_bytes(arr)` and prints it.
   - Times `sum(floats)` vs `arr.sum()` using `time_sum` and prints both.
   - Asserts the ratio is greater than 2.

   ```python
   if __name__ == "__main__":
       import numpy as np

       floats = [1.0] * 1_000_000
       arr = np.ones(1_000_000, dtype=np.float64)

       lb = list_bytes(floats)
       ab = array_bytes(arr)
       ratio = lb / ab

       print(f"list  memory: {lb:>12,} bytes")
       print(f"array memory: {ab:>12,} bytes")
       print(f"ratio:        {ratio:.2f}x")

       list_time = time_sum(lambda: sum(floats))
       arr_time  = time_sum(lambda: arr.sum())
       print(f"list sum time:  {list_time:.4f} s")
       print(f"array sum time: {arr_time:.4f} s")

       assert ratio > 2, f"Expected ratio > 2, got {ratio:.2f}"
       print("assertion passed: list is materially heavier than array")
   ```

6. Run `python measure.py` from the exercise folder. Confirm it exits 0 and prints both memory numbers, the ratio (you should see roughly 4.0x), and the timing comparison.

## Done When

`python measure.py` exits 0, prints a memory ratio greater than 2.0, and reaches the line `assertion passed: list is materially heavier than array`. The assert line in `main()` is the machine-checkable gate.

Expected output shape (exact numbers vary by platform):

```
list  memory:   32,000,056 bytes
array memory:    8,000,000 bytes
ratio:        4.00x
list sum time:  0.0412 s
array sum time: 0.0008 s
assertion passed: list is materially heavier than array
```

## Note on Reuse

`measure.py` is this book's reusable benchmark helper. Later lessons import `list_bytes`, `array_bytes`, and `time_sum` directly. Design it to be imported cleanly: all reusable functions at module level, the main block guarded by `if __name__ == "__main__"`.

## Stretch

Allocate a batch of 512 embedding vectors (1,536 dimensions each) as a Python list of lists and as a 2-D NumPy array of shape `(512, 1536)` with `dtype=float32`. Call `list_bytes` on the list of lists (you will need to sum over rows) and `array_bytes` on the array. Print the ratio. How does it compare to the 1M-float case?
