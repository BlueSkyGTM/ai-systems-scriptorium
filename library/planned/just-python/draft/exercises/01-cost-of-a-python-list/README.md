# Exercise 01: The Cost of a Python List

## Goal

Write a script that makes Python's object overhead concrete by measuring the true memory
cost of the same numerical data stored two ways: as a Python list of floats and as a NumPy
`float64` array. Then scale the measurement to a realistic AI workload: a batch of embedding
vectors.

## Why

You cannot develop an intuition for when NumPy matters until you have seen the numbers.
The 4x memory gap between a Python list and a NumPy array is not folklore; it is measurable
in a dozen lines. Once you have measured it on floats, measuring it on embedding batches
shows you exactly why the Production AI Engineer reaches for NumPy at the data boundary.

## Steps

1. Create a file `exercises/module1/engine.py` (this file will grow across the module).
   Start with an `import sys` and `import numpy as np`.

2. Implement `list_cost(n: int) -> dict` that:
   - Allocates `[float(i) for i in range(n)]`.
   - Measures `sys.getsizeof(lst)` (the container header only; note this in a comment).
   - Measures true total cost: `sys.getsizeof(lst) + sum(sys.getsizeof(f) for f in lst)`.
   - Returns both measurements in a dict under the keys `"header_bytes"` and `"total_bytes"`.

3. Implement `array_cost(n: int) -> dict` that:
   - Allocates `np.arange(n, dtype=np.float64)`.
   - Records `arr.nbytes` (the buffer cost; note why this is the correct measure).
   - Records `sys.getsizeof(arr)` (the Python object wrapper; note it is nearly constant).
   - Returns both under `"buffer_bytes"` and `"wrapper_bytes"`.

4. Implement `compare(n: int) -> None` that calls both functions and prints a table:

   ```
   n = 1,000,000 floats
   -----------------------------------------------
   Python list   header:       8,056,104 bytes
   Python list   total:       32,056,104 bytes
   NumPy float64 buffer:       8,000,000 bytes
   NumPy float64 wrapper:            112 bytes
   Ratio (list total / array buffer):  4.01x
   ```

   The exact numbers will vary slightly by Python version; the ratio should be near 4.

5. Extend the script to handle an embedding batch. Add `embedding_compare()` that:
   - Loads (or generates) a matrix of shape `(512, 1536)` float values.
   - Represents it as a list-of-lists: `[[float(x) for x in row] for row in data]`.
   - Represents it as `np.array(data, dtype=np.float32)`.
   - Reports total bytes for both and the ratio.
   - Hint: for the list-of-lists, `sys.getsizeof` on the outer list does not count inner
     lists or their floats. Use a recursive or two-level sum.

6. Add a `if __name__ == "__main__":` block that calls `compare(1_000_000)` and
   `embedding_compare()`. Running `python exercises/module1/engine.py` must exit 0.

## Done When

- `python exercises/module1/engine.py` exits 0 and prints both comparison tables.
- The ratio for one million floats is printed and is between 3.5x and 5x (accounting for
  Python version variation).
- The embedding batch section reports `float32` array size in bytes and shows the ratio
  against the list-of-lists cost.
- Comments in the code explain why `sys.getsizeof` is shallow and why `ndarray.nbytes`
  is the correct measure for the buffer.

## Stretch

Add a third comparison: `array('d', floats)` from Python's standard library `array` module
(not NumPy). This is a typed contiguous array in pure Python. Measure its buffer cost with
`array_obj.buffer_info()[1] * array_obj.itemsize`. Compare to the NumPy equivalent: same
buffer layout, but without NumPy's vectorized operations. This isolates what dtypes and
contiguous storage buy you versus what vectorized math on top of them buys you.
