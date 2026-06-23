"""
smoke.py
Module 3 — Orchestration smoke test.

Run:
    python smoke.py
Exits 0 if all assertions pass, non-zero otherwise.
Prints PASS/FAIL per assertion.

Each assertion is self-contained and uses a fresh temp DB + temp CSV so
they can run in any order and are fully deterministic.
"""

import os
import shutil
import sqlite3
import sys
import tempfile
import time

# ---------------------------------------------------------------------------
# Bootstrap: make sure we can import from this directory
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pipeline_flow as pf
from pipeline_flow import pipeline_flow, ALERTS, on_flow_failure
from ingest import run_ingest, bootstrap_db

SEEDS_CSV = os.path.join(HERE, "seeds", "corpus_raw.csv")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_db(tmp_dir: str) -> str:
    """Return path to a new empty corpus DB in tmp_dir."""
    return os.path.join(tmp_dir, "corpus.db")


def count_source_docs(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    n = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
    conn.close()
    return n


def count_versions_for_doc(db_path: str, doc_id: str) -> int:
    conn = sqlite3.connect(db_path)
    n = conn.execute(
        "SELECT COUNT(*) FROM source_documents WHERE doc_id = ?", (doc_id,)
    ).fetchone()[0]
    conn.close()
    return n


# ---------------------------------------------------------------------------
# Assertion runners
# ---------------------------------------------------------------------------

results: list[tuple[str, bool, str]] = []  # (label, passed, detail)


def check(label: str, passed: bool, detail: str = "") -> bool:
    tag = "PASS" if passed else "FAIL"
    line = f"  [{tag}] {label}"
    if detail:
        line += f"  -- {detail}"
    print(line)
    results.append((label, passed, detail))
    return passed


# ---------------------------------------------------------------------------
# 1. Structure: tasks exist and the module defines the expected task names
# ---------------------------------------------------------------------------

def assert_structure():
    """
    The flow module exposes four tasks in the expected dependency order.
    We verify by name (Prefect wraps each function in a Task object whose
    .name attribute we seeded explicitly).
    """
    from prefect import Task
    import pipeline_flow as pf_mod

    task_names = []
    for attr_name in ("extract", "ingest", "transform", "freshness_gate"):
        obj = getattr(pf_mod, attr_name, None)
        is_task = isinstance(obj, Task)
        check(
            f"structure: '{attr_name}' is a Prefect Task",
            is_task,
            f"type={type(obj).__name__}",
        )
        if is_task:
            task_names.append(obj.name)

    # Order assertion: all four are present
    expected = {"extract", "ingest", "transform", "freshness_gate"}
    check(
        "structure: all four tasks present",
        expected == set(task_names),
        f"found={set(task_names)}",
    )

    # on_failure hook is registered on the flow.
    # In Prefect 3.x the registered hooks live in on_failure_hooks (a list),
    # not on_failure (which is a bound method for registering new hooks).
    from prefect import Flow
    flow_obj = getattr(pf_mod, "pipeline_flow", None)
    hooks = getattr(flow_obj, "on_failure_hooks", None)
    has_hook = (
        isinstance(flow_obj, Flow)
        and hooks is not None
        and len(hooks) > 0
    )
    check(
        "structure: pipeline_flow has on_failure hook",
        has_hook,
        f"on_failure_hooks={hooks}",
    )


# ---------------------------------------------------------------------------
# 2. Topological run: tasks execute in order, gold tables populated
# ---------------------------------------------------------------------------

def assert_topological_run():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        db = fresh_db(tmp)

        result = pipeline_flow(
            run_date="2026-01-15",
            corpus_csv=SEEDS_CSV,
            db_path=db,
        )

        # ingest summary present
        check(
            "topological_run: ingest_summary in result",
            "ingest_summary" in result and result["ingest_summary"]["status"] == "success",
            str(result.get("ingest_summary")),
        )

        # source_documents populated
        n = count_source_docs(db)
        check(
            "topological_run: source_documents populated",
            n > 0,
            f"rows={n}",
        )

        # freshness_results present (gate passed)
        fr = result.get("freshness_results", [])
        check(
            "topological_run: freshness_gate returned results",
            isinstance(fr, list) and len(fr) > 0,
            f"freshness_results={fr}",
        )

        # transform_status present
        ts = result.get("transform_status")
        check(
            "topological_run: transform returned a status string",
            ts in ("dbt_success", "transform_skipped"),
            f"transform_status={ts!r}",
        )


# ---------------------------------------------------------------------------
# 3. Retry: injected transient failure recovers; task attempted expected times
# ---------------------------------------------------------------------------

def assert_retry():
    """
    Monkey-patch run_ingest to fail once then succeed; verify the flow
    completes and the ingest task was called more than once.
    """
    import ingest as ingest_mod

    original_run_ingest = ingest_mod.run_ingest
    call_count = {"n": 0}

    def flaky_run_ingest(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise RuntimeError("Transient DB lock — injected failure")
        return original_run_ingest(*args, **kwargs)

    # Patch inside pipeline_flow module since it imports run_ingest at module level
    import pipeline_flow as pf_mod
    original_in_pf = pf_mod.run_ingest
    pf_mod.run_ingest = flaky_run_ingest

    try:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            db = fresh_db(tmp)
            result = pipeline_flow(
                run_date="2026-01-16",
                corpus_csv=SEEDS_CSV,
                db_path=db,
            )

        check(
            "retry: flow completed despite initial failure",
            result["ingest_summary"]["status"] == "success",
            f"ingest_summary={result['ingest_summary']}",
        )
        check(
            "retry: ingest called more than once (retry fired)",
            call_count["n"] >= 2,
            f"call_count={call_count['n']}",
        )
    finally:
        pf_mod.run_ingest = original_in_pf


# ---------------------------------------------------------------------------
# 4. Alert on freshness breach: stale DB -> run fails, ALERTS fires
# ---------------------------------------------------------------------------

def assert_alert_on_breach():
    """
    Run the flow with freshness_now_ts set far in the future (> SLO) so
    check_freshness sees a stale corpus.  Assert the run raises (Prefect marks
    it Failed), and that ALERTS is non-empty with the stale source referenced.
    """
    pf.ALERTS.clear()

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        db = fresh_db(tmp)
        # Ingest so there IS a load row, but then advance time by 1000 hours
        run_ingest(csv_path=SEEDS_CSV, db_path=db)

        # 1000 hours from now — well past the 25-hour SLO
        from datetime import datetime, timedelta
        far_future = (datetime.utcnow() + timedelta(hours=1000)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        flow_failed = False
        try:
            pipeline_flow(
                run_date="2026-01-17",
                corpus_csv=SEEDS_CSV,
                db_path=db,
                freshness_now_ts=far_future,
            )
        except Exception:
            flow_failed = True

        check(
            "alert_breach: flow raises when freshness gate breaches",
            flow_failed,
            "expected exception not raised" if not flow_failed else "",
        )
        check(
            "alert_breach: ALERTS list non-empty after breach",
            len(pf.ALERTS) > 0,
            f"ALERTS={pf.ALERTS}",
        )


# ---------------------------------------------------------------------------
# 5. Backfill idempotency: two runs, identical CSV -> zero new versions on 2nd
# ---------------------------------------------------------------------------

def assert_backfill_idempotency():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        db = fresh_db(tmp)

        # First run
        r1 = pipeline_flow(
            run_date="2026-01-18",
            corpus_csv=SEEDS_CSV,
            db_path=db,
        )
        count_after_1 = count_source_docs(db)

        # Second run — same CSV, same content
        r2 = pipeline_flow(
            run_date="2026-01-19",  # different date, same data
            corpus_csv=SEEDS_CSV,
            db_path=db,
        )
        count_after_2 = count_source_docs(db)

        check(
            "backfill_idempotency: first run inserts rows",
            count_after_1 > 0,
            f"rows_after_1={count_after_1}",
        )
        check(
            "backfill_idempotency: second run adds zero new source_document versions",
            count_after_2 == count_after_1,
            f"rows_after_1={count_after_1}, rows_after_2={count_after_2}",
        )
        # new_versions on 2nd run should be 0
        new_v2 = r2["ingest_summary"]["new_versions"]
        check(
            "backfill_idempotency: new_versions=0 on repeat run",
            new_v2 == 0,
            f"new_versions={new_v2}",
        )


# ---------------------------------------------------------------------------
# 6. Negative / freshness breach is a real failure
#    (re-uses the breach scenario from #4 but specifically asserts run FAILS)
# ---------------------------------------------------------------------------

def assert_negative_freshness_fails():
    """
    Demonstrates the negative path: the flow is a hard gate, not a soft warning.

    Two sub-cases:
    a) Missing source CSV -> extract() fails -> flow fails immediately.
    b) freshness_gate.fn called directly on a never-loaded DB -> stale -> raises.

    ignore_cleanup_errors=True avoids Windows "file in use" errors when
    Prefect's temp SQLite still has a handle at TemporaryDirectory exit.
    """
    # Sub-case a: missing CSV -> extract raises -> flow fails
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        db = fresh_db(tmp)
        flow_raised = False
        try:
            pipeline_flow(
                run_date="2026-01-20",
                corpus_csv="/nonexistent/missing.csv",
                db_path=db,
            )
        except Exception:
            flow_raised = True
        check(
            "negative: missing CSV causes flow failure (DAG hard-fails early)",
            flow_raised,
        )

    # Sub-case b: check_freshness on a never-loaded DB -> all sources are stale.
    # We call check_freshness directly (the same logic freshness_gate wraps)
    # to isolate the staleness check without requiring a Prefect run context.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        db = fresh_db(tmp)
        bootstrap_db(db)   # schema + SLOs, no load rows
        from freshness_check import check_freshness
        fc_results = check_freshness(db_path=db, now_ts=None)
        all_stale = all(r["is_stale"] for r in fc_results)
        check(
            "negative: never-loaded DB -> all sources stale (freshness gate would fail)",
            all_stale and len(fc_results) > 0,
            f"freshness_results={fc_results}",
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("smoke.py — M3 Orchestration smoke tests")
    print("=" * 60)

    print("\n[1] Structure assertions")
    assert_structure()

    print("\n[2] Topological run")
    assert_topological_run()

    print("\n[3] Retry on transient failure")
    assert_retry()

    print("\n[4] Alert on freshness breach")
    assert_alert_on_breach()

    print("\n[5] Backfill idempotency")
    assert_backfill_idempotency()

    print("\n[6] Negative: stale DB fails the flow")
    assert_negative_freshness_fails()

    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for _, p, _ in results if p)
    total  = len(results)
    print(f"Results: {passed}/{total} passed")
    if passed < total:
        print("\nFailed assertions:")
        for label, p, detail in results:
            if not p:
                print(f"  FAIL  {label}  {detail}")
        print("=" * 60)
        sys.exit(1)
    else:
        print("ALL PASS")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
