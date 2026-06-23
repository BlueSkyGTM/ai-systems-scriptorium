# Module 3 — Dataset Craft — Build Plan

Status: **PLAN LOCKED 2026-06-21** (`GATE-LOCK-PLAN` self-cleared; W&M M3–M8 straight-through, Ray-approved "go straight through M3-M8"). Third stage (M1, M2 shipped).

## The stage in one line

M1 ran a loop; M2 read whether it was working. M3 is the input side of quality: a fine-tune is only as
good as its data, so this module teaches curation as engineering — the JSONL contract, deduplication
and leakage, held-out set design, and why a small clean set beats a large noisy one. The thesis: data
quality is the first quality gate, enforced by code, before a single epoch runs.

## THE locked decision: data quality is a gate, not a vibe

Most fine-tuning failures are data failures. M3 makes the dataset auditable: a validator that fails
loudly on a malformed line, a duplicate, or a train/val leak, the same "the gate is the deliverable"
move M2 applied to loss curves, now applied to the corpus.

## Locked decisions

1. Stage = module; writes `build-log/weights-and-measures/m3/`. Hands the clean-dataset contract
   forward to M4 (the fine-tune build consumes it) and M6 (the portfolio data-curation script).
2. Held to STYLE + STANDARDS; house cadence overview + 4 lessons + 4 exercises.
3. Grounded: `made-with-ml` data prep (`data.py` split/label, `utils.py`) + MS-Learn Azure OpenAI /
   Azure ML fine-tuning **data preparation** (the JSONL chat schema, validation, "quality over quantity").
   The JSONL schema and any counts are Sonnet-written + RUN; no invented numbers.
4. Real-format only: the JSONL chat contract (`messages` of `{role, content}`) is the canonical format.

## M3 split (overview + 4 lessons + 4 exercises)

| # | Lesson (slug) | The move | Ore |
|---|---------------|----------|-----|
| 0 | `00-overview` | Data as the first quality gate; the four lessons; what feeds forward to M4/M6. | blueprint |
| 1 | `quality-over-quantity` | Why small + clean beats large + noisy; the data-centric view; what "quality" means for a fine-tune set (coverage, correctness, consistency). | MS-Learn data-prep; mwml |
| 2 | `the-jsonl-contract` | The fine-tuning data format: JSONL, one example per line, the `messages` chat schema (`role`/`content`); validating each line; the failure modes (bad JSON, missing role, empty content). | MS-Learn Azure OpenAI fine-tune data format |
| 3 | `deduplication-and-leakage` | Exact + near-duplicate detection (hashing/normalization); train/val leakage (the same example or a paraphrase in both splits); held-out set design that gives a trustworthy signal. | mwml split; aefs |
| 4 | `building-the-curation-gate` | The payoff: a `curate.py` that dedupes + splits a raw JSONL into clean train/val, and a `check_dataset.py` validator that gates format + no-dupes + a documented split. The module deliverable. | the spine |

## Throughline (the data segment of the spine; stdlib, no torch)

- `exercises/spine/check_dataset.py` — stdlib validator: every line is valid JSON with a non-empty
  `messages` list of `{role, content}`; no exact-duplicate examples (hash of normalized content); a
  train/val split manifest present with no overlapping example hashes (leakage gate). `--selftest`
  covers a GOOD dataset + BAD cases (bad JSON, dup, leak).
- `exercises/spine/curate.py` — stdlib: read a raw JSONL, normalize + dedupe (by content hash), split
  into train/val by a seed, write the two files + a tiny manifest; `--selftest` proves dedupe + split
  + that `check_dataset.py` passes the output. The rubric (and the cleaner) are code.

## Fleet (conductor-direct, code-don't-write mandate)

Round 1: 1 Haiku (vault `made-with-ml` data prep) + 1 Haiku (MS-Learn fine-tune data-prep / JSONL).
Round 2: 1 Sonnet artifact-engineer writes + RUNS `check_dataset.py` + `curate.py` (stdlib) and a
FREEZE-VERIFIED report; 5 Sonnet authors fill the schema. Opus designs the schema + reviews, does NOT
hand-code. VERIFY (em-dash + STYLE + grounding) -> BUILD (`check_dataset --selftest` + `curate
--selftest` + `mdbook build`) -> SHIP (CATALOG + ship record + route-lint + atomic commit in a window).
