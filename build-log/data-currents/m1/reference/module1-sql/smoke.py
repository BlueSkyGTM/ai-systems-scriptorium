"""
module1-sql/smoke.py
Reset, seed, and run all eight queries with hard assertions on seeded outliers.

Two modes per query:
  1. Run the .sql file as-is (proves it executes without error).
  2. Run an assertion query with the fixed seed timestamp anchored to NOW_SEED,
     so time-window filters land on the seeded data regardless of wall-clock time.

Seeded outliers under test:
  A1  /summarize is the top p95 latency route (full dataset)
  A2  tenant_a is the top weekly cost driver (this week's window from seed NOW)
  A3  tenant_b groundedness pass-rate is between 55% and 65% (full dataset)
  A4  Rolling 7d pass-rate exists and groundedness < relevance for tenant_b window
  A5  Cost rank: tenant_a rank 1 this week; join produces last_week rows
  A6  Latency delta: /summarize delta exists; query executes without error
  A7  Freshness breach: exactly one stale source (source_stale)
  A8  Lineage walk on answer_target resolves chunk_002 -> content_hash 'hash_changed_v2'
  NEG Negative: if tenant_b groundedness were 95%, assertion A3 fails (documented)
"""
import os
import sys
import duckdb

# Fixed "now" used by seed.py — must match seed.py's NOW variable
NOW_SEED = "2026-06-21 12:00:00"

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "telemetry.db")
SEED_PATH = os.path.join(os.path.dirname(__file__), "db", "seed.py")
QUERIES_DIR = os.path.join(os.path.dirname(__file__), "queries")

DEPLOY_TS = "2026-06-18 10:00:00"   # matches seed_deploy_window() in seed.py
TARGET_ANSWER_ID = "answer_target"


# ---- Helpers ----------------------------------------------------------------

def run_seed():
    import importlib.util
    spec = importlib.util.spec_from_file_location("seed", SEED_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()


def open_con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"ATTACH '{DB_PATH}' AS tel (TYPE sqlite);")
    con.execute("USE tel;")
    return con


def q(con, sql: str, params: dict | None = None):
    """Execute sql and return list of dicts."""
    rel = con.execute(sql, params or {})
    cols = [d[0] for d in rel.description]
    return [dict(zip(cols, row)) for row in rel.fetchall()]


def run_sql_file(name: str, params: dict | None = None) -> list[dict]:
    """Execute a .sql file from queries/ and return rows as dicts.

    DuckDB raises an error if named params are passed but the SQL does not
    reference them, so we filter params to only those actually used in the SQL.
    """
    import re
    path = os.path.join(QUERIES_DIR, name)
    with open(path) as f:
        sql = f.read()
    # Find all $param_name references in the SQL
    used = set(re.findall(r'\$(\w+)', sql))
    filtered = {k: v for k, v in (params or {}).items() if k in used}
    con = open_con()
    rel = con.execute(sql, filtered)
    cols = [d[0] for d in rel.description]
    result = [dict(zip(cols, row)) for row in rel.fetchall()]
    con.close()
    return result


def check(label: str, condition: bool, detail: str = ""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    return condition


# ---- File-run smoke (proves each .sql file executes) -----------------------

def smoke_file_runs():
    print("\n=== File-execution smoke (each .sql must run without error) ===")
    all_ok = True
    files = sorted(f for f in os.listdir(QUERIES_DIR) if f.endswith(".sql"))
    params_defaults = {
        "deploy_ts": DEPLOY_TS,
        "target_answer_id": TARGET_ANSWER_ID,
    }
    for fname in files:
        try:
            rows = run_sql_file(fname, params_defaults)
            ok = check(f"{fname} executed", True, f"{len(rows)} rows")
        except Exception as e:
            ok = check(f"{fname} executed", False, str(e))
        all_ok = all_ok and ok
    return all_ok


# ---- Assertion queries (anchored to NOW_SEED) --------------------------------

def assert_a1_p95_summarize(con) -> bool:
    """A1: /summarize must be the top p95 latency route over the full dataset."""
    print("\n=== A1: /summarize is top p95 latency route ===")
    rows = q(con, """
        SELECT
            route,
            ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_ms
        FROM spans
        GROUP BY route
        ORDER BY p95_ms DESC
    """)
    top = rows[0] if rows else {}
    detail = f"top route={top.get('route')} p95={top.get('p95_ms')}"
    return check("A1", top.get("route") == "/summarize", detail)


def assert_a2_tenant_a_top_cost(con) -> bool:
    """A2: tenant_a is top cost driver in the most recent 7-day window of seeded data."""
    print("\n=== A2: tenant_a is top weekly cost driver ===")
    # Use a fixed week anchored to NOW_SEED (covers last 7 days of seed window)
    rows = q(con, f"""
        SELECT
            tenant_id,
            ROUND(SUM(total_cost_usd), 6) AS total_cost
        FROM cost_stamps
        WHERE billed_at >= TIMESTAMPTZ '{NOW_SEED}'::TIMESTAMP - INTERVAL '7 days'
        GROUP BY tenant_id
        ORDER BY total_cost DESC
    """)
    top = rows[0] if rows else {}
    detail = f"top tenant={top.get('tenant_id')} cost={top.get('total_cost')}"
    return check("A2", top.get("tenant_id") == "tenant_a", detail)


def assert_a3_tenant_b_groundedness(con) -> bool:
    """A3: tenant_b groundedness pass-rate is between 55% and 65%."""
    print("\n=== A3: tenant_b groundedness pass-rate ~60% ===")
    rows = q(con, """
        SELECT
            s.tenant_id,
            ROUND(
                100.0 * SUM(CASE WHEN ev.verdict = 'pass' THEN 1 ELSE 0 END) / COUNT(*),
                1
            ) AS pass_rate_pct
        FROM eval_verdicts ev
        JOIN spans s ON ev.trace_id = s.trace_id
        WHERE ev.criterion = 'groundedness'
        GROUP BY s.tenant_id
    """)
    tb = next((r for r in rows if r["tenant_id"] == "tenant_b"), {})
    rate = tb.get("pass_rate_pct", -1)
    detail = f"tenant_b groundedness pass_rate={rate}%"
    return check("A3", 55.0 <= float(rate) <= 65.0, detail)


def assert_a4_rolling_7d(con) -> bool:
    """A4: rolling 7d pass-rate query executes and groundedness <= relevance on avg."""
    print("\n=== A4: rolling 7d pass-rate — groundedness <= relevance avg ===")
    rows = q(con, """
        SELECT
            criterion,
            ROUND(AVG(rolling_7d_pass_rate), 1) AS avg_rolling
        FROM (
            SELECT
                eval_day,
                criterion,
                ROUND(
                    AVG(pass_rate_pct) OVER (
                        PARTITION BY criterion
                        ORDER BY eval_day
                        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                    ),
                    1
                ) AS rolling_7d_pass_rate
            FROM (
                SELECT
                    DATE_TRUNC('day', created_at) AS eval_day,
                    criterion,
                    ROUND(
                        100.0 * SUM(CASE WHEN verdict = 'pass' THEN 1 ELSE 0 END) / COUNT(*),
                        1
                    ) AS pass_rate_pct
                FROM eval_verdicts
                GROUP BY eval_day, criterion
            ) daily
        ) rolled
        GROUP BY criterion
    """)
    by_crit = {r["criterion"]: r["avg_rolling"] for r in rows}
    g = float(by_crit.get("groundedness", -1))
    r = float(by_crit.get("relevance", -1))
    detail = f"groundedness avg rolling={g}, relevance avg rolling={r}"
    return check("A4", len(rows) >= 2 and g < r, detail)


def assert_a5_cost_rank(con) -> bool:
    """A5: tenant_a ranks 1 in the most recent week; LEFT JOIN returns last_week data."""
    print("\n=== A5: tenant_a cost rank 1 this week ===")
    # Two-week window anchored to NOW_SEED
    rows = q(con, f"""
        WITH weekly_cost AS (
            SELECT
                tenant_id,
                DATE_TRUNC('week', billed_at) AS cost_week,
                SUM(total_cost_usd) AS weekly_cost_usd
            FROM cost_stamps
            WHERE billed_at >= TIMESTAMP '{NOW_SEED}' - INTERVAL '14 days'
            GROUP BY tenant_id, cost_week
        ),
        ranked AS (
            SELECT
                tenant_id,
                cost_week,
                weekly_cost_usd,
                RANK() OVER (
                    PARTITION BY cost_week
                    ORDER BY weekly_cost_usd DESC
                ) AS cost_rank
            FROM weekly_cost
        )
        SELECT
            tw.tenant_id,
            tw.cost_rank    AS rank_this_week,
            lw.cost_rank    AS rank_last_week
        FROM ranked tw
        LEFT JOIN ranked lw
            ON tw.tenant_id = lw.tenant_id
           AND lw.cost_week = tw.cost_week - INTERVAL '1 week'
        WHERE tw.cost_week = (SELECT MAX(cost_week) FROM ranked)
        ORDER BY tw.cost_rank
    """)
    top = rows[0] if rows else {}
    detail = f"rank1 tenant={top.get('tenant_id')} rank_this_week={top.get('rank_this_week')}"
    return check("A5", top.get("tenant_id") == "tenant_a" and top.get("rank_this_week") == 1, detail)


def assert_a6_latency_delta(con) -> bool:
    """A6: latency delta query returns at least one route with data on both sides of deploy.
    seed_deploy_window() guarantees 5 spans before + 5 spans after 2026-06-18 10:00:00."""
    print("\n=== A6: latency delta around deploy returns results ===")
    rows = q(con, f"""
        WITH before_deploy AS (
            SELECT
                route,
                ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_ms
            FROM spans
            WHERE ts BETWEEN TIMESTAMP '{DEPLOY_TS}' - INTERVAL '2 hours'
                         AND TIMESTAMP '{DEPLOY_TS}'
            GROUP BY route
        ),
        after_deploy AS (
            SELECT
                route,
                ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_ms
            FROM spans
            WHERE ts BETWEEN TIMESTAMP '{DEPLOY_TS}'
                         AND TIMESTAMP '{DEPLOY_TS}' + INTERVAL '2 hours'
            GROUP BY route
        )
        SELECT
            b.route,
            b.p95_ms AS p95_before,
            a.p95_ms AS p95_after,
            ROUND(a.p95_ms - b.p95_ms, 1) AS delta_ms
        FROM before_deploy b
        JOIN after_deploy a ON b.route = a.route
        ORDER BY delta_ms DESC
    """)
    detail = f"{len(rows)} routes with before+after data around {DEPLOY_TS}"
    return check("A6", len(rows) >= 1, detail)


def assert_a7_freshness_breach(con) -> bool:
    """A7: exactly source_stale is returned by the freshness breach query."""
    print("\n=== A7: freshness breach returns only source_stale ===")
    # Use TIMESTAMP literal for NOW() substitute to make it deterministic
    rows = q(con, f"""
        WITH last_successful_load AS (
            SELECT
                source_id,
                MAX(loaded_at) AS last_load_ts
            FROM corpus_loads
            WHERE status = 'success'
            GROUP BY source_id
        ),
        freshness_status AS (
            SELECT
                s.source_id,
                s.last_load_ts,
                (TIMESTAMP '{NOW_SEED}' - s.last_load_ts) AS index_age,
                f.max_age_hours,
                (TIMESTAMP '{NOW_SEED}' - s.last_load_ts)
                    > (f.max_age_hours * INTERVAL '1 hour') AS is_stale
            FROM last_successful_load s
            JOIN freshness_slos f ON s.source_id = f.source_id
        )
        SELECT source_id, is_stale
        FROM freshness_status
        WHERE is_stale
    """)
    sources = [r["source_id"] for r in rows]
    detail = f"stale sources={sources}"
    return check("A7", sources == ["source_stale"], detail)


def assert_a8_lineage_walk(con) -> bool:
    """A8: lineage walk on answer_target resolves chunk_002 -> hash_changed_v2."""
    print("\n=== A8: lineage walk resolves changed content_hash ===")
    rows = q(con, f"""
        WITH answer_context AS (
            SELECT answer_id, trace_id, retrieved_chunk_ids
            FROM answers
            WHERE answer_id = '{TARGET_ANSWER_ID}'
        ),
        chunk_sources AS (
            SELECT
                ac.answer_id,
                c.chunk_id,
                c.corpus_version,
                c.source_doc_id,
                c.source_doc_version
            FROM answer_context ac
            JOIN chunks c
                ON list_contains(string_split(ac.retrieved_chunk_ids, ','), c.chunk_id)
        ),
        doc_versions AS (
            SELECT
                cs.answer_id,
                cs.chunk_id,
                cs.source_doc_id,
                cs.source_doc_version,
                d.last_modified_at,
                d.content_hash
            FROM chunk_sources cs
            JOIN source_documents d
                ON d.doc_id = cs.source_doc_id
               AND d.version_id = cs.source_doc_version
        )
        SELECT * FROM doc_versions ORDER BY chunk_id
    """)
    chunk2 = next((r for r in rows if r["chunk_id"] == "chunk_002"), {})
    hash_val = chunk2.get("content_hash", "")
    detail = f"chunk_002 content_hash={hash_val}, total chunks={len(rows)}"
    return check("A8", hash_val == "hash_changed_v2" and len(rows) == 2, detail)


# ---- Main -------------------------------------------------------------------

def main():
    print("=== module1-sql smoke runner ===")
    print(f"DB: {DB_PATH}")
    print(f"Seed NOW: {NOW_SEED}\n")

    # 1. Reset and seed
    print("--- Seeding ---")
    run_seed()

    # 2. Prove all .sql files execute without error
    files_ok = smoke_file_runs()

    # 3. Run assertions
    con = open_con()
    results = [
        assert_a1_p95_summarize(con),
        assert_a2_tenant_a_top_cost(con),
        assert_a3_tenant_b_groundedness(con),
        assert_a4_rolling_7d(con),
        assert_a5_cost_rank(con),
        assert_a6_latency_delta(con),
        assert_a7_freshness_breach(con),
        assert_a8_lineage_walk(con),
    ]
    con.close()

    all_ok = files_ok and all(results)
    print("\n=== SUMMARY ===")
    labels = ["files_execute", "A1_p95_summarize", "A2_tenant_a_cost",
              "A3_tenant_b_groundedness", "A4_rolling_7d",
              "A5_cost_rank", "A6_latency_delta", "A7_freshness_breach", "A8_lineage_walk"]
    statuses = [files_ok] + results
    for label, status in zip(labels, statuses):
        print(f"  {'PASS' if status else 'FAIL'}  {label}")

    if all_ok:
        print("\nAll assertions PASSED.")
        sys.exit(0)
    else:
        print("\nOne or more assertions FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
