# Exercise: Type Hints

**Goal:** Write a self-contained script, `type_hints_check.py`, with three fully annotated functions and a runtime proof that the annotations exist. The script exits 0 when every assertion passes.

**Why:** A clean annotation layer plus a green mypy run is a production signal that reviewers look for. Writing it from scratch once makes you fast at it in an interview.

## Steps

1. Create `exercises/module5/type-hints/type_hints_check.py`. This is a new file; there is no throughline artifact to extend here.

2. Implement three functions with complete type annotations:

   **Function 1** returns `list[float]`. Normalize a list of scores so they sum to 1.0:

   ```python
   def normalize(scores: list[float]) -> list[float]:
       ...
   ```

   **Function 2** takes an `Optional` parameter (use `int | None`). Return the top-k scores, or all scores if `k` is `None`:

   ```python
   def top_k(scores: list[float], k: int | None = None) -> list[float]:
       ...
   ```

   **Function 3** takes a `Callable`. Apply a transform to every score in a list:

   ```python
   from typing import Callable

   def apply_transform(
       scores: list[float],
       transform: Callable[[float], float],
   ) -> list[float]:
       ...
   ```

3. Add a runtime check block. Use `typing.get_type_hints()` on one function and assert the expected annotation keys are present:

   ```python
   import typing

   hints = typing.get_type_hints(normalize)
   assert "scores" in hints, "normalize must annotate 'scores'"
   assert "return" in hints, "normalize must annotate return type"
   print(f"normalize annotations: {hints}")
   ```

4. Add behavioral assertions that exercise all three functions:

   ```python
   # normalize: output sums to 1.0
   normed = normalize([1.0, 3.0, 6.0])
   assert abs(sum(normed) - 1.0) < 1e-9, f"normalized scores must sum to 1.0, got {sum(normed)}"

   # top_k with k=2: returns 2 highest
   top = top_k([0.1, 0.5, 0.3, 0.9], k=2)
   assert len(top) == 2, f"expected 2 scores, got {len(top)}"
   assert top[0] >= top[1], "top_k must return scores in descending order"

   # top_k with k=None: returns all scores
   all_scores = top_k([0.1, 0.5, 0.3], k=None)
   assert len(all_scores) == 3, "top_k with k=None must return all scores"

   # apply_transform: scales every score
   scaled = apply_transform([0.2, 0.4, 0.8], lambda x: x * 2)
   assert scaled == [0.4, 0.8, 1.6], f"unexpected scaled output: {scaled}"

   print("all assertions passed")
   ```

5. Run the script:

   ```
   python type_hints_check.py
   ```

   Expected output (exact order may vary):

   ```
   normalize annotations: {'scores': list[float], 'return': list[float]}
   all assertions passed
   ```

## Done When

`python type_hints_check.py` exits 0, prints the annotation dict for `normalize`, reaches `all assertions passed`, and all four behavioral assertions pass. Standard library only (`typing` module). No random seed; all inputs are deterministic.

## Stretch: Protocol

Add a `Scorer` Protocol and a `rank_texts` function that uses it:

```python
from typing import Protocol

class Scorer(Protocol):
    def score(self, text: str) -> float:
        ...

def rank_texts(texts: list[str], scorer: Scorer) -> list[str]:
    return sorted(texts, key=scorer.score, reverse=True)
```

Write a concrete `LengthScorer` class that implements `score` without inheriting from `Scorer`. Instantiate it, call `rank_texts`, and assert the texts come back longest-first. Then call `isinstance(LengthScorer(), Scorer)` and note the result: structural typing does not guarantee `isinstance` returns `True` without `runtime_checkable`; add `@typing.runtime_checkable` to `Scorer` if you want the check to pass. Print the result either way.

```python
assert rank_texts(["hi", "hello", "hey there"], LengthScorer())[0] == "hey there"
print("stretch: Protocol assertion passed")
```

## mypy Readiness

This script is written to be mypy-clean. To verify (optional, requires `pip install mypy`):

```
mypy type_hints_check.py
```

A clean run with no errors confirms the annotations are consistent with how the functions are called. The exercise passes without mypy installed; the behavioral assertions cover the same contract from the runtime side.
