# CONTEXT — System Semantics (PLANNED)

A planned book covering the **data-engineering seam** — interpreting and routing data for AI
systems. The focus: SQL and the data platform (batch ingestion, streaming, orchestration, warehouses,
lakehouses, lineage) as the AI engineer's operational instruments. Extends directly from Sans Python
M5 L14 "The Data Seam": that lesson names the boundary; this book is the deep build of everything
it deferred. The **52% SQL + data-eng hiring screen** (row 4 of
`build-log/sans-python/antilibrary-gap-report.md`).

**Working title:** System Semantics. Final title is gated at `GATE-NAME-BOOK`.

**Not started.** Starting it is gated at `GATE-NAME-BOOK` (propose the real title first).

## Ore (in the vault — not yet distilled)

- `made-with-ml` — data pipeline, data versioning, MLOps workflow, batch orchestration
  (`data.py`, `datasets/`, `deploy/jobs/`). Primary ore for M1–M4.
- `ai-engineering-from-scratch` — M4/M5 infrastructure and production chapters. Secondary ore for
  M5–M6.
- `ai-performance-engineering` — deploy/serving docs. Supporting ore for M5.
- Survey at process-ore time via `vault/MANIFEST.md` and
  `ingredients/source/_repos/<repo>/curriculum-map.md`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain markdown.
The same page serves either party.

## Load / don't-load

- **Load (when it graduates):** this folder's `README.md`, the named vault ore via `vault/MANIFEST.md`,
  `ingredients`, `platform/pipeline`.
- **Do NOT load:** the shipped book (Sans Python), other planned books.

## Handoff & gates

`GATE-NAME-BOOK` → process ore via `vault/CONTEXT.md` → `platform/pipeline/CONTEXT.md`
(`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`). See `platform/HUMAN-GATES.md`.
