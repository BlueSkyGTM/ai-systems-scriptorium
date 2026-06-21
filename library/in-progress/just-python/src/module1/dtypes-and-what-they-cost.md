# Dtypes and What They Cost

Every NumPy array has a dtype, and if you did not choose it, NumPy chose for you: probably `float64`. That default costs twice the memory of `float32` for no precision gain you will ever see from a model output.

## The dtype Contract

A dtype is a fixed-size C type. It tells NumPy two things: how many bytes each slot in the buffer occupies, and how to interpret those bytes. Every element in the array shares the same dtype; there is no boxing, no per-element overhead. That uniformity is where the speed comes from.

```python
import numpy as np

scores = np.array([0.91, 0.74, 0.88, 0.62], dtype=np.float64)
print(scores.dtype)     # float64
print(scores.itemsize)  # 8  (bytes per element)
print(scores.nbytes)    # 32 (total bytes)
```

`arr.dtype` always tells you what you have. `arr.itemsize` tells you the per-element cost. `arr.nbytes` tells you the bill.

## The AI-Relevant Types

Five dtypes cover almost every AI pipeline:

| dtype | Bytes | When you use it |
|-------|-------|-----------------|
| `float64` | 8 | NumPy default; computation, intermediate results |
| `float32` | 4 | Model output embeddings; halves memory vs float64 |
| `int64` | 8 | Label arrays, index arrays |
| `int32` | 4 | Compact labels when the count fits in 32 bits |
| `bool` | 1 | Mask arrays; boolean indexing |

The decision that matters most in practice is `float64` versus `float32`. Most embedding models emit `float32` vectors. Azure AI Search documents this directly: `Float32` (32-bit floating point) is the default vector field data type for Azure AI Search indexes because "most embedding models emit vectors as `Float32`," while choosing `Float16` "often leads to faster query times and reduced memory footprint" at the cost of some precision. ([Microsoft Learn: Supported data types, Azure AI Search](https://learn.microsoft.com/rest/api/searchservice/supported-data-types#edm-data-types-for-vector-fields))

Loading those `float32` embeddings into a `float64` array doubles your memory silently. At 1,536 dimensions and one million rows, that is the difference between 6 GB and 12 GB.

## astype Versus view

Two operations change what dtype label an array carries. Only one of them is safe for type conversion.

**`astype`** converts values. It reads each element, converts it to the target type, and writes it into a new buffer. The result is a separate array with correct values.

```python
embeddings_f64 = np.random.rand(1000, 1536)   # float64, 8 bytes/element
embeddings_f32 = embeddings_f64.astype(np.float32)

print(embeddings_f64.nbytes)  # 12,288,000
print(embeddings_f32.nbytes)  #  6,144,000  -- new buffer, half the size
```

**`view`** reinterprets bytes. It does not convert values; it reads the same bytes through a different lens. Viewing 8-byte `float64` slots as 4-byte `float32` slots does not halve your values: it reads each 8-byte block as two 4-byte floats and returns garbage.

```python
trap = embeddings_f64[0].view(np.float32)
# trap has 2 * 1536 = 3072 elements, all meaningless
# it shares the buffer -- no copy occurred, no conversion occurred
print(np.shares_memory(embeddings_f64, trap))  # True
```

The trap is real. `arr.view(np.float32)` will not raise an error; it silently gives you wrong data. Reach for `view` only when you intend raw byte reinterpretation, which in AI pipelines is almost never.

## The float32 Decision

When a model hands you embeddings, read the dtype before assuming:

```python
# Simulate receiving embeddings from a model
model_output = np.random.rand(512, 1536).astype(np.float32)

# Check what you have
print(model_output.dtype)   # float32
print(model_output.nbytes)  # 3,145,728

# If you had loaded into float64 by accident:
bloated = model_output.astype(np.float64)
print(bloated.nbytes)       # 6,291,456 -- doubled for nothing
```

The fix is one line: `arr.astype(np.float32)`. The cost of not fixing it scales with every row in your corpus.

## Core Concepts

- A dtype is a fixed-size C type specifying bytes-per-slot and how those bytes are interpreted; every element in an array shares it, which is why NumPy is fast.
- `astype` converts values into a new buffer; `view` reinterprets the existing bytes without converting them: using `view` as a type conversion yields garbage.
- Most embedding models emit `float32`; loading their output into a `float64` array doubles memory silently and wastes the budget before any computation begins.
- `arr.dtype`, `arr.itemsize`, and `arr.nbytes` are the three numbers to read before operating on any array you did not create yourself.

<div class="claude-handoff" data-exercise="exercises/module1/dtypes-and-what-they-cost/">

**Build It in Claude Code:** build a dtype audit script that measures the real memory cost of float64 vs float32 embeddings and proves the view trap produces garbage.

</div>
