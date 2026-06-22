"""
module1-sql/runner.py
Run a single named query file against the SQLite telemetry store via DuckDB.

Usage:
  python runner.py queries/01_p95_latency_by_route.sql
  python runner.py queries/06_latency_delta_around_deploy.sql --deploy-ts "2026-06-20 10:00:00"
  python runner.py queries/08_lineage_walk.sql --answer-id answer_target
"""
import sys
import os
import argparse
import duckdb

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "telemetry.db")
QUERIES_DIR = os.path.join(os.path.dirname(__file__), "queries")


def open_connection(db_path: str) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"ATTACH '{db_path}' AS tel (TYPE sqlite);")
    con.execute("USE tel;")
    return con


def format_table(rows, columns: list[str]) -> str:
    if not rows:
        return "(no rows)"
    col_widths = [max(len(str(c)), max((len(str(r[i])) for r in rows), default=0))
                  for i, c in enumerate(columns)]
    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header = "| " + " | ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(columns)) + " |"
    lines = [sep, header, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(columns))) + " |")
    lines.append(sep)
    return "\n".join(lines)


def run_query(sql_path: str, params: dict | None = None) -> tuple[list, list[str]]:
    import re
    if not os.path.exists(sql_path):
        # Allow bare names like '01_p95_latency_by_route'
        candidate = os.path.join(QUERIES_DIR, sql_path)
        if not sql_path.endswith(".sql"):
            candidate += ".sql"
        sql_path = candidate
    with open(sql_path) as f:
        sql = f.read()
    # Filter params to only those referenced as $name in the SQL
    used = set(re.findall(r'\$(\w+)', sql))
    filtered = {k: v for k, v in (params or {}).items() if k in used}
    con = open_connection(DB_PATH)
    rel = con.execute(sql, filtered)
    columns = [d[0] for d in rel.description]
    rows = rel.fetchall()
    con.close()
    return rows, columns


def main():
    parser = argparse.ArgumentParser(description="Run a module1-sql query against telemetry.db")
    parser.add_argument("query", help="Path or name of the .sql file to run")
    parser.add_argument("--deploy-ts", default="2026-06-18 10:00:00",
                        help="Deploy timestamp for query 6 (default: 2026-06-18 10:00:00)")
    parser.add_argument("--answer-id", default="answer_target",
                        help="Answer ID for query 8 (default: answer_target)")
    args = parser.parse_args()

    params = {
        "deploy_ts": args.deploy_ts,
        "target_answer_id": args.answer_id,
    }

    rows, columns = run_query(args.query, params)
    print(f"\n--- {os.path.basename(args.query)} ---")
    print(format_table(rows, columns))
    print(f"({len(rows)} row{'s' if len(rows) != 1 else ''})")


if __name__ == "__main__":
    main()
