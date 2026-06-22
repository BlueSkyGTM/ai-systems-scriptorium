"""
module1-sql/tests/test_negative.py
Negative-case tests: demonstrate that a deliberately wrong seed makes gate A3 fail.

These tests do NOT reseed the real DB. Instead they build an in-memory DuckDB
database with a corrupted seed (tenant_b groundedness ~95%) and confirm:
  - The A3 assertion FAILS (pass-rate outside 55-65% band).
  - The A1 assertion still PASSES (unrelated to tenant groundedness).

Run: python -m pytest tests/test_negative.py -v
"""
import pytest
import duckdb


# ---------------------------------------------------------------------------
# Fixture: in-memory DuckDB with a bad groundedness seed
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def bad_con():
    """
    Build a tiny in-memory DuckDB with tenant_b groundedness seeded at ~95%
    instead of ~60%. No SQLite file involved.
    """
    c = duckdb.connect(database=":memory:")
    # Create the minimal tables needed for the assertions
    c.execute("""
        CREATE TABLE spans (
            trace_id TEXT, route TEXT, tenant_id TEXT,
            latency_ms INTEGER, ts TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE eval_verdicts (
            id INTEGER, trace_id TEXT, criterion TEXT,
            verdict TEXT, score REAL, created_at TIMESTAMP
        )
    """)

    # Seed spans: 30 per tenant across 3 routes
    import random
    rng = random.Random(999)  # different seed from real data
    route_latency = {
        "/summarize": (1200, 2000),
        "/classify":  (80, 200),
        "/retrieve":  (150, 400),
    }
    spans = []
    ev = []
    ev_id = 1
    for i in range(90):
        tenant = ["tenant_a", "tenant_b", "tenant_c"][i % 3]
        route = ["/summarize", "/classify", "/retrieve"][i % 3]
        lo, hi = route_latency[route]
        lat = rng.randint(lo, hi)
        ts = f"2026-06-{(i % 14) + 7:02d} 12:00:00"
        trace_id = f"t{i:04d}"
        spans.append((trace_id, route, tenant, lat, ts))

        for criterion in ["groundedness", "relevance"]:
            if criterion == "groundedness":
                # BAD SEED: tenant_b groundedness ~95%, not ~60%
                prob = 0.95 if tenant == "tenant_b" else 0.85
            else:
                prob = 0.90
            verdict = "pass" if rng.random() < prob else "fail"
            score = round(rng.uniform(0.7, 1.0) if verdict == "pass" else 0.3, 3)
            ev.append((ev_id, trace_id, criterion, verdict, score, ts))
            ev_id += 1

    c.executemany("INSERT INTO spans VALUES (?,?,?,?,?)", spans)
    c.executemany("INSERT INTO eval_verdicts VALUES (?,?,?,?,?,?)", ev)
    yield c
    c.close()


def rows(con, sql):
    rel = con.execute(sql)
    cols = [d[0] for d in rel.description]
    return [dict(zip(cols, row)) for row in rel.fetchall()]


# ---------------------------------------------------------------------------
# Negative case: A3 gate MUST fail with bad seed
# ---------------------------------------------------------------------------

def test_negative_a3_bad_seed_fails_gate(bad_con):
    """
    With tenant_b groundedness seeded at ~95%, the A3 assertion (55-65% band)
    must be OUTSIDE the band — confirming the gate catches the bad seed.
    """
    result = rows(bad_con, """
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
    tenant_b_rate = by_tenant["tenant_b"]

    # The gate check: 55 <= rate <= 65 — this MUST be False with the bad seed
    gate_would_pass = (55.0 <= tenant_b_rate <= 65.0)
    assert not gate_would_pass, (
        f"Negative case: gate should FAIL with bad seed. "
        f"tenant_b groundedness={tenant_b_rate}% is inside 55-65% band (unexpected)."
    )
    # Confirm the bad seed actually produced a high rate
    assert tenant_b_rate > 80.0, (
        f"Bad seed should yield >80% groundedness for tenant_b; got {tenant_b_rate}%"
    )


# ---------------------------------------------------------------------------
# Control: A1 is unaffected by the bad groundedness seed
# ---------------------------------------------------------------------------

def test_negative_a1_p95_unaffected_by_bad_groundedness(bad_con):
    """
    Even with the bad groundedness seed, the p95 latency assertion still holds:
    /summarize is still the highest-latency route (independent of eval data).
    """
    result = rows(bad_con, """
        SELECT
            route,
            ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_ms
        FROM spans
        GROUP BY route
        ORDER BY p95_ms DESC
    """)
    assert result[0]["route"] == "/summarize", (
        f"Even with bad seed, /summarize should be top p95; got {result[0]['route']}"
    )
