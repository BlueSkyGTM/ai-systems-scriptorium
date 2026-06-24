# Exercise: Smoke and Portfolio

## Goal

Write `smoke.py` so it proves the gate works in both directions, then complete the skill
card after the first green run.

## Why

A regression suite you never see fail is a rumor. The smoke test's job is to corrupt the
adapter on purpose and confirm the gate catches it; that negative case is what makes a
green run evidence rather than decoration.

## What You Are Building

A `smoke.py` that tunes, confirms PASS on the real adapter, confirms BLOCK on a random
adapter, restores the real one, and a completed `outputs/skill-instruct.md`.

## Steps

1. Run `tune.py` (in-process or as a subprocess). Assert `base.pt` and the adapter exist,
   and that the adapter is a small fraction of the model.

2. Call the regression evaluation. Assert the tuned model passes every case, improves on
   the base, and the gate result is PASS.

3. Run `regress.py` as a subprocess on the real adapter; assert exit 0.

4. Back up the adapter, overwrite it with `torch.randn_like` tensors of the same shape, run
   `regress.py` again, and assert exit 1. Restore the real adapter and confirm it is intact.

5. Count assertions, print a PASS summary, exit 0 only if there are zero failures.

6. After the run is green, fill in `outputs/skill-instruct.md`: the three skills, the
   regression cases, and the negative-control proof.
