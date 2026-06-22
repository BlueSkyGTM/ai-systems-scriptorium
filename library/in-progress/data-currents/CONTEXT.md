# CONTEXT — Data Currents (IN PROGRESS)

The **data-engineering seam** seen from the AI engineer's seat: interpreting and routing data for AI
systems. SQL and the data platform (batch and streaming ingestion, orchestration, warehouses,
lakehouses, lineage) taught as operational instruments, not as a data-engineering degree. Extends
directly from Sans Python M5 L14 "The Data Seam": that lesson names the boundary; this book is the
deep build of everything it deferred. Fills antilibrary gap row 4 (the 52% SQL + data-eng hiring
screen) from `build-log/sans-python/antilibrary-gap-report.md`.

**Graduated to in-progress 2026-06-21.** `GATE-NAME-BOOK` cleared (title **Data Currents**, slug
`data-currents`; lead candidate from the blueprint, the two-word house-style pairing that names the
directional flow of data toward an AI system). The blueprint's eight-module arc (`README.md`) and the
already-drafted Module 1 material ("SQL as an Operator Skill": overview + 2 lessons + 2 exercises in
`draft/`) are the starting material; authoring upgrades that draft, grounds it in the named ore, and
brings it to ship quality. See `README.md` for the full blueprint.

**Scope boundary (recorded):** cluster operations (standing up Kafka, sizing Spark, running Airflow
workers), data-warehouse modeling depth (star schemas, slowly-changing dimensions), feature-store
internals, stream-processing internals, and BI/reporting are OUT of scope. The reader uses these as
services and queries against schemas the data team owns; the operator skill is writing the query and
authoring the pipeline, not operating the platform.

**Post-Sans-Python positioning:** Sans Python is the core roadmap (LLM engineering, agents, fleet,
deploy) and stops at the data seam. Data Currents branches from it for readers who want to own the
platform side of that seam: the SQL screen, the freshness SLO, the orchestration DAG, and the
end-to-end lineage an interviewer probes.

## Ore (in the vault — not yet distilled)

- `made-with-ml` (`mwml`): data pipeline, data versioning, batch orchestration (`data.py`,
  `datasets/`, `deploy/jobs/`). Primary ore for M1–M4.
- `ai-engineering-from-scratch` (`aefs`): M4/M5 infrastructure and production chapters. Secondary ore
  for M5–M6.
- `ai-performance-engineering` (`aipe`): deploy/serving docs. Supporting ore for M5.
- Survey at process-ore time via `vault/MANIFEST.md` and `ingredients/source/_repos/<repo>/`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain markdown. An
LLM navigating this book should be able to answer "what does the freshness SLO for the batch leg of
the M7 pipeline look like" from the lesson text alone. The same density makes the human reader fast.

## Load / don't-load

- **Load:** this folder's `README.md` and `draft/`, the named vault ore via `vault/MANIFEST.md`,
  `ingredients`, `platform/conventions` (AUTHORING + STANDARDS + STYLE), `platform/pipeline`.
- **Do NOT load:** the shipped Sans Python book; other books; anything under `skills/` or `gstack/`.

## Handoff & gates

`GATE-NAME-BOOK` cleared. **Module 1 "SQL as an Operator Skill" shipped 2026-06-21** (`GATE-LOCK-PLAN`
+ `GATE-APPROVE-SHIP` cleared): overview + 4 lessons + 5 exercises in `src/module1/` + `exercises/
module1/`; the `module1-sql/` throughline seeded; reference at `build-log/data-currents/m1/reference/`.
**M2–M8 `GATE-APPROVE-SHIP` self-cleared (Ray, 2026-06-21)** — author straight through, pushing each
module as it lands. For each next module: draft + self-lock `build-log/data-currents/mN/PLAN.md`, then
author via `platform/pipeline/CONTEXT.md` (Haiku-fetch / Sonnet-author / Opus-conduct: the conductor
locks the schema + oracle, a Sonnet artifact-engineer builds+tests it, Sonnet authors write the
lessons), VERIFY + BUILD/TEST, fold into `src/` + `exercises/`, record in
`build-log/data-currents/build-progress.md`, commit+push. See `platform/HUMAN-GATES.md`.
