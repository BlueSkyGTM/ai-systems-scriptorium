# The Cost of a Python List

A million floats in a Python list consume roughly 32 MB; the same data in a NumPy array costs 8 MB. That ratio is not a quirk: it is the Python object model behaving exactly as designed, and knowing why it happens is what lets you pick the right container before the data gets big.

## Every Value Is a Box

Python represents every value, no exceptions, as a `PyObject`: a C struct on the heap carrying three fields. The first is a type pointer (which class owns this object). The second is a reference count (how many names point to it, so CPython knows when to free it). The third is the value itself.

For a float, that struct costs 24 bytes on a 64-bit CPython. The float `1.0` is not four bytes of IEEE 754; it is a 24-byte heap allocation. This uniformity is what makes duck typing, dynamic dispatch, and the garbage collector work. It is also the tax on every number you store.

## A List Stores Pointers, Not Values

When you write `[1.0, 2.0, 3.0]`, the list object does not hold those floats directly. It holds a pointer array: one 8-byte pointer per element, each pointing at a `PyObject` on the heap. Accessing element `i` requires two memory reads: first to the pointer array to find the address, then to the heap to dereference the object. That double indirection is the cost of generality.

The math for one million floats:

- Pointer array: 1,000,000 pointers × 8 bytes = **8 MB**
- Float objects: 1,000,000 PyObjects × 24 bytes = **24 MB**
- Total: **~32 MB**

`sys.getsizeof` gives you only the first part, the container header and its pointer array. It does not follow references. To measure the true cost, you follow the pointers yourself:

```python
import sys

floats = [1.0] * 1_000_000
shallow = sys.getsizeof(floats)
deep = shallow + sum(sys.getsizeof(f) for f in floats)
print(f"shallow (pointer array):  {shallow:>12,} bytes")
print(f"deep (list + all floats): {deep:>12,} bytes")
```

The shallow number flatters the list. The deep number is what the allocator actually touched.

## The Contiguous Alternative

NumPy's `ndarray` stores values in a single typed, contiguous buffer. No per-element allocation. No per-element reference count. A `float64` array of one million elements is exactly 8,000,000 bytes of memory, 8 bytes per slot, laid out so the CPU can prefetch it, apply SIMD instructions across it, and page it without chasing pointers.

```python
import numpy as np

arr = np.ones(1_000_000, dtype=np.float64)
print(f"buffer: {arr.nbytes:>12,} bytes")   # 8,000,000
print(f"dtype:  {arr.dtype}")                # float64
print(f"per element: {arr.itemsize} bytes")  # 8
```

`arr.nbytes` is the honest measure: the buffer size, nothing else. Microsoft Learn's "Explore and Analyze Data with Python" module frames exactly this distinction when it introduces NumPy for numerical work, noting that operations on typed arrays execute far more efficiently than operations on Python sequences ([learn.microsoft.com/training/modules/explore-analyze-data-with-python](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/)).

The dtype choice multiplies this: `float32` halves the buffer to 4 MB; `float16` halves it again to 2 MB. The list gives you no such lever.

## Why AI Work Compounds This

An embedding vector with 1,536 dimensions stored as a Python list of floats is 1,536 heap allocations per vector. A batch of 512 such vectors is 786,432 heap objects, each individually reference-counted. Cosine similarity computed element-by-element in Python loops is not just slow; it is slow in a way that scales with batch size. Production AI systems use NumPy arrays (or tensors backed by the same contiguous-buffer design) for exactly this reason: the bottleneck in any numerical workload is memory bandwidth, and lists spend that bandwidth on bookkeeping, not on data.

## When Lists Are Still Correct

The object model is not the enemy in every situation. A list of file paths, a queue of config records, a mixed container of strings and integers: these are correct as Python lists. The boundary is precise: when the container holds fixed-type numerical data that will be operated on mathematically, the list pays a cost that compounds with scale. When the container is heterogeneous, small, or not numerically operated on, the list is the right tool.

Knowing the boundary is the skill. Measuring it is how you confirm you are on the right side of it.

## Core Concepts

- Every Python value is a `PyObject` carrying a type pointer, a reference count, and a value; a float is 24 bytes, not 4, and a list of floats is 4x heavier than a contiguous array because each element is a separate heap allocation.
- A Python list stores pointers to boxed objects, not the objects themselves; accessing any element requires two memory reads, not one.
- `sys.getsizeof` measures the container header only; the true memory cost of a list of numbers requires following each pointer, while `ndarray.nbytes` gives the honest buffer size directly.
- The list-vs-array choice is a boundary decision: fixed-type numerical data belongs in NumPy; heterogeneous or non-numerical data belongs in Python containers.

<div class="claude-handoff" data-exercise="exercises/module1/the-cost-of-a-python-list/">

**Build It in Claude Code**: Build `measure.py`, a reusable benchmark helper that measures true list memory, array buffer size, and operation timing, then run it on 1M floats and confirm the ratio.

</div>
