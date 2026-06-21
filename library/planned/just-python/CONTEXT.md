# CONTEXT — Only Python (PLANNED)

The direct sequel to Sans Python. Where Sans Python teaches AI engineering without making
Python the subject, Only Python makes it the subject: the applied Python an AI Engineer
is screened on but the core book never drills. NumPy arrays, Pandas DataFrames,
vectorization discipline, and the Python idioms that appear in every AI/ML codebase.
Fills row 1 of `build-log/sans-python/antilibrary-gap-report.md` — the **94%-of-postings
"Python" screen**, the single largest gap the first book left by design.

Post-Sans-Python, pre-Machine-Learning. The name plays off the first book deliberately:
first you learned the field *Sans Python*; now you focus *Only Python*.

**Not started** (not graduated to in-progress). A Chapter 1 preview is drafted in `draft/` to
pressure-test the blueprint; authoring that preview is autonomous, but graduating the book to
in-progress, and locking its title, is gated at `GATE-NAME-BOOK` (candidates in this folder's `README.md`).

## Ore (in the vault — not yet distilled)

- **`made-with-ml`** (`vault/made-with-ml/`): `data.py`, `evaluate.py`, `utils.py`, and
  the `madewithml.ipynb` notebook — the richest NumPy/Pandas vein in the vault. Data
  loading, sliced evaluation, and data-layer testing patterns.
- **`ai-engineering-from-scratch`** (`vault/ai-engineering-from-scratch/`): Phase 00
  data-management and debugging lessons; Phase 02 (antilibrary for Sans Python, in-seam
  here) for ML-fundamentals data idioms; Phase 19 data-pipeline capstones
  (`42-large-corpus-downloader`, `43-hdf5-tokenized-corpus`, `64`-`65` hybrid retrieval).
- Survey both at process-ore time via `vault/MANIFEST.md` and the per-repo
  `ingredients/source/_repos/` metadata.

## Dual-Use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain
markdown. The same page serves either party. Stable section anchors; machine-parseable
ore map and module table in `README.md`.

## Load / Don't-Load

- **Load (when it graduates):** this folder's `README.md`, the named vault ore via
  `vault/MANIFEST.md`, `ingredients`, `platform/pipeline`.
- **Do NOT load:** the shipped book, other planned books.

## Handoff & Gates

`GATE-NAME-BOOK` → process ore via `vault/CONTEXT.md` → `platform/pipeline/CONTEXT.md`
(`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`). See `platform/HUMAN-GATES.md`.
