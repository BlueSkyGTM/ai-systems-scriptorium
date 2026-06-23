# Exercise: Building the Curation Gate (Capstone)

## Goal

Run `curate.py` on a raw JSONL file to produce clean train and val splits plus a manifest. Run
`check_dataset.py` on each output and `--check-leak` across them. All gates must exit 0. The
manifest is your proof of delivery.

## Why

The curation gate is the promise you make to M4. The fine-tune build in the next module will
consume `train.jsonl` and `val.jsonl` without re-validating them: it trusts the gate upstream.
If that gate is a checklist you ran by eye, the trust is unfounded. If it is a script that exits
0, the trust has a machine behind it. That is the "rubric in code" move this book has applied to
every deliverable: not "I checked" but "the checker passed." This capstone makes you run the
full pipeline, confirms every gate exits 0, and keeps the manifest as the auditable record.

## What You Are Building

A raw JSONL file with enough variety to produce a meaningful split, and the clean output
artifacts that prove the pipeline ran correctly.

## Steps

1. Create `exercises/module3/building-the-curation-gate/raw.jsonl` with at least 15 examples.
   Include at least one invalid line (not parseable JSON) and at least one exact duplicate, so
   the curation step has real work to do and the manifest reflects it.

2. Run `curate.py` with a fixed seed:

   ```
   python exercises/spine/curate.py raw.jsonl out/ --seed 0
   ```

   This writes three files into `out/`: `train.jsonl`, `val.jsonl`, and `manifest.json`. Inspect
   `manifest.json` and confirm:

   - `raw_count` equals the number of non-blank lines in `raw.jsonl`.
   - `dropped` is at least 1 (the invalid line was dropped).
   - `deduped` is at least 1 (the duplicate was removed).
   - `train_count + val_count == valid_unique`.
   - `seed` is 0.

3. Run the format gate on each output:

   ```
   python exercises/spine/check_dataset.py out/train.jsonl
   python exercises/spine/check_dataset.py out/val.jsonl
   ```

   Both must exit 0. If either fails, the problem is in `raw.jsonl`, not in `curate.py`: fix
   the raw data and re-run step 2.

4. Run the leakage gate across both outputs:

   ```
   python exercises/spine/check_dataset.py --check-leak out/train.jsonl out/val.jsonl
   ```

   It must exit 0.

## Pass Condition

All four of the following are true, and you have not deleted any output:

- `check_dataset.py out/train.jsonl` exits 0.
- `check_dataset.py out/val.jsonl` exits 0.
- `check_dataset.py --check-leak out/train.jsonl out/val.jsonl` exits 0.
- `out/manifest.json` exists, is valid JSON, and shows `dropped >= 1` and `deduped >= 1`.

## Done When

All four pass conditions are met. Keep `out/manifest.json` in your working directory: M4 will
reference the path to `train.jsonl` and `val.jsonl` recorded in it.

## Estimated Time

45 to 60 minutes.

## Stretch

Run the self-test on each tool to confirm the tools themselves are working before you point them
at your data:

```
python exercises/spine/check_dataset.py --selftest
python exercises/spine/curate.py --selftest
```

Both must print `selftest: OK`. If either prints `BROKEN`, report the failure before continuing.
This is the same verification discipline the tools apply to your data, applied to the tools
themselves.
