# Exercise: The Pipeline Artifact

## Goal

Stand up `module8-pipeline/` with its vendored `lib/` and confirm the five modules import
cleanly before you write the conductor.

## Why

Composition only works if the pieces agree on a contract. The fastest way to find a broken
seam is to vendor the five modules and import them; a mismatch surfaces at import time, not
in production.

## What You Are Building

The directory layout, the vendored `lib/` with all five modules, and the `VENDORED`
registry in `lib/__init__.py`.

## Steps

1. Create `pipeline.py`, `rubric.py`, `smoke.py`, `tests/`, `outputs/`, and `lib/`.

2. Vendor the five modules into `lib/`, copied read-only from their source modules:
   `m3_curate`, `m4_tune`, `m6_train`, `m5_eval`, `m7_regress`.

3. Record the registry in `lib/__init__.py`:

   ```python
   VENDORED = ("m3_curate", "m4_tune", "m6_train", "m5_eval", "m7_regress")
   ```

4. Confirm each vendored module imports without error (add `lib/` to `sys.path` first).

5. Resist editing the vendored code. If a contract is wrong, fix it upstream and re-vendor.
