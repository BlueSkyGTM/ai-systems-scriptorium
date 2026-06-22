"""
module1-sql/db/seed.py
Seed deterministic synthetic telemetry into db/telemetry.db (SQLite).

KNOWN, ASSERTABLE OUTLIERS (used by smoke.py / tests/):
  - /summarize has the highest p95 latency (seeded 1200-2000 ms range).
  - tenant_a is the top weekly cost driver (higher cost-per-request + volume).
  - tenant_b has ~60% groundedness pass-rate (outlier below tenant_a ~85%, tenant_c ~80%).
  - One corpus source (source_stale) breaches its freshness SLO.
  - One answer (answer_target) resolves via lineage to content_hash 'hash_changed_v2'.

Run:  python db/seed.py
"""
import sqlite3
import random
import os
from datetime import datetime, timedelta

SEED = 42
DB_PATH = os.path.join(os.path.dirname(__file__), "telemetry.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

# --- Config ---
ROUTES = ["/summarize", "/classify", "/retrieve", "/generate"]
TENANTS = ["tenant_a", "tenant_b", "tenant_c"]
CRITERIA = ["groundedness", "relevance"]
NUM_DAYS = 14
TOTAL_SPANS = 140

# Latency ranges per route (ms) — /summarize is the high-latency outlier
ROUTE_LATENCY = {
    "/summarize":  (1200, 2000),
    "/classify":   (80,   200),
    "/retrieve":   (150,  400),
    "/generate":   (300,  700),
}

# Cost-per-request weights per tenant (higher = more expensive calls)
TENANT_COST_WEIGHT = {
    "tenant_a": 3.5,   # clear top driver
    "tenant_b": 1.0,
    "tenant_c": 1.4,
}

# Groundedness pass probability per tenant
GROUNDEDNESS_PASS_PROB = {
    "tenant_a": 0.85,
    "tenant_b": 0.60,   # outlier ~60%
    "tenant_c": 0.80,
}

# Relevance pass probability (high and similar across tenants)
RELEVANCE_PASS_PROB = {
    "tenant_a": 0.90,
    "tenant_b": 0.88,
    "tenant_c": 0.89,
}

NOW = datetime(2026, 6, 21, 12, 0, 0)   # fixed "now" for determinism
WINDOW_START = NOW - timedelta(days=NUM_DAYS)
# Week boundary within our window (for cost-rank week-over-week)
# Week 1: days 0-6 back; Week 2: days 7-13 back
WEEK_BOUNDARY = NOW - timedelta(days=7)


def reset_db(conn):
    cur = conn.cursor()
    for table in [
        "source_documents", "chunks", "answers",
        "freshness_slos", "corpus_loads",
        "cost_stamps", "eval_verdicts", "spans",
    ]:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()


def ts_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def seed_spans(rng, conn) -> list[dict]:
    rows = []
    for i in range(TOTAL_SPANS):
        # Distribute spans across tenants with tenant_a getting ~40% volume
        tenant = rng.choices(TENANTS, weights=[4, 3, 3])[0]
        route = rng.choice(ROUTES)
        lo, hi = ROUTE_LATENCY[route]
        latency = rng.randint(lo, hi)
        input_tok = rng.randint(200, 1500)
        output_tok = rng.randint(50, 800)
        # Spread timestamps across the 14-day window
        offset_secs = rng.uniform(0, NUM_DAYS * 86400)
        ts = WINDOW_START + timedelta(seconds=offset_secs)
        trace_id = f"trace_{i:04d}"
        rows.append({
            "trace_id": trace_id,
            "route": route,
            "tenant_id": tenant,
            "latency_ms": latency,
            "input_tokens": input_tok,
            "output_tokens": output_tok,
            "ts": ts,
        })
    conn.executemany(
        "INSERT INTO spans VALUES (:trace_id,:route,:tenant_id,:latency_ms,"
        ":input_tokens,:output_tokens,:ts)",
        [{**r, "ts": ts_str(r["ts"])} for r in rows],
    )
    conn.commit()
    return rows


def seed_eval_verdicts(rng, conn, spans: list[dict]):
    rows = []
    ev_id = 1
    for span in spans:
        tenant = span["tenant_id"]
        for criterion in CRITERIA:
            if criterion == "groundedness":
                prob = GROUNDEDNESS_PASS_PROB[tenant]
            else:
                prob = RELEVANCE_PASS_PROB[tenant]
            verdict = "pass" if rng.random() < prob else "fail"
            score = round(rng.uniform(0.7, 1.0) if verdict == "pass" else rng.uniform(0.1, 0.5), 3)
            created_at = span["ts"] + timedelta(seconds=rng.randint(1, 30))
            rows.append({
                "id": ev_id,
                "trace_id": span["trace_id"],
                "criterion": criterion,
                "verdict": verdict,
                "score": score,
                "created_at": ts_str(created_at),
            })
            ev_id += 1
    conn.executemany(
        "INSERT INTO eval_verdicts VALUES (:id,:trace_id,:criterion,:verdict,:score,:created_at)",
        rows,
    )
    conn.commit()


def seed_cost_stamps(rng, conn, spans: list[dict]):
    rows = []
    cs_id = 1
    for span in spans:
        tenant = span["tenant_id"]
        weight = TENANT_COST_WEIGHT[tenant]
        # Base cost from tokens + route multiplier; tenant_a has higher weight
        base = (span["input_tokens"] * 0.000002 + span["output_tokens"] * 0.000006) * weight
        total_cost = round(base + rng.uniform(0, 0.002) * weight, 6)
        billed_at = span["ts"] + timedelta(seconds=rng.randint(1, 60))
        rows.append({
            "id": cs_id,
            "trace_id": span["trace_id"],
            "tenant_id": tenant,
            "total_cost_usd": total_cost,
            "input_tokens": span["input_tokens"],
            "output_tokens": span["output_tokens"],
            "billed_at": ts_str(billed_at),
        })
        cs_id += 1
    conn.executemany(
        "INSERT INTO cost_stamps VALUES "
        "(:id,:trace_id,:tenant_id,:total_cost_usd,:input_tokens,:output_tokens,:billed_at)",
        rows,
    )
    conn.commit()


def seed_deploy_window(rng, conn, spans: list[dict]):
    """
    Seed 10 guaranteed spans bracketing the deploy timestamp so Query 6
    (latency delta around deploy) always has before+after data.

    Deploy timestamp: 2026-06-18 10:00:00 (within the 14-day seed window).
    5 spans: [-2h, -1h] before deploy; 5 spans: [+0h, +1h] after deploy.
    """
    deploy_dt = datetime(2026, 6, 18, 10, 0, 0)
    extra_spans = []
    for i, (offset_minutes, label) in enumerate([
        (-90, "before"), (-60, "before"), (-45, "before"), (-30, "before"), (-10, "before"),
        (10,  "after"),  (30,  "after"),  (50,  "after"),  (70,  "after"),  (100, "after"),
    ]):
        route = rng.choice(ROUTES)
        lo, hi = ROUTE_LATENCY[route]
        tenant = rng.choice(TENANTS)
        trace_id = f"deploy_{i:02d}"
        ts = deploy_dt + timedelta(minutes=offset_minutes)
        extra_spans.append({
            "trace_id": trace_id,
            "route": route,
            "tenant_id": tenant,
            "latency_ms": rng.randint(lo, hi),
            "input_tokens": rng.randint(200, 800),
            "output_tokens": rng.randint(50, 300),
            "ts": ts,
        })
    conn.executemany(
        "INSERT OR IGNORE INTO spans VALUES "
        "(:trace_id,:route,:tenant_id,:latency_ms,:input_tokens,:output_tokens,:ts)",
        [{**r, "ts": ts_str(r["ts"])} for r in extra_spans],
    )
    conn.commit()
    # Also seed eval_verdicts and cost_stamps for these extra spans
    ev_rows = []
    cs_rows = []
    # Use high IDs to avoid collisions
    ev_id_start = 10000
    cs_id_start = 10000
    for i, span in enumerate(extra_spans):
        for j, criterion in enumerate(CRITERIA):
            prob = GROUNDEDNESS_PASS_PROB.get(span["tenant_id"], 0.80) if criterion == "groundedness" \
                   else RELEVANCE_PASS_PROB.get(span["tenant_id"], 0.88)
            verdict = "pass" if rng.random() < prob else "fail"
            score = round(rng.uniform(0.7, 1.0) if verdict == "pass" else 0.3, 3)
            created_at = span["ts"] + timedelta(seconds=5)
            ev_rows.append({
                "id": ev_id_start + i * 2 + j,
                "trace_id": span["trace_id"],
                "criterion": criterion,
                "verdict": verdict,
                "score": score,
                "created_at": ts_str(created_at),
            })
        weight = TENANT_COST_WEIGHT[span["tenant_id"]]
        base = (span["input_tokens"] * 0.000002 + span["output_tokens"] * 0.000006) * weight
        cs_rows.append({
            "id": cs_id_start + i,
            "trace_id": span["trace_id"],
            "tenant_id": span["tenant_id"],
            "total_cost_usd": round(base + 0.001, 6),
            "input_tokens": span["input_tokens"],
            "output_tokens": span["output_tokens"],
            "billed_at": ts_str(span["ts"]),
        })
    conn.executemany(
        "INSERT OR IGNORE INTO eval_verdicts VALUES "
        "(:id,:trace_id,:criterion,:verdict,:score,:created_at)",
        ev_rows,
    )
    conn.executemany(
        "INSERT OR IGNORE INTO cost_stamps VALUES "
        "(:id,:trace_id,:tenant_id,:total_cost_usd,:input_tokens,:output_tokens,:billed_at)",
        cs_rows,
    )
    conn.commit()
    return extra_spans


def seed_freshness(conn):
    # Two sources: one fresh, one stale
    # source_fresh: loaded 1 hour ago, SLO = 6 hours -> NOT stale
    # source_stale: loaded 48 hours ago, SLO = 24 hours -> IS stale
    fresh_load_ts = NOW - timedelta(hours=1)
    stale_load_ts = NOW - timedelta(hours=48)

    conn.executemany(
        "INSERT INTO corpus_loads (source_id, status, loaded_at) VALUES (?,?,?)",
        [
            ("source_fresh", "success", ts_str(fresh_load_ts)),
            ("source_fresh", "failure", ts_str(fresh_load_ts - timedelta(hours=2))),
            ("source_stale", "success", ts_str(stale_load_ts)),
            ("source_stale", "failure", ts_str(stale_load_ts + timedelta(hours=1))),
        ],
    )
    conn.executemany(
        "INSERT INTO freshness_slos VALUES (?,?)",
        [
            ("source_fresh", 6),    # SLO: 6 hours; age ~1 hour -> fresh
            ("source_stale", 24),   # SLO: 24 hours; age ~48 hours -> STALE
        ],
    )
    conn.commit()


def seed_lineage(conn, spans: list[dict]):
    # Pick a real trace_id for our target answer
    target_trace = spans[0]["trace_id"]

    # answer: retrieved two chunks; chunk_002 is the "changed" one
    conn.execute(
        "INSERT INTO answers VALUES (?,?,?)",
        ("answer_target", target_trace, "chunk_001,chunk_002"),
    )
    conn.executemany(
        "INSERT INTO chunks VALUES (?,?,?,?)",
        [
            ("chunk_001", "corpus_v1", "doc_alpha", "v1"),
            ("chunk_002", "corpus_v2", "doc_beta",  "v2"),   # the changed chunk
        ],
    )
    conn.executemany(
        "INSERT INTO source_documents VALUES (?,?,?,?)",
        [
            ("doc_alpha", "v1", ts_str(NOW - timedelta(days=10)), "hash_stable_v1"),
            ("doc_beta",  "v2", ts_str(NOW - timedelta(days=1)),  "hash_changed_v2"),
        ],
    )
    conn.commit()


def print_summary(conn):
    tables = [
        "spans", "eval_verdicts", "cost_stamps",
        "corpus_loads", "freshness_slos",
        "answers", "chunks", "source_documents",
    ]
    print("\n--- Seed row counts ---")
    for t in tables:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<20} {n:>4} rows")
    print()


def main():
    rng = random.Random(SEED)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    reset_db(conn)
    spans = seed_spans(rng, conn)
    seed_eval_verdicts(rng, conn, spans)
    seed_cost_stamps(rng, conn, spans)
    seed_deploy_window(rng, conn, spans)
    seed_freshness(conn)
    seed_lineage(conn, spans)
    print_summary(conn)
    conn.close()
    print(f"Seeded: {DB_PATH}")


if __name__ == "__main__":
    main()
