The user wants me to generate only the `diagnose.py` file for Module 8's exam. This is the diagnostic query set that students would write to identify the three defects in the broken pipeline.

Let me think about what needs to be in diagnose.py:

1. It's a diagnostic query set with six SQL/Python queries
2. Each query is a function returning a finding dict
3. Uses only sqlite3 + the lineage + corpus DBs
4. The reference impl is provided for self-checking
5. When run against a fixed pipeline, all 6 findings should be None

The defects to find:
- Defect 1: batch_now_ts hardcoded to "2099-01-01" → batch freshness breach always fires
- Defect 2: capture_lineage skips record_verdict → lineage chain is incomplete
- Defect 3: freshness_gate has retries=2 (should be 0) → gate doesn't fail loud

Six queries for three defects — so likely 2 queries per defect, or some queries overlap.

Let me design this carefully. Each function returns a finding dict (with defect info) or None (no defect found).

For the three defects:

**Defect 1 (batch_now_ts hardcoded to "2099-01-01"):**
- Query 1a: Check the batch timestamp in the corpus store — find documents with batch_now_ts far in the future
- Query 1b: Check freshness breach records in the lineage/gate tables

**Defect 2 (capture_lineage skips record_verdict):**
- Query 2a: Walk the lineage chain and find missing record_verdict edges
- Query 2b: Count lineage edge types — record_verdict should appear

**Defect 3 (freshness_gate has retries=2):**
- Query 3a: Inspect the gate configuration/metadata table for retries value
- Query 3b: Check gate failure logs for retry behavior

Let me write this more concretely. Since I don't have the exact M7 schema, I'll need to infer reasonable table structures:

- corpus_store: source_document table with version timestamps
- lineage DB: a lineage table with edges (source, target, edge_type, timestamp)
- gate metadata: a table tracking gate runs with retries, status

Let me structure the 6 queries:

```python
def find_freshness_breach_in_corpus(corpus_db_path) -> dict | None:
    """Query 1: Check if batch_now_ts is in the future."""
    
def find_freshness_breach_in_gate(corpus_db_path) -> dict | None:
    """Query 2: Check gate failure records for false freshness breaches."""

def find_missing_record_verdict_lineage(lineage_db_path) -> dict | None:
    """Query 3: Check if record_verdict edges exist in lineage."""

def find_incomplete_lineage_chain(lineage_db_path) -> dict | None:
    """Query 4: Walk lineage and find verdicts without record_verdict edges."""

def find_gate_retry_config(corpus_db_path) -> dict | None:
    """Query 5: Check gate config for non-zero retries."""

def find_gate_retry_behavior(corpus_db_path) -> dict | None:
    """Query 6: Check gate execution logs for retry attempts."""
```

Each function connects to the appropriate sqlite DB, runs a query, and returns either a finding dict (defect found) or None (no defect).

When the pipeline is FIXED, all functions return None.
When the pipeline is BROKEN, each function returns its finding.

Let me write the actual implementation. I need to be careful about what tables/schema exist. Since this is M7's pipeline, let me assume reasonable schema based on the description:

corpus_store DB tables:
- source_document: (doc_id, version, source, content_hash, ingested_at, batch_ts)
- gate_runs: (run_id, gate_name, status, retries, batch_ts, reason)

lineage DB tables:
- lineage_edges: (edge_id, source_id, source_type, target_id, target_type, edge_type, ts)
  - edge_type values: "capture_doc", "record_verdict", "freshness_check", etc.

Let me write robust queries that check for the defects.

Actually, let me think about this differently. The diagnose.py is supposed to run against the output of broken_pipeline.py OR fix.py. It inspects the databases produced by a run.

Let me make the queries defensive — if a table doesn't exist, treat that as no finding (or as a finding depending on context).

Here's my approach:

```python
"""
diagnose.py
Diagnostic Query Set for Module 8: The Diagnostic Exam.

Six queries that probe the corpus and lineage databases produced by
a pipeline run. Each function returns a finding dict describing the
defect it detected, or None if the database is clean.

Usage:
    python diagnose.py [--corpus path/to/corpus.db] [--lineage path/to/lineage.db]

Expected behaviour:
    - Against broken_pipeline output: queries 1-6 surface their respective defects.
    - Against fix output: every query returns None.
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
```

Now let me think about each query more carefully.

**Query 1 — find_batch_ts_in_future:**
Looks at the corpus DB for a batch_now_ts that's far in the future (e.g., after 2030 or any date more than 1 year from now). If found, returns the finding.

```python
def q1_batch_timestamp_future(corpus_db: str) -> dict[str, Any] | None:
    """Q1: Check whether any batch timestamp is implausibly in the future."""
    conn = sqlite3.connect(corpus_db)
    try:
        # Look at the batch metadata or gate runs for batch_now_ts
        rows = conn.execute("""
            SELECT batch_ts FROM gate_runs
            WHERE batch_ts > '2030-01-01'
            LIMIT 1
        """).fetchall()
        if rows:
            return {
                "defect_id": "D1",
                "title": "Batch timestamp hardcoded to future date",
                "detail": f"Found batch_ts = {rows[0][0]} which is implausibly far in the future. "
                          "Check batch_now_ts assignment in the pipeline.",
                "severity": "critical",
            }
    finally:
        conn.close()
    return None
```

Wait, I need to be more careful. Let me think about what tables M7's pipeline would actually produce.

From the M7 spec: "corpus_store has batch documents as source_document versions." So the corpus DB likely has:
- A table for documents/versions
- Metadata about batch ingestion

The lineage DB tracks edges between artifacts.

Let me also think about where the gate config/retries would be stored. The freshness_gate might write its config to a metadata table or the gate_runs table.

Since I'm the reference implementation author, I can define the schema expectations. But the broken_pipeline.py and fix.py would need to produce compatible schemas. Let me be reasonable about what tables exist.

Let me define the expected schema explicitly in comments and write queries against it.

Actually, the key constraint is: "diagnose.py uses only sqlite3 + the lineage + corpus DBs produced by a run of broken_pipeline.py."

So the DBs are produced by broken_pipeline.py. The schema is whatever broken_pipeline.py creates. Since this is an exam, the schema would be documented in the README.

Let me make reasonable assumptions and write the queries. I'll also add helper functions for safe DB access.

Let me finalize my design:

Tables in corpus DB:
- `source_document` (doc_id TEXT, version INT, source TEXT, content_hash TEXT, content TEXT, batch_id TEXT, ingested_at TEXT, batch_now_ts TEXT)
- `gate_run` (run_id TEXT, gate_name TEXT, status TEXT, retries INT, batch_now_ts TEXT, reason TEXT, ts TEXT)

Tables in lineage DB:
- `lineage_edge` (edge_id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT, source_type TEXT, target_id TEXT, target_type TEXT, edge_type TEXT, metadata TEXT, ts TEXT)
  - edge_type: 'batch_capture', 'record_verdict', 'freshness_gate_eval', 'gate_retry'

Now the six queries:

**Q1: batch_now_ts_in_future** — D1 detector
Query the corpus DB for any batch_now_ts that's implausibly in the future.

**Q2: false_freshness_breach** — D1 detector (confirming side)
Query gate_run table for freshness gate failures. If the gate failed but the documents aren't actually stale, that's the breach being caused by the future timestamp.

**Q3: missing_record_verdict_edges** — D2 detector
Query lineage DB for record_verdict edge type. If count == 0 but verdicts were captured, the chain is broken.

**Q4: incomplete_verdict_chain** — D2 detector (confirming side)
Walk lineage from verdict to source_document — if there's no record_verdict edge connecting them, the chain is incomplete.

**Q5: gate_retries_nonzero** — D3 detector
Query gate metadata/config for retries value. If retries > 0, the gate doesn't fail loud.

**Q6: gate_retry_evidence** — D3 detector (confirming side)
Query lineage or gate logs for retry attempts. If retries > 0 in execution, the gate retried instead of failing.

Let me also think about what happens when fix.py is run. All queries should return None because:
- Q1: batch_now_ts is real-time, not in future → None
- Q2: no false freshness breaches → None
- Q3: record_verdict edges exist → None
- Q4: chain is complete → None
- Q5: retries == 0 → None
- Q6: no retry evidence → None

Good.

Now let me write this. I'll also add a main() that runs all queries and prints findings.

```python
#!/usr/bin/env python3
"""
diagnose.py — Module 8 Diagnostic Query Set

Six probes that inspect the corpus and lineage databases produced by
a pipeline run.  Each probe returns a finding dict when it detects the
defect it targets, or None when the database is clean.

Run against the *broken* pipeline:
    python diagnose.py --corpus ./outputs/corpus.db --lineage ./outputs/lineage.db
    → six findings printed, one per defect (two probes per defect).

Run against the *fixed* pipeline:
    python diagnose.py --corpus ./outputs/corpus.db --lineage ./outputs/lineage.db
    → "No defects detected."  Every probe returns None.

Schema expectations (produced by pipeline_flow.py / broken_pipeline.py):

  corpus.db
    source_document(doc_id, version, source, content_hash, content,
                    batch_id, ingested_at, batch_now_ts)
    gate_run(run_id, gate_name, status, retries, batch_now_ts,
             reason, ts)

  lineage.db
    lineage_edge(edge_id PK, source_id, source_type, target_id,
                 target_type, edge_type, metadata_json, ts)
      edge_type ∈ {'batch_capture', 'record_verdict',
                   'freshness_gate_eval', 'gate_retry_attempt'}
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── helpers ──────────────────────────────────────────────────────────────────

FUTURE_THRESHOLD = "2030-01-01T00:00:00"


def _connect(db_path: str) -> sqlite3.Connection:
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def _defect(
    defect_id: str,
    title: str,
    detail: str,
    severity: str = "critical",
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "defect_id": defect_id,
        "title": title,
        "detail": detail,
        "severity": severity,
        "evidence": evidence or {},
    }
```

Now the six query functions:

```python
# ══════════════════════════════════════════════════════════════════════════════
#  DEFECT 1  —  batch_now_ts hardcoded to a future date
# ══════════════════════════════════════════════════════════════════════════════

def q01_batch_ts_in_future(corpus_db: str) -> dict[str, Any] | None:
    """
    Q1  — Probe the corpus store for an implausible future batch timestamp.

    Checks ``source_document.batch_now_ts`` and ``gate_run.batch_now_ts``.
    If any value exceeds FUTURE_THRESHOLD the probe fires.
    """
    conn = _connect(corpus_db)
    try:
        evidence: dict[str, Any] = {}

        if _table_exists(conn, "source_document"):
            row = conn.execute(
                f"SELECT batch_now_ts, COUNT(*) AS n "
                f"FROM source_document "
                f"WHERE batch_now_ts > '{FUTURE_THRESHOLD}' "
                f"GROUP BY batch_now_ts ORDER BY n DESC LIMIT 1"
            ).fetchone()
            if row:
                evidence["source_document"] = {
                    "batch_now_ts": row["batch_now_ts"],
                    "count": row["n"],
                }

        if _table_exists(conn, "gate_run"):
            row = conn.execute(
                f"SELECT batch_now_ts, COUNT(*) AS n "
                f"FROM gate_run "
                f"WHERE batch_now_ts > '{FUTURE_THRESHOLD}' "
                f"GROUP BY batch_now_ts ORDER BY n DESC LIMIT 1"
            ).fetchone()
            if row:
                evidence["gate_run"] = {
                    "batch_now_ts": row["batch_now_ts"],
                    "count": row["n"],
                }

        if evidence:
            bad_ts = (
                evidence.get("source_document", {}).get("batch_now_ts")
                or evidence.get("gate_run", {}).get("batch_now_ts")
            )
            return _defect(
                "D1",
                "Batch timestamp is hardcoded to a future date",
                f"batch_now_ts = {bad_ts!r} exceeds {FUTURE_THRESHOLD}. "
                "The freshness gate will always fire because every "
                "document appears stale relative to the wall clock. "
                "Inspect the assignment of batch_now_ts in the pipeline.",
                severity="critical",
                evidence=evidence,
            )
    finally:
        conn.close()
    return None


def q02_false_freshness_breach(corpus_db: str) -> dict[str, Any] | None:
    """
    Q2  — Cross-check gate_run failures against actual document freshness.

    If the freshness gate reported a 'breach' but the source documents'
    ``ingested_at`` timestamps are recent (within 24 h of the batch),
    the breach is a false positive caused by Defect 1.
    """
    conn = _connect(corpus_db)
    try:
        if not (_table_exists(conn, "gate_run")
                and _table_exists(conn, "source_document")):
            return None

        # Find freshness gate failures
        failed_gates = conn.execute(
            "SELECT run_id, batch_now_ts, reason FROM gate_run "
            "WHERE gate_name = 'freshness_gate' AND status = 'FAIL'"
        ).fetchall()

        if not failed_gates:
            return None

        # Are the documents actually stale?
        # If ingested_at is within a reasonable window of *now*, the breach
        # is false.
        now_iso = datetime.now(timezone.utc).isoformat()
        total_docs = conn.execute(
            "SELECT COUNT(*) AS n FROM source_document"
        ).fetchone()["n"]
        # Documents whose ingested_at is recent (< 7 days from now)
        recent_cutoff = datetime.now(timezone.utc)
        recent_cutoff_str = recent_cutoff.replace(
            day=max(1, recent_cutoff.day - 7)
        ).isoformat()
        recent_docs = conn.execute(
            f"SELECT COUNT(*) AS n FROM source_document "
            f"WHERE ingested_at >= '{recent_cutoff_str}'"
        ).fetchone()["n"]

        # If >50% of documents are recent but gate failed → false breach
        if total_docs > 0 and recent_docs / total_docs > 0.5:
            return _defect(
                "D1",
                "Freshness gate fails on documents that are actually fresh",
                f"The freshness gate reported FAIL for {len(failed_gates)} "
                f"run(s), but {recent_docs}/{total_docs} source documents "
                f"have recent ingested_at timestamps (>= {recent_cutoff_str}). "
                "This is a false-positive breach — the batch_now_ts "
                "comparison is using a bogus reference timestamp.",
                severity="critical",
                evidence={
                    "failed_gate_runs": [dict(r) for r in failed_gates],
                    "recent_docs": recent_docs,
                    "total_docs": total_docs,
                },
            )
    finally:
        conn.close()
    return None
```

Hmm, wait. The `recent_cutoff` calculation with `.replace(day=max(1, recent_cutoff.day - 7))` is fragile. Let me use a simpler approach — just check the ingested_at against a reasonable date like "2020-01-01" to "2030-01-01". If the ingested_at is in a normal range but the batch_now_ts is in 2099, that's the issue.

Actually, let me simplify. The key check for Q2 is:
- Gate failed with a freshness breach
- But the documents' ingested_at are recent (not stale)
- This means the breach is false

Let me just compare ingested_at against a reasonable "stale" threshold. If documents were ingested within the last 30 days (relative to now), they're fresh.

Let me use `datetime.now()` properly:

```python
from datetime import timedelta
recent_cutoff = datetime.now(timezone.utc) - timedelta(days=30)
```

OK let me now write Q3-Q6.

```python
# ══════════════════════════════════════════════════════════════════════════════
#  DEFECT 2  —  capture_lineage skips record_verdict edges
# ═════════════════════════════════════