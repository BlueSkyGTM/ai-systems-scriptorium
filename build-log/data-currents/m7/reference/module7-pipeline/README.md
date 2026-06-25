# Module 7: The Pipeline Artifact

## The business problem

An AI retrieval system is only as good as the data feeding it. Two sources of truth compete:

- **The nightly batch load** processes a full document corpus on a schedule. It is comprehensive
  but inherently delayed: by morning the corpus is already hours old.
- **The CDC stream** delivers individual document changes in seconds. It is fast but thin:
  only the changed keys flow, so it depends on the batch baseline being present.

The retrieval system needs **both legs running and fresh**. If the batch load stalls (file
delivery late, ETL error), the corpus grows stale even if the stream is healthy. If the stream
lags (consumer overloaded, broker unreachable), recent edits go unseen even if the nightly
batch completed. Neither check alone is sufficient.

On top of freshness, **every answer the system generates must be traceable** to the exact
document version and content hash that produced it. "Why did the model say that?" must be
answerable months later, even after the document was updated.

This artifact is the proof that all of it works together.

## What this module builds

`module7-pipeline/` is a fully executable capstone that composes the five prior reference
artifacts into a single orchestrated pipeline:

| Leg               | Source module | Function                                               |
|-------------------|---------------|--------------------------------------------------------|
| `batch_ingest`    | M2            | Bronze -> silver -> gold MERGE into SQLite corpus store |
| `stream_apply`    | M4            | In-process Kafka CDC; `apply_event` per-key MERGE      |
| `land_lakehouse`  | M5            | Delta Lake v0 (pre-stream) and v1 (post-stream) with time-travel |
| `capture_lineage` | M6            | `LineageCapture` on every indexed chunk; one full RAG answer |
| `freshness_gate`  | M2 + M4       | Hours SLO (batch) + seconds SLO (stream); fails loud    |

The flow is orchestrated with Prefect 3.x (`@flow` / `@task`), retries on I/O tasks, and
an `on_failure` hook that fires an alert when either freshness gate is breached.

## Freshness SLOs

| Leg     | Source ID      | SLO         | Measured by                        |
|---------|----------------|-------------|-------------------------------------|
| Batch   | `corpus_raw`   | 25 hours    | M2 `check_freshness` vs corpus_loads |
| Stream  | `corpus_cdc`   | 5 seconds   | M4 `LagMonitor.is_breached()`       |

## Lineage guarantee

Every indexed document version is recorded in the M6 lineage store before the pipeline exits.
`trace_answer_to_sources(conn, answer_id)` walks the full chain:

```
answer -> retrievals -> chunks -> source_documents -> content_hash
```

`impact_of_version(conn, doc_id, version_id)` answers the reverse question: which answers
cited this version, and will break if the document is updated?

## Quickstart

```bash
# One pipeline run (no Prefect server needed):
python pipeline_flow.py

# End-to-end oracle:
python smoke.py

# CI:
python -m pytest tests/ -v
```

## Module composition map

```
module7-pipeline/
  lib/
    m2_ingest.py            <- M2 run_ingest, bootstrap_db, merge_gold
    m2_freshness_check.py   <- M2 check_freshness
    m4_kafka_sim.py         <- M4 Topic, Producer, ConsumerGroup
    m4_cdc_pipeline.py      <- M4 cdc_source, apply_event, LagMonitor
    m4_corpus_store.py      <- M4 bootstrap_db, merge_one_document (extends M2)
    m5_lakehouse.py         <- M5 write_corpus_v0/v1, read_version
    m5_choose_tier.py       <- M5 choose_tier (reference)
    m6_lineage.py           <- M6 LineageCapture, trace_answer_to_sources, impact_of_version
    m6_schema.py            <- M6 init_schema
  pipeline_flow.py          <- Prefect flow composing all five legs
  smoke.py                  <- End-to-end oracle (7 assertions, exits non-zero on failure)
  tests/
    test_pipeline.py        <- pytest form of same assertions
  seeds/
    corpus_raw.csv          <- Five-document batch seed corpus
  outputs/
    skill-pipeline.md       <- Portfolio write-up stub
```

## Engine versions (confirmed offline)

`prefect`, `deltalake`, `pandas`, `pyarrow`, `duckdb`, `sqlite3` (stdlib). All confirmed
available in the prior module builds.
