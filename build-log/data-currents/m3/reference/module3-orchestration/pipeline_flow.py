"""
pipeline_flow.py
Module 3 — Orchestration: the nightly corpus pipeline as a Prefect 3.x DAG.

The flow schedules and runs the M2 ingest pipeline on a nightly cadence,
adds a dbt-build transform step (no-op if dbt is absent), then gates on
freshness before marking the run complete.

Schedule (for documentation/deployment — the scheduler is NOT started here):
    Nightly at 02:00 UTC:  cron="0 2 * * *"

Offline test usage (no Prefect server needed):
    python pipeline_flow.py              # one run with today's date
    python pipeline_flow.py --date 2026-01-15

The flow is also importable:
    from pipeline_flow import pipeline_flow
    result = pipeline_flow(run_date="2026-01-15",
                           corpus_csv="seeds/corpus_raw.csv",
                           db_path="/tmp/test.db")
"""

import os
import subprocess
import sys
from datetime import datetime

from prefect import flow, task, get_run_logger

# ---------------------------------------------------------------------------
# M2 imports (copied into this artifact)
# ---------------------------------------------------------------------------
from ingest import run_ingest
from freshness_check import check_freshness

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# In-memory alert log — fires on flow failure via on_failure hook
# ---------------------------------------------------------------------------
ALERTS: list[dict] = []


def on_flow_failure(flow, flow_run, state):
    """
    Prefect on_failure hook: called when the flow run enters a Failed state.
    Appends a record to the module-level ALERTS list and writes a log line.
    The hook signature is (flow, flow_run, state) per Prefect 3.x convention.
    """
    message = (
        f"ALERT: flow '{flow.name}' run '{flow_run.name}' failed "
        f"at {datetime.utcnow().isoformat()} — state={state.name}"
    )
    ALERTS.append({
        "flow":     flow.name,
        "run":      flow_run.name,
        "state":    state.name,
        "fired_at": datetime.utcnow().isoformat(),
        "message":  message,
    })
    # Write to stderr so it surfaces in pytest capture as well
    print(f"[ALERT HOOK] {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@task(name="extract", retries=2, retry_delay_seconds=0.1)
def extract(run_date: str, corpus_csv: str) -> str:
    """
    Extract: locate / validate the source CSV for this run_date.

    In production this task would fetch the CSV from S3/GCS or a DB export
    scoped to run_date.  Here it confirms the local seed file exists and
    returns its path — that is the teachable contract: extract yields a path.

    retries=2 means transient I/O failures get two more attempts before the
    task (and therefore the flow) fails.
    """
    logger = get_run_logger()
    if not os.path.isfile(corpus_csv):
        raise FileNotFoundError(f"[extract] CSV not found: {corpus_csv}")
    logger.info(f"[extract] run_date={run_date}  source={corpus_csv}")
    return corpus_csv


@task(name="ingest", retries=2, retry_delay_seconds=0.1)
def ingest(csv_path: str, db_path: str) -> dict:
    """
    Ingest: run the M2 idempotent MERGE (bronze -> silver -> gold).

    Accepts the CSV path emitted by extract() and the target DB path.
    Returns the ingest summary dict for downstream tasks.

    retries=2 guards against transient SQLite lock contention.
    """
    logger = get_run_logger()
    logger.info(f"[ingest] csv={csv_path}  db={db_path}")
    summary = run_ingest(csv_path=csv_path, db_path=db_path)
    logger.info(f"[ingest] summary={summary}")
    return summary


@task(name="transform", retries=0)
def transform(ingest_summary: dict, db_path: str) -> str:
    """
    Transform: run dbt build if dbt is available; skip gracefully if not.

    In a production pipeline this task runs 'dbt build --select tag:corpus'
    against the M2 dbt project, promoting bronze -> silver -> gold SQL models.
    Because dbt is an optional dependency in this artifact (and in CI), the
    task degrades to a documented no-op rather than failing the pipeline.

    Returns: "dbt_success" | "transform_skipped"
    """
    logger = get_run_logger()

    # Locate the M2 dbt project (sibling in the build-log tree)
    m2_dbt = os.path.join(
        HERE, "..", "..", "..", "..", "m2", "reference", "module2-ingestion"
    )
    m2_dbt = os.path.normpath(m2_dbt)

    dbt_available = False
    try:
        result = subprocess.run(
            ["dbt", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        dbt_available = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if dbt_available and os.path.isdir(m2_dbt):
        logger.info(f"[transform] running dbt build in {m2_dbt}")
        proc = subprocess.run(
            ["dbt", "build"],
            cwd=m2_dbt,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"[transform] dbt build failed:\n{proc.stdout}\n{proc.stderr}"
            )
        logger.info("[transform] dbt build succeeded")
        return "dbt_success"
    else:
        logger.warning(
            "[transform] dbt not available or M2 project not found — "
            "transform step skipped. "
            "Install dbt-duckdb and ensure M2 project is present to enable."
        )
        return "transform_skipped"


@task(name="freshness_gate", retries=0)
def freshness_gate(db_path: str, now_ts: str | None = None) -> list[dict]:
    """
    Freshness gate: check every source_id in freshness_slos against its SLO.

    Raises RuntimeError (-> Prefect Failed state -> on_failure hook fires) if
    ANY source is stale.  This is the hard gate: a stale corpus must not
    silently serve retrieval traffic.

    now_ts: optional ISO timestamp for test injection (skews 'now' forward).
    """
    logger = get_run_logger()
    logger.info(f"[freshness_gate] db={db_path}  now_ts={now_ts!r}")
    results = check_freshness(db_path=db_path, now_ts=now_ts)

    stale = [r for r in results if r["is_stale"]]
    if stale:
        stale_ids = [r["source_id"] for r in stale]
        raise RuntimeError(
            f"[freshness_gate] STALE sources detected: {stale_ids}. "
            "Pipeline marked FAILED; on_failure alert hook should fire."
        )

    logger.info(f"[freshness_gate] all {len(results)} source(s) are fresh")
    return results


# ---------------------------------------------------------------------------
# Flow
# ---------------------------------------------------------------------------

# Schedule: nightly at 02:00 UTC.  To activate in a Prefect deployment:
#   from prefect.schedules import CronSchedule
#   @flow(..., schedules=[CronSchedule(cron="0 2 * * *")])
# We do NOT attach a live schedule here — the artifact is tested by calling
# pipeline_flow() directly; no Prefect server is required.

@flow(
    name="corpus-pipeline",
    description=(
        "Nightly scheduled DAG: extract -> ingest -> transform -> freshness_gate. "
        "Fires on_flow_failure alert if any task fails or the freshness gate breaches."
    ),
    on_failure=[on_flow_failure],
)
def pipeline_flow(
    run_date: str | None = None,
    corpus_csv: str | None = None,
    db_path: str | None = None,
    freshness_now_ts: str | None = None,
) -> dict:
    """
    Orchestrated nightly corpus pipeline.

    Args:
        run_date:          ISO date string for this batch (defaults to today).
        corpus_csv:        Path to the source CSV (defaults to seeds/corpus_raw.csv).
        db_path:           Path to the SQLite corpus DB (defaults to corpus.db next to this file).
        freshness_now_ts:  Override for 'now' in the freshness gate (for testing).

    Returns dict with keys: run_date, csv_path, ingest_summary, transform_status,
    freshness_results.
    """
    if run_date is None:
        run_date = datetime.utcnow().strftime("%Y-%m-%d")
    if corpus_csv is None:
        corpus_csv = os.path.join(HERE, "seeds", "corpus_raw.csv")
    if db_path is None:
        db_path = os.path.join(HERE, "corpus.db")

    # ---- DAG edges (each result passes into the next task) ----
    csv_path       = extract(run_date=run_date, corpus_csv=corpus_csv)
    ingest_summary = ingest(csv_path=csv_path, db_path=db_path)
    transform_status = transform(ingest_summary=ingest_summary, db_path=db_path)
    freshness_results = freshness_gate(db_path=db_path, now_ts=freshness_now_ts)
    # ---- End DAG ----

    return {
        "run_date":          run_date,
        "csv_path":          csv_path,
        "ingest_summary":    ingest_summary,
        "transform_status":  transform_status,
        "freshness_results": freshness_results,
    }


# ---------------------------------------------------------------------------
# __main__ convenience runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the M3 corpus pipeline flow for one date (offline, no server)."
    )
    parser.add_argument(
        "--date", default=None,
        help="Run date (ISO, e.g. 2026-01-15). Defaults to today.",
    )
    parser.add_argument(
        "--csv", default=None,
        help="Path to corpus CSV. Defaults to seeds/corpus_raw.csv.",
    )
    parser.add_argument(
        "--db", default=None,
        help="Path to SQLite DB. Defaults to corpus.db next to this file.",
    )
    args = parser.parse_args()

    result = pipeline_flow(
        run_date=args.date,
        corpus_csv=args.csv,
        db_path=args.db,
    )
    print(f"\n[pipeline_flow] result={result}")
    print("[pipeline_flow] DONE")
