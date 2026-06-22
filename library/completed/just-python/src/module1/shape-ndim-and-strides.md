# Shape, ndim, and Strides

Every array is a flat buffer in memory plus a small descriptor sitting on top; the buffer never moves, but the descriptor is cheap to rewrite, and that is where both the power and the trap live.

## The Buffer and Its Descriptor

You built `measure.py` in Lesson 1. You know a Python list is a box of pointers to boxed objects: a dozen floats in a list spend their bytes on twelve pointer-sized slots plus twelve individual float objects, scattered wherever the allocator put them. A NumPy array collapses that into one contiguous block: all the element bytes sit side by side, and a small descriptor tells NumPy how to read them.

The descriptor holds four things you can read off any array:

```python
import numpy as np

arr = np.zeros((3, 4), dtype=np.float32)

print(arr.shape)   # (3, 4)  -- 3 rows, 4 columns
print(arr.ndim)    # 2       -- two axes
print(arr.strides) # (16, 4) -- bytes to step along each axis
print(arr.flags)   # C_CONTIGUOUS: True, OWNDATA: True, WRITEABLE: True, ...
```

`shape` and `ndim` are familiar. `strides` is the key: it tells NumPy how many bytes to advance in the buffer to move one step along each axis. For this `float32` array with 4 columns, stepping one row down means skipping `4 cols × 4 bytes = 16 bytes`. Stepping one column right means skipping 4 bytes. That is `(16, 4)`.

The general rule for a C-contiguous array with shape `(rows, cols)` and element size `k` bytes: strides are `(cols * k, k)`. Microsoft's DirectML documentation [captures this precisely](https://learn.microsoft.com/windows/ai/directml/dml-strides): "the packed stride of a dimension is equal to the product of the sizes of the lower-order dimensions." NumPy follows the same formula.

## The Transpose Is Free

When you transpose a 2D array, NumPy does not move a single byte. It swaps the stride values in the descriptor and calls it done:

```python
t = arr.T
print(t.shape)    # (4, 3)
print(t.strides)  # (4, 16)  -- swapped from (16, 4)
print(np.shares_memory(arr, t))  # True
```

`np.shares_memory` returns `True` because both arrays point at the same underlying buffer. The cost of a transpose is a descriptor copy: negligible. This is the power side of the model.

## Views and Copies: the Rule

The trap is that the same sharing mechanism applies everywhere slicing happens, and NumPy does not warn you.

**Basic indexing** (slices, integer scalars, `...`) returns a **view** that shares the buffer with its parent. Mutating the view mutates the parent:

```python
base = np.arange(12, dtype=np.int32).reshape(3, 4)

row = base[1, :]          # view: same buffer, offset to row 1
row[0] = 999
print(base[1, 0])         # 999 -- base changed through the view
print(row.flags['OWNDATA'])  # False -- the view does not own its buffer
```

**Fancy indexing** (integer arrays, boolean arrays) returns a **copy** that owns its own buffer. Mutating the copy leaves the parent untouched:

```python
rows = base[[0, 2], :]    # fancy index: copy
rows[0, 0] = -1
print(base[0, 0])         # 0 -- base unchanged
print(rows.flags['OWNDATA'])    # True
print(np.shares_memory(base, rows))  # False
```

The diagnostics are `arr.flags['OWNDATA']` and `np.shares_memory(a, b)`. Read them before assuming an operation is zero-copy.

One more note the NumPy docs flag explicitly: a slice that extracts a small portion from a large array still holds a reference to that large buffer. The large buffer cannot be freed until every view derived from it is garbage-collected. When you pull a small result from a large intermediate, call `.copy()` explicitly if you want the original to release its memory.

## Where the Trap Bites

In a hot loop over a large corpus, unintended copies accumulate. Each fancy-indexed selection allocates a new buffer; a thousand such selections inside a batch loop allocate a thousand buffers. Checking `np.shares_memory` or `flags['OWNDATA']` before committing to a loop is the same reflex as reading a table schema before writing a query: it tells you what you are actually paying for.

Views cost nothing to create. Copies cost an allocation and a memcpy proportional to the data size. Knowing which you have is not an optimization detail; it is the difference between an embedding pipeline that fits in memory and one that does not.

## Core Concepts

- An ndarray is a flat buffer plus a descriptor; `shape`, `ndim`, and `strides` live in the descriptor, not the buffer.
- Strides encode how many bytes to advance per step along each axis: for a C-contiguous `(rows, cols)` array with element size `k`, strides are `(cols * k, k)`.
- Transposing an array swaps stride values in the descriptor and moves no bytes; `np.shares_memory(arr, arr.T)` is always `True`.
- Basic indexing (slices, integer scalars) returns a view that shares the parent buffer; fancy indexing (integer arrays, boolean arrays) returns a copy that owns its buffer; `arr.flags['OWNDATA']` and `np.shares_memory` are the diagnostic tools.

<div class="claude-handoff" data-exercise="exercises/module1/shape-ndim-and-strides/">

**Build It in Claude Code:** print the full descriptor of a 2D array, prove the transpose shares memory, mutate a slice and watch the parent change, then confirm fancy indexing returns a copy that does not.

</div>
