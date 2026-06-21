# Only Python: Blueprint

## Positioning

Sans Python ships an AI Engineer who can build RAG pipelines, multi-agent fleets, and
production serving stacks. It earns that by deliberately keeping Python at the margins:
point-of-use imports, no NumPy drills, no Pandas idioms taught as subject matter.

The payoff is focus. The cost is a gap that 94% of AI-Engineer job postings close on:
"proficiency in Python" as a screened skill, not a background assumption. When a hiring
screen includes a take-home data exercise or a live NumPy/Pandas question, Sans Python
does not prepare you for it. That is the gap this book fills.

Only Python is the direct sequel. It branches from Sans Python, inherits its purposes,
and then makes Python the subject. It covers the applied Python an AI Engineer is actually
screened on: numerical computing with NumPy, tabular data with Pandas, vectorization
patterns, and the Python idioms that appear in AI/ML codebases. Everything is grounded
in the use cases Sans Python already established. Readers do not re-learn the field;
they learn the Python the field runs on.

Position in the library: **post-Sans-Python, pre-Machine-Learning**. It closes row 1 of
`build-log/sans-python/antilibrary-gap-report.md` before the reader moves to PyTorch
or classical ML (rows 2 and 3).

[MS-Learn: "Explore and analyze data with Python" — NumPy/Pandas/Matplotlib module:
https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/]

## Thesis

The name is the argument. Sans Python said: learn the field without Python as the
subject. Only Python says: now make it the subject, but only the Python that connects
to what you just learned.

The bet is that Python is a vast black box, and it only makes sense to drill it once
you know what it is for. Sans Python establishes the for. Only Python delivers the
drill: arrays, DataFrames, vectorized ops, the data-wrangling idioms that underlie every
AI/ML pipeline a reader will encounter in the job market. Born from belief, not just
need.

## Scope

### In

- **NumPy fundamentals**: arrays, dtypes, broadcasting, indexing, vectorized math,
  memory layout. The mental model behind fast numerical code, not just the API.
- **Pandas for AI pipelines**: Series, DataFrame, groupby, merge, apply, and the
  split-apply-combine pattern. Reading and writing the data formats that appear in
  AI pipelines (CSV, Parquet, JSONL).
- **Vectorization discipline**: when to vectorize, when a loop is correct, how to
  profile. The cognitive shift from Python loops to array operations.
- **Python idioms at interview speed**: list comprehensions, generators, context
  managers, decorators, type hints, `dataclasses`. The subset screened in take-homes
  and phone screens.
- **Data wrangling for AI**: cleaning, reshaping, joining, handling missing values in
  the context of preparing a corpus or evaluation dataset, not a finance spreadsheet.
- **Connecting back to Sans Python**: exercises use structures from the Sans Python
  ecosystem (evaluation tables, batch prediction outputs, embedding stores) so the
  reader sees the same data in a new light.

### Deliberately Out

- **PyTorch and model training**: that is Machine Learning (rows 2/3 of the gap report),
  not this book. Only Python stops at the data layer.
- **Matplotlib/Seaborn visualization**: literacy is noted where NumPy/Pandas produce
  arrays for plotting, but building charts is not a focus of the 94% screen.
- **Classic ML algorithms**: no scikit-learn pipelines, no model evaluation loops. The
  Machine Learning book owns those.
- **Distributed data (Spark, Dask, Ray)**: row 4 of the gap report, belongs to Upstream.
- **Python packaging, CI, Docker**: Sans Python covered environment setup. Ops is M5
  territory.
- **Math depth (linear algebra, calculus)**: row 6 of the gap report, covered
  conceptually in Sans Python M1 and deferred to Machine Learning for applied depth.

The antilibrary discipline: every cut named above has a home. Nothing is lost; it is
pointed at the right book.

## Ore to Module Map

Two primary ore sources; both are in the vault.

**`made-with-ml` (`vault/made-with-ml/`, prefix `mwml`)**
- `data.py`: data loading, stratified split, text cleaning, tokenization into Ray
  datasets. Rich Pandas and NumPy usage throughout.
- `evaluate.py`: per-class and slice-level metric computation; NumPy array ops for
  aggregation.
- `utils.py`: reproducibility, file I/O, padding/collation, MLflow run tracking.
- `tests/code/`: `test_data.py`, `test_utils.py` — pytest patterns for data-layer code.
- `notebooks/madewithml.ipynb`: the end-to-end ML notebook; data sections are the
  primary ore vein.
- Already inventoried at `ingredients/source/_repos/made-with-ml/inventory.md`.

**`ai-engineering-from-scratch` (`vault/ai-engineering-from-scratch/`, prefix `aefs`)**
- Phase 00 `06-python-environments`, `09-data-management`, `12-debugging-and-profiling`:
  Python setup and data-handling foundations.
- Phase 02 (antilibrary in aefs, usable here): ML fundamentals lessons include
  feature engineering, model evaluation idioms, data preprocessing — the applied
  Python the antilibrary deferred from Sans Python's seam.
- Phase 19 capstone items `42-large-corpus-downloader`, `43-hdf5-tokenized-corpus`,
  `64-chunking-strategies-advanced`, `65-hybrid-retrieval-bm25-dense`: data-pipeline
  Python in the context of AI engineering tasks.
- Already inventoried at `ingredients/source/_repos/ai-engineering-from-scratch/inventory.md`.

At process-ore time: survey both repos via `vault/MANIFEST.md` and the per-repo
`antilibrary.md` files. The mwml data/evaluate/utils/tests vein and the aefs Phase 02
and Phase 19 data capstones are the richest veins for this book.

## Curriculum Arc

Eight modules, mirroring the Sans Python shape. Modules 6 and 7 are portfolio
artifacts; Module 8 is the final integrated exam.

| Module | Title | What It Covers |
|--------|-------|----------------|
| 1 | Python as a Data Engine | The mental model: Python's data model, object overhead, why NumPy exists |
| 2 | NumPy in Depth | Arrays, dtypes, broadcasting, indexing, vectorized math, memory layout |
| 3 | Pandas for AI Pipelines | Series, DataFrame, merge/groupby/apply, reading/writing AI-relevant formats |
| 4 | Vectorization Discipline | Profiling loops vs. arrays; when vectorization wins; the hidden cost of apply |
| 5 | Python Idioms at Interview Speed | Comprehensions, generators, decorators, type hints, dataclasses; the screened subset |
| 6 | Data Wrangling Artifact | Portfolio artifact: a production-grade data-cleaning pipeline (see below) |
| 7 | Evaluation Engine Artifact | Portfolio artifact: a batch eval pipeline over a Sans Python evaluation table |
| 8 | Integrated Python Engineering Exam | Timed exercise: ingest a raw corpus, wrangle, vectorize, emit results; graded rubric |

Every lesson ends in a runnable Claude Code exercise. The pattern from Sans Python holds:
a specific task, a specific expected output, a Claude Code prompt that executes it. No
pseudo-code capstones.

## Portfolio Artifact Strategy

The same proof-of-skill logic as Sans Python M6/M7/M8 applies here.

**Module 6 — Data Wrangling Pipeline**
A self-contained Python script (`exercises/module6/wrangle.py`) that:
- Ingests a raw JSONL corpus (same format as the mwml dataset; reuses `data.py` patterns)
- Cleans, deduplicates, and reshapes it with Pandas
- Emits a Parquet output with schema validation
- Has a `pytest`-based `smoke.py` that verifies row counts, dtypes, and no null leakage
Runnable: `python exercises/module6/wrangle.py` exits 0.

**Module 7 — Evaluation Engine**
A script (`exercises/module7/eval_engine.py`) that:
- Reads a batch prediction output (CSV: `id, prediction, label`)
- Computes per-class precision/recall/F1 using NumPy (no sklearn)
- Emits a Markdown evaluation table
- Links back to the Sans Python M7 evaluation tables so the reader sees the connection
Runnable: `python exercises/module7/eval_engine.py` exits 0.

**Module 8 — Final Exam**
A timed, unseen exercise (`exercises/module8/exam.py`) that chains M1-M7 skills:
ingest, clean, vectorize, compute metrics, emit a structured report. The grading rubric
checks correctness of outputs, not line-by-line code style. Mirrors Sans Python M8.

The reader ships a GitHub repo where three scripts run clean, demonstrating applied
Python at AI-Engineer level: data in, structured output out, tested.

## Dual-Use Note

This blueprint and the book that will grow from it are written to be read by a human
learner and ingested by an LLM without loss. Dense, linked, plain markdown. No
dependency on rendered formatting for meaning. Section headers are stable anchors;
the ore map and module table are machine-parseable. An LLM processing this file can
reconstruct the full scope, locate the ore, and understand the exclusion logic without
supplemental context.

## Name (GATE-NAME-BOOK — Cleared)

**Locked 2026-06-20: the title is _Only Python_, the slug is `only-python`.** The candidates below are
kept as the record of the decision.

| Name | Rationale |
|------|-----------|
| **Only Python** (lead candidate) | Deliberate play on "Sans Python": first you learned the field without Python as the subject; now you focus only on it. The echo is the argument. Memorable, positioned, self-explanatory to anyone who read the first book. |
| **Applied Python for AI Engineers** | Descriptive and SEO-clear for standalone readers who did not read Sans Python. Trades resonance for discoverability. |
| **Python, Properly** | Captures the "finally drill it correctly" feeling; signals opinion and confidence. Less explicit about AI-engineering scope. |

Decision: **Only Python**. The book has graduated to `library/in-progress/only-python`.
