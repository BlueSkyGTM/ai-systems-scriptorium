# Exercise: Loss Is Not Enough

## Goal

Write a loss-curve analyzer that detects three failure modes from epoch history and
confirms each with a deterministic selftest.

## Why

Reading loss curves is a skill, but a loop that manually scans numbers is not a skill
you can automate. Encoding the failure modes as functions makes the diagnosis reproducible
and catchable by CI. The same rubric-in-code move the book applies to data quality and
loop structure applies here to training health.

## What You Are Building

A Python script with three detector functions (one per failure mode) and a `--selftest`
that plants each failure mode and asserts the detector catches it.

## Steps

1. Define the input type: a list of `(train_loss, val_loss)` tuples, one per epoch,
   in chronological order.

2. Write `detect_stalled(history) -> bool`: returns True if `val_loss` at the final epoch
   is not lower than `val_loss` at epoch 1. A model that never improved validation loss
   from its starting point has stalled.

3. Write `detect_overfit(history) -> bool`: returns True if there exists an epoch at which
   `val_loss` is at a minimum, followed by three consecutive epochs where `val_loss`
   increases. The three-epoch window matches the `patience=3` default in the M2 `fit()`
   function.

4. Write `detect_divergence(history) -> bool`: returns True if `train_loss` and `val_loss`
   both increase for two consecutive epochs at any point in the history.

5. Write a `--selftest`:

   ```python
   # stalled: val_loss never drops
   stalled_history = [(1.0, 1.5), (0.9, 1.5), (0.8, 1.5), (0.7, 1.6)]
   assert detect_stalled(stalled_history)
   assert not detect_stalled([(1.0, 1.5), (0.9, 1.2)])

   # overfit: val improves then rises for 3 consecutive epochs
   overfit_history = [(1.0, 1.5), (0.8, 1.2), (0.6, 1.0), (0.5, 1.1), (0.4, 1.2), (0.3, 1.3)]
   assert detect_overfit(overfit_history)

   # divergence: both train and val rise together
   diverge_history = [(0.5, 0.9), (0.4, 0.8), (0.6, 1.1), (0.7, 1.3)]
   assert detect_divergence(diverge_history)
   ```

   Print `[PASS]` or `[FAIL]` for each case and `selftest: OK` or `selftest: BROKEN` at the end.

## Pass Condition

- `detect_stalled` returns True on the stalled case and False on a healthy case
- `detect_overfit` returns True on the overfit case
- `detect_divergence` returns True on the divergence case
- `--selftest` prints `selftest: OK` and exits 0

## Done When

All four pass conditions are met.

## Estimated Time

30 to 45 minutes.

## Stretch

Add a `diagnose(history) -> list[str]` function that returns a list of all failure mode
names detected: `["stalled"]`, `["overfit"]`, `["divergence"]`, or any combination. An
empty list means the history looks healthy. Test it on a history that triggers both
`stalled` and `divergence` and confirm both names appear in the output.
