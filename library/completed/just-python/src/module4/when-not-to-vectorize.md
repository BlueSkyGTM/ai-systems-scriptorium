# When Not to Vectorize

Vectorizing blindly trades a slow job for one that crashes the box. The `(N, D)` broadcast you learned in M2 is lazy until arithmetic forces it; the moment it materializes, it lands as `N * D * itemsize` bytes in RAM, all at once, no warning.

## The Memory Blowup Case

M2 showed that `np.broadcast_to` returns a zero-stride view with no new allocation. The cost arrives when you subtract, add, or multiply: NumPy writes the full output buffer. For embeddings, that is immediate.

```python
import numpy as np
from measure import broadcast_allocates   # import path set up in the M4 exercise

# 50 000 embeddings, 1 536 dimensions, float32
N, D = 50_000, 1_536
mean = np.zeros((1, D), dtype=np.float32)

stats = broadcast_allocates(mean, (N, D))

print(f"source (mean row):    {stats['source_bytes']:>14,} bytes")
print(f"view (lazy):          {stats['view_bytes']:>14,} bytes")
print(f"result (materialized):{stats['result_bytes']:>14,} bytes")
print(f"view still lazy?      {bool(stats['view_shares'])}")
```

Expected output on any platform:

```
source (mean row):              6,144 bytes
view (lazy):            307,200,000 bytes
result (materialized):  307,200,000 bytes
view still lazy?      True
```

307 MB for one subtraction step. A batch of 50 000 embeddings is not exotic; Azure Machine Learning's own scoring guidance warns that "whether or not you can load the entire mini-batch in memory depends on the size of the mini-batch" and that out-of-memory exceptions are a routine design constraint in production inference pipelines ([learn.microsoft.com/azure/machine-learning/how-to-batch-scoring-script](https://learn.microsoft.com/azure/machine-learning/how-to-batch-scoring-script?view=azureml-api-2#best-practices-for-writing-scoring-scripts)). The materialization is not a bug; it is how array arithmetic works. The discipline is knowing it is coming before you commit to the shape.

## The Readability Cost

Memory is one cost. The second is maintenance. Consider centering embeddings in two ways:

```python
# Version A: loop
def center_loop(embeddings: np.ndarray) -> np.ndarray:
    mean = embeddings.mean(axis=0)
    result = np.empty_like(embeddings)
    for i in range(len(embeddings)):
        result[i] = embeddings[i] - mean
    return result

# Version B: one-liner vectorized
def center_vec(embeddings: np.ndarray) -> np.ndarray:
    return embeddings - embeddings.mean(axis=0)
```

Version B is the right call here: it is faster, it fits in memory at normal batch sizes, and any NumPy practitioner reads it at a glance. Now consider a more elaborate version that a deadline-rushed engineer might write:

```python
# Version C: clever, but opaque
def center_weird(e):
    return e - e[np.arange(len(e))].mean(0)[None]
```

The `[np.arange(len(e))]` is a no-op index that copies the array, paying full allocation twice. The `[None]` inserts a size-1 axis to broadcast the mean. It produces the correct answer, passes tests, and will cost the next reader ten minutes to verify. Clever is not the same as clear. When a vectorized expression requires a comment longer than the line itself, the loop version is not the slower option; it is the cheaper one.

## The Chunking Alternative

When the full vectorized form blows the memory budget, the fix is to process the data in slices instead of refusing to vectorize at all.

```python
def center_chunked(
    embeddings: np.ndarray,
    chunk_size: int = 5_000,
) -> np.ndarray:
    """Center embeddings in chunks to cap peak memory at chunk_size * D * itemsize."""
    mean = embeddings.mean(axis=0)           # shape (D,) -- cheap, stays small
    result = np.empty_like(embeddings)
    for start in range(0, len(embeddings), chunk_size):
        end = min(start + chunk_size, len(embeddings))
        result[start:end] = embeddings[start:end] - mean  # one chunk at a time
    return result
```

With `chunk_size=5_000` and `D=1_536` float32, each loop iteration peaks at 30 MB instead of 307 MB. The loop is not a retreat; it is a budget control. The vectorized arithmetic inside each slice still runs at C speed.

## The Decision Rule

Three costs, measured before you choose:

| Cost | Measure it with | Acceptable threshold |
|------|----------------|----------------------|
| Speed | `time_sum` from `measure.py` | Is it faster than the loop? |
| Memory | `broadcast_allocates` from `measure.py` | Does the materialized buffer fit your budget? |
| Clarity | Can the next reader understand it in 30 seconds? | If not, the loop is the default. |

Vectorize when it is faster, fits in memory, and stays readable. Keep the loop when it does not. Chunk when it would fit in pieces but not whole. The decision is not "is there a one-liner?"; it is "what is the cheapest way to get a correct result on production hardware with a budget?"

## Core Concepts

- A broadcast that materializes a large intermediate allocates `N * D * itemsize` bytes at the moment of arithmetic, not lazily; `broadcast_allocates` from `measure.py` makes that cost visible before it becomes a crash.
- A vectorized expression is only superior when it wins on all three axes: speed, memory, and readability; winning on one while losing the other two is a bad trade.
- Chunking is not a fallback to loops: it applies vectorized arithmetic one slice at a time, keeping peak memory bounded without sacrificing C-speed element operations.
- The decision rule is a three-way check, not a reflex: measure speed with `time_sum`, measure memory with `broadcast_allocates`, and ask whether the next reader can verify the expression in 30 seconds cold.

<div class="claude-handoff" data-exercise="exercises/module4/when-not-to-vectorize/">

**Build It in Claude Code:** Extend `vectorization_report.py` with a memory check that imports `broadcast_allocates` and `time_sum` from the M1 `measure.py`, runs both fixtures (one where vectorizing wins, one where it OOMs), and prints a final "vectorize / keep the loop / chunk it" recommendation with the numbers behind it.

</div>
