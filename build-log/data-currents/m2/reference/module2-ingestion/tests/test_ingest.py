"""
tests/test_ingest.py
pytest test suite for module2-ingestion.

Covers:
  - Bronze layer (read_bronze)
  - Silver layer (to_silver / clean_text / content_hash)
  - Chunking (chunk_text)
  - MERGE idempotency (run_ingest twice -> zero new versions)
  - MERGE change detection (mutated body -> one new version, old retained)
  - freshness_check (fresh passes, stale fails)
  - Negative: null content_hash fails assertion (inline assertion, not dbt)

All tests are offline; no network access required.
"""

import csv
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_CSV = os.path.join(HERE, "seeds", "corpus_raw.csv")

# ---------------------------------------------------------------------------
# Import helpers from ingest.py
# ---------------------------------------------------------------------------
import sys
sys.path.insert(0, HERE)

from ingest import (
    bootstrap_db,
    clean_text,
    content_hash,
    chunk_text,
    read_bronze,
    to_silver,
    merge_gold,
    run_ingest,
    write_load_row,
)
from freshness_check import check_freshness


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    """Temporary SQLite corpus DB, cleaned up after each test."""
    db_path = str(tmp_path / "corpus_test.db")
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def tmp_csv(tmp_path):
    """Copy of the seed CSV that tests can mutate safely."""
    import shutil
    dst = str(tmp_path / "corpus_test.csv")
    shutil.copy(SEED_CSV, dst)
    return dst


# ---------------------------------------------------------------------------
# Bronze tests
# ---------------------------------------------------------------------------

class TestBronze:
    def test_read_bronze_row_count(self):
        rows = read_bronze(SEED_CSV)
        assert len(rows) == 120, f"Expected 120 docs, got {len(rows)}"

    def test_read_bronze_fields(self):
        rows = read_bronze(SEED_CSV)
        required = {"doc_id", "created_on", "title", "body", "category", "ingested_at"}
        assert required.issubset(set(rows[0].keys()))

    def test_read_bronze_no_null_doc_ids(self):
        rows = read_bronze(SEED_CSV)
        for r in rows:
            assert r["doc_id"], f"Null doc_id in row: {r}"

    def test_read_bronze_ingested_at_is_timestamp(self):
        rows = read_bronze(SEED_CSV)
        # Should parse as a timestamp
        ts = rows[0]["ingested_at"]
        datetime.fromisoformat(ts)  # raises if invalid


# ---------------------------------------------------------------------------
# Silver / text-cleaning tests
# ---------------------------------------------------------------------------

class TestSilver:
    def test_clean_text_lowercases(self):
        text = clean_text("TITLE", "BODY")
        assert text == text.lower()

    def test_clean_text_strips_urls(self):
        text = clean_text("title", "visit https://example.com for details")
        assert "https://" not in text
        assert "example.com" not in text

    def test_clean_text_collapses_whitespace(self):
        text = clean_text("a  b", "c   d")
        # Should not have double spaces
        assert "  " not in text

    def test_clean_text_concat_order(self):
        text = clean_text("alpha", "beta")
        assert text.startswith("alpha")
        assert "beta" in text

    def test_content_hash_deterministic(self):
        h1 = content_hash("hello world")
        h2 = content_hash("hello world")
        assert h1 == h2

    def test_content_hash_changes_on_mutation(self):
        h1 = content_hash("hello world")
        h2 = content_hash("hello world CHANGED")
        assert h1 != h2

    def test_content_hash_not_null(self):
        h = content_hash("any text")
        assert h is not None and len(h) > 0

    def test_to_silver_count(self):
        bronze = read_bronze(SEED_CSV)
        silver = to_silver(bronze)
        assert len(silver) == 120

    def test_to_silver_unique_doc_ids(self):
        bronze = read_bronze(SEED_CSV)
        silver = to_silver(bronze)
        doc_ids = [r["doc_id"] for r in silver]
        assert len(doc_ids) == len(set(doc_ids)), "Duplicate doc_ids in silver"

    def test_to_silver_no_null_content_hash(self):
        bronze = read_bronze(SEED_CSV)
        silver = to_silver(bronze)
        for r in silver:
            assert r["content_hash"], f"Null content_hash for {r['doc_id']}"

    def test_to_silver_text_not_null(self):
        bronze = read_bronze(SEED_CSV)
        silver = to_silver(bronze)
        for r in silver:
            assert r["text"], f"Empty text for {r['doc_id']}"


# ---------------------------------------------------------------------------
# Chunking tests
# ---------------------------------------------------------------------------

class TestChunking:
    def test_chunk_text_returns_at_least_one(self):
        chunks = chunk_text("doc_0000", "word " * 10)
        assert len(chunks) >= 1

    def test_chunk_text_max_three(self):
        # Long text: 300 words -> 3 chunks
        text = " ".join(f"word{i}" for i in range(300))
        chunks = chunk_text("doc_big", text)
        assert len(chunks) <= 3

    def test_chunk_ids_deterministic(self):
        text = "hello world " * 50
        c1 = chunk_text("doc_0001", text)
        c2 = chunk_text("doc_0001", text)
        assert [cid for cid, _ in c1] == [cid for cid, _ in c2]

    def test_chunk_ids_include_doc_id(self):
        chunks = chunk_text("doc_0099", "some text here")
        for chunk_id, _ in chunks:
            assert "doc_0099" in chunk_id

    def test_chunk_text_nonempty(self):
        chunks = chunk_text("doc_0000", "hello world")
        for _, ct in chunks:
            assert ct.strip(), "Empty chunk text"

    def test_chunk_empty_text_gives_one_chunk(self):
        chunks = chunk_text("doc_empty", "")
        assert len(chunks) == 1


# ---------------------------------------------------------------------------
# Idempotency tests (core MERGE contract)
# ---------------------------------------------------------------------------

class TestIdempotency:
    def test_two_runs_same_version_count(self, tmp_db, tmp_csv):
        s1 = run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        assert s1["status"] == "success"

        conn = sqlite3.connect(tmp_db)
        count1 = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
        conn.close()

        s2 = run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        assert s2["status"] == "success"

        conn = sqlite3.connect(tmp_db)
        count2 = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
        conn.close()

        assert count1 == count2, f"Version count changed: {count1} -> {count2}"

    def test_second_run_new_versions_zero(self, tmp_db, tmp_csv):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        s2 = run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        assert s2["new_versions"] == 0, \
            f"Expected 0 new versions, got {s2['new_versions']}"

    def test_content_hashes_identical_after_two_runs(self, tmp_db, tmp_csv):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        hashes1 = frozenset(
            r[0] for r in conn.execute("SELECT content_hash FROM source_documents").fetchall()
        )
        conn.close()

        run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        hashes2 = frozenset(
            r[0] for r in conn.execute("SELECT content_hash FROM source_documents").fetchall()
        )
        conn.close()

        assert hashes1 == hashes2


# ---------------------------------------------------------------------------
# Change detection tests
# ---------------------------------------------------------------------------

class TestChangeDetection:
    def _make_mutated_csv(self, src: str, doc_id: str, suffix: str, dst: str):
        with open(src, newline="", encoding="utf-8") as fin, \
             open(dst, "w", newline="", encoding="utf-8") as fout:
            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                if row["doc_id"] == doc_id:
                    row["body"] = row["body"] + f" {suffix}"
                writer.writerow(row)

    def test_mutation_inserts_one_new_version(self, tmp_db, tmp_csv, tmp_path):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)

        conn = sqlite3.connect(tmp_db)
        count_before = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
        conn.close()

        mut_csv = str(tmp_path / "mutated.csv")
        self._make_mutated_csv(tmp_csv, "doc_0001", "PYTEST_MUTATION", mut_csv)

        s2 = run_ingest(csv_path=mut_csv, db_path=tmp_db)

        conn = sqlite3.connect(tmp_db)
        count_after = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
        conn.close()

        assert count_after == count_before + 1, \
            f"Expected exactly one new version; before={count_before} after={count_after}"
        assert s2["new_versions"] == 1

    def test_old_version_retained_after_mutation(self, tmp_db, tmp_csv, tmp_path):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)

        conn = sqlite3.connect(tmp_db)
        orig_hash = conn.execute(
            "SELECT content_hash FROM source_documents WHERE doc_id='doc_0001'"
        ).fetchone()[0]
        conn.close()

        mut_csv = str(tmp_path / "mutated.csv")
        self._make_mutated_csv(tmp_csv, "doc_0001", "RETAIN_TEST_MUTATION", mut_csv)
        run_ingest(csv_path=mut_csv, db_path=tmp_db)

        conn = sqlite3.connect(tmp_db)
        retained = conn.execute(
            "SELECT COUNT(*) FROM source_documents "
            "WHERE doc_id='doc_0001' AND content_hash=?",
            (orig_hash,)
        ).fetchone()[0]
        conn.close()

        assert retained == 1, "Original version (old hash) not retained after mutation"

    def test_new_version_has_different_hash(self, tmp_db, tmp_csv, tmp_path):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)

        conn = sqlite3.connect(tmp_db)
        orig_hash = conn.execute(
            "SELECT content_hash FROM source_documents WHERE doc_id='doc_0002'"
        ).fetchone()[0]
        conn.close()

        mut_csv = str(tmp_path / "mutated2.csv")
        self._make_mutated_csv(tmp_csv, "doc_0002", "NEW_HASH_TEST_MUTATION", mut_csv)
        run_ingest(csv_path=mut_csv, db_path=tmp_db)

        conn = sqlite3.connect(tmp_db)
        hashes = [
            r[0] for r in conn.execute(
                "SELECT content_hash FROM source_documents WHERE doc_id='doc_0002'"
            ).fetchall()
        ]
        conn.close()

        assert len(hashes) == 2, f"Expected 2 versions, got {hashes}"
        assert orig_hash in hashes, "Original hash missing"
        assert len(set(hashes)) == 2, "Both versions must have distinct hashes"


# ---------------------------------------------------------------------------
# Corpus loads audit
# ---------------------------------------------------------------------------

class TestCorpusLoads:
    def test_load_row_written(self, tmp_db, tmp_csv):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        count = conn.execute("SELECT COUNT(*) FROM corpus_loads").fetchone()[0]
        conn.close()
        assert count >= 1

    def test_load_row_status_success(self, tmp_db, tmp_csv):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT status, rows_ingested FROM corpus_loads WHERE status='success'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[1] == 120

    def test_two_runs_two_load_rows(self, tmp_db, tmp_csv):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        count = conn.execute("SELECT COUNT(*) FROM corpus_loads").fetchone()[0]
        conn.close()
        assert count == 2


# ---------------------------------------------------------------------------
# Freshness tests
# ---------------------------------------------------------------------------

class TestFreshness:
    def test_fresh_source_passes(self, tmp_db, tmp_csv):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        loaded_at = conn.execute(
            "SELECT MAX(loaded_at) FROM corpus_loads WHERE status='success'"
        ).fetchone()[0]
        conn.close()

        # now = loaded_at + 1h  -> age=1h < SLO=25h
        now_ts = (datetime.fromisoformat(loaded_at) + timedelta(hours=1)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        results = check_freshness(db_path=tmp_db, now_ts=now_ts)
        corpus_raw = next(r for r in results if r["source_id"] == "corpus_raw")
        assert not corpus_raw["is_stale"], \
            f"corpus_raw should be fresh: {corpus_raw}"

    def test_stale_source_fails(self, tmp_db, tmp_csv):
        run_ingest(csv_path=tmp_csv, db_path=tmp_db)
        conn = sqlite3.connect(tmp_db)
        loaded_at = conn.execute(
            "SELECT MAX(loaded_at) FROM corpus_loads WHERE status='success'"
        ).fetchone()[0]
        conn.close()

        # now = loaded_at + 30h -> age=30h > SLO=25h
        now_ts = (datetime.fromisoformat(loaded_at) + timedelta(hours=30)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        results = check_freshness(db_path=tmp_db, now_ts=now_ts)
        corpus_raw = next(r for r in results if r["source_id"] == "corpus_raw")
        assert corpus_raw["is_stale"], \
            f"corpus_raw should be stale at age>SLO: {corpus_raw}"

    def test_never_loaded_is_stale(self, tmp_db):
        # Bootstrap DB (creates freshness_slos) but never run ingest
        conn = bootstrap_db(tmp_db)
        conn.close()   # close before check_freshness opens the same file (Windows lock)
        results = check_freshness(db_path=tmp_db)
        corpus_raw = next(r for r in results if r["source_id"] == "corpus_raw")
        assert corpus_raw["is_stale"], \
            "A source that has never been loaded must be stale"


# ---------------------------------------------------------------------------
# Negative / assertion tests
# ---------------------------------------------------------------------------

class TestNegative:
    def test_null_content_hash_fails_assertion(self, tmp_db):
        """
        Negative: the NOT NULL constraint on source_documents.content_hash is the
        guard against null hashes reaching the store.

        Attempting to INSERT a row with content_hash=NULL must raise IntegrityError.
        This mirrors what dbt's not_null test catches at the dbt layer; here we
        demonstrate the same invariant at the SQLite schema layer.
        """
        conn = bootstrap_db(tmp_db)
        # Attempt to violate the not_null contract
        with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
            conn.execute(
                "INSERT INTO source_documents "
                "(doc_id, version_id, last_modified_at, content_hash) "
                "VALUES ('bad_doc', 'v1', '2026-01-01 00:00:00', NULL)"
            )
        conn.close()

    def test_stale_source_explicitly_stale(self, tmp_db):
        """Stale source past SLO must be flagged is_stale=True (negative gate fires)."""
        conn = bootstrap_db(tmp_db)
        stale_ts = (datetime.utcnow() - timedelta(hours=30)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO corpus_loads (load_id, source_id, status, loaded_at, rows_ingested) "
            "VALUES ('load_neg_test','corpus_raw','success',?,120)",
            (stale_ts,),
        )
        conn.commit()
        conn.close()

        now_ts = (datetime.fromisoformat(stale_ts) + timedelta(hours=30)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        results = check_freshness(db_path=tmp_db, now_ts=now_ts)
        corpus_raw = next(r for r in results if r["source_id"] == "corpus_raw")
        assert corpus_raw["is_stale"], \
            f"Expected stale; got {corpus_raw}"
