"""
module1-sql/tests/test_queries.py
pytest mirror of the smoke assertions. Each test is independent; the session-scoped
fixture seeds the DB once per test run.

Run: python -m pytest tests/ -v
"""
import os
import sys
import pytest
import duckdb

# Make the package root importable when running from any cwd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "db", "telemetry.db")
SEED_PATH = os.path.join(ROOT, "db", "seed.py")
NOW_SEED = "2026-06-21 12:00:00"
DEPLOY_TS = "2026-06-18 10:00:00"   # matches seed_deploy_window() in seed.py
TARGET_ANSWER_ID = "answer_target"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def seed_db():
    """Seed the SQLite DB once for the whole test session."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("seed", SEED_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()


@pytest.fixture
def con():
    """Open a DuckDB in-memory connection over the seeded SQLite file."""
    c = duckdb.connect(database=":memory:")
    c.execute("INSTALL sqlite; LOAD sqlite;")
    c.execute(f"ATTACH '{DB_PATH}' AS tel (TYPE sqlite);")
    c.execute("USE tel;")
    yield c
    c.close()


def rows(con, sql: str, params: dict | None = None) -> list[dict]:
    rel = con.execute(sql, params or {})
    cols = [d[0] for d in rel.description]
    return [dict(zip(cols, row)) for row in rel.fetchall()]


# ---------------------------------------------------------------------------
# A1: P95 latency by route — /summarize is top
# ---------------------------------------------------------------------------

def test_a1_summarize_is_top_p95_route(con):
    result = rows(con, """
        SELECT
            route,
            ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_ms
        FROM spans
        GROUP BY route
        ORDER BY p95_ms DESC
    """)
    assert result, "Expected at least one route"
    assert result[0]["route"] == "/summarize", (
        f"/summarize should have highest p95; got {result[0]['route']} = {result[0]['p95_ms']} ms"
    )


def test_a1_summarize_p95_above_1000ms(con):
    result = rows(con, """
        SELECT ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_ms
        FROM spans WHERE route = '/summarize'
    """)
    assert result[0]["p95_ms"] > 1000, (
        f"Expected /summarize p95 > 1000 ms; got {result[0]['p95_ms']}"
    )


# ---------------------------------------------------------------------------
# A2: Cost by tenant — tenant_a is top cost driver in recent window
# ---------------------------------------------------------------------------

def test_a2_tenant_a_top_cost(con):
    result = rows(con, f"""
        SELECT
            tenant_id,
            ROUND(SUM(total_cost_usd), 6) AS total_cost
        FROM cost_stamps
        WHERE billed_at >= TIMESTAMP '{NOW_SEED}' - INTERVAL '7 days'
        GROUP BY tenant_id
        ORDER BY total_cost DESC
    """)
    assert result, "Expected cost rows"
    assert result[0]["tenant_id"] == "tenant_a", (
        f"tenant_a should be top cost driver; got {result[0]}"
    )


# ---------------------------------------------------------------------------
# A3: tenant_b groundedness pass-rate ~60%
# ---------------------------------------------------------------------------

def test_a3_tenant_b_groundedness_55_to_65_pct(con):
    result = rows(con, """
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
    by_tenant = {r["tenant_id"]: float(r["pass_rate_pct"]) for r in result}
    assert "tenant_b" in by_tenant, "tenant_b not found in groundedness results"
    rate = by_tenant["tenant_b"]
    assert 55.0 <= rate <= 65.0, (
        f"tenant_b groundedness should be 55-65%; got {rate}%"
    )


def test_a3_tenant_b_groundedness_below_tenant_a(con):
    result = rows(con, """
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
    by_tenant = {r["tenant_id"]: float(r["pass_rate_pct"]) for r in result}
    assert by_tenant["tenant_b"] < by_tenant["tenant_a"], (
        f"tenant_b groundedness ({by_tenant['tenant_b']}%) should be below "
        f"tenant_a ({by_tenant['tenant_a']}%)"
    )


# ---------------------------------------------------------------------------
# A4: Rolling 7-day pass-rate — groundedness rolling avg < relevance rolling avg
# ---------------------------------------------------------------------------

def test_a4_rolling_7d_produces_results(con):
    result = rows(con, """
        SELECT criterion, COUNT(*) AS n_days
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
        GROUP BY criterion
    """)
    assert len(result) == 2, f"Expected 2 criteria; got {len(result)}"
    for r in result:
        assert r["n_days"] >= 7, f"Expected >=7 days of data for {r['criterion']}; got {r['n_days']}"


def test_a4_rolling_7d_groundedness_below_relevance(con):
    result = rows(con, """
        SELECT
            criterion,
            ROUND(AVG(rolling_rate), 1) AS mean_rolling
        FROM (
            SELECT
                criterion,
                AVG(pass_rate_pct) OVER (
                    PARTITION BY criterion
                    ORDER BY eval_day
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
                ) AS rolling_rate
            FROM (
                SELECT
                    DATE_TRUNC('day', created_at) AS eval_day,
                    criterion,
                    100.0 * SUM(CASE WHEN verdict = 'pass' THEN 1 ELSE 0 END) / COUNT(*)
                        AS pass_rate_pct
                FROM eval_verdicts
                GROUP BY eval_day, criterion
            ) daily
        ) rolled
        GROUP BY criterion
    """)
    by_crit = {r["criterion"]: float(r["mean_rolling"]) for r in result}
    assert by_crit["groundedness"] < by_crit["relevance"], (
        f"groundedness rolling ({by_crit['groundedness']}) should be below "
        f"relevance ({by_crit['relevance']})"
    )


# ---------------------------------------------------------------------------
# A5: Cost rank week-over-week — tenant_a rank 1 in most recent week
# ---------------------------------------------------------------------------

def test_a5_tenant_a_rank_1_this_week(con):
    result = rows(con, f"""
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
                RANK() OVER (PARTITION BY cost_week ORDER BY weekly_cost_usd DESC) AS cost_rank
            FROM weekly_cost
        )
        SELECT
            tw.tenant_id,
            tw.cost_rank AS rank_this_week,
            lw.cost_rank AS rank_last_week
        FROM ranked tw
        LEFT JOIN ranked lw
            ON  tw.tenant_id = lw.tenant_id
            AND lw.cost_week = tw.cost_week - INTERVAL '1 week'
        WHERE tw.cost_week = (SELECT MAX(cost_week) FROM ranked)
        ORDER BY tw.cost_rank
    """)
    assert result, "Expected rank rows"
    top = result[0]
    assert top["tenant_id"] == "tenant_a", f"Expected tenant_a rank 1; got {top}"
    assert top["rank_this_week"] == 1, f"Expected rank 1; got {top['rank_this_week']}"


# ---------------------------------------------------------------------------
# A6: Latency delta around deploy — query returns at least one route
# ---------------------------------------------------------------------------

def test_a6_latency_delta_returns_rows(con):
    result = rows(con, f"""
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
    """)
    assert len(result) >= 1, (
        f"Expected >=1 route with before+after data around {DEPLOY_TS}; got 0"
    )


# ---------------------------------------------------------------------------
# A7: Freshness breach — only source_stale returned
# ---------------------------------------------------------------------------

def test_a7_only_source_stale_breaches(con):
    result = rows(con, f"""
        WITH last_successful_load AS (
            SELECT source_id, MAX(loaded_at) AS last_load_ts
            FROM corpus_loads
            WHERE status = 'success'
            GROUP BY source_id
        ),
        freshness_status AS (
            SELECT
                s.source_id,
                (TIMESTAMP '{NOW_SEED}' - s.last_load_ts) > (f.max_age_hours * INTERVAL '1 hour')
                    AS is_stale
            FROM last_successful_load s
            JOIN freshness_slos f ON s.source_id = f.source_id
        )
        SELECT source_id FROM freshness_status WHERE is_stale
    """)
    stale = [r["source_id"] for r in result]
    assert stale == ["source_stale"], f"Expected only source_stale stale; got {stale}"


def test_a7_source_fresh_is_not_stale(con):
    result = rows(con, f"""
        WITH last_successful_load AS (
            SELECT source_id, MAX(loaded_at) AS last_load_ts
            FROM corpus_loads
            WHERE status = 'success'
            GROUP BY source_id
        ),
        freshness_status AS (
            SELECT
                s.source_id,
                (TIMESTAMP '{NOW_SEED}' - s.last_load_ts) > (f.max_age_hours * INTERVAL '1 hour')
                    AS is_stale
            FROM last_successful_load s
            JOIN freshness_slos f ON s.source_id = f.source_id
        )
        SELECT source_id, is_stale FROM freshness_status WHERE source_id = 'source_fresh'
    """)
    assert result, "source_fresh row missing"
    assert not result[0]["is_stale"], "source_fresh should not be stale"


# ---------------------------------------------------------------------------
# A8: Lineage walk — answer_target resolves to hash_changed_v2 via chunk_002
# ---------------------------------------------------------------------------

def test_a8_lineage_walk_chunk002_hash(con):
    result = rows(con, f"""
        WITH answer_context AS (
            SELECT answer_id, trace_id, retrieved_chunk_ids
            FROM answers WHERE answer_id = '{TARGET_ANSWER_ID}'
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
    assert len(result) == 2, f"Expected 2 chunks in lineage; got {len(result)}"
    chunk2 = next((r for r in result if r["chunk_id"] == "chunk_002"), None)
    assert chunk2 is not None, "chunk_002 missing from lineage walk"
    assert chunk2["content_hash"] == "hash_changed_v2", (
        f"Expected hash_changed_v2; got {chunk2['content_hash']}"
    )


def test_a8_lineage_walk_returns_two_chunks(con):
    result = rows(con, f"""
        WITH ac AS (
            SELECT answer_id, retrieved_chunk_ids FROM answers WHERE answer_id = '{TARGET_ANSWER_ID}'
        )
        SELECT
            c.chunk_id,
            c.source_doc_id
        FROM ac
        JOIN chunks c ON list_contains(string_split(ac.retrieved_chunk_ids, ','), c.chunk_id)
    """)
    assert len(result) == 2, f"Expected 2 chunks for answer_target; got {len(result)}"
