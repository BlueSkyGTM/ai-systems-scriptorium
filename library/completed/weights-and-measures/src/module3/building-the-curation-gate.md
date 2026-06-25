# Building the Curation Gate

Raw JSONL sitting in a directory is not a dataset. It is ore. The distance between ore and a
fine-tune you can trust is three operations: drop the lines that would corrupt training, remove
the copies that waste epochs and mislead validation, and cut a held-out split that the model
never trains on. Run those three operations, stamp the result with a manifest, then gate the
output with a checker that exits non-zero if anything failed. That sequence is what ships to
M4's fine-tune build. Everything else is bookkeeping.

This is the same discipline M2 applied to the training run: the gate is the deliverable. There,
the gate was `check_loop.py` refusing to exit 0 on a loop missing `model.eval()`. Here, the gate
is `check_dataset.py` refusing to exit 0 on a corpus that has not been cleaned. A dataset that
has not passed `check_dataset.py` is a dataset you do not ship to a fine-tune.

## What Curation Fixes and Why the Order Matters

Azure OpenAI fine-tuning documentation states it plainly: doubling dataset size can raise quality
linearly, but low-quality examples hurt. One broken line does not fail silently; it corrupts the
loss signal at every step where the model tries and fails to learn from garbage. One exact duplicate
in a 50-example set inflates the training signal for that example by 2x relative to everything
else. One train/val overlap means the validation loss M2 taught you to read is reporting on data
the model has already memorized.

The three defects demand three distinct fixes, in this order:

1. **Drop invalid lines.** A JSONL fine-tune file is one JSON object per line, each with a
   `messages` array of `{role, content}` pairs where role is `system`, `user`, or `assistant` and
   content is a non-empty string. Lines that fail this schema are invalid; they cannot produce a
   meaningful gradient.

2. **Deduplicate by content hash.** Normalize each example to a stable string (role and content
   concatenated per message, joined), SHA-256 it, and keep only the first occurrence. Exact
   copies vanish; the order of first appearance is preserved before the seeded shuffle.

3. **Split with a seed.** A seeded shuffle followed by a ceiling split gives reproducible
   train/val boundaries from the same inputs every time. The seed is recorded in the manifest so
   the split can be explained and reproduced.

## The Two Tools and What Each Owns

`curate.py` is the pipeline. It reads a raw JSONL, applies the three steps above, writes
`train.jsonl` and `val.jsonl`, and records the accounting in `manifest.json`. The cleaner feeds
the gate: before exiting, it calls `check_dataset.validate` on both output files internally.

`check_dataset.py` is the gate. It validates any JSONL file independently and exits non-zero on
any failure. Its `--check-leak` flag crosses the two split files for shared content hashes.
It is importable as a library (both tools share the same hash function, normalized the same way),
and it ships a `--selftest` that exercises every failure mode with a named reason.

The two tools are not interchangeable. `curate.py` fixes; `check_dataset.py` refuses to pass
what has not been fixed. Running the gate on the cleaner's output before you commit the manifest
is the contract M4 depends on.

## The Selftest Output as the Acceptance Record

Both tools carry a `--selftest` that proves every code path with real inputs. The results below
are not illustrative; they are the captured output from the freeze run on 2026-06-22.

`check_dataset.py --selftest` exercises a good dataset, a bad-JSON line, an unknown role, empty
content, an exact duplicate, and a deliberate train/val leak. Every bad case fails with a named
reason; the good dataset and the clean cross-file check pass:

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

`curate.py --selftest` runs on 7 raw lines (5 valid, 1 invalid JSON, 1 exact duplicate of line A)
and verifies every accounting field before calling the gate on its own output:

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

Both tools exit 0. The manifest fields are the accounting ledger: `raw_count` is what arrived,
`dropped` is what was invalid, `deduped` is what was a copy, `valid_unique` is what remained,
`train_count` and `val_count` are the split, and `seed` and `val_frac` make the split
reproducible. These are the numbers M4 reads to know what it is training on.

## The Manifest as the Contract

The manifest is not a log. It is a contract: a machine-readable record of exactly how this
dataset was produced, committed alongside the clean files. When M4 runs the fine-tune job, it
reads `raw_count`, `valid_unique`, and `val_frac` to confirm it is operating on the dataset it
expects. When M6 productionizes data curation for the portfolio, the manifest fields become the
standard output shape that any downstream consumer can depend on.

The analogous discipline in M2 was saving `valid_loss` in the checkpoint dict so the promoted
model's performance was not reconstructed from memory later. Here it is recording `seed` and
`val_frac` in the manifest so the split can be explained and reproduced. Accountability is
always a matter of writing the right thing down at the right moment.

## What the Gate Refuses

The power of a code gate is in what it rejects. `check_dataset.py` exits non-zero on:

- Any line that is not valid JSON
- A `messages` key that is absent, not a list, or an empty list
- Any message whose role is not `system`, `user`, or `assistant`
- Any message with missing or whitespace-only content
- Any example whose content hash matches an earlier example in the same file
- Any content hash that appears in both the train and val files

None of those failures are ambiguous. Each has a named reason in the output, pinned to a line
number. A corpus that passes all six checks is a corpus worth submitting. The gate's exit code
is the proof; the manifest is the receipt.

## Core Concepts

- Curation is three operations in a fixed order: drop invalid lines, deduplicate by content hash,
  split with a seeded shuffle. Running them out of order or skipping any one produces a corpus
  the fine-tune cannot safely consume.
- The content hash (SHA-256 of normalized role:content pairs) is the deduplication and leakage
  key: the same function in both `curate.py` and `check_dataset.py` means the cleaner and the
  gate agree on what "identical" means.
- The gate is independent of the cleaner: `check_dataset.py` imports cleanly as a library, exits
  non-zero on any failure, and can be run on any JSONL file from any source. The cleaner passes
  through it before exiting; that is not optional wiring.
- The manifest is the contract, not the log: `seed`, `val_frac`, `raw_count`, `dropped`,
  `deduped`, `valid_unique`, `train_count`, `val_count` are the fields M4 reads and M6
  standardizes. Commit the manifest alongside the splits or the split cannot be explained.
- A dataset that has not passed `check_dataset.py` is a dataset you do not ship to a fine-tune.
  The fine-tune's loss curve is a function of what the dataset contains; every invalid line and
  every duplicate is a noise term you paid for with GPU time.
- The `--selftest` on each tool is the acceptance record: it names every failure mode, plants
  each one, and confirms exit 0 only when all bad cases fail with a named reason and the good
  case passes. Selftest is not optional; it is the evidence the gate works.

<div class="claude-handoff" data-exercise="exercises/module3/building-the-curation-gate/">

**Build It in Claude Code**: Run `python curate.py raw.jsonl out/` on a raw JSONL of your own
construction (at least 10 lines; include at least one invalid line and one exact duplicate) to
produce `out/train.jsonl`, `out/val.jsonl`, and `out/manifest.json`; then run
`python check_dataset.py out/train.jsonl` and `python check_dataset.py out/val.jsonl` to
confirm each split is clean, run `python check_dataset.py --check-leak out/train.jsonl out/val.jsonl`
to confirm there is no leakage across the boundary, and commit `manifest.json` as the proof that
every gate passed.

</div>
