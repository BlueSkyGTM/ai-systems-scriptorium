# Module 1 — SQL as an Operator Skill — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared).** Ray locked the four decisions as
recommended ("otherwise lock and move on") with one refinement: **the conductor does not hand-code the
artifact** ("no need for excessive coding on your part, that's what the sonnets are for"). Opus locks
the schema + acceptance oracle (the contract) and reviews; a Sonnet artifact-engineer (coding tools)
builds and tests `module1-sql/`; the Sonnet author tier writes the lessons around it. First authoring
stage for Data Currents
(graduated to in-progress 2026-06-21; `GATE-NAME-BOOK` cleared, title **Data Currents**, slug
`data-currents`). M1 turns the blueprint's Module 1 + the two already-drafted lessons
(`draft/01-telemetry-queries.md`, `draft/02-window-functions-ctes.md`) into finished mdBook lessons +
Claude Code exercises, in the locked Style Contract voice, at the STANDARDS difficulty bar, under
AUTHOR → VERIFY → BUILD/TEST → SHIP.

## The stage in one line

M1 teaches the Production AI Engineer to answer the three production questions (where did the
**latency**, the **cost**, or the **quality** go) with a query, not a guess. Seam: Sans Python M5 L14
named the data seam and ran one `GROUP BY`; M1 is the deep build of operator SQL over AI telemetry,
and it seeds the book's compounding artifact, `module1-sql/`, the telemetry store every later module
queries, transforms, and traces.

## The mandate this stage runs under (2026-06-21)

**Code, don't write. Good writing is one big schema handoff.** ([[code-dont-write-schema-handoff]])
For a SQL module this is literal: the lesson *is* a schema + a query + a test oracle. The plan locks
the artifact's schema and its machine-checkable acceptance oracle as conductor-owned, tested code
**before** a lesson is authored; the prose is the thin handoff layer that explains the locked
artifact, never the source of truth. **Haikus fetch** the grounding (vault ore + MS-Learn SQL-surface
docs) and return fact/URL packs; **Sonnets author** prose around the byte-identical locked SQL;
**Opus owns and tests** every query, the seed, and the smoke/pytest gate.

## Settled decisions (from the blueprint + the contracts + the drafts)

1. **Stage = module.** Same module-as-stage ICM shape as the shipped books: M1 reads its sources,
   writes `build-log/data-currents/m1/output/{author,verify,ship}/`, and hands the locked
   voice/exemplars forward to M2.
2. **Held to the three contracts.** AUTHORING (process + three-source rule), `STANDARDS.md`
   (difficulty ramp + strong-project rubric + the artifact contract), `STYLE.md` (voice). Every
   worker brief carries all three plus the canonical exemplar (`src/README.md`, this book's preface);
   cold workers do not inherit them.
3. **The artifact is a runnable telemetry store, offline.** `module1-sql/` is **self-contained** (no
   dependency on having the Sans Python repo on disk). It seeds synthetic-but-realistic telemetry of
   the kind M5 emits and runs entirely on `sqlite3` (stdlib, the store) + `duckdb` (pip, the analytic
   query engine), no cloud calls. (Fix from the drafts, which assumed a sibling `module5-serving/`.)
4. **Teach the warehouse dialect; run the local engine.** Lessons show standard / T-SQL forms
   (`PERCENTILE_CONT ... WITHIN GROUP`, `DATE_TRUNC`, window frames, `WITH`) grounded in MS-Learn for
   the warehouse context an AI engineer meets on the job; the runnable artifact executes the
   equivalent in DuckDB (`QUANTILE_CONT`, `?`-params), which supports percentile/window/CTE natively
   and reads the SQLite file directly. Each lesson states the one-line dialect note where it bites.
5. **The throughline starts here: `module1-sql/`.** M1 seeds the book's capstone repo. M2 (Batch
   Ingestion) extends this store into a warehouse target + dbt models; M3 orchestrates its loads; M6
   traces lineage through it; M7 composes it into the full pipeline. The reuse is real (later modules
   read and append to the store and its query library on disk), not restated.

## Proposed M1 split (5 lessons, one idea each)

The two drafts are strong but lesson 02 carries three ideas (window functions + CTEs + the lineage
walk), which violates one-idea-per-lesson (STYLE §3). M1 splits into the house 5-lesson shape:

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | Every production question lands in data first; SQL is how you reach it. The three-table telemetry schema and the arc from a `GROUP BY` to a lineage walk. | concept | blueprint M1 + draft 00 |
| 1 | `your-telemetry-is-a-table` | AI telemetry is three tables (spans / eval_verdicts / cost_stamps) joined on `trace_id`; the foundational `GROUP BY` operator queries answer the first-round latency/cost/quality questions. | build | draft 01 |
| 2 | `window-functions` | A window function computes over a partition and keeps every row; rolling 7-day pass-rate and per-tenant cost rank (this week vs last) answer the trend/rank questions `GROUP BY` cannot. | build | draft 02 (queries 4–5) |
| 3 | `ctes-and-the-diagnostic-chain` | A CTE names an intermediate result so a multi-step diagnosis reads top-to-bottom; the freshness-breach chain and the deploy-delta are written as named CTEs, not nested subqueries. | build | draft 02 (queries 6–7) |
| 4 | `the-lineage-walk` | One query walks an answer back to the exact source-document version that produced it; this is the manual shape of the provenance M6 automates, and it finalizes the M1 query library + smoke gate. | build | draft 02 (query 8) + STANDARDS artifact contract |

Each lesson ends in a Claude Code exercise (`exercises/module1/<slug>/README.md`) with a concrete,
machine-checkable done-when against the shared `module1-sql/` artifact.

## The artifact schema + acceptance oracle (the schema handoff — locked first)

The conductor builds and tests this **before** any lesson is authored; it is the schema every lesson
hands to the reader. (Concrete column lists, seed distribution, and assertions are finalized in the
AUTHOR stage scratch build; the shape below is what locks.)

**Store (`module1-sql/db/schema.sql`), the three core tables + a minimal lineage extension:**

- `spans(trace_id PK, route, tenant_id, latency_ms, input_tokens, output_tokens, ts)`
- `eval_verdicts(id PK, trace_id FK, criterion, verdict, score, created_at)`
- `cost_stamps(id PK, trace_id FK, tenant_id, total_cost_usd, input_tokens, output_tokens, billed_at)`
- `corpus_loads(id PK, source_id, status, loaded_at)` + `freshness_slos(source_id PK, max_age_hours)` (for L3)
- `answers(answer_id PK, trace_id, retrieved_chunk_ids)` + `chunks(chunk_id PK, corpus_version, source_doc_id, source_doc_version)` + `source_documents(doc_id, version_id, last_modified_at, content_hash)` (for L4)

**Query library (`module1-sql/queries/*.sql`), the operator queries built across L1–L4:** p95 latency
by route, cost by tenant, eval pass-rate by day+criterion, rolling 7-day pass-rate, per-tenant cost
rank week-over-week, latency delta around a deploy, freshness-breach diagnosis, lineage walk.

**The oracle (`module1-sql/smoke.py` + `tests/test_queries.py`), deterministic + offline:** seed.py
plants known outliers; the gate asserts them by code — `/summarize` is the top-p95 route, `tenant_a`
is the top cost driver, `tenant_b` is the groundedness outlier, the rolling average matches a known
7-day sequence, the cost rank flags the tenant that jumped, the freshness breach fires for the stale
source only, and the lineage walk resolves the target answer to the changed `content_hash`. `python
smoke.py` prints PASS/FAIL per assertion; `python -m pytest tests/` is the CI gate. A deliberately
wrong seed must fail the gate (STANDARDS negative-case rule).

This artifact + oracle is the M1 strong-project surface (STANDARDS Part 2) and the `outputs/skill-*.md`
write-up is the portfolio/progression signal.

## Sources (three-source rule, M1)

1. **Ingredient (vault):** the Sans Python M5 telemetry seam (the spans/eval/cost shape) is the
   substrate; `made-with-ml` (`data.py`, `datasets/`) is **thin** for M1 (it is pandas data-loading,
   not SQL telemetry) and enters properly at M2 (batch ingestion). A **Haiku** surveys
   `vault/made-with-ml` to confirm what M1 can legitimately draw vs. what defers to M2, and returns a
   fact pack — it does not author.
2. **MS-Learn (the grounding for M1).** Unlike Local Metal M1 (consumer hardware, MS-Learn out of
   coverage), M1 here is **squarely in MS-Learn's wheelhouse**: T-SQL `PERCENTILE_CONT`/`PERCENTILE_DISC`
   ordered-set aggregates, window functions (`PARTITION BY`/`ORDER BY`/`ROWS BETWEEN`), CTEs (`WITH`),
   and RBAC/read-replica access patterns in Azure SQL / Fabric Warehouse / Databricks SQL. **Haikus
   verify every `[MS-Learn: …]` marker already in the drafts against a real, current URL** and return
   a `| Fact | URL | Type |` pack; the conductor captures it to `vault/data-currents/m1-sources/
   PROVENANCE.md`. Zero fabricated citations (the Just Python M2/M3 fix).
3. **Editorial seam framing** — "why does a Production AI Engineer need this?" in every lead (the
   3 a.m. incident, the question an engineering manager asks in the first five minutes).

## The fleet plan (orchestration)

Per `platform/ORCHESTRATION.md` and the Local Metal result (conductor-direct, no handler tier for a
single ≤4-worker cluster), under the 2026-06-21 mandate:

- **Haiku fetch tier (2):** (a) MS-Learn SQL-surface verifier (percentile / window / CTE / RBAC docs),
  (b) vault `made-with-ml` surveyor (M1-vs-M2 scope). Each returns a fact/URL pack, writes no files.
- **Sonnet artifact-engineer (1, coding tools):** builds + tests `module1-sql/` against the locked
  schema/oracle in this PLAN — `schema.sql`, `seed.py`, all eight queries (the shown dialect + the
  runnable DuckDB form), `runner.py`, `smoke.py`, `tests/`. Runs the positive gate + the
  deficient-seed negative case to green, then returns the byte-identical SQL/Python the author tier
  reproduces. (Ray's 2026-06-21 refinement: the coding lives with the Sonnets, not the conductor;
  Opus locks the contract and reviews. Refines [[haiku-fetch-tier-feeds-sonnet-authors]].)
- **Sonnet author tier (4, one lesson each, background Agents):** L1–L4. Briefs carry the three
  contracts, the book preface as voice exemplar, the grounded source pack, and the EXACT locked
  SQL/code from the artifact-engineer to reproduce verbatim.
- **Opus conductor:** locks the schema/oracle contract (above), writes `00-overview` (voice anchor),
  integrates `SUMMARY.md` + `exercises/CLAUDE.md`, runs the Zinsser + STYLE + STANDARDS review on
  every draft, re-runs the artifact's gate to confirm the shipped code matches, then runs the em-dash
  sweep + `mdbook build`. Reviews; does not hand-code.

## Locked decisions (GATE-LOCK-PLAN, 2026-06-21 — all as recommended)

1. **Lesson granularity — LOCKED at 5** (overview + the four build lessons above). The drafts'
   overloaded window+CTE+lineage lesson is split so each holds one idea (STYLE §3).
2. **Dialect policy — LOCKED: teach warehouse SQL, run DuckDB.** Lessons show standard/T-SQL
   (grounded in MS-Learn) for the surface the job uses; the artifact runs DuckDB over a SQLite file,
   offline, preserving the deterministic gate.
3. **M1 ore scope — LOCKED: MS-Learn-primary grounding; `made-with-ml` deferred to M2.** A Tier-2
   narrowing (the inverse of Local Metal M1's MS-Learn substitution): M1 SQL is squarely in MS-Learn
   coverage, and `made-with-ml` is pandas data-loading that belongs to the M2 batch-ingestion module.
4. **Lineage in M1 — LOCKED: include the lineage walk as a tested query** over a minimal lineage
   schema extension (answers/chunks/source_documents), so L4 ships runnable code and seeds the M6
   thread; scoped to the manual query shape only (the automated store is M6).

On lock: the fleet scaffolds `exercises/` + `exercises/CLAUDE.md`, the conductor builds + tests
`module1-sql/`, the Sonnet tier authors L1–L4 around the locked SQL, VERIFY gates voice + claims +
grounding, BUILD/TEST runs `mdbook build` + `smoke.py` + `pytest`, and the stage stops at
`GATE-APPROVE-SHIP` before folding lessons into `src/` and exercises into `exercises/`.
