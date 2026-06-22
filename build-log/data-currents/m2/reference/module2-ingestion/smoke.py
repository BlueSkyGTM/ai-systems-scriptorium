"""
module2-ingestion/smoke.py
Full oracle: build, idempotency, change detection, M1 lineage reuse,
freshness, and two deliberate negative cases.

Assertions:
  A1  Medallion build: dbt build + dbt test green (all layers materialize).
  A2  Idempotency: run ingest twice on unchanged source -> zero new versions.
  A3  Change detection: mutate one doc's body, re-run -> exactly one new version,
      old version retained.
  A4  Lineage reuse: M1 query runs against M2 gold tables and returns the
      changed content_hash for the seeded answer.
  A5  Freshness: fresh source passes; stale source fails the SLO gate.
  N1  Negative — broken silver (null content_hash) fails a dbt assertion.
  N2  Negative — stale source past SLO fails freshness gate as expected.

Usage:
  python smoke.py
Exits 0 if all positive assertions PASS and all negative cases FAIL as expected.
"""

import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import csv

import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASS_COUNT = 0
FAIL_COUNT = 0


def check(label: str, condition: bool, detail: str = "") -> bool:
    global PASS_COUNT, FAIL_COUNT
    status = "PASS" if condition else "FAIL"
    if condition:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
    msg = f"  [{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return condition


def run_cmd(cmd: list[str], cwd: str = HERE, capture: bool = True) -> tuple[int, str]:
    """Run a subprocess; return (returncode, combined stdout+stderr)."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=capture, text=True
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output


def dbt_cmd(args: list[str], cwd: str = HERE) -> tuple[int, str]:
    """Run a dbt command with the profiles.yml in the project dir."""
    return run_cmd(
        ["dbt", "--no-use-colors"] + args + ["--profiles-dir", "."],
        cwd=cwd,
    )


def open_duckdb_on_sqlite(db_path: str) -> duckdb.DuckDBPyConnection:
    """Open an in-memory DuckDB connection attached to a SQLite file."""
    con = duckdb.connect(database=":memory:")
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"ATTACH '{db_path}' AS corpus (TYPE sqlite);")
    con.execute("USE corpus;")
    return con


def q(con: duckdb.DuckDBPyConnection, sql: str, params: dict | None = None) -> list[dict]:
    """Execute sql, return list of dicts."""
    rel = con.execute(sql, params or {})
    cols = [d[0] for d in rel.description]
    return [dict(zip(cols, row)) for row in rel.fetchall()]


# ---------------------------------------------------------------------------
# A1: Medallion build (dbt build + dbt test)
# ---------------------------------------------------------------------------

def assert_a1_medallion_build() -> bool:
    print("\n=== A1: Medallion build (dbt seed + dbt build + dbt test) ===")
    results = []

    # Seed
    rc, out = dbt_cmd(["seed", "--full-refresh"])
    ok = check("A1.1 dbt seed", rc == 0, f"rc={rc}")
    if not ok:
        print(out[-2000:])
    results.append(ok)

    # Build models
    rc, out = dbt_cmd(["build", "--select", "models/", "--full-refresh"])
    ok = check("A1.2 dbt build models", rc == 0, f"rc={rc}")
    if not ok:
        print(out[-2000:])
    results.append(ok)

    # Schema tests
    rc, out = dbt_cmd(["test", "--select", "models/"])
    ok = check("A1.3 dbt test schema", rc == 0, f"rc={rc}")
    if not ok:
        print(out[-3000:])
    results.append(ok)

    # Verify key tables exist in dbt's DuckDB (across all schemas)
    try:
        con = duckdb.connect(database=os.path.join(HERE, "corpus.duckdb"))
        # dbt-duckdb places tables in schema-specific schemas (main_bronze, main_silver, main_gold)
        all_tables = con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema != 'pg_catalog'"
        ).fetchall()
        con.close()
        table_names = {r[0].lower() for r in all_tables}
        expected = {
            "bronze_corpus_raw", "silver_corpus_clean",
            "gold_source_documents", "gold_chunks",
            "gold_corpus_loads", "gold_freshness_slos",
        }
        missing = expected - table_names
        ok = check("A1.4 all layers materialized", len(missing) == 0,
                   f"found={sorted(table_names)}, missing={missing}")
    except Exception as e:
        ok = check("A1.4 all layers materialized", False, str(e))
    results.append(ok)

    return all(results)


# ---------------------------------------------------------------------------
# A2: Idempotency
# ---------------------------------------------------------------------------

def assert_a2_idempotency() -> bool:
    print("\n=== A2: Idempotency (two runs on unchanged source -> zero new versions) ===")
    from ingest import run_ingest

    db_path = os.path.join(HERE, "test_idempotency.db")
    csv_path = os.path.join(HERE, "seeds", "corpus_raw.csv")

    # Clean slate
    if os.path.exists(db_path):
        os.remove(db_path)

    # First run
    s1 = run_ingest(csv_path=csv_path, db_path=db_path)
    check("A2.1 first run succeeds", s1["status"] == "success", str(s1))

    # Snapshot state after run 1
    conn = sqlite3.connect(db_path)
    versions_after_1 = conn.execute(
        "SELECT doc_id, version_id, content_hash FROM source_documents ORDER BY doc_id, version_id"
    ).fetchall()
    hashes_after_1 = frozenset(
        conn.execute("SELECT content_hash FROM source_documents").fetchall()
    )
    conn.close()

    # Second run — identical source
    s2 = run_ingest(csv_path=csv_path, db_path=db_path)
    check("A2.2 second run succeeds", s2["status"] == "success", str(s2))

    # Compare
    conn = sqlite3.connect(db_path)
    versions_after_2 = conn.execute(
        "SELECT doc_id, version_id, content_hash FROM source_documents ORDER BY doc_id, version_id"
    ).fetchall()
    hashes_after_2 = frozenset(
        conn.execute("SELECT content_hash FROM source_documents").fetchall()
    )
    conn.close()

    versions_equal = versions_after_1 == versions_after_2
    hashes_equal   = hashes_after_1   == hashes_after_2
    zero_new       = s2["new_versions"] == 0

    ok_v = check("A2.3 version count unchanged", versions_equal,
                 f"after_1={len(versions_after_1)} after_2={len(versions_after_2)}")
    ok_h = check("A2.4 content_hash set identical", hashes_equal)
    ok_z = check("A2.5 new_versions==0 on second run", zero_new,
                 f"new_versions={s2['new_versions']}")

    os.remove(db_path)
    return all([ok_v, ok_h, ok_z])


# ---------------------------------------------------------------------------
# A3: Change detection
# ---------------------------------------------------------------------------

def assert_a3_change_detection() -> bool:
    print("\n=== A3: Change detection (one doc changed -> one new version, old retained) ===")
    from ingest import run_ingest

    db_path  = os.path.join(HERE, "test_change.db")
    csv_orig = os.path.join(HERE, "seeds", "corpus_raw.csv")

    if os.path.exists(db_path):
        os.remove(db_path)

    # Initial load
    s1 = run_ingest(csv_path=csv_orig, db_path=db_path)
    check("A3.1 initial load succeeds", s1["status"] == "success")

    conn = sqlite3.connect(db_path)
    versions_before = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
    # Record the original content_hash for doc_0000
    original_row = conn.execute(
        "SELECT version_id, content_hash FROM source_documents WHERE doc_id = 'doc_0000'"
    ).fetchone()
    conn.close()

    original_version_id   = original_row[0]
    original_content_hash = original_row[1]

    check("A3.2 doc_0000 initially at v1", original_version_id == "v1",
          f"version_id={original_version_id}")

    # Build mutated CSV: change doc_0000's body
    mutated_csv = os.path.join(HERE, "test_mutated_corpus.csv")
    with open(csv_orig, newline="", encoding="utf-8") as fin, \
         open(mutated_csv, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if row["doc_id"] == "doc_0000":
                row["body"] = row["body"] + " MUTATED_BODY_CHANGE_FOR_VERSION_DETECTION"
            writer.writerow(row)

    # Second load with mutation
    s2 = run_ingest(csv_path=mutated_csv, db_path=db_path)
    check("A3.3 mutated load succeeds", s2["status"] == "success")

    conn = sqlite3.connect(db_path)
    versions_after = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
    doc0_rows = conn.execute(
        "SELECT version_id, content_hash FROM source_documents "
        "WHERE doc_id = 'doc_0000' ORDER BY version_id"
    ).fetchall()
    conn.close()

    new_version_count = versions_after - versions_before
    old_retained = any(r[1] == original_content_hash for r in doc0_rows)
    new_version_exists = any(r[1] != original_content_hash for r in doc0_rows)

    ok_count = check("A3.4 exactly one new version inserted", new_version_count == 1,
                     f"versions_before={versions_before} versions_after={versions_after}")
    ok_old = check("A3.5 old version retained (original hash present)",
                   old_retained, f"doc_0000 rows={doc0_rows}")
    ok_new = check("A3.6 new version exists (new hash present)",
                   new_version_exists, f"doc_0000 rows={doc0_rows}")
    ok_new_v = check("A3.7 new_versions==1 reported", s2["new_versions"] == 1,
                     f"new_versions={s2['new_versions']}")

    os.remove(db_path)
    os.remove(mutated_csv)
    return all([ok_count, ok_old, ok_new, ok_new_v])


# ---------------------------------------------------------------------------
# A4: M1 lineage walk reuse
# ---------------------------------------------------------------------------

def assert_a4_lineage_reuse() -> bool:
    """
    Seed an answers row referencing a chunk that points at the CHANGED version
    of doc_0000. Run the M1 lineage walk SQL and assert it returns the new
    content_hash.

    This assertion:
      1. Runs a fresh initial + mutation ingest (same as A3 logic).
      2. Seeds an answers row whose chunk resolves to the doc_0000 v2 (changed) row.
      3. Runs queries/08_lineage_walk.sql via DuckDB ATTACH.
      4. Asserts the walk returns the new content_hash.
    """
    print("\n=== A4: M1 lineage walk runs against M2 gold tables ===")
    from ingest import run_ingest, content_hash as ch, clean_text

    db_path  = os.path.join(HERE, "test_lineage.db")
    csv_orig = os.path.join(HERE, "seeds", "corpus_raw.csv")

    if os.path.exists(db_path):
        os.remove(db_path)

    # Initial load
    run_ingest(csv_path=csv_orig, db_path=db_path)

    # Mutated load
    mutated_csv = os.path.join(HERE, "test_lineage_mutated.csv")
    with open(csv_orig, newline="", encoding="utf-8") as fin, \
         open(mutated_csv, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()
        original_doc = None
        for row in reader:
            if row["doc_id"] == "doc_0000":
                original_doc = dict(row)
                row["body"] = row["body"] + " LINEAGE_MUTATION_MARKER"
            writer.writerow(row)

    run_ingest(csv_path=mutated_csv, db_path=db_path)

    # Compute expected new hash
    mutated_text = clean_text(
        original_doc["title"],
        original_doc["body"] + " LINEAGE_MUTATION_MARKER"
    )
    expected_new_hash = ch(mutated_text)

    # Find the chunk for doc_0000, v2
    conn = sqlite3.connect(db_path)
    changed_row = conn.execute(
        "SELECT version_id, content_hash FROM source_documents "
        "WHERE doc_id = 'doc_0000' AND content_hash = ?",
        (expected_new_hash,)
    ).fetchone()

    if not changed_row:
        check("A4.1 changed version exists in DB", False,
              f"expected_hash={expected_new_hash}")
        conn.close()
        os.remove(db_path)
        os.remove(mutated_csv)
        return False

    changed_version_id = changed_row[0]
    check("A4.1 changed version exists in DB", True,
          f"version_id={changed_version_id} hash={expected_new_hash[:8]}...")

    # The chunk for doc_0000 that points at v2
    target_chunk_id = f"doc_0000_c00"   # first chunk of doc_0000
    chunk_row = conn.execute(
        "SELECT chunk_id, source_doc_version FROM chunks "
        "WHERE chunk_id = ? AND source_doc_version = ?",
        (target_chunk_id, changed_version_id)
    ).fetchone()

    if not chunk_row:
        # After mutation the chunk is replaced (INSERT OR REPLACE) pointing at v2
        check("A4.2 chunk references changed version", False,
              f"chunk_id={target_chunk_id} expected version={changed_version_id}")
        conn.close()
        os.remove(db_path)
        os.remove(mutated_csv)
        return False

    check("A4.2 chunk references changed version", True,
          f"chunk_id={target_chunk_id} version={changed_version_id}")

    # Seed an answers row referencing this chunk
    # (answers uses a fake trace_id — M2 doesn't have spans)
    conn.execute("DELETE FROM answers WHERE answer_id = 'answer_lineage_test'")
    conn.execute(
        "INSERT INTO answers (answer_id, trace_id, retrieved_chunk_ids) VALUES (?,?,?)",
        ("answer_lineage_test", "trace_m2_synthetic", target_chunk_id),
    )
    conn.commit()
    conn.close()

    # Run the M1 lineage walk SQL
    sql_path = os.path.join(HERE, "queries", "08_lineage_walk.sql")
    with open(sql_path, encoding="utf-8") as f:
        sql = f.read()

    con = open_duckdb_on_sqlite(db_path)
    rows = q(con, sql, {"target_answer_id": "answer_lineage_test"})
    con.close()

    found_hash = rows[0]["content_hash"] if rows else None
    ok_hash = check("A4.3 lineage walk returns changed content_hash",
                    found_hash == expected_new_hash,
                    f"found={found_hash} expected={expected_new_hash[:8]}...")
    ok_rows = check("A4.4 lineage walk returns exactly one chunk row",
                    len(rows) == 1, f"rows={len(rows)}")

    os.remove(db_path)
    os.remove(mutated_csv)
    return ok_hash and ok_rows


# ---------------------------------------------------------------------------
# A5: Freshness (positive: fresh passes; sub-test for stale already covered by N2)
# ---------------------------------------------------------------------------

def assert_a5_freshness() -> bool:
    print("\n=== A5: Freshness — fresh source passes SLO gate ===")
    from ingest import run_ingest
    from freshness_check import check_freshness

    db_path  = os.path.join(HERE, "test_freshness_pos.db")
    csv_path = os.path.join(HERE, "seeds", "corpus_raw.csv")

    if os.path.exists(db_path):
        os.remove(db_path)

    run_ingest(csv_path=csv_path, db_path=db_path)

    # Use a "now" that is 1 hour after the load (well within 25h SLO)
    # We query the actual load timestamp then set now = load_ts + 1h
    conn = sqlite3.connect(db_path)
    loaded_at = conn.execute(
        "SELECT MAX(loaded_at) FROM corpus_loads WHERE status='success'"
    ).fetchone()[0]
    conn.close()

    from datetime import datetime, timedelta
    now_ts = (datetime.fromisoformat(loaded_at) + timedelta(hours=1)).isoformat(sep=" ")

    results = check_freshness(db_path=db_path, now_ts=now_ts)
    corpus_raw_result = next((r for r in results if r["source_id"] == "corpus_raw"), None)

    ok = check("A5.1 corpus_raw is fresh (age<SLO) when now=load+1h",
               corpus_raw_result is not None and not corpus_raw_result["is_stale"],
               str(corpus_raw_result))

    os.remove(db_path)
    return ok


# ---------------------------------------------------------------------------
# N1: Negative — broken silver (null content_hash) fails dbt assertion
# ---------------------------------------------------------------------------

def assert_n1_broken_silver_fails() -> bool:
    """
    Inject a deliberately broken silver model that produces a NULL content_hash.
    Run dbt test — it MUST fail the not_null test.
    We restore the original model after the test.
    Expected outcome: dbt test fails -> our assertion is PASS (negative confirmed).
    """
    print("\n=== N1: Negative — null content_hash fails dbt not_null test ===")

    silver_path = os.path.join(HERE, "models", "silver", "silver_corpus_clean.sql")
    with open(silver_path, encoding="utf-8") as f:
        original_sql = f.read()

    # Inject NULL for content_hash
    broken_sql = original_sql.replace(
        "md5(text) AS content_hash",
        "NULL::TEXT AS content_hash   -- deliberately broken for N1 negative test"
    )

    with open(silver_path, "w", encoding="utf-8") as f:
        f.write(broken_sql)

    try:
        # Rebuild broken silver
        rc_build, out_build = dbt_cmd(["build", "--select", "silver_corpus_clean", "--full-refresh"])
        # Run tests (specifically the not_null on content_hash)
        rc_test, out_test = dbt_cmd(["test", "--select", "silver_corpus_clean"])

        # We expect dbt test to fail (rc != 0)
        dbt_failed_as_expected = (rc_test != 0)
        ok = check("N1 broken silver fails dbt not_null test (expected fail)",
                   dbt_failed_as_expected,
                   f"dbt test rc={rc_test} (rc!=0 means test caught the null)")
    finally:
        # Restore original
        with open(silver_path, "w", encoding="utf-8") as f:
            f.write(original_sql)
        # Rebuild correct silver
        dbt_cmd(["build", "--select", "silver_corpus_clean", "--full-refresh"])

    return ok


# ---------------------------------------------------------------------------
# N2: Negative — stale source fails freshness gate
# ---------------------------------------------------------------------------

def assert_n2_stale_fails_freshness() -> bool:
    """
    Write a corpus_loads row 30 hours old for a source with a 25h SLO.
    Run freshness_check with now=row_ts+30h.
    Expected: is_stale=True -> gate returns non-zero (FAIL) -> our assertion is PASS.
    """
    print("\n=== N2: Negative — stale source fails freshness gate (expected fail) ===")
    from freshness_check import check_freshness

    db_path = os.path.join(HERE, "test_stale_negative.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    from ingest import bootstrap_db
    from datetime import datetime, timedelta

    conn = bootstrap_db(db_path)

    # Write a load that is 30 hours old (SLO is 25h -> stale)
    stale_ts = (datetime.utcnow() - timedelta(hours=30)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO corpus_loads (load_id, source_id, status, loaded_at, rows_ingested) "
        "VALUES (?, ?, ?, ?, ?)",
        ("load_stale_test", "corpus_raw", "success", stale_ts, 120),
    )
    conn.commit()
    conn.close()

    # Now = stale_ts + 30h  -> age = 30h > 25h SLO
    now_ts = (datetime.fromisoformat(stale_ts) + timedelta(hours=30)).strftime("%Y-%m-%d %H:%M:%S")
    results = check_freshness(db_path=db_path, now_ts=now_ts)
    corpus_raw = next((r for r in results if r["source_id"] == "corpus_raw"), None)

    stale_detected = corpus_raw is not None and corpus_raw["is_stale"]
    ok = check("N2 stale source detected as stale (expected)", stale_detected,
               f"age_hours={corpus_raw['age_hours'] if corpus_raw else 'N/A'} slo={25}")

    os.remove(db_path)
    return ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 68)
    print("  module2-ingestion smoke runner")
    print("=" * 68)

    # Pre-flight: ensure dbt seed ran (corpus.duckdb must have the seed table)
    print("\n--- Pre-flight: dbt seed ---")
    rc, out = dbt_cmd(["seed", "--full-refresh"])
    if rc != 0:
        print(out[-1000:])
        print("ABORT: dbt seed failed. Cannot continue.")
        sys.exit(2)
    print("  dbt seed OK")

    results = {
        "A1_medallion_build":   assert_a1_medallion_build(),
        "A2_idempotency":       assert_a2_idempotency(),
        "A3_change_detection":  assert_a3_change_detection(),
        "A4_lineage_reuse":     assert_a4_lineage_reuse(),
        "A5_freshness":         assert_a5_freshness(),
        "N1_broken_silver_neg": assert_n1_broken_silver_fails(),
        "N2_stale_neg":         assert_n2_stale_fails_freshness(),
    }

    print("\n" + "=" * 68)
    print("  SUMMARY")
    print("=" * 68)
    all_ok = True
    for label, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {status}  {label}")
        if not passed:
            all_ok = False

    print()
    if all_ok:
        print("All assertions PASSED.")
        sys.exit(0)
    else:
        print("One or more assertions FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
