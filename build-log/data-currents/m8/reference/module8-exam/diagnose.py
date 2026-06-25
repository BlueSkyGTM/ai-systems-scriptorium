"""diagnose.py — the diagnostic query set.

Six checks that locate the three defects in a pipeline run. Each returns a finding dict:
{name, defect, found, detail}. `found=True` means the defect is present. Run these against
a broken run and all three defects light up; run them against a fixed run and they go dark.

This is the diagnostic skill the book has been building toward: every defect leaves a
SQL-queryable or result-visible trace, and finding it is the job.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import store

FUTURE_THRESHOLD = "2090-01-01 00:00:00"


def q1_freshness_uses_future_now(db_path: str, result: dict) -> dict:
    """Defect 1: the freshness check's 'now' is a far-future hardcoded date."""
    now_used = result["fresh"]["now_used"]
    found = now_used >= FUTURE_THRESHOLD
    return {"name": "q1_future_now", "defect": "freshness_check hardcoded future now",
            "found": found, "detail": f"now_used={now_used}"}


def q2_stale_despite_recent_load(db_path: str, result: dict) -> dict:
    """Defect 1 symptom: source reads stale even though it was loaded moments ago.

    The tell is a stale verdict produced against a future 'now' rather than the real one.
    """
    loaded = store.last_load(db_path)
    reported_stale = result["fresh"]["is_stale"]
    found = reported_stale and result["fresh"]["now_used"] >= FUTURE_THRESHOLD
    return {"name": "q2_stale_despite_load", "defect": "freshness false positive",
            "found": found, "detail": f"is_stale={reported_stale} loaded_at={loaded}"}


def q3_answer_missing_verdict(db_path: str, result: dict) -> dict:
    """Defect 2: an answer exists with no eval verdict recorded."""
    conn = store.connect(db_path)
    rows = conn.execute(
        """
        SELECT a.answer_id
        FROM answers a
        LEFT JOIN eval_verdicts v ON v.answer_id = a.answer_id
        WHERE v.answer_id IS NULL
        """
    ).fetchall()
    conn.close()
    missing = [r["answer_id"] for r in rows]
    return {"name": "q3_missing_verdict", "defect": "capture_lineage skips record_verdict",
            "found": len(missing) > 0, "detail": f"answers without verdict: {missing}"}


def q4_lineage_chain_incomplete(db_path: str, result: dict) -> dict:
    """Defect 2 symptom: the answer -> retrieval -> chunk -> source -> verdict chain
    cannot be walked to a verdict."""
    conn = store.connect(db_path)
    row = conn.execute(
        """
        SELECT a.answer_id, r.chunk_id, c.doc_id, v.result AS verdict
        FROM answers a
        JOIN retrievals r ON r.answer_id = a.answer_id
        JOIN chunks c ON c.chunk_id = r.chunk_id
        LEFT JOIN eval_verdicts v ON v.answer_id = a.answer_id
        WHERE a.answer_id = 'ans_001'
        """
    ).fetchone()
    conn.close()
    incomplete = row is None or row["verdict"] is None
    return {"name": "q4_chain_incomplete", "defect": "lineage chain missing its verdict",
            "found": incomplete, "detail": f"traced verdict={None if row is None else row['verdict']}"}


def q5_gate_did_not_block(db_path: str, result: dict) -> dict:
    """Defect 3: the source is stale but the gate let the run continue."""
    stale = result["fresh"]["is_stale"]
    blocked = result["gate"]["blocked"]
    found = stale and not blocked
    return {"name": "q5_silent_gate", "defect": "freshness_gate swallows the breach",
            "found": found, "detail": f"is_stale={stale} blocked={blocked}"}


def q6_summary(db_path: str, result: dict) -> dict:
    """Roll-up: how many of the targeted defects are present."""
    checks = [q1_freshness_uses_future_now, q2_stale_despite_recent_load,
              q3_answer_missing_verdict, q5_gate_did_not_block]
    n = sum(1 for c in checks if c(db_path, result)["found"])
    return {"name": "q6_summary", "defect": "defect count", "found": n > 0,
            "detail": f"{n} defect(s) detected"}


ALL_CHECKS = [
    q1_freshness_uses_future_now,
    q2_stale_despite_recent_load,
    q3_answer_missing_verdict,
    q4_lineage_chain_incomplete,
    q5_gate_did_not_block,
    q6_summary,
]


def diagnose(db_path: str, result: dict) -> list[dict]:
    return [check(db_path, result) for check in ALL_CHECKS]


if __name__ == "__main__":
    import broken_pipeline
    res = broken_pipeline.run("outputs/broken.db", "2026-06-24 12:00:00", "2026-06-24 12:05:00")
    for f in diagnose("outputs/broken.db", res):
        flag = "DEFECT" if f["found"] else "  ok  "
        print(f"  [{flag}] {f['name']}: {f['detail']}")
