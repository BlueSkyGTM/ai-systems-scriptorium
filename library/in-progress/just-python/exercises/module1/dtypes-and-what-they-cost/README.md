# Exercise: Dtypes and What They Cost

**Goal:** Build a script that measures the memory cost of float64 versus float32 embeddings and demonstrates, by assertion, that `view` is not a type conversion.

**Why:** Choosing the wrong dtype at ingestion time is the most common silent tax in an embedding pipeline. Knowing the cost in bytes, and knowing that `view` does not fix it, is the difference between a pipeline that fits in memory and one that crashes at scale.

## Steps

1. **Create the embedding arrays.** Generate a synthetic batch of 10,000 embedding vectors at 1,536 dimensions (a common model output size):
   ```python
   import numpy as np
   f64 = np.random.rand(10_000, 1_536)          # float64 by default
   f32 = f64.astype(np.float32)                  # real conversion, new buffer
   ```

2. **Measure and compare memory.** Use `ndarray.nbytes` directly (or import `measure.py` from the lesson-1 exercise at `exercises/module1/the-cost-of-a-python-list/` if you built it there). Print a report:
   ```
   float64 embeddings: 245,760,000 bytes
   float32 embeddings: 122,880,000 bytes
   saving: 122,880,000 bytes (50.0%)
   ```

3. **Assert the saving is exact.** Add this assertion before printing; the script must pass it:
   ```python
   assert f32.nbytes == f64.nbytes // 2
   ```

4. **Demonstrate the view trap.** Create a view of the float64 array cast as float32 and prove it is not equal to the astype result:
   ```python
   trap = f64.ravel().view(np.float32)         # reinterprets bytes, does NOT convert
   converted = f64.ravel().astype(np.float32)  # actual conversion
   assert not np.array_equal(trap[:f64.size], converted), \
       "view and astype should NOT agree: view is byte reinterpretation, not conversion"
   ```
   Print a line confirming the trap: `"view trap confirmed: view != astype"`.

5. **Print `arr.itemsize` and `arr.nbytes` for both arrays.** Show the per-element byte cost alongside the total.

6. **Exit 0.** The script runs with `python dtype_audit.py` and exits clean. No exceptions, all assertions pass.

## Done When

- `assert f32.nbytes == f64.nbytes // 2` passes.
- A printed line shows the byte saving in absolute bytes and as a percentage.
- `assert not np.array_equal(trap[:f64.size], converted)` passes, and a line confirms `"view trap confirmed: view != astype"`.
- The script exits with code 0.

## Stretch

1. Add a timing comparison: measure how long a dot-product of the full matrix against a query vector takes in float64 versus float32. Use `time.perf_counter`. Report both times and the speedup ratio.
2. Write a `skill.md` in this folder (not committed to git) describing what you learned: which dtype you would choose by default for embedding pipelines, and what you would use `view` for instead.
