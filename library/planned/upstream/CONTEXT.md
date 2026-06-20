# CONTEXT — Upstream (PLANNED)

A planned book covering the **data-engineering gap** — the MLOps-native half Sans Python kept light: SQL
and the data platform (ingestion, pipelines, streaming, warehouses, lineage — Kafka / Spark / Airflow and
kin) beyond the Docling ingestion front-door the core book already teaches. The **52% SQL + data-eng
screen**.

Sans Python stays the core roadmap; this branches from it, picking up where the M5 ingestion thread
stops. Origin: row 4 of `build-log/sans-python/antilibrary-gap-report.md`.

**Not started.** Starting it is gated at `GATE-NAME-BOOK` (propose the real title first).

## Ore (in the vault — not yet distilled)

- `made-with-ml` data-engineering / pipeline chapters and the data-platform material across the vault.
  Survey at process-ore time via `vault/MANIFEST.md`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain markdown. The
same page serves either party.

## Load / don't-load

- **Load (when it graduates):** this folder's `README.md`, the named vault ore via `vault/MANIFEST.md`,
  `ingredients`, `platform/pipeline`.
- **Do NOT load:** the shipped book, other planned books.

## Handoff & gates

`GATE-NAME-BOOK` → process ore via `vault/CONTEXT.md` → `platform/pipeline/CONTEXT.md`
(`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`). See `platform/HUMAN-GATES.md`.
