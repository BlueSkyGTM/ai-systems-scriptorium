# Exercise 02: dtype and Strides

## Goal

Inspect the full descriptor of a NumPy array: shape, dtype, strides, flags, and nbytes.
Cast between dtypes and measure the memory impact. Transpose a matrix and confirm it shares
the buffer. Select rows via fancy indexing and confirm it does not. Print a structured report
of every finding. By the end, reading an array's descriptor is as automatic as reading a
table schema.

## Why

Every NumPy performance problem is ultimately a dtype-or-strides problem: the wrong type,
an unintended copy, a non-contiguous layout slowing down a downstream operation. The
Production AI Engineer diagnoses these by inspection, not by guessing. This exercise builds
that diagnostic muscle on a realistic embedding matrix before you encounter the same issues
in a live pipeline.

## Steps

All work goes in `exercises/module1/engine.py`, which you started in Exercise 01.

1. Add a function `describe(arr: np.ndarray, label: str) -> None` that prints:

   ```
   [label]
     shape:   (512, 1536)
     dtype:   float64
     ndim:    2
     strides: (12288, 8)
     nbytes:  6,291,456
     C_CONTIGUOUS: True
     OWNDATA:      True
   ```

   Use `arr.shape`, `arr.dtype`, `arr.ndim`, `arr.strides`, `arr.nbytes`,
   `arr.flags['C_CONTIGUOUS']`, `arr.flags['OWNDATA']`.

2. Create a test matrix: `base = np.random.rand(512, 1536).astype(np.float64)`. Call
   `describe(base, "base float64")`.

3. Add `cast_compare(arr: np.ndarray) -> None` that:
   - Casts to `float32` with `arr.astype(np.float32)` and calls `describe` on the result.
   - Confirms `np.shares_memory(arr, casted)` is `False` (astype always copies).
   - Prints the memory saving as a percentage.

4. Add `transpose_check(arr: np.ndarray) -> None` that:
   - Transposes: `t = arr.T`.
   - Calls `describe` on the transpose.
   - Asserts `np.shares_memory(arr, t)` is `True` and prints "Transpose: shared buffer".
   - Notes the swapped strides in the output.

5. Add `fancy_vs_basic(arr: np.ndarray) -> None` that:
   - Basic slice: `basic = arr[100:200, :]`. Check `np.shares_memory(arr, basic)`.
   - Fancy index: `fancy = arr[[10, 50, 200, 400], :]`. Check `np.shares_memory(arr, fancy)`.
   - Print "Basic slice: shared buffer" or "Basic slice: copy" accordingly.
   - Print "Fancy index: shared buffer" or "Fancy index: copy" accordingly.
   - Expected: basic is shared; fancy is a copy.

6. Add a `contiguous_roundtrip(arr: np.ndarray) -> None` that:
   - Transposes the array.
   - Passes the transpose to `np.ascontiguousarray`.
   - Confirms the result is C-contiguous and owns its data.
   - Reports the byte cost of the explicit copy versus the zero-cost view.

7. Wire everything into `if __name__ == "__main__":` so all four functions run in sequence
   after the Exercise 01 comparisons. `python exercises/module1/engine.py` must exit 0.

## Done When

- Running `python exercises/module1/engine.py` exits 0 and prints the full descriptor for
  `base float64` and `base float32`.
- The output correctly identifies the transpose as a shared buffer and confirms its strides
  are swapped relative to the original.
- Basic slicing is identified as a shared buffer; fancy indexing is identified as a copy.
- `np.ascontiguousarray` on the transpose produces a new allocation with `C_CONTIGUOUS: True`
  and `OWNDATA: True`, and the report notes the byte cost.

## Stretch

Add a `view_reinterpret(arr: np.ndarray) -> None` section. Take a `float32` array and call
`arr.view(np.uint8)`. Confirm it shares the buffer. Explain in a comment what `view` is
doing at the byte level: no conversion, only reinterpretation. Then demonstrate what goes
wrong if you call `view(np.float64)` on an odd-length `float32` array (it raises a
`ValueError`). Understanding why is understanding the stride and buffer contract at the
byte level.
