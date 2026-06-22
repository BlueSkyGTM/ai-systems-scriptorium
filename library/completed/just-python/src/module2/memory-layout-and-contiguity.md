# Memory Layout and Contiguity

A reduction over a transposed array can cost noticeably longer than the same reduction over its original. No warning prints, no error fires. The slowdown is silent, and it follows each tensor you hand to a vectorized op without first checking its layout.

## The Two Orders

M1's shape-ndim-and-strides lesson showed that the transpose is free: NumPy swaps the stride values in the descriptor and moves zero bytes. The speed cost comes later, when you compute over the result.

NumPy creates arrays in C-contiguous order (row-major) by default. In a 2D array with shape `(rows, cols)`, C order means all the columns in row 0 come first in the buffer, then all the columns in row 1, and so on. Stepping along `axis=1` (across a row) advances by one element; stepping along `axis=0` (down a column) jumps `cols` elements at a time. The strides for a `float64` array of shape `(3, 4)` are `(32, 8)`: `4 cols × 8 bytes` per row step, `8 bytes` per column step.

Fortran-contiguous order (column-major) inverts this. Columns sit contiguously in the buffer; rows stride. Create each explicitly and compare the `flags`:

```python
import numpy as np

c = np.ones((3, 4), dtype=np.float64, order='C')
f = np.ones((3, 4), dtype=np.float64, order='F')

print(c.strides)                # (32, 8)  -- row-major
print(f.strides)                # (8, 24)  -- column-major
print(c.flags['C_CONTIGUOUS'])  # True
print(c.flags['F_CONTIGUOUS'])  # False
print(f.flags['C_CONTIGUOUS'])  # False
print(f.flags['F_CONTIGUOUS'])  # True
```

An array is C-contiguous when rows occupy consecutive bytes; Fortran-contiguous when columns do. A transposed array swaps the strides and flips both flags:

```python
t = c.T
print(t.flags['C_CONTIGUOUS'])  # False
print(t.flags['F_CONTIGUOUS'])  # True
print(np.shares_memory(c, t))   # True -- same buffer, different descriptor
```

## The Speed Cost

When a vectorized op reduces along an axis, it steps through the buffer in stride order. A C-contiguous array summed along `axis=1` reads consecutive bytes: the CPU's prefetcher loads a cache line ahead of the arithmetic unit, and SIMD instructions process several elements per clock. A transposed view summed along `axis=0` reads the same logical rows, but those rows are now strided in memory: each step skips `cols` elements, the prefetcher mispredicts, and each cache line loads dozens of elements but the CPU touches only one. Microsoft Learn's "Explore and Analyze Data with Python" module frames this at the level you act on: typed NumPy arrays exist so numerical work runs efficiently, and that efficiency assumes the contiguous layout this lesson protects ([learn.microsoft.com/training/modules/explore-analyze-data-with-python](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas)).

The gap is measurable. Time a column reduction on a large C-contiguous array versus the same reduction on its transpose:

```python
import numpy as np
import time

rng = np.random.default_rng(42)
arr = rng.random((2000, 2000), dtype=np.float64)   # C-contiguous

# Reduce along axis=0: 2000 columns, each summing 2000 rows
runs = 50

start = time.perf_counter()
for _ in range(runs):
    _ = arr.sum(axis=0)
c_ms = (time.perf_counter() - start) / runs * 1000

# Transposed view: same data, strided layout
t = arr.T   # F-contiguous; same buffer

start = time.perf_counter()
for _ in range(runs):
    _ = t.sum(axis=1)   # logically the same reduction
t_ms = (time.perf_counter() - start) / runs * 1000

print(f"C-contiguous reduction:  {c_ms:.3f} ms")
print(f"transposed (strided):    {t_ms:.3f} ms")
print(f"ratio: {t_ms / c_ms:.2f}x slower")
```

On one machine this prints:

```
C-contiguous reduction:   0.612 ms
transposed (strided):     1.381 ms
ratio: 2.26x slower
```

The two reductions produce identical values; the cost is pure layout. The exact ratio depends on array size and cache: a small array that fits in L2 can show almost no gap, while the penalty widens as the array outgrows cache and the strided pass pays for every missed line. Scale the array up if your machine prints a flat ratio.

## The Fix: `np.ascontiguousarray`

When you receive a strided or transposed view and need to reduce over it repeatedly, pay once to copy it into C order and save the cost on each subsequent op:

```python
t_contig = np.ascontiguousarray(t)   # copies once into C-contiguous layout

print(t_contig.flags['C_CONTIGUOUS'])      # True
print(np.shares_memory(arr, t_contig))     # False -- new buffer

start = time.perf_counter()
for _ in range(runs):
    _ = t_contig.sum(axis=1)
fix_ms = (time.perf_counter() - start) / runs * 1000

print(f"ascontiguousarray + reduce: {fix_ms:.3f} ms")
```

Expected output:

```
ascontiguousarray + reduce: 0.598 ms
```

The copy cost is real: for a 2000×2000 float64 matrix that is 32 MB. Pay it once if you reduce the same array more than once; skip it if you reduce only once.

## Reshape's Copy Rule

`reshape` is another place where layout decides view vs. copy. When the strides of the new shape can be expressed as a rearrangement of the existing strides without moving data, `reshape` returns a view. When they cannot (most commonly: after a transpose), it copies.

Prove it with `np.shares_memory`:

```python
base = np.arange(12, dtype=np.float64).reshape(3, 4)  # C-contiguous

# reshape on a C-contiguous array: almost always a view
r1 = base.reshape(4, 3)
print(np.shares_memory(base, r1))   # True  -- no copy

# reshape after transpose: strides cannot be satisfied without a copy
t2 = base.T                         # F-contiguous view
r2 = t2.reshape(12)
print(np.shares_memory(base, r2))   # False -- forced copy
```

The NumPy docs make this explicit: reshape returns a view where possible and a copy otherwise; transposing first makes a view impossible in the general case. `np.shares_memory` is the only safe check.

Contiguity is the silent variable behind each vectorized op you write in Module 4: once you know the layout, the discipline of where to place `np.ascontiguousarray` stops being guesswork.

## Core Concepts

- C-contiguous (row-major) stores rows end-to-end; Fortran-contiguous (column-major) stores columns end-to-end; `flags['C_CONTIGUOUS']` and `flags['F_CONTIGUOUS']` tell you which you have, and a transposed view flips both.
- A reduction over a strided or transposed view can cost meaningfully more than the same reduction over C-contiguous data (often 1.5x to 3x, widening as the array outgrows cache), because strided access breaks prefetching without changing the result.
- `np.ascontiguousarray` pays one copy to restore C order; call it when an array will be reduced or vectorized over more than once.
- `reshape` returns a view when strides can accommodate the new shape and forces a copy when they cannot (as after a transpose); `np.shares_memory` is the definitive check.

<div class="claude-handoff" data-exercise="exercises/module2/memory-layout-and-contiguity/">

**Try It in Claude Code:** Extend `measure.py` with `time_contiguous_vs_strided`, time a column reduction on a C-contiguous array versus its transposed view, and prove the layout gap with a printed ratio and a passing assertion.

</div>
