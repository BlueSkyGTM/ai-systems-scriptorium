"""broken_pipeline.py — the exam. A corpus pipeline with three injected defects.

This is the distilled Data Currents pipeline (ingest -> freshness check -> lineage
capture -> freshness gate) with three deliberate bugs, the same failure modes the M7
pipeline can hit:

  DEFECT 1 (freshness_check): a hardcoded future 'now' makes every source look ancient,
           so freshness fires even right after a successful load.
  DEFECT 2 (capture_lineage): the eval verdict is never recorded, so the lineage chain
           from answer to verdict is incomplete and impact analysis is blind.
  DEFECT 3 (freshness_gate): the breach is swallowed and logged instead of raised, so the
           pipeline reports success on a stale corpus. The gate does not fail loud.

Run it, see retrieval quality degrade with no alarm, then write diagnose.py to find the
three defects and fix.py to correct them.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import store

# DEFECT 1: a hardcoded future timestamp used as "now" in the freshness check.
FRESHNESS_NOW_BUG = "2099-01-01 00:00:00"


def freshness_check(db_path: str, now_ts: str) -> dict:
    now = FRESHNESS_NOW_BUG  # DEFECT 1: ignores now_ts, uses a hardcoded future date
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
    # DEFECT 2: the verdict is never recorded -> lineage chain is incomplete.
    conn.commit()
    conn.close()
    return {"answer_id": answer_id}


def freshness_gate(fresh: dict) -> dict:
    if fresh["is_stale"]:
        # DEFECT 3: the breach is logged and swallowed, never raised. Silent failure.
        print(f"[gate] WARNING stale source {fresh['source']} (continuing anyway)", file=sys.stderr)
        return {"blocked": False}
    return {"blocked": False}


def run(db_path: str, loaded_at: str, now_ts: str) -> dict:
    store.init_db(db_path)
    ingest = store.ingest(db_path, loaded_at)
    fresh = freshness_check(db_path, now_ts)
    lineage = capture_lineage(db_path)
    gate = freshness_gate(fresh)
    return {"ingest": ingest, "fresh": fresh, "lineage": lineage, "gate": gate, "raised": False}


if __name__ == "__main__":
    result = run("outputs/broken.db", loaded_at="2026-06-24 12:00:00", now_ts="2026-06-24 12:05:00")
    print(f"[broken_pipeline] ran to 'success'; stale={result['fresh']['is_stale']} "
          f"blocked={result['gate']['blocked']} (the corpus is stale but nothing stopped)")
