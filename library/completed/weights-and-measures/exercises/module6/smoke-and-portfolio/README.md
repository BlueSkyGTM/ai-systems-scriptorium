# Exercise: Smoke and Portfolio

## Goal

Write `smoke.py` so it proves both directions of the gate, then fill in the portfolio
write-up after the first green run.

## Why

A smoke test that only checks the happy path proves nothing about the gate. The
load-bearing assertion is the negative case: an untrained model must BLOCK. The write-up
is the translation of that proof for an interviewer, and it is evidence only after the
run is green.

## What You Are Building

A `smoke.py` that trains on a small fixture, asserts the trained model PASSES, asserts an
untrained model BLOCKS, and exits 0 only if every assertion holds; plus a completed
`outputs/skill-classifier.md`.

## Steps

1. Train on a small fixture in-process (for example 300 train / 120 test) and assert the
   checkpoint exists and carries all five contract keys.

2. Call the gate on the trained checkpoint. Assert `passed is True` and both margins clear
   5 percentage points.

3. Build an **untrained** model with the same config, save it as a checkpoint, and run the
   gate on it. Assert `passed is False` and that `eval.py` exits 1 on it.

4. Count assertions and print a PASS summary. Exit 0 only if there are zero failures.

5. Run both layers together:

   ```bash
   python smoke.py && python -m pytest tests/ -q
   ```

6. After the run is green, fill in every `[TODO]` in `outputs/skill-classifier.md` with
   your real numbers. The write-up is evidence, not aspiration.
