# The Cost of a Python List

Call `sys.getsizeof([])` and you get 56 bytes. Add one float and it jumps to 64 bytes. Add a
million floats, and Python has allocated the list header plus a million eight-byte pointers,
each pointing at a heap object that itself costs at least 24 bytes. A million floats in a
Python list consumes roughly 32 MB (an 8 MB pointer array plus 24 MB of float objects), four
times the 8 MB a contiguous float64 array would. That gap is not a bug. It is the price of Python's data model, and understanding it is the prerequisite
for knowing when NumPy pays.

## Python's Object Model

Every value in Python is a `PyObject`: a C struct carrying a type pointer, a reference count,
and the value itself. CPython uses this uniformly; a float `3.14` on the heap is a 24-byte
struct, not four bytes of IEEE 754. When you store values in a list, the list stores pointers
to those objects, not the objects themselves. This indirection enables duck typing, dynamic
dispatch, and garbage collection. It also means accessing element N of a list requires two
memory lookups: one to follow the list's internal pointer array to the right slot, and one to
dereference the pointer to the actual object.

The reference count in each `PyObject` is what keeps CPython's garbage collector fast on
the common case: object lifetime is tracked by increment and decrement, not by periodic
tracing. The cost is that every assignment is a reference-count operation, and in a tight
numerical loop over a million elements, those operations dominate.

For AI workloads, this is not an academic concern. An embedding vector with 1,536 dimensions
represented as a Python list of floats carries 1,536 heap allocations per vector. A batch of
512 such vectors is 786,432 heap objects, each individually reference-counted. Cosine
similarity computed element-by-element in a Python loop is not just slow: it is slow in a way
that compounds with batch size. [MS-Learn: Explore and analyze data with Python,
https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/]

## Measuring the Gap

Python's `sys` module exposes the surface-level cost:

```python
import sys

floats = [1.0] * 1_000_000
print(f"List size (header + pointers): {sys.getsizeof(floats):,} bytes")

# sys.getsizeof does NOT follow pointers. The real cost includes each object:
import gc
gc.collect()
total = sys.getsizeof(floats) + sum(sys.getsizeof(f) for f in floats)
print(f"List + all float objects: {total:,} bytes")
```

Running this on CPython 3.11 produces roughly 8 MB for the pointer array and 24 MB for the
float objects: 32 MB total for one million floats. The same data in a NumPy `float64` array
costs 8 MB, exactly eight bytes per element in a contiguous block.

`sys.getsizeof` is shallow: it does not follow references. This is the right call for measuring
the container itself, but it will mislead you about total memory if you stop there. The principle
to carry forward: measure what the CPU actually touches, the buffer, not the Python object wrapper.

## The Contiguous Alternative

NumPy's `ndarray` solves the indirection problem by storing values in a single contiguous
buffer of a declared C type. There are no heap allocations per element. There is no
reference counting per element. The buffer is a flat block of bytes: `float64` gives eight
bytes per slot, `float32` gives four, `int16` gives two. The CPU can prefetch this buffer,
operate on it with SIMD instructions, and page it efficiently because it is typed and
contiguous. None of that is possible with a Python list.

```python
import numpy as np

arr = np.ones(1_000_000, dtype=np.float64)
print(f"NumPy array buffer: {arr.nbytes:,} bytes")  # 8,000,000
print(f"dtype: {arr.dtype}")                          # float64
print(f"itemsize: {arr.itemsize} bytes")              # 8
```

The `nbytes` attribute is the honest measure: it counts only the buffer, matching what the
CPU sees. `itemsize` tells you the per-element cost of the chosen dtype. Choosing `float32`
instead of `float64` halves both.

## When Lists Are Correct

The object model is not always the enemy. Python lists shine when:

- Elements are heterogeneous (strings, integers, and None in the same container).
- The collection is small and allocation cost is negligible.
- You need dynamic growth, slicing into new lists, or in-place mutation with type changes.
- You are building a pipeline stage whose output is another Python object, not a numerical
  computation.

The wrong instinct is to replace every list with a NumPy array. A configuration dictionary,
a list of file paths, a queue of task records: these are correct as Python containers. The
right instinct is to know the boundary: when the container holds fixed-type numerical data
that will be operated on mathematically, the Python list is the wrong tool and the cost
is real.

In Sans Python's evaluation tables, the score column is numerical, fixed-type, and
mathematically operated on. That is where the list pays its cost and where NumPy earns its place.

## Core Concepts

- Every Python value is a `PyObject` carrying type, reference count, and value overhead;
  a million floats in a list consume roughly four times the memory of a contiguous `float64`
  array because each float is a separate 24-byte heap allocation.
- `sys.getsizeof` measures the container header only; total memory cost requires following
  references or using buffer-aware tools like `ndarray.nbytes`.
- NumPy stores values in a single typed, contiguous buffer: no per-element allocation, no
  per-element reference counting, SIMD-amenable layout.
- The list versus array choice is a boundary decision: heterogeneous, small, or
  non-numerical collections belong in Python containers; fixed-type numerical data that will
  be mathematically operated on belongs in NumPy arrays.

<div class="claude-handoff" data-exercise="draft/exercises/01-cost-of-a-python-list/">

**Build It in Claude Code**: Write a script that allocates a million floats as a Python list and as a NumPy `float64` array, measures true memory cost for both using `sys.getsizeof` (shallow) and `ndarray.nbytes` (buffer), computes the ratio, and prints a structured comparison table. Then replace the float data with a batch of 512 embedding vectors (1,536 dims each), synthetic or loaded from a CSV, and repeat the measurement.

</div>
