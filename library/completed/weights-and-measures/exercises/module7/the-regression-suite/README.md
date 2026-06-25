# Exercise: The Regression Suite

## Goal

Write `regress.py` so it gates the adapter: PASS only if the tuned model regresses nothing
and improves at least one behavior.

## Why

Instruction-tuning that adds a skill but quietly breaks another is worse than no tuning,
because the damage is invisible until production. The regression suite is the test that
makes "did not break anything" a falsifiable, exit-coded claim.

## What You Are Building

A `regress.py` with a behaviour suite mixing the new skill and the old skills, a paired
base-vs-tuned scorer, and a two-clause gate.

## Steps

1. Define `SUITE`: a list of `(verb, name, expected_response)`. Include `greet` cases (the
   new skill) and `thank`/`bye` cases (the old skills), on held-out names.

2. Write `score(model, suite)`: 1 if the greedy-decoded response exactly matches the
   expected string, else 0.

3. In `evaluate()`, score both the base and the tuned model. Compute:
   - regressions: any case where `tuned < base`,
   - improvements: cases where `tuned > base`.

4. Gate: `passed = (no regressions) and (improvements > 0)`. Return exit 0 on PASS, 1 on
   BLOCK.

5. Make MLflow logging optional behind `--no-mlflow`.

6. Verify by hand: `python regress.py` then `echo $?` on a trained adapter prints 0.
