# Exercise: Shape, ndim, and Strides

**Goal:** Build a script that proves, with assertions, that an ndarray is a flat buffer plus a descriptor: the transpose is free (shares memory), a slice is a view (mutating it mutates the parent), and a fancy-indexed selection is a copy (mutating it leaves the parent unchanged).

**Why:** Knowing which operations allocate and which do not is the difference between an embedding pipeline that fits in memory and one that silently blows up on a large corpus.

## Steps

1. Create a 2D array with shape `(4, 5)` and dtype `np.int32`. Fill it with `np.arange(20).reshape(4, 5)`.

2. Print its full descriptor in a structured report:

   ```
   shape:   (4, 5)
   ndim:    2
   strides: (20, 4)
   dtype:   int32
   OWNDATA: True
   C_CONTIGUOUS: True
   ```

3. Transpose the array. Print `t.shape`, `t.strides`, and `np.shares_memory(arr, t)`. Assert that they share memory:

   ```python
   assert np.shares_memory(arr, arr.T), "Transpose must share the buffer"
   ```

4. Slice row 1 as a view: `row = arr[1, :]`. Mutate `row[0] = 999`. Assert the parent changed:

   ```python
   assert arr[1, 0] == 999, "Mutating the view must change the parent"
   assert not row.flags['OWNDATA'], "A basic-indexed row must not own its buffer"
   ```

5. Fancy-index a subset of rows: `fancy = arr[[0, 2], :]`. Mutate `fancy[0, 0] = -1`. Assert the parent did not change and the copy does not share memory:

   ```python
   assert arr[0, 0] != -1, "Mutating the fancy-indexed copy must not change the parent"
   assert fancy.flags['OWNDATA'], "Fancy-indexed result must own its buffer"
   assert not np.shares_memory(arr, fancy), "Fancy-indexed result must not share memory"
   ```

6. Print a final report line for each finding:

   ```
   [PASS] transpose shares buffer
   [PASS] slice view: mutating row changed parent
   [PASS] fancy copy: mutating rows did not change parent
   ```

7. Exit with code 0 if all assertions pass.

## Done When

All five assertions pass, the structured descriptor report prints, the three `[PASS]` lines appear, and the script exits with code 0. Run it with:

```sh
python shape_strides.py
```

No external dependencies beyond NumPy.

## Stretch

Add a sixth check: slice a small patch from a large array (`big = np.ones((1000, 1000), dtype=np.float32); patch = big[:2, :2]`), confirm `patch.base is not None`, then call `patch = patch.copy()` and confirm `patch.base is None`. Print both findings and assert both. This demonstrates the explicit-copy pattern for releasing large intermediate buffers.
