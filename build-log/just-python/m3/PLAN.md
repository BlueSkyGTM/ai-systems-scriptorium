# Module 3 — Pandas for AI Pipelines — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared — Ray locked as drafted: all 4 open decisions
accepted, including the no-handler orchestration A/B).** **SHIPPED 2026-06-21 (`GATE-APPROVE-SHIP` cleared).** Third authoring stage for
Just Python. M1 + M2 shipped
(2026-06-20 / 2026-06-21). M3 turns the blueprint's third module into finished mdBook lessons + Claude Code
exercises, in the locked Style Contract voice, at the STANDARDS difficulty bar, under
AUTHOR → VERIFY → BUILD/TEST → SHIP. Do not author until Ray locks.

## The stage in one line

M2 drove the raw NumPy buffer; M3 puts a labeled, heterogeneous table on top of it (the DataFrame) and the
four operations AI data-prep actually runs on: load/save the real formats, split-apply-combine, join, and
clean. Seam: every take-home that hands you a messy CSV or a corpus of JSONL is testing whether you can turn
rows into a training or evaluation set with Pandas, not a Python loop.

## Settled decisions (from the blueprint + the contracts)

1. **Stage = module.** Same module-as-stage ICM shape: M3 reads its sources, writes `output/author|verify|
   ship/`, and hands its locked exemplars + the extended `measure.py` forward to M4.
2. **Held to the three contracts.** AUTHORING (process + three-source rule), `STANDARDS.md` (difficulty ramp
   + strong-project rubric + the artifact contract), `STYLE.md` (voice). Every worker brief carries all
   three plus the canonical exemplar — the M1 + M2 lessons (`src/module1/*.md`, `src/module2/*.md`), the
   book's own voice. Cold workers do not inherit them.
3. **Ore = `vault/pandas-docs/` (reference-grade) + made-with-ml as the applied seam example.** Confirmed in
   the vault: `vault/pandas-docs/` is BSD-3-Clause, vendored 2026-06-20, the pandas user guide (`dsintro`,
   `basics`, `io`, `groupby`, `merging`, `reshaping`, `missing_data`, `duplicates`, `text`, `categorical`,
   `user_defined_functions`, …) — the same reference-grade pattern numpy-docs gave M1/M2. The applied seam
   example is **made-with-ml's `madewithml/data.py`** (load → clean_text → stratified split → tokenize; see
   `ingredients/source/_repos/made-with-ml/curriculum-map.md`), grounding the lessons in a real production
   data pipeline. **No vault→ingredients distillation pass is needed** — pandas-docs is reference-grade, read
   by the worker at author time, not loaded into the conductor. (This corrects the prior stress-test guess
   that M3 would force the distillation machinery; see Open Decision 2 and `build-log/stress-test/`.)
4. **M3 is the Core-build rung (STANDARDS Part 1).** Four build lessons, each a runnable script with a
   machine-checkable done-when; the throughline grows; difficulty earned from real corpus/eval prep, not API
   breadth. No forward dependencies: M3 uses M1's memory model and M2's vectorization, never the reverse.
5. **Don't reproduce, link (AUTHORING non-negotiable).** Lessons teach Pandas patterns *using* made-with-ml's
   real `data.py` as the grounded example; they do not rebuild made-with-ml. The spine is the
   business-application artifact (an eval/corpus prep pipeline), not a from-scratch reimplementation.

## Proposed M3 split (5 lessons, one idea each)

Ramp order: the structure first, then the I/O that fills it, then the combine operations, then the clean-up
that makes it a dataset.

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | M2 drove the buffer; M3 puts a labeled table on top of it. The DataFrame and the load / combine / clean operations that turn raw rows into a training or eval set. | concept | conductor-integrated; frames the four below |
| 1 | `series-and-dataframe` | A DataFrame is a dict of NumPy-backed Series sharing one index; each column carries its own dtype, and `memory_usage(deep=True)` shows the object-dtype string tax M1 predicted. | concept/build | pandas-docs `dsintro` + `basics` |
| 2 | `reading-and-writing-ai-formats` | Read and write the three formats AI pipelines run on: CSV for eval tables, JSONL for corpora, Parquet for columnar data at scale; control dtypes on load, and know why Parquet beats CSV past a point. | build | pandas-docs `io`; applied: made-with-ml `datasets/dataset.csv` |
| 3 | `groupby-merge-apply` | Split-apply-combine with `groupby` + agg, `merge` to join predictions to labels, and `apply` — which is a disguised Python loop you vectorize away (the M2/M4 tie). | build | pandas-docs `groupby` + `merging` + `user_defined_functions`; applied: made-with-ml `data.py` stratified split |
| 4 | `cleaning-and-missing-data` | The corpus-prep toolkit: dedup, handle `NaN` (drop or fill), reshape with melt/pivot, clean text — the operations that turn raw rows into a usable dataset. | build | pandas-docs `missing_data` + `duplicates` + `reshaping` + `text`; applied: made-with-ml `data.py` clean_text |

Each lesson ends in a Claude Code exercise (`exercises/module3/<slug>/README.md`) with a concrete,
machine-checkable done-when (a printed shape/count, a passing assertion, exit 0), per STANDARDS Part 2 and
matching the M1/M2 exercise format.

## The compounding throughline (STANDARDS Part 3)

M3 **extends the existing `measure.py`** (at `exercises/module1/the-cost-of-a-python-list/measure.py`) once,
and seeds the data-prep patterns M6 will reuse:

- **L1** adds `frame_bytes(df)`: reports a DataFrame's true memory via `memory_usage(deep=True)` and compares
  it to the equivalent contiguous ndarray, making the object-dtype string overhead (M1's boxed-object model,
  now in Pandas) measurable. Real import-and-extend, not restated.
- **L2–L4** establish the load → clean → reshape patterns that **M6's `wrangle.py`** imports off disk (the
  blueprint's M6 artifact reuses made-with-ml `data.py` patterns); M3 is where the reader first writes them.

## Sources (three-source rule, non-negotiable)

1. **Ingredient:** `vault/pandas-docs/` sections named per lesson + made-with-ml `data.py` as the applied
   example (via the existing `ingredients/source/_repos/made-with-ml/` metadata). Read at author time by the
   worker; not loaded into the conductor.
2. **Microsoft Learn** via the connector ("Explore and Analyze Data with Python" — the Pandas/DataFrame
   sections). Resolve every `[MS-Learn: …]` marker at VERIFY against the live connector; **M2 proved the
   workers will invent plausible citations, so VERIFY checks each one resolves** (zero markers is a smell,
   fabricated markers are a failure).
3. **Editorial seam framing** — "why does a Production AI Engineer need this?": eval tables as CSV, corpora
   as JSONL, joining predictions to labels, NaN handling before a metric runs.

## The fleet plan (orchestration A/B — testing the M2 handler finding)

M2's stress-test finding: the Opus handler tier was mild overhead for a single 4-worker cluster with no
concurrent gate to service. **M3 runs the counterfactual: the conductor manages the 4 Sonnet workers
directly, no handler tier.** ORCHESTRATION's rule of thumb says 3+ workers → handler, but its stated
rationale (keep the human loop alive during concurrent gates) is inactive during authoring. Running M3
conductor-direct tests whether the handler earned its keep in M2 or was pure overhead — a real data point
for `platform/ORCHESTRATION.md`.

- **Conductor (Opus, this session):** locks the plan, briefs and dispatches 4 Sonnet workers directly,
  authors/integrates `00-overview` and the `measure.py` extension, and runs the Zinsser + STYLE + STANDARDS
  review gate on every draft before it lands.
- **Workers (Sonnet, parallel):** lessons 1–4, one worker per lesson, one writer per file. Each brief is
  self-contained: AUTHORING + STANDARDS + STYLE + the M1/M2 exemplar lessons + that lesson's pandas-docs
  slice + the made-with-ml applied reference. Workers never touch `SUMMARY.md`, `measure.py`, or
  `exercises/CLAUDE.md` (conductor-folded shared state).

## Open decisions to pressure-test (lock these with Ray)

1. **Granularity.** 5 lessons (proposed) vs a 6-lesson split (L3 `groupby-merge-apply` is the densest — could
   split `groupby` + agg from `merge` + `apply`). Recommendation: **5**, but L3 is the one to watch; if a
   draft bloats past one idea, split it at author time and report.
2. **Ore + the untested distillation stage.** Confirm M3 uses **pandas-docs as the reference-grade primary
   source** (like numpy-docs for M1/M2) with made-with-ml as the applied seam, rather than a heavy
   vault→ingredients distillation. Recommendation: **yes.** Honest flag: this means the `ingredients/dossiers`
   distillation machinery stays **unexercised** for Just Python — JP's veins keep turning out doc-grade. If
   you want the test to actually stress distillation, that lives in a code-ore book (e.g. the made-with-ml
   serving vein, or a planned book), not here.
3. **Throughline.** Confirm M3 extends `measure.py` with `frame_bytes` (L1) and seeds the load/clean patterns
   M6's `wrangle.py` reuses, vs starting a separate M3 artifact. Recommendation: **extend `measure.py`** —
   it keeps the memory-cost throughline alive into Pandas and lands the object-dtype lesson concretely.
4. **Orchestration A/B.** Confirm M3 runs **conductor-direct (no handler tier)** to test M2's handler-overhead
   finding. Recommendation: **yes** — it is a cheap, honest experiment and the result feeds ORCHESTRATION.

On lock: the fleet authors M3, VERIFY gates it against STYLE + the live MS-Learn connector, BUILD/TEST runs
`mdbook build` + each exercise's smoke path, and the stage stops at `GATE-APPROVE-SHIP` before folding into
`src/`.
