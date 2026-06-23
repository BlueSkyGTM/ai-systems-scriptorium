# Exercise: Building the Eval Gate (Capstone)

## Goal

Run `eval_gate.py`'s gate on two sets of predictions (high quality and low quality),
confirm the gate promotes the better model and blocks the worse one, and verify the
selftest exits 0.

## Why

The gate is only correct if it promotes the model that actually scores higher and blocks
the one that scores lower. Writing both orderings and confirming the gate gets both right
proves the gate logic is working, not just that it returns True for one particular input.
This is the same "PASS and FAIL must both be tested" discipline the book applies to every
validator.

## What You Are Building

A script that creates two prediction sets, runs the gate in both directions, and asserts
the correct outcome each time.

## Steps

1. Import from the spine:

   ```python
   import sys
   sys.path.insert(0, "exercises/spine")
   from eval_gate import run_eval, eval_gate, mean_aggregate, EvalResult
   ```

2. Create ten high-quality (pred, ref) pairs where predictions closely match references.
   At least four should be exact matches; the rest should have token F1 > 0.7.

3. Create ten low-quality (pred, ref) pairs using the same references but poor predictions.
   At least four should have no token overlap; the rest should have token F1 < 0.3.

4. Run `run_eval` on both sets:

   ```python
   tuned = run_eval(high_quality_pairs)
   base  = run_eval(low_quality_pairs)
   ```

5. Print a per-example table for the tuned set showing EM, F1, judge, and aggregate.

6. Print both mean aggregates and the gate result:

   ```
   tuned mean aggregate : 0.xxxx
   base  mean aggregate : 0.xxxx
   gate result          : PASS -- promote checkpoint
   ```

7. Assert `eval_gate(tuned, base, margin=0.01)` returns `True` (PASS).

8. Assert `eval_gate(base, tuned, margin=0.0)` returns `False` (BLOCK). Use `margin=0.0`
   so the gate blocks even a small regression.

9. Run the selftest:

   ```
   python exercises/spine/eval_gate.py --selftest
   ```

   Confirm it prints `selftest: OK` and exits 0 before reporting the exercise complete.

## Pass Condition

- Tuned vs base gate returns `True` (PASS)
- Base vs tuned gate returns `False` (BLOCK)
- `eval_gate.py --selftest` exits 0
- Both mean aggregates print correctly

## Done When

All four pass conditions are met. Keep the high-quality pair set: M6 uses the same
held-out evaluation pattern to gate the classifier artifact.

## Estimated Time

45 to 60 minutes.

## Stretch

Add perplexity to the evaluation by providing fake `neg_log_probs` and `token_counts`
to `run_eval`. Use lower NLL values for the high-quality set (better perplexity) and
higher NLL values for the low-quality set. Confirm the perplexity column appears in the
results and the gate still returns the correct outcomes. This is the full four-metric
aggregate the production gate uses.
