# Module 2 — Batch Ingestion — Build Plan (self-locked)

Status: **PLAN SELF-LOCKED 2026-06-21.** Under Ray's straight-through mandate (`GATE-APPROVE-SHIP`
self-cleared M2–M8, 2026-06-21), `GATE-LOCK-PLAN` is self-cleared for this module; a genuine
strategic fork would still stop. M2 turns the blueprint's Module 2 into finished lessons + exercises,
extending the M1 `module1-sql/` throughline into the corpus-ingestion layer.

## The stage in one line

M2 builds the nightly corpus reload as a production system: an idempotent incremental merge, the
bronze/silver/gold medallion as the transformation pattern, dbt models + tests as the transform layer,
and a batch freshness SLO that measures and alerts on source-to-table lag. Seam: M1 queried the
telemetry and walked lineage; M2 builds the ingestion that fills the corpus and lineage tables those
queries read.

## The mandate

Code, don't write ([[code-dont-write-schema-handoff]]). The conductor locks the artifact schema + the
acceptance oracle; a **Sonnet artifact-engineer** builds + tests it; **Haikus fetch** (MS-Learn dbt /
medallion / Fabric + the `made-with-ml` batch ore, now in scope); **Sonnet authors** write the lessons
around the byte-identical locked code.

## Settled decisions

1. **Throughline extends M1.** M2 builds `module2-ingestion/` that produces the clean corpus tables
   (`source_documents`, `chunks`) the M1 lineage walk already queries; the compounding is real (M2
   populates what M1 read). The store stays the same SQLite-file + DuckDB engine, offline.
2. **Teach dbt; run it offline.** Same shape as M1's "teach warehouse SQL, run DuckDB." The lessons
   teach dbt models + tests as the production transform layer (grounded in MS-Learn dbt-in-Fabric);
   the runnable artifact uses **`dbt-duckdb`** (pip, offline, file-based) so the reader writes real dbt
   models (bronze/silver/gold) and runs `dbt build` + `dbt test` against a local DuckDB. **Fallback
   (artifact-engineer decides at build time):** if `dbt-duckdb` is not cleanly offline-installable, a
   dbt-shaped SQL runner (a tiny Python runner over ordered `models/*.sql` + an assertions file) stands
   in, and the lessons note dbt as the production form. The artifact-engineer reports which path held.
3. **Incremental merge is idempotent.** The reload is a `MERGE`/upsert keyed on a natural key + a
   content hash, not a truncate-and-reload; running it twice changes nothing. This is the testable core.
4. **Batch freshness SLO connects to M1.** M2 writes `corpus_loads` rows (the table M1's freshness
   breach query reads) and defines a per-source `max_age_hours`; the freshness check is the gate.
5. **MS-Learn-primary + made-with-ml batch ore.** `made-with-ml` (`data.py` load/clean/split,
   `datasets/*.csv`, `deploy/jobs/`) is the in-scope batch-pipeline ore for M2 (confirmed by the M1
   vault survey: it is batch data-engineering, which is M2's subject). MS-Learn grounds dbt + medallion.

## Proposed M2 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind |
|---|---------------|----------|------|
| 0 | `00-overview` | The nightly reload is a production system; here is the medallion, the merge, dbt, and the freshness SLO. | concept |
| 1 | `the-incremental-merge` | A batch reload is an idempotent `MERGE` keyed on a content hash, not a truncate-and-reload; re-running changes nothing. | build |
| 2 | `the-medallion-pattern` | Bronze (raw), silver (cleaned/typed), gold (serving) layers make corpus data trustworthy before it is queried. | build |
| 3 | `dbt-as-the-transform-layer` | dbt turns the medallion into versioned models with tests that gate promotion; the transform is code, reviewed and tested. | build |
| 4 | `the-batch-freshness-slo` | A freshness SLO is a measured, alerting objective: source-to-table lag against a per-source target, writing the `corpus_loads` row M1's breach query reads. | build |

## The artifact + oracle (locked first, by the conductor)

`module2-ingestion/`: a raw document source (synthetic corpus CSV/JSONL) → bronze/silver/gold dbt
models (or the fallback runner) → `source_documents` + `chunks` tables → an incremental `MERGE` →
`corpus_loads` freshness rows. Oracle (`smoke.py` + `pytest`, offline): the medallion build is green;
the incremental merge is **idempotent** (second run = zero changes, asserted by row+hash diff); a
changed source document produces a new `source_documents` version (new `content_hash`) the M1 lineage
walk resolves; the freshness check flags a stale source and passes a fresh one; a deficient run (a
broken silver transform, or a stale source past SLO) fails the gate. The reused M1 lineage query runs
green against the M2-produced tables (the compounding proof).

## Fleet plan

- **Haiku fetch tier (2):** (a) MS-Learn dbt-in-Fabric + medallion (bronze/silver/gold) + Lakehouse
  ingestion + incremental/MERGE patterns, returning a verified `| Fact | URL | Type |` pack; (b)
  `made-with-ml` batch ore deep-dive (`data.py`, `datasets/`, `deploy/jobs/workloads.*`) returning the
  reusable load/clean/split patterns + file paths.
- **Sonnet artifact-engineer (1):** builds + tests `module2-ingestion/` against the locked schema +
  oracle; confirms the dbt-duckdb-vs-fallback path; returns byte-identical code + a green run.
- **Sonnet authors (4):** L1–L4 around the locked code + fetched grounding.
- **Opus conductor:** writes `00-overview`, integrates `SUMMARY.md`, reviews every draft (Zinsser +
  STYLE + STANDARDS), re-runs the gate, em-dash sweep + `mdbook build`, ships + pushes.
