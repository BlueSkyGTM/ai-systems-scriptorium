# dtype and Strides

An `ndarray` is not just a bag of numbers. It is a buffer plus a description of how to read
that buffer: the element type (`dtype`), the number of dimensions (`ndim`), the shape
(`shape`), and the stride per axis (`strides`). Two arrays can share the same buffer and
describe completely different logical shapes. A transpose is not a copy; it is a stride
rewrite. A slice is not a copy; it is an offset and a stride. Understanding this is the
difference between writing NumPy code that allocates on every operation and writing NumPy
code that moves no data until it has to.

## The dtype Contract

Every element in a NumPy array shares the same dtype: a fixed-size C type that determines
how many bytes each slot occupies and how those bytes are interpreted. NumPy's dtype system
covers the numerical types that appear in AI pipelines:

| dtype | Bytes | Typical Use |
|-------|-------|-------------|
| `float64` | 8 | Default floating-point; cosine similarity, score arrays |
| `float32` | 4 | Embedding vectors from most model outputs; halves memory |
| `int64` | 8 | Label arrays, index arrays |
| `int32` | 4 | Compact label storage when label count fits in 32 bits |
| `bool` | 1 | Mask arrays; boolean indexing |

Choosing the wrong dtype is the most common NumPy performance error. A model that outputs
`float32` embeddings loaded into a `float64` array doubles memory consumption silently.
`arr.dtype` always tells you what you have; `arr.astype(np.float32)` copies to the target
type. `arr.view(np.float32)` reinterprets the buffer in place (zero copy) when the total
byte count is compatible, but view is only safe when you understand the byte layout.
[MS-Learn: Explore and analyze data with Python,
https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/]

```python
import numpy as np

scores = np.array([0.91, 0.74, 0.88, 0.62], dtype=np.float64)
print(scores.dtype)      # float64
print(scores.itemsize)   # 8
print(scores.nbytes)     # 32

compact = scores.astype(np.float32)
print(compact.nbytes)    # 16 -- a copy, half the size
```

## The Stride Model

A stride is the number of bytes to advance in the buffer to move one step along a given axis.
For a C-contiguous (row-major) 2D array with shape `(rows, cols)` and itemsize `k`, the
strides are `(cols * k, k)`: to move one row down, skip `cols * k` bytes; to move one
column right, skip `k` bytes. For a 1D array of float64, strides is `(8,)`.

This is the same model that DirectML uses internally for tensor memory layout: a stride of
zero along a dimension means that dimension broadcasts rather than allocates. NumPy exposes
this explicitly. [MS-Learn: Using strides to express padding and memory layout,
https://learn.microsoft.com/windows/ai/directml/dml-strides]

```python
arr = np.zeros((3, 4), dtype=np.float32)
print(arr.shape)    # (3, 4)
print(arr.strides)  # (16, 4)  -- 4 cols * 4 bytes, then 4 bytes per col
```

The stride model is what makes the transpose free:

```python
t = arr.T
print(t.shape)    # (4, 3)
print(t.strides)  # (4, 16)  -- strides swapped, same buffer
print(np.shares_memory(arr, t))  # True
```

No bytes moved. The stride values simply swapped, describing a different traversal order
over the identical buffer.

## Views Versus Copies

A view shares the buffer with its parent. A copy owns its buffer. This distinction matters
everywhere in NumPy, and NumPy does not always make it obvious.

```python
base = np.arange(12, dtype=np.int32).reshape(3, 4)

# Basic slicing: view
row = base[1, :]
row[0] = 999
print(base[1, 0])  # 999 -- base was mutated through the view

# Fancy indexing: copy
rows = base[[0, 2], :]
rows[0, 0] = -1
print(base[0, 0])  # 0 -- base unchanged
```

The rule: basic indexing (integer scalars, slices, `None`) produces a view. Fancy indexing
(integer arrays, boolean arrays) produces a copy. `arr.flags['OWNDATA']` reports whether an
array owns its buffer. `np.shares_memory(a, b)` checks whether two arrays share any bytes.

Knowing this matters operationally. In an embedding pipeline, transposing a matrix for a dot
product is free (view). Selecting a non-contiguous subset of rows by fancy index is a copy:
you have paid an allocation. In a hot path over a large corpus, unintended copies accumulate.

## Contiguous Layout and Performance

A C-contiguous array traverses memory in row-major order: the last axis changes fastest.
An F-contiguous array traverses in column-major order. An array that is neither (produced,
for example, by transposing a C-contiguous array and then modifying it) may trigger a copy
when passed to functions that require contiguous data.

```python
arr = np.ones((1000, 1536), dtype=np.float32)   # C-contiguous; row = one embedding
print(arr.flags['C_CONTIGUOUS'])   # True

transposed = arr.T                 # F-contiguous view
print(transposed.flags['C_CONTIGUOUS'])   # False
print(transposed.flags['F_CONTIGUOUS'])   # True

# np.dot handles non-contiguous arrays by copying internally when needed
# np.ascontiguousarray makes it explicit:
contiguous_t = np.ascontiguousarray(transposed)
print(contiguous_t.flags['C_CONTIGUOUS'])  # True -- new allocation
```

For embedding similarity workloads: store embeddings as `(n, d)` float32, C-contiguous.
Transpose only when the math requires it, and make the copy explicit with
`np.ascontiguousarray` rather than letting internal functions decide.

## Reading an ndarray's Descriptor

The full descriptor of any array is accessible without any computation:

```python
arr = np.random.rand(512, 1536).astype(np.float32)

print(arr.shape)      # (512, 1536)
print(arr.dtype)      # float32
print(arr.ndim)       # 2
print(arr.strides)    # (6144, 4)  -- 1536*4 bytes per row, 4 bytes per col
print(arr.nbytes)     # 3,145,728  -- 512 * 1536 * 4
print(arr.flags)      # C_CONTIGUOUS: True, OWNDATA: True, WRITEABLE: True, ...
```

Reading these before operating on an array is the NumPy equivalent of reading a table
schema before writing a SQL query: it tells you what you are actually holding.

## Core Concepts

- `dtype` is the per-element type contract: choosing `float32` over `float64` halves memory
  and is the correct choice for model-output embedding vectors.
- Strides describe how to traverse the buffer along each axis: stride zero broadcasts,
  stride reversal transposes, all without moving data.
- Basic indexing (slices, integer scalars) returns views that share the parent buffer;
  fancy indexing (integer arrays, boolean arrays) returns copies that own their buffer.
- `arr.flags['OWNDATA']` and `np.shares_memory(a, b)` are the diagnostic tools for
  view-versus-copy ambiguity; use them before assuming an operation is zero-copy.
- C-contiguous layout (row-major) is the default and the layout most NumPy and external
  routines expect; transposing produces an F-contiguous view, and passing it to a
  routine that requires C-contiguous data triggers an internal copy.

<div class="claude-handoff" data-exercise="draft/exercises/02-dtype-and-strides/">

**Build It in Claude Code**: Load a batch of embedding vectors from a CSV (or generate synthetic float64 ones), inspect the full descriptor (shape, dtype, strides, flags, nbytes), cast to float32 and measure the memory saving, transpose the matrix and confirm it shares memory with the original, then select a non-contiguous row subset via fancy indexing and confirm it does not share memory. Print a structured report of each finding.

</div>
