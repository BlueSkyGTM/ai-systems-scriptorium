# Dataset Catalog — Weights and Measures M3 Reference Ingredient

Distilled 2026-06-21 (Haiku fetch tier) from MS-Learn Azure OpenAI / Azure ML fine-tuning data-prep
docs + `made-with-ml` data pipeline. The schema M3 authors fill.

**Grounding rule:** the canonical fine-tune format is the **JSONL chat contract** (docs-grounded). The
`made-with-ml` Ray + Great-Expectations code is conceptual: it teaches the CHECKS (schema match,
label-in-set, compound-uniqueness as a leakage guard, no-null, type, stratified split, label
round-trip), which the reader reimplements in **stdlib** against JSONL. Do NOT hand the reader Ray /
Great Expectations / pandas; the spine tooling is stdlib (`json`, `hashlib`, `random`).

## Doc anchors

| Topic | URL | Facts |
|---|---|---|
| JSONL chat contract | https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning | one JSON object per line; a `messages` array of `{role: system|user|assistant, content: str}`; optional per-assistant `weight` (0/1) to skip an example from the loss. |
| Requirements + quality | https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning | min 10 examples, 50+ recommended; UTF-8; "doubling the dataset can linearly raise quality, but low-quality examples hurt: prune to the highest-quality examples first." |
| Train/val split | https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning | a SEPARATE `validation_set.jsonl`; the validation file drives the `valid_loss` / `full_valid_loss` metrics M2 reads to catch overfitting. |
| Azure ML framing | https://learn.microsoft.com/azure/machine-learning/how-to-use-foundation-models | broader tasks (classification/QA/summarization) accept JSONL/CSV/TSV; column mapping to a task schema; optional automatic split. |

**Real example line (verbatim from docs):**
```json
{"messages": [{"role": "system", "content": "Clippy is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who discovered Antarctica?"}, {"role": "assistant", "content": "Some chaps named Fabian Gottlieb von Bellingshausen and Mikhail Lazarev, as if they don't teach that in every school!"}]}
```

## L1 — `quality-over-quantity`
- The data-centric view: a fine-tune is bounded by its data; the first quality gate is the corpus.
- "Quality" = coverage (the behaviors you want), correctness (no wrong targets), consistency (one
  format, one style). Doubling size helps linearly; one bad example can cost more than a good one adds.
- Prune before you train: the cheapest epoch is the one you never run on garbage.

## L2 — `the-jsonl-contract`
- JSONL, one example per line; the `messages` chat schema (`role` in system/user/assistant, non-empty
  `content`). The failure modes a validator must catch: invalid JSON, missing/extra keys, an unknown
  role, empty content, a non-list `messages`.
- The optional `weight` (0/1) on an assistant turn skips it from the loss (advanced; mention, not core).

## L3 — `deduplication-and-leakage`
- Exact dedup: hash the normalized example (e.g. the concatenated message contents); drop repeats.
  made-with-ml's `expect_compound_columns_to_be_unique(["title","description"])` is the same idea.
- Leakage: the same example (or a trivial paraphrase) in both train and val inflates the validation
  signal M2 trusts. The gate: no example hash appears in both splits.
- Held-out design: a random seeded split (chat data is unlabeled, so a stratified split is optional);
  made-with-ml's `stratify_split(test_size=0.2, seed=...)` is the labeled-data analogue.

## L4 — `building-the-curation-gate` (capstone)
- `curate.py`: read raw JSONL, drop invalid lines, dedupe by content hash, split train/val by a seed,
  write `train.jsonl` + `val.jsonl` + `manifest.json` (counts + the seed).
- `check_dataset.py`: gate the result. Every line valid + schema-correct; no exact dupes within a file;
  no hash overlap between train and val (leakage). Exit non-zero on any failure. The data quality gate.

## Throughline (the spine-engineer builds + freezes; stdlib only, NO torch)

- `exercises/spine/check_dataset.py` — stdlib (`json`, `hashlib`, `argparse`). `validate(path)` checks
  every JSONL line is a valid chat example; `--check-leak train.jsonl val.jsonl` checks no shared
  example hash. `--selftest`: GOOD dataset passes; BAD cases (invalid JSON, unknown role, empty
  content, an exact dup, a train/val leak) each fail with a named reason. Exit 0 only when clean.
- `exercises/spine/curate.py` — stdlib. `curate(raw, out_dir, seed, val_frac)`: drop-invalid + dedupe +
  seeded split + write the two files + manifest. `--selftest`: a planted duplicate is removed, split
  sizes match `val_frac`, and `check_dataset` passes the output (the cleaner feeds the gate).
