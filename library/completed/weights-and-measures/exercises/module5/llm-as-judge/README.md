# Exercise: LLM-as-Judge

## Goal

Write ten (prediction, reference) pairs that span all five mock judge score levels,
assert each pair scores as expected, and build a `classify_by_criteria` function that
returns scores per criterion.

## Why

The judge is the qualitative signal in the eval gate. Understanding when the mock judge
assigns each score, and what that score means in terms of lexical overlap, makes the
aggregate meaningful rather than opaque. Building the criterion classifier makes the rubric
structure explicit in code.

## What You Are Building

A script with ten test pairs, per-pair assertions, a criterion classifier, and a printed
table of results.

## Steps

1. Import from the spine:

   ```python
   import sys
   sys.path.insert(0, "exercises/spine")
   from eval_gate import mock_judge
   ```

2. Define ten (pred, ref) pairs targeting each score level. Required distribution:
   - Two pairs that score 1.0 (exact match after normalization)
   - Two pairs that score 0.8 (token F1 >= 0.8 but not exact match)
   - Two pairs that score 0.6 (token F1 >= 0.5 but < 0.8)
   - Two pairs that score 0.4 (token F1 >= 0.2 but < 0.5)
   - Two pairs that score 0.2 (token F1 < 0.2)

3. Assert each pair's `mock_judge` output matches the expected score within 1e-9.
   Print `[PASS]` or `[FAIL]` for each.

4. Write `classify_by_criteria(pred, ref) -> dict[str, float]` that returns:

   ```python
   {
       "relevance":   mock_judge(pred, ref),
       "correctness": mock_judge(pred, ref),
       "helpfulness": mock_judge(pred, ref),
   }
   ```

   All three criteria map to the same mock score because the mock does not distinguish
   criteria. This is the correct behavior for a mock judge; a real judge would call the
   API separately per criterion.

5. Print a results table:

   ```
   #   Expected   Got    Relevance  Correctness  Helpfulness  PASS/FAIL
   1   1.000      1.000  1.000      1.000        1.000        PASS
   ...
   ```

## Pass Condition

- All ten assertions pass
- `classify_by_criteria` returns a dict with exactly three keys
- The table prints without error
- The script exits 0

## Done When

All pass conditions are met.

## Estimated Time

30 to 45 minutes.

## Stretch

Write three pairs that are semantically correct paraphrases with low lexical overlap
(the prediction uses synonyms or reordered phrasing to express the same meaning as the
reference). Note which score level the mock judge assigns and add a comment explaining
why the mock judge would under-score a real judge on these cases. This is the documented
limitation of mock-judge-as-proxy for qualitative correctness.
