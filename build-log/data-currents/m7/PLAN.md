# M7 Plan: The Pipeline Artifact

**Status: SELF-LOCKED** -- Ray self-cleared GATE-LOCK-PLAN per standing mandate (2026-06-21).

## Objective

Build `module7-pipeline/`: the runnable, GitHub-postable portfolio artifact that composes M2-M6
into one coherent AI corpus pipeline. The pipeline ingests via batch (M2) and streaming (M4),
lands data in a Delta lakehouse (M5), captures full lineage per indexed document (M6), and
orchestrates everything with a Prefect flow (M3). A freshness SLO gate per leg fires an alert
hook on breach.

## Composition contract (STANDARDS Part 3 -- compose, do not rebuild)

| Leg | Source module | Key API used |
|-----|--------------|--------------|
| Batch ingestion | M2 `ingest.py` | `run_ingest(csv_path, db_path)` |
| Batch freshness | M2 `freshness_check.py` | `check_freshness(db_path, now_ts)` |
| Streaming | M4 `kafka_sim.py` + `cdc_pipeline.py` | `cdc_source`, `apply_event`, `LagMonitor` |
| Delta landing | M5 `lakehouse.py` | `write_deltalake`, `DeltaTable` |
| Lineage | M6 `schema.py` + `lineage.py` | `init_schema`, `LineageCapture`, `trace_answer_to_sources` |
| Orchestration | M3 Prefect pattern | `@flow`, `@task`, `on_failure` hook |

## Locked design decisions

- Vendor M2-M6 modules into `lib/` (verbatim copies) and import via
  `sys.path.insert(0, lib_dir)` so the artifact is self-contained for GitHub.
- Batch and streaming use separate SQLite DBs (`batch.db`, `stream.db`) because M4's schema
  adds `is_deleted` and `cdc_event_log` columns not present in M2's schema.
- Delta landing reads `source_documents` from `batch.db` and writes a DataFrame of
  (doc_id, version_id, content_hash, last_modified_at) to the Delta table.
- Lineage captures the first 5 batch docs per run to prove the trace without indexing all 120.
- Deficient run for STANDARDS negative case: `batch_now_ts="2099-01-01 00:00:00"` makes the
  batch load appear stale, `batch_freshness_gate` raises RuntimeError, flow enters Failed state,
  on_failure hook appends to `ALERTS`. The smoke test asserts `len(ALERTS) >= 1`.
- Streaming lag breach: inject events with `event_time = time.time() - 100.0` and
  `lag_slo_seconds = 5.0` to prove the `stream_freshness_gate` fails.

## File structure

```
build-log/data-currents/m7/reference/module7-pipeline/
  lib/
    ingest.py             M2 batch ingestion (run_ingest)
    freshness_check.py    M2 batch freshness SLO
    kafka_sim.py          M4 offline Kafka simulation
    cdc_pipeline.py       M4 CDC source + apply_event + LagMonitor
    corpus_store.py       M4 per-event SQLite merge (required by cdc_pipeline)
    lakehouse.py          M5 Delta Lake read/write
    schema.py             M6 lineage store DDL (init_schema)
    lineage.py            M6 LineageCapture + trace_answer_to_sources + impact_of_version
  seeds/
    corpus_raw.csv        same 120-row fixture as M2
  pipeline_flow.py        Prefect flow composing all legs
  smoke.py                end-to-end proof (28 assertions, deficient run must fail)
  tests/
    __init__.py
    test_pipeline.py      pytest suite
  outputs/
    skill-pipeline.md     portfolio write-up
  README.md               business problem framing
```

## Lesson split (src/module7/ -- 4 lessons + overview)

- `00-overview.md` -- the portfolio architecture; why composing beats rebuilding
- `the-architecture.md` -- two legs, one landing, one lineage store; the on_failure gate
- `wiring-the-legs.md` -- how M2 and M4 share the MERGE contract; Delta as the shared output
- `the-freshness-lineage-proof.md` -- gate fires on stale source; trace resolves answer to version
- `the-orchestrated-run.md` -- Prefect coordinates the legs; what the smoke test proves

## Dependencies

- prefect 3.7.5 (offline, ephemeral SQLite backend -- no server needed)
- deltalake 1.6.0
- pandas + pyarrow
- stdlib: sqlite3, hashlib, csv, uuid, re, time, pathlib, sys, tempfile

## Verification before ship

1. `python smoke.py` exits 0 (all 28 assertions pass, deficient run fires alert as designed)
2. `python -m pytest tests/ -v` exits 0
3. `grep -rn "---" library/in-progress/data-currents/src/module7/` returns nothing (em-dash sweep)
4. `~/.tools/mdbook/mdbook.exe build library/in-progress/data-currents` is clean
5. `python platform/bin/route-lint` exits 0
6. Commit + push
