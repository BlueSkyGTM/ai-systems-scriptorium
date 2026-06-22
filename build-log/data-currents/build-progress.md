# Data Currents — Build Progress

Per-stage authoring status. One row per module. Eight modules: M1–M6 build the data-platform layers
(SQL, batch ingestion, orchestration, streaming, warehouses/lakehouses, lineage), M7 is the runnable
pipeline portfolio artifact, M8 is the diagnostic exam. See
`library/in-progress/data-currents/README.md` for the full blueprint.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | SQL as an Operator Skill | ✅ Authored, verified, built — shipped `GATE-APPROVE-SHIP` | 2026-06-21 | Overview + 4 lessons (your-telemetry-is-a-table, window-functions, ctes-and-the-diagnostic-chain, the-lineage-walk) + 5 exercises + `exercises/CLAUDE.md`. Throughline seeded: `module1-sql/` — a self-contained telemetry store (`sqlite3` file) + a query library run in DuckDB, gated by `smoke.py` (8 assertions) + a `pytest` suite (15) with a negative-seed case. Locked decisions: 5-lesson split; teach warehouse SQL / run DuckDB; MS-Learn-primary grounding (made-with-ml deferred to M2, confirmed by vault survey: zero M1 SQL ore); lineage walk included as a tested query seeding the M6 thread. Authored Haiku-fetch (MS-Learn SQL-surface verifier + vault made-with-ml surveyor) / Sonnet-author (4 lessons, one each) / Opus-conduct (overview + the reference artifact contract + review + integration). Per Ray's 2026-06-21 refinement, the conductor locked the schema/oracle and a Sonnet artifact-engineer built+tested `module1-sql/` (reference at `build-log/data-currents/m1/reference/`). VERIFY: STYLE clean (zero em-dashes); 6 MS-Learn citations verified live (PERCENTILE_CONT, OVER/ROWS-BETWEEN, CTE WITH, DENSE_RANK, read-scale-out RBAC, DATE_BUCKET). BUILD/TEST: `mdbook build` clean; reference `smoke.py` 8/8 + `pytest` 15/15 green, negative-seed fails as designed. Plan: `m1/PLAN.md`. |
| M2 | Batch Ingestion | ✅ Authored, verified, built — shipped `GATE-APPROVE-SHIP` (self-clear) | 2026-06-21 | Overview + 4 lessons (the-incremental-merge, the-medallion-pattern, dbt-as-the-transform-layer, the-batch-freshness-slo) + 4 exercises. Throughline `module2-ingestion/`: a real **dbt-duckdb** medallion (bronze/silver/gold models + 31 schema tests) + the operational `ingest.py` idempotent MERGE (keyed on (doc_id, content_hash): re-run = 0 new versions, changed doc = 1 new retained version) + `freshness_check.py` (last-successful-load age vs per-source SLO gate). **Compounding proven:** the M1 lineage walk runs unchanged against M2's gold tables; M2 writes the `corpus_loads`/`freshness_slos` rows the M1 freshness-breach query reads. Locked decisions: teach dbt / run dbt-duckdb offline (the real adapter held, no fallback needed); silver applies the made-with-ml text recipe; MS-Learn-grounded (medallion, dbt-in-Fabric, MERGE INTO, monitor-pipeline-runs — freshness framed honestly as a check you build, no native SLA). Authored Haiku-fetch (MS-Learn + made-with-ml batch ore) / Sonnet-author (4 lessons) / Sonnet-artifact-engineer (built+tested the reference) / Opus-conduct (overview, schema/oracle lock, review). VERIFY: STYLE clean (em-dash sweep caught + fixed 2 in the L4 exercise). BUILD/TEST: `mdbook build` clean; reference `dbt build` 37/37, `smoke.py` 7/7, `pytest` 39/39, both negative cases fail as designed. Reference at `build-log/data-currents/m2/reference/`. Plan: `m2/PLAN.md`. |
| M3 | Orchestration | ⬜ Not started | — | Airflow DAGs / Prefect flows scheduling the pipeline; dbt + Airflow pattern. |
| M4 | Streaming and Change-Data-Capture | ⬜ Not started | — | Kafka + CDC; Eventstream to lakehouse/eventhouse; the streaming-vs-batch freshness decision. |
| M5 | Warehouses and Lakehouses | ⬜ Not started | — | Snowflake/BigQuery vs Delta/Iceberg lakehouse; Fabric OneLake medallion; the AI engineer's access pattern. |
| M6 | Lineage: From Document to Eval Verdict | ⬜ Not started | — | The automated lineage store (the M1 lineage walk, productionized); Purview Unified Catalog. |
| M7 | The Pipeline Artifact (Portfolio) | ⬜ Not started | — | Runnable multi-source ingestion feeding an AI retrieval system; freshness SLO per leg + lineage row per document; `smoke.py` end-to-end. |
| M8 | The Data Platform Exam (Portfolio) | ⬜ Not started | — | Diagnose a broken pipeline with SQL; walk the lineage; ship the fix; graded by a rubric in code. The capstone composes M7. |

## Provenance

Graduated to in-progress 2026-06-21 (`GATE-NAME-BOOK` cleared: title **Data Currents**, slug
`data-currents`), from `library/planned/upstream`. Fourth book into production after Sans Python
(completed), Just Python (completed), Local Metal (completed); concurrent with Answer Engineering and
Machine Math. Fills antilibrary gap row 4 (SQL + data-eng, 52% screen) from
`build-log/sans-python/antilibrary-gap-report.md`; extends Sans Python M5 L14 "The Data Seam".
`GATE-APPROVE-SHIP` self-cleared per module M2–M8 (Ray, 2026-06-21), authoring straight through and
pushing each module as it lands.
