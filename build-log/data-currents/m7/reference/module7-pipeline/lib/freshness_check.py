"""
freshness_check.py
Compare each source's last successful load against its SLO.

Reads corpus.db (SQLite) and prints a report:
  source_id | last_load | age_hours | max_age_hours | status
Exits non-zero if ANY source is stale.

Usage:
  python freshness_check.py
  python freshness_check.py --db path/to.db
  python freshness_check.py --now "2026-06-22 10:00:00"  # override "now" for tests
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(HERE, "corpus.db")


def check_freshness(db_path: str, now_ts: str | None = None) -> list[dict]:
    """
    Return a list of dicts, one per source in freshness_slos:
      source_id, last_load_ts, age_hours, max_age_hours, is_stale

    now_ts: override for "now" (ISO string). Defaults to UTC wall clock.
    """
    now = datetime.fromisoformat(now_ts) if now_ts else datetime.utcnow()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT
            s.source_id,
            s.max_age_hours,
            MAX(cl.loaded_at) AS last_load_ts
        FROM freshness_slos s
        LEFT JOIN corpus_loads cl
            ON cl.source_id = s.source_id
           AND cl.status = 'success'
        GROUP BY s.source_id, s.max_age_hours
    """).fetchall()

    conn.close()

    results = []
    for row in rows:
        source_id     = row["source_id"]
        max_age_hours = row["max_age_hours"]
        last_load_str = row["last_load_ts"]

        if last_load_str is None:
            # Never loaded -> always stale
            age_hours = float("inf")
            is_stale  = True
        else:
            last_load = datetime.fromisoformat(last_load_str)
            age_hours = (now - last_load).total_seconds() / 3600
            is_stale  = age_hours > max_age_hours

        results.append({
            "source_id":     source_id,
            "last_load_ts":  last_load_str,
            "age_hours":     round(age_hours, 2) if age_hours != float("inf") else None,
            "max_age_hours": max_age_hours,
            "is_stale":      is_stale,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="M2 freshness check")
    parser.add_argument("--db",  default=DEFAULT_DB, help="Path to SQLite corpus DB")
    parser.add_argument("--now", default=None,        help='Override "now" timestamp')
    args = parser.parse_args()

    results = check_freshness(db_path=args.db, now_ts=args.now)

    print(f"\n{'source_id':<25} {'last_load':<22} {'age_h':>6} {'slo_h':>6}  status")
    print("-" * 72)
    any_stale = False
    for r in results:
        last_load = r["last_load_ts"] or "NEVER"
        age = f"{r['age_hours']:.1f}" if r["age_hours"] is not None else "  inf"
        status = "STALE" if r["is_stale"] else "fresh"
        if r["is_stale"]:
            any_stale = True
        print(f"{r['source_id']:<25} {last_load:<22} {age:>6} {r['max_age_hours']:>6}  {status}")

    if any_stale:
        print("\nFRESHNESS GATE: FAIL — one or more sources are stale.")
        sys.exit(1)
    else:
        print("\nFRESHNESS GATE: PASS — all sources are fresh.")
        sys.exit(0)


if __name__ == "__main__":
    main()
