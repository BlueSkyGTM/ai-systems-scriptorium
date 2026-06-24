# The Freshness-Lineage Proof

A pipeline that runs is not enough; it must refuse a stale corpus and trace every answer to a content hash.

## The Gate Fires on a Stale Source

You inject a current timestamp 30 hours past the ingest time. This action pushes the data beyond the 25-hour SLO defined in the [batch freshness SLO](../module2/the-batch-freshness-slo.md). The freshness gate raises an exception. The pipeline halts immediately. The system catches the exception and triggers the alert hook configured for [alerting on breach](../module3/alerting-on-breach.md).

The `_run_negative` function in `smoke.py` executes this exact failure path.

```python
def _run_negative(tmp: str) -> None:
    """
    7. Negative / deficient run:
       Inject a 'now' timestamp that is 30 hours after the last batch load
       (past the 25-hour corpus_raw SLO) and verify the gate fails + alert fires.
    """
    from pipeline_flow import run_pipeline, ALERTS, clear_alerts

    csv_path        = os.path.join(tmp, "corpus_raw.csv")
    db_path         = os.path.join(tmp, "corpus.db")
    lineage_db_path = os.path.join(tmp, "lineage.db")
    delta_path      = os.path.join(tmp, "corpus_delta")

    write_csv(csv_path, BATCH_DOCS)

    base_time = 1_750_000_000.0
    # Inject a 'now' 30 hours after ingest -> age_hours=30 > SLO=25 -> STALE
    batch_now_ts_stale = "2026-06-16 18:00:00"

    clear_alerts()
    gate_failed = False
    try:
        run_pipeline(
            csv_path=csv_path,
            db_path=db_path,
            lineage_db_path=lineage_db_path,
            delta_path=delta_path,
            cdc_events=[
                {
                    "op":         "update",
                    "doc_id":     "doc_alpha",
                    "title":      "Vector Databases Explained (v2)",
                    "body":       "Updated body text for the negative run.",
                    "event_time": base_time,
                }
            ],
            stream_slo_seconds=5.0,
            stream_apply_time=base_time,
            batch_now_ts=batch_now_ts_stale,
        )
    except Exception:
        gate_failed = True

    print("\n--- 7. Negative run ---")
    check("7a. Stale batch source FAILS the freshness gate",
          gate_failed,
          "Expected RuntimeError from freshness_gate on stale corpus_raw")

    check("7b. on_failure alert hook fired",
          len(ALERTS) >= 1,
          f"ALERTS: {ALERTS}")
```

## Tracing an Answer to Its Sources

Freshness guarantees valid data at ingest. Lineage guarantees verifiable data at query time. Walk the graph backward from a generated answer. Unpack the answer to its source documents, chunks, exact content hashes, and final evaluation verdicts. This replaces the manual CTE walks from [querying the lineage store](../module6/querying-the-lineage-store.md) and relies on the structure of the [lineage graph](../module6/the-lineage-graph.md).

The `trace_answer_to_sources` function in `lib/m6_lineage.py` performs this backward lookup.

```python
def trace_answer_to_sources(
    conn: sqlite3.Connection,
    answer_id: str,
) -> list[dict[str, Any]]:
    """
    BACKWARD lineage walk (M1's 08_lineage_walk.sql, automated and extended).

    For a given answer_id, follows:
        answers -> retrievals -> chunks -> source_documents -> (content_hash)
    and joins in the eval_verdicts so the caller sees the full terminal state.

    Returns a list of dicts, one per (chunk, source_doc_version, verdict) row.
    Returns [] for unknown answer_id.

    This replaces M1's manual WITH-CTE walk: the lineage store guarantees
    every join resolves (capture-by-construction), so no NULL-checking needed.
    """
    cur = conn.execute(
        """
        SELECT
            a.answer_id,
            a.query,
            a.answer_text,
            r.chunk_id,
            r.rank,
            r.score           AS retrieval_score,
            c.source_doc_id,
            c.source_doc_version,
            sd.content_hash,
            ev.criterion,
            ev.verdict,
            ev.score          AS verdict_score
        FROM answers a
        JOIN retrievals r     ON r.answer_id  = a.answer_id
        JOIN chunks c         ON c.chunk_id   = r.chunk_id
        JOIN source_documents sd
                              ON sd.doc_id    = c.source_doc_id
                             AND sd.version_id= c.source_doc_version
        LEFT JOIN eval_verdicts ev ON ev.answer_id = a.answer_id
        WHERE a.answer_id = ?
        ORDER BY r.rank, ev.criterion
        """,
        (answer_id,),
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
```

## Impact Analysis: Which Answers Break?

Lineage also works forward. A Change Data Capture event updates `doc_alpha` to version 2. The existing answers built on version 1 become stale. Reverse the query to find them. Ask the system which answers cited `doc_alpha` version 1. The store returns the exact affected records. You can now invalidate or regenerate them automatically. This capability stems from [capturing lineage automatically](../module6/capturing-lineage-automatically.md).

The `impact_of_version` function in `lib/m6_lineage.py` executes this forward impact analysis.

```python
def impact_of_version(
    conn: sqlite3.Connection,
    doc_id: str,
    version_id: str,
) -> list[dict[str, Any]]:
    """
    FORWARD impact analysis.

    Given a source-doc version, return every answer that cited a chunk from it.
    Use case: "If I update doc-1 v1, which answers are affected?"

    Returns a list of dicts with answer_id, query, answer_text, chunk_id.
    Returns [] if no answers cited any chunk from this version.
    """
    cur = conn.execute(
        """
        SELECT DISTINCT
            a.answer_id,
            a.query,
            a.answer_text,
            c.chunk_id
        FROM source_documents sd
        JOIN chunks c         ON c.source_doc_id      = sd.doc_id
                             AND c.source_doc_version  = sd.version_id
        JOIN retrievals r     ON r.chunk_id            = c.chunk_id
        JOIN answers a        ON a.answer_id           = r.answer_id
        WHERE sd.doc_id = ? AND sd.version_id = ?
        ORDER BY a.answer_id
        """,
        (doc_id, version_id),
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
```

## Core Concepts

A stale batch source fails the pipeline by raising an exception and firing an alert hook.
Backward lineage walks from an answer to its exact source documents, chunks, and content hashes.
Forward impact analysis uses lineage to identify existing answers degraded by a source document update.

"Why did the model say that?" is now a query.

<div class="claude-handoff" data-exercise="exercises/module7/the-freshness-lineage-proof/">
**Inspect It in Claude Code** · Exercise · exercises/module7/the-freshness-lineage-proof/
</div>