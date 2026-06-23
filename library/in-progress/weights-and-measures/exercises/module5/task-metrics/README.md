# Exercise: Task Metrics

## Goal

Write at least ten test cases for each of the three task metrics in `eval_gate.py` and
confirm every assertion passes.

## Why

Reading the metric formulas is not the same as knowing what they do at their boundaries.
The edge cases in exact match (trailing punctuation, internal whitespace) and token F1
(repeated tokens, one empty) are where bugs hide. Writing the cases forces each boundary
into code before it can surprise you in a real eval run.

## What You Are Building

A test suite script that imports the metric functions from `eval_gate.py` and asserts
expected values across boundary cases.

## Steps

1. Import from the spine:

   ```python
   import sys
   sys.path.insert(0, "exercises/spine")
   from eval_gate import exact_match, token_f1, perplexity_from_nll, normalise_perplexity
   ```

2. Write at least ten test cases for `exact_match`. Required cases:
   - Identical strings: score 1.0
   - Case difference only: score 1.0
   - Trailing period on one side: score 1.0
   - Leading/trailing whitespace on one side: score 1.0
   - Extra word on one side: score 0.0
   - Completely different strings: score 0.0
   - Both empty strings: score 1.0
   - Empty vs non-empty: score 0.0
   - Multi-word exact match: score 1.0
   - Punctuation mid-string (not trailing): score depends on normalization

3. Write at least ten test cases for `token_f1`. Required cases:
   - Perfect match: score 1.0
   - Both empty: score 1.0
   - Pred empty, ref non-empty: score 0.0
   - Ref empty, pred non-empty: score 0.0
   - One common token out of two: score < 1.0, verify manually
   - Known 3-vs-2 token overlap (the cat sat / the cat): expected 0.8
   - Repeated token in pred not in ref: should not double-count
   - No overlap at all: score 0.0
   - High overlap but not perfect: score in (0.8, 1.0)
   - Case difference only: score 1.0 (normalize applies)

4. Write at least five test cases for `perplexity_from_nll` and `normalise_perplexity`:
   - `nll=[0.0], tc=[1]`: ppl should be `exp(0) = 1.0`
   - `nll=[1.0], tc=[1]`: ppl should be `exp(1) = e`
   - `nll=[2.0], tc=[2]`: ppl should be `exp(1) = e`
   - `ppl=1.0`: normalised to 1.0
   - `ppl=e`: normalised to approximately 0.5 (within 1e-9)

5. For each assertion, use `abs(result - expected) < 1e-9` for float comparisons.
   Print `[PASS]` or `[FAIL]` for each case and a final `OK` or `BROKEN` count.

## Pass Condition

- All ten-plus exact match cases pass
- All ten-plus token F1 cases pass
- All five perplexity cases pass
- The script exits 0

## Done When

All cases pass and the script exits 0.

## Estimated Time

45 to 60 minutes.

## Stretch

Write a case where the prediction contains repeated tokens that the reference has only
once. Manually compute the multiset intersection and verify that `token_f1` returns the
expected value. Confirm that removing the repeated token from the prediction changes
the score, and explain in a comment why the change happens.
