# M3 Spine Tools — Freeze Verified

**Date:** 2026-06-22
**Scope:** `library/in-progress/weights-and-measures/exercises/spine/check_dataset.py` +
`library/in-progress/weights-and-measures/exercises/spine/curate.py`
**Constraint:** stdlib only (`json`, `hashlib`, `random`, `argparse`, `sys`, `os`, `math`,
`tempfile`, `importlib.util`). No torch, no third-party deps.

---

## check_dataset.py --selftest (real captured output)

```
check_dataset.py --selftest
[PASS] GOOD dataset (all valid)
[FAIL] BAD invalid JSON line
    - line 2: invalid-json
[FAIL] BAD unknown role
    - line 2 message[0]: role-unknown ('oracle')
[FAIL] BAD empty content
    - line 2 message[0]: content-empty
[FAIL] BAD exact duplicate
    - line 3: duplicate (matches line 1)
[FAIL] BAD train/val leak
    - leak: 1 example(s) appear in both .../train_leak.jsonl and .../val_leak.jsonl
[PASS] GOOD no train/val leak

selftest: OK
```

Exit: **0**

---

## curate.py --selftest (real captured output)

```
curate.py --selftest
[PASS] duplicate removed (valid_unique=5)
[PASS] invalid line dropped (dropped=1)
[PASS] dedup count correct (deduped=1)
[PASS] split sizes correct (train=4, val=1)
[PASS] check_dataset.validate passes train.jsonl
[PASS] check_dataset.validate passes val.jsonl
[PASS] check_dataset.check_leak finds no leak

manifest.json:
{
  "raw_count": 7,
  "dropped": 1,
  "deduped": 1,
  "valid_unique": 5,
  "train_count": 4,
  "val_count": 1,
  "seed": 42,
  "val_frac": 0.2,
  "train_path": "...",
  "val_path": "..."
}

selftest: OK
```

Exit: **0**

---

## Live example: curate a tiny raw set

Raw input: 7 lines (1 with a system-message turn, 4 plain user/assistant, 1 invalid
JSON, 1 valid duplicate of the system-message turn).

```
python curate.py raw.jsonl out/ --seed 7 --val-frac 0.2
```

```json
{
  "raw_count": 7,
  "dropped": 1,
  "deduped": 0,
  "valid_unique": 6,
  "train_count": 4,
  "val_count": 2,
  "seed": 7,
  "val_frac": 0.2,
  "train_path": "...",
  "val_path": "..."
}
```

Note: `deduped=0` here because the "duplicate" in this set has a `system` turn that
the other copy omits -- content hashes differ. The selftest uses an exact byte-for-byte
copy, which triggers `deduped=1` as expected.

---

## Gate status

- `check_dataset.py --selftest`: **OK (exit 0)**
- `curate.py --selftest`: **OK (exit 0)**
- Both tools: stdlib only, no torch, no third-party packages.
- The selftest tempdir pattern matches the house style of `check_loop.py`.
