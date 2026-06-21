# Exercise: Why NumPy Exists

**Goal:** Build a side-by-side comparison of a Python list and a NumPy array that makes the container-to-buffer leap visible in numbers.

**Why:** The buffer model is not a slogan; it is a measurable property. Once you can read `dtype`, `itemsize`, and `nbytes` off an array and verify the identity `nbytes == n * itemsize`, you have the mental model you need to reason about every numeric library built on NumPy.

## Steps

1. Create a new file called `buffer_vs_container.py` in this folder.

2. At the top, import the `measure_memory` function from the `measure.py` you wrote in the previous exercise. That file lives at `exercises/module1/the-cost-of-a-python-list/measure.py`. Import it rather than copying it:
   ```python
   import sys
   import os
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'the-cost-of-a-python-list'))
   from measure import measure_memory
   ```

3. Create the same five numbers in two forms:
   ```python
   import numpy as np

   N = 5
   py_list = [1.0, 2.0, 3.0, 4.0, 5.0]
   arr = np.array(py_list, dtype=np.float64)
   ```

4. Print the array's buffer properties:
   ```python
   print(f"dtype:    {arr.dtype}")
   print(f"itemsize: {arr.itemsize} bytes")
   print(f"nbytes:   {arr.nbytes} bytes")
   print(f"identity check: nbytes == N * itemsize → {arr.nbytes == N * arr.itemsize}")
   ```

5. Assert the buffer identity and the dtype so the script fails loudly if something is wrong:
   ```python
   assert arr.dtype == np.float64, f"expected float64, got {arr.dtype}"
   assert arr.nbytes == N * arr.itemsize, "buffer identity failed"
   ```

6. Use `measure_memory` to print the memory cost of each, side by side:
   ```python
   list_bytes  = measure_memory(py_list)
   array_bytes = measure_memory(arr)
   print(f"\nMemory — list: {list_bytes} bytes, array: {array_bytes} bytes")
   print(f"Array is {list_bytes / array_bytes:.1f}x smaller than the list")
   ```

7. Run the script:
   ```
   python buffer_vs_container.py
   ```

## Done When

- The script exits with code 0.
- The output prints `dtype`, `itemsize`, and `nbytes` for the array.
- The line `identity check: nbytes == N * itemsize → True` appears.
- Both asserts pass silently (no exception).
- A memory comparison line prints with a ratio greater than 1.0.

## Stretch

Repeat the comparison with `dtype=np.float32` and `dtype=np.int8`. Print `nbytes` for each. Observe how choosing a narrower dtype halves (or further reduces) memory. Add an assert that `np.array(py_list, dtype=np.float32).itemsize == 4`.
