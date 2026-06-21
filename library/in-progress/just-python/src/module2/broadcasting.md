# Broadcasting

Subtracting the per-feature mean from a 512x1536 embedding matrix takes one line in NumPy, no loop, no copy of the mean array. That is broadcasting: NumPy aligns trailing dimensions, expands size-1 axes conceptually, and performs the arithmetic in C. Knowing the rule is the difference between writing that line with confidence and puzzling over a `ValueError` at 2 AM.

## The Alignment Rule

NumPy compares two arrays' shapes from the right (trailing dimensions) and works left. At each position, the dimensions are compatible when they are equal or one of them is 1. If an array has fewer dimensions than the other, NumPy pads its shape with 1s on the left until the ranks match.

```python
import numpy as np

embeddings = np.random.randn(512, 1536).astype(np.float32)  # shape (512, 1536)
mean       = np.mean(embeddings, axis=0)                    # shape (1536,)

# alignment check:
#   embeddings:  512 x 1536
#   mean:              1536   <- NumPy pads left: becomes (1, 1536)
#   result:      512 x 1536

centered = embeddings - mean   # one line, no loop

print(embeddings.shape)   # (512, 1536)
print(mean.shape)         # (1536,)
print(centered.shape)     # (512, 1536)
```

The 1536 trailing dimensions match, so the subtraction broadcasts the `(1536,)` mean across all 512 rows. The result is a new `(512, 1536)` array.

Microsoft Learn's "Explore and Analyze Data with Python" module introduces these vectorized array operations as the standard way to process numerical data with NumPy ([learn.microsoft.com/training/modules/explore-analyze-data-with-python](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas)).

## The Size-1 Axis

Sometimes you want to broadcast across *columns* rather than rows. The shape `(512, 1)` broadcasts across all 1536 columns of a `(512, 1536)` array, because the trailing `1` expands to match `1536`.

```python
row_max = np.max(embeddings, axis=1, keepdims=True)  # shape (512, 1)

# alignment check:
#   embeddings:  512 x 1536
#   row_max:     512 x 1       <- the 1 expands to 1536
#   result:      512 x 1536

scaled = embeddings / row_max

print(row_max.shape)   # (512, 1)
print(scaled.shape)    # (512, 1536)
```

`keepdims=True` is the lever here: it preserves the axis that `max` collapsed, delivering shape `(512, 1)` instead of `(512,)`. A `(512,)` mean would not broadcast correctly against `(512, 1536)` because the trailing dimensions would be `1536` vs `512`.

When `keepdims` is not available (for example, on an intermediate array you computed earlier), reshape to insert the size-1 axis:

```python
norms = np.linalg.norm(embeddings, axis=1)         # shape (512,)
norms_col = norms.reshape(512, 1)                   # shape (512, 1)
# equivalently:
norms_col = norms[:, np.newaxis]                    # shape (512, 1)

unit = embeddings / norms_col                       # (512, 1536) / (512, 1)
print(unit.shape)                                   # (512, 1536)
```

`np.newaxis` is just `None`; it inserts a length-1 axis at the chosen position. Use it whenever you need to promote a 1-D array into a column vector for row-wise broadcast. Reshaping a 1-D reduction to `(N, 1)` before dividing an `(N, D)` matrix is the standard normalization move you will reach for constantly.

## Lazy View vs. Materialized Buffer

Broadcasting does not allocate memory for the expanded shape until an arithmetic operation forces it. You can inspect this with `np.broadcast_to`:

```python
mean_row = mean[np.newaxis, :]               # shape (1, 1536)
view = np.broadcast_to(mean_row, (512, 1536))  # shape (512, 1536): no copy

print(view.shape)                            # (512, 1536)
print(view.nbytes)                           # 3,145,728 -- the logical size it reports
print(view.base.nbytes)                      # 6,144 -- the actual backing buffer
print(np.shares_memory(view, mean))          # True

# Arithmetic forces materialization:
result = view + 0.0                          # new buffer allocated

print(result.nbytes)                         # 3,145,728 bytes (512 * 1536 * 4)
print(np.shares_memory(result, mean))        # False
```

`view.nbytes` reports the logical size of the broadcast shape, 3,145,728 bytes, but no buffer of that size exists yet: `np.broadcast_to` returns a read-only view with zero-strides on the broadcast axes, and the real backing memory is still the `(1, 1536)` source at 6,144 bytes (`view.base.nbytes`). `np.shares_memory(view, mean)` returning `True` is the proof. The moment you write `embeddings - mean`, NumPy allocates the full `(512, 1536)` output buffer. M1's strides lesson established how zero-strides achieve this without a copy; the key thing to carry here is *when* the materialization happens, and that it scales with output size.

## When Broadcasting Fails

If the trailing dimensions are neither equal nor 1, NumPy raises `ValueError`:

```python
a = np.zeros((512, 1536))
b = np.zeros((512,))       # trailing dim is 512, not 1536 or 1

try:
    _ = a - b
except ValueError as e:
    print(e)
    # operands could not be broadcast together with shapes (512,1536) (512,)
```

The fix is always the same: decide which axis `b` represents and reshape or add a new axis to make the trailing dimensions line up. A `(512,)` row-wise bias becomes `(512, 1)` via `b[:, np.newaxis]`.

## Core Concepts

- Broadcasting aligns shapes from the right (trailing dimension first); NumPy pads the shorter shape with 1s on the left, then checks: each pair of dimensions must be equal or one must be 1.
- A size-1 axis on either array expands to match the other; use `keepdims=True` on reductions, or `[:, np.newaxis]` / `reshape`, to place that axis correctly before broadcasting.
- `np.broadcast_to` returns a read-only zero-stride view with no new allocation; an arithmetic operation (subtraction, division) forces materialization of the full output buffer.
- Broadcasting fails with `ValueError` when trailing dimensions are neither equal nor 1; the fix is always to reshape one operand so its dimensions align.

<div class="claude-handoff" data-exercise="exercises/module2/broadcasting/">

**Try It in Claude Code:** Add `broadcast_allocates` to your existing `measure.py` to prove that a broadcast view is near-zero bytes until an arithmetic op forces the full buffer.

</div>
