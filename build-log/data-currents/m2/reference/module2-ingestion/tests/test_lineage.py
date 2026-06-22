"""
tests/test_lineage.py
pytest tests for M1 lineage walk reuse against M2 gold tables.

Seeds a answers row referencing a chunk that points at the CHANGED version
of a document, then runs the M1 lineage query and asserts it returns the
correct (changed) content_hash.
"""

import csv
import os
import sqlite3
import sys
from datetime import datetime

import duckdb
import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from ingest import run_ingest, clean_text, content_hash

LINEAGE_SQL_PATH = os.path.join(HERE, "queries", "08_lineage_walk.sql")
SEED_CSV = os.path.join(HERE, "seeds", "corpus_raw.csv")


def open_duckdb_on_sqlite(db_path: str) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(database=":memory:")
    con.execute("INSTALL sqlite; LOAD sqlite;")
    con.execute(f"ATTACH '{db_path}' AS corpus (TYPE sqlite);")
    con.execute("USE corpus;")
    return con


def q(con, sql, params=None):
    rel = con.execute(sql, params or {})
    cols = [d[0] for d in rel.description]
    return [dict(zip(cols, row)) for row in rel.fetchall()]


@pytest.fixture
def lineage_db(tmp_path):
    """
    Build a corpus DB with two ingest runs:
      1. Initial load of all 120 docs.
      2. Mutation of doc_0000's body.

    Seeds an answers row referencing doc_0000_c00 at the changed version.
    Returns (db_path, expected_new_hash).
    """
    db_path = str(tmp_path / "lineage_test.db")

    # Initial load
    run_ingest(csv_path=SEED_CSV, db_path=db_path)

    # Read doc_0000 original values
    original_doc = None
    with open(SEED_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["doc_id"] == "doc_0000":
                original_doc = dict(row)
                break

    # Mutation
    mutated_csv = str(tmp_path / "lineage_mutated.csv")
    with open(SEED_CSV, newline="", encoding="utf-8") as fin, \
         open(mutated_csv, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if row["doc_id"] == "doc_0000":
                row["body"] = row["body"] + " LINEAGE_PYTEST_MARKER"
            writer.writerow(row)

    run_ingest(csv_path=mutated_csv, db_path=db_path)

    # Compute expected new hash
    mutated_text = clean_text(
        original_doc["title"],
        original_doc["body"] + " LINEAGE_PYTEST_MARKER"
    )
    expected_new_hash = content_hash(mutated_text)

    # Find the version_id for the changed doc_0000
    conn = sqlite3.connect(db_path)
    changed = conn.execute(
        "SELECT version_id FROM source_documents WHERE doc_id='doc_0000' AND content_hash=?",
        (expected_new_hash,)
    ).fetchone()
    assert changed is not None, f"Changed version not found for hash={expected_new_hash}"
    changed_version_id = changed[0]

    # Seed answers row pointing at the chunk for doc_0000 at the changed version
    target_chunk_id = "doc_0000_c00"
    conn.execute("DELETE FROM answers WHERE answer_id='lineage_pytest_answer'")
    conn.execute(
        "INSERT INTO answers (answer_id, trace_id, retrieved_chunk_ids) VALUES (?,?,?)",
        ("lineage_pytest_answer", "trace_m2_pytest", target_chunk_id),
    )
    conn.commit()
    conn.close()

    return db_path, expected_new_hash


class TestLineageWalk:
    def test_lineage_query_executes(self, lineage_db):
        db_path, _ = lineage_db
        with open(LINEAGE_SQL_PATH, encoding="utf-8") as f:
            sql = f.read()
        con = open_duckdb_on_sqlite(db_path)
        rows = q(con, sql, {"target_answer_id": "lineage_pytest_answer"})
        con.close()
        assert isinstance(rows, list), "Lineage query must return a list"

    def test_lineage_returns_changed_hash(self, lineage_db):
        db_path, expected_new_hash = lineage_db
        with open(LINEAGE_SQL_PATH, encoding="utf-8") as f:
            sql = f.read()
        con = open_duckdb_on_sqlite(db_path)
        rows = q(con, sql, {"target_answer_id": "lineage_pytest_answer"})
        con.close()

        assert len(rows) == 1, f"Expected 1 row, got {len(rows)}: {rows}"
        assert rows[0]["content_hash"] == expected_new_hash, (
            f"Lineage returned wrong hash: {rows[0]['content_hash']!r}, "
            f"expected {expected_new_hash!r}"
        )

    def test_lineage_result_has_required_columns(self, lineage_db):
        db_path, _ = lineage_db
        with open(LINEAGE_SQL_PATH, encoding="utf-8") as f:
            sql = f.read()
        con = open_duckdb_on_sqlite(db_path)
        rows = q(con, sql, {"target_answer_id": "lineage_pytest_answer"})
        con.close()

        required = {"answer_id", "chunk_id", "source_doc_id", "source_doc_version",
                    "last_modified_at", "content_hash"}
        if rows:
            assert required.issubset(set(rows[0].keys())), \
                f"Missing columns. Got: {set(rows[0].keys())}"

    def test_lineage_empty_for_unknown_answer(self, lineage_db):
        db_path, _ = lineage_db
        with open(LINEAGE_SQL_PATH, encoding="utf-8") as f:
            sql = f.read()
        con = open_duckdb_on_sqlite(db_path)
        rows = q(con, sql, {"target_answer_id": "nonexistent_answer_xyz"})
        con.close()
        assert rows == [], f"Expected empty result for unknown answer, got {rows}"
