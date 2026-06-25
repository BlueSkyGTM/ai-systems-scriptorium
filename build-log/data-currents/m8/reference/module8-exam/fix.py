"""fix.py — the corrected pipeline. The three defects of broken_pipeline.py, repaired.

  FIX 1 (freshness_check): use the real `now_ts`, so a freshly loaded source reads fresh.
  FIX 2 (capture_lineage): record the eval verdict, completing the lineage chain.
  FIX 3 (freshness_gate): raise FreshnessBreach on a stale source, so the gate fails loud.

A fix restores the contract the defect broke; it does not just silence the symptom.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import store


class FreshnessBreach(RuntimeError):
    """Raised when the freshness gate finds a stale source. The pipeline must stop."""


def freshness_check(db_path: str, now_ts: str) -> dict:
    now = now_ts  # FIX 1: use the real 'now', not a hardcoded date
    loaded = store.last_load(db_path)
    age = store.hours_between(loaded, now)
    return {
        "source": store.SOURCE_ID,
        "loaded_at": loaded,
        "now_used": now,
        "age_hours": round(age, 2),
        "is_stale": age > store.MAX_AGE_HOURS,
    }


def capture_lineage(db_path: str) -> dict:
    conn = store.connect(db_path)
    answer_id = "ans_001"
    conn.execute(
        "INSERT INTO answers VALUES (?, ?, ?)",
        (answer_id, "what is a vector database?", "it stores embeddings for retrieval"),
    )
    conn.execute("INSERT INTO retrievals VALUES (?, ?)", (answer_id, "doc_alpha_c0"))
    # FIX 2: record the verdict so the answer -> verdict chain is complete.
    conn.execute(
        "INSERT INTO eval_verdicts VALUES (?, ?, ?)", (answer_id, "groundedness", "pass")
    )
    conn.commit()
    conn.close()
    return {"answer_id": answer_id}


def freshness_gate(fresh: dict) -> dict:
    if fresh["is_stale"]:
        # FIX 3: fail loud. A stale corpus must stop the pipeline.
        raise FreshnessBreach(
            f"stale source {fresh['source']}: age {fresh['age_hours']}h > {store.MAX_AGE_HOURS}h"
        )
    return {"blocked": False}


def run(db_path: str, loaded_at: str, now_ts: str, *, raise_on_breach: bool = True) -> dict:
    store.init_db(db_path)
    ingest = store.ingest(db_path, loaded_at)
    fresh = freshness_check(db_path, now_ts)
    lineage = capture_lineage(db_path)
    raised = False
    try:
        gate = freshness_gate(fresh)
    except FreshnessBreach:
        raised = True
        gate = {"blocked": True}
        if raise_on_breach:
            raise
    return {"ingest": ingest, "fresh": fresh, "lineage": lineage, "gate": gate, "raised": raised}


if __name__ == "__main__":
    result = run("outputs/fixed.db", loaded_at="2026-06-24 12:00:00", now_ts="2026-06-24 12:05:00")
    print(f"[fix] healthy run: stale={result['fresh']['is_stale']} "
          f"blocked={result['gate']['blocked']} lineage_answer={result['lineage']['answer_id']}")
