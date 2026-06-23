"""
tests/test_cdc_pipeline.py
pytest suite for the CDC streaming pipeline (cdc_pipeline.py + corpus_store.py).

Covers:
  - cdc_source: validation, produce, routing
  - apply_event: insert, update, delete, idempotency, corpus state
  - LagMonitor: injectable clock, SLO, breach, report
  - Negative: malformed events, corpus isolation

All tests are offline, deterministic, no network.
"""

import os
import sqlite3
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka_sim import Topic
from corpus_store import bootstrap_db, content_hash, clean_text
from cdc_pipeline import (
    ValidationError,
    apply_event,
    cdc_source,
    LagMonitor,
    validate_event,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    """Temporary SQLite corpus DB; cleaned up after each test."""
    db_path = str(tmp_path / "corpus_test.db")
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def topic():
    """Fresh 4-partition topic for each test."""
    return Topic("docs", num_partitions=4)


def insert_evt(doc_id, body="body text", title="title",
               event_time=1000.0, event_id=None):
    return {
        "op": "insert",
        "doc_id": doc_id,
        "title": title,
        "body": body,
        "event_time": event_time,
        "event_id": event_id or f"evt_{doc_id}_i",
    }


def update_evt(doc_id, body="updated body", title="title",
               event_time=1001.0, event_id=None):
    return {
        "op": "update",
        "doc_id": doc_id,
        "title": title,
        "body": body,
        "event_time": event_time,
        "event_id": event_id or f"evt_{doc_id}_u",
    }


def delete_evt(doc_id, event_time=1002.0, event_id=None):
    return {
        "op": "delete",
        "doc_id": doc_id,
        "event_time": event_time,
        "event_id": event_id or f"evt_{doc_id}_d",
    }


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------

class TestValidation:
    def test_valid_insert_passes(self):
        validate_event(insert_evt("doc_001"))  # no exception

    def test_valid_update_passes(self):
        validate_event(update_evt("doc_001"))

    def test_valid_delete_passes(self):
        validate_event(delete_evt("doc_001"))

    def test_missing_doc_id_raises(self):
        with pytest.raises(ValidationError, match="doc_id"):
            validate_event({"op": "insert", "title": "T", "body": "B"})

    def test_empty_doc_id_raises(self):
        with pytest.raises(ValidationError):
            validate_event({"op": "insert", "doc_id": "", "title": "T", "body": "B"})

    def test_invalid_op_raises(self):
        with pytest.raises(ValidationError, match="op"):
            validate_event({"op": "upsert", "doc_id": "d1", "title": "T", "body": "B"})

    def test_insert_missing_body_raises(self):
        with pytest.raises(ValidationError, match="body"):
            validate_event({"op": "insert", "doc_id": "d1", "title": "T"})

    def test_insert_missing_title_raises(self):
        with pytest.raises(ValidationError, match="title"):
            validate_event({"op": "insert", "doc_id": "d1", "body": "B"})

    def test_update_missing_body_raises(self):
        with pytest.raises(ValidationError):
            validate_event({"op": "update", "doc_id": "d1", "title": "T"})

    def test_delete_no_body_required(self):
        validate_event({"op": "delete", "doc_id": "d1"})  # no exception


# ---------------------------------------------------------------------------
# cdc_source (producer) tests
# ---------------------------------------------------------------------------

class TestCdcSource:
    def test_produce_one_event(self, topic):
        addresses = cdc_source([insert_evt("d1")], topic)
        assert len(addresses) == 1
        assert topic.total_records() == 1

    def test_produce_multiple_events(self, topic):
        events = [insert_evt(f"d{i}") for i in range(10)]
        addresses = cdc_source(events, topic)
        assert len(addresses) == 10
        assert topic.total_records() == 10

    def test_same_doc_id_same_partition(self, topic):
        events = [insert_evt("doc_stable"), update_evt("doc_stable"), delete_evt("doc_stable")]
        addresses = cdc_source(events, topic)
        parts = {addr[0] for addr in addresses}
        assert len(parts) == 1, "All events for same doc_id must land in same partition"

    def test_malformed_event_raises_before_produce(self, topic):
        bad = {"op": "insert", "title": "T", "body": "B"}  # missing doc_id
        with pytest.raises(ValidationError):
            cdc_source([bad], topic)

    def test_records_readable_from_topic(self, topic):
        evt = insert_evt("doc_r1", body="readable body")
        addresses = cdc_source([evt], topic)
        part, offset = addresses[0]
        records = topic.read_from(part, offset)
        assert len(records) == 1
        assert records[0].value["doc_id"] == "doc_r1"


# ---------------------------------------------------------------------------
# apply_event tests
# ---------------------------------------------------------------------------

class TestApplyEvent:
    def test_insert_creates_version_v1(self, tmp_db):
        evt = insert_evt("doc_001", body="hello world")
        result = apply_event(evt, tmp_db, now_ts="2026-01-01 00:00:00")
        assert result["is_new"] is True
        assert result["version_id"] == "v1"
        assert result["op"] == "insert"

    def test_insert_source_documents_row(self, tmp_db):
        evt = insert_evt("doc_002", body="some body")
        apply_event(evt, tmp_db, now_ts="2026-01-01 00:00:00")
        conn = sqlite3.connect(tmp_db)
        row = conn.execute(
            "SELECT version_id, is_deleted FROM source_documents WHERE doc_id='doc_002'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "v1"
        assert row[1] == 0

    def test_update_same_body_is_idempotent(self, tmp_db):
        evt = insert_evt("doc_003", body="same body")
        apply_event(evt, tmp_db, now_ts="2026-01-01 00:00:00")
        # Apply again with same body
        result2 = apply_event(evt, tmp_db, now_ts="2026-01-01 00:00:01")
        assert result2["is_new"] is False
        assert result2["skipped"] is True

    def test_update_different_body_creates_new_version(self, tmp_db):
        insert = insert_evt("doc_004", body="original body")
        apply_event(insert, tmp_db, now_ts="2026-01-01 00:00:00")
        upd = update_evt("doc_004", body="completely different body")
        result2 = apply_event(upd, tmp_db, now_ts="2026-01-01 00:00:01")
        assert result2["is_new"] is True
        assert result2["version_id"] == "v2"

    def test_two_versions_in_source_documents_after_update(self, tmp_db):
        apply_event(insert_evt("doc_005", body="v1 body"), tmp_db,
                    now_ts="2026-01-01 00:00:00")
        apply_event(update_evt("doc_005", body="v2 body"), tmp_db,
                    now_ts="2026-01-01 00:00:01")
        conn = sqlite3.connect(tmp_db)
        count = conn.execute(
            "SELECT COUNT(*) FROM source_documents WHERE doc_id='doc_005'"
        ).fetchone()[0]
        conn.close()
        assert count == 2

    def test_old_version_retained_after_update(self, tmp_db):
        apply_event(insert_evt("doc_006", body="v1 body"), tmp_db,
                    now_ts="2026-01-01 00:00:00")
        v1_hash = content_hash(clean_text("title", "v1 body"))
        apply_event(update_evt("doc_006", body="v2 body"), tmp_db,
                    now_ts="2026-01-01 00:00:01")
        conn = sqlite3.connect(tmp_db)
        retained = conn.execute(
            "SELECT COUNT(*) FROM source_documents "
            "WHERE doc_id='doc_006' AND content_hash=?",
            (v1_hash,),
        ).fetchone()[0]
        conn.close()
        assert retained == 1, "Old version must be retained (history preserved)"

    def test_delete_soft_deletes_all_versions(self, tmp_db):
        apply_event(insert_evt("doc_007", body="v1"), tmp_db,
                    now_ts="2026-01-01 00:00:00")
        apply_event(update_evt("doc_007", body="v2"), tmp_db,
                    now_ts="2026-01-01 00:00:01")
        apply_event(delete_evt("doc_007"), tmp_db, now_ts="2026-01-01 00:00:02")
        conn = sqlite3.connect(tmp_db)
        live = conn.execute(
            "SELECT COUNT(*) FROM source_documents "
            "WHERE doc_id='doc_007' AND is_deleted=0"
        ).fetchone()[0]
        deleted = conn.execute(
            "SELECT COUNT(*) FROM source_documents "
            "WHERE doc_id='doc_007' AND is_deleted=1"
        ).fetchone()[0]
        conn.close()
        assert live == 0
        assert deleted == 2

    def test_delete_idempotent(self, tmp_db):
        apply_event(insert_evt("doc_008", body="body"), tmp_db,
                    now_ts="2026-01-01 00:00:00")
        r1 = apply_event(delete_evt("doc_008"), tmp_db, now_ts="2026-01-01 00:00:01")
        r2 = apply_event(delete_evt("doc_008"), tmp_db, now_ts="2026-01-01 00:00:02")
        assert not r1["skipped"]   # first delete: real change
        assert r2["skipped"]       # second delete: no-op

    def test_chunks_created_on_insert(self, tmp_db):
        apply_event(insert_evt("doc_009", body="word " * 100), tmp_db,
                    now_ts="2026-01-01 00:00:00")
        conn = sqlite3.connect(tmp_db)
        chunk_count = conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE source_doc_id='doc_009'"
        ).fetchone()[0]
        conn.close()
        assert chunk_count >= 1

    def test_replay_same_event_no_duplicate(self, tmp_db):
        """At-least-once idempotency: replaying an event must not add a version."""
        evt = insert_evt("doc_010", body="unique body xyz", event_id="evt_010_stable")
        apply_event(evt, tmp_db, now_ts="2026-01-01 00:00:00")
        apply_event(evt, tmp_db, now_ts="2026-01-01 00:00:01")
        conn = sqlite3.connect(tmp_db)
        count = conn.execute(
            "SELECT COUNT(*) FROM source_documents WHERE doc_id='doc_010'"
        ).fetchone()[0]
        conn.close()
        assert count == 1, "Replaying the same event must not create a duplicate version"

    def test_insert_after_delete_resurrects_doc(self, tmp_db):
        apply_event(insert_evt("doc_011", body="original"), tmp_db,
                    now_ts="2026-01-01 00:00:00")
        apply_event(delete_evt("doc_011"), tmp_db, now_ts="2026-01-01 00:00:01")
        # Re-insert with same content: should un-delete
        apply_event(insert_evt("doc_011", body="original"), tmp_db,
                    now_ts="2026-01-01 00:00:02")
        conn = sqlite3.connect(tmp_db)
        live = conn.execute(
            "SELECT COUNT(*) FROM source_documents "
            "WHERE doc_id='doc_011' AND is_deleted=0"
        ).fetchone()[0]
        conn.close()
        assert live == 1

    def test_apply_invalid_event_raises_validation_error(self, tmp_db):
        with pytest.raises(ValidationError):
            apply_event({"op": "insert", "doc_id": "d1"}, tmp_db)  # missing body

    def test_apply_event_does_not_corrupt_other_docs(self, tmp_db):
        apply_event(insert_evt("doc_good", body="good body"), tmp_db,
                    now_ts="2026-01-01 00:00:00")
        try:
            apply_event({"op": "insert", "doc_id": ""}, tmp_db)
        except ValidationError:
            pass
        conn = sqlite3.connect(tmp_db)
        count = conn.execute(
            "SELECT COUNT(*) FROM source_documents WHERE doc_id='doc_good'"
        ).fetchone()[0]
        conn.close()
        assert count == 1


# ---------------------------------------------------------------------------
# Corpus store direct tests
# ---------------------------------------------------------------------------

class TestCorpusStore:
    def test_bootstrap_creates_tables(self, tmp_db):
        conn = bootstrap_db(tmp_db)
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        conn.close()
        expected = {"source_documents", "chunks", "corpus_loads",
                    "freshness_slos", "cdc_event_log"}
        assert expected.issubset(tables)

    def test_bootstrap_idempotent(self, tmp_db):
        conn1 = bootstrap_db(tmp_db)
        conn1.close()
        conn2 = bootstrap_db(tmp_db)  # second call must not raise
        conn2.close()

    def test_content_hash_deterministic(self):
        h1 = content_hash("hello world")
        h2 = content_hash("hello world")
        assert h1 == h2

    def test_content_hash_changes_on_mutation(self):
        h1 = content_hash("hello world")
        h2 = content_hash("hello world CHANGED")
        assert h1 != h2

    def test_not_null_content_hash_constraint(self, tmp_db):
        conn = bootstrap_db(tmp_db)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO source_documents "
                "(doc_id, version_id, last_modified_at, content_hash, is_deleted) "
                "VALUES ('bad', 'v1', '2026-01-01 00:00:00', NULL, 0)"
            )
        conn.close()


# ---------------------------------------------------------------------------
# LagMonitor tests
# ---------------------------------------------------------------------------

class TestLagMonitor:
    def test_record_returns_lag(self):
        m = LagMonitor(slo_seconds=5.0)
        lag = m.record("src", event_time=1000.0, applied_time=1003.0)
        assert abs(lag - 3.0) < 1e-9

    def test_current_lag_returns_latest_sample(self):
        m = LagMonitor(slo_seconds=5.0)
        m.record("src", event_time=1000.0, applied_time=1002.0)
        m.record("src", event_time=1000.0, applied_time=1004.0)
        assert abs(m.current_lag("src") - 4.0) < 1e-9

    def test_max_lag_returns_worst(self):
        m = LagMonitor(slo_seconds=5.0)
        m.record("src", event_time=1000.0, applied_time=1002.0)
        m.record("src", event_time=1000.0, applied_time=1010.0)
        m.record("src", event_time=1000.0, applied_time=1003.0)
        assert abs(m.max_lag("src") - 10.0) < 1e-9

    def test_within_slo_is_ok(self):
        m = LagMonitor(slo_seconds=5.0)
        m.record("src", event_time=1000.0, applied_time=1003.0)
        assert m.status("src") == "ok"
        assert not m.is_breached("src")

    def test_exceeds_slo_is_breached(self):
        m = LagMonitor(slo_seconds=5.0)
        m.record("src", event_time=1000.0, applied_time=1010.0)
        assert m.status("src") == "breached"
        assert m.is_breached("src")

    def test_exactly_at_slo_is_ok(self):
        m = LagMonitor(slo_seconds=5.0)
        m.record("src", event_time=1000.0, applied_time=1005.0)
        # lag == SLO exactly is NOT a breach (> not >=)
        assert not m.is_breached("src")

    def test_no_data_status(self):
        m = LagMonitor(slo_seconds=5.0)
        assert m.status("unknown") == "no_data"
        assert m.current_lag("unknown") is None
        assert m.max_lag("unknown") is None

    def test_no_data_not_breached(self):
        m = LagMonitor(slo_seconds=5.0)
        assert not m.is_breached("unknown")

    def test_multiple_sources_independent(self):
        m = LagMonitor(slo_seconds=5.0)
        m.record("fast", event_time=1000.0, applied_time=1001.0)
        m.record("slow", event_time=1000.0, applied_time=1020.0)
        assert m.status("fast") == "ok"
        assert m.status("slow") == "breached"

    def test_report_covers_all_sources(self):
        m = LagMonitor(slo_seconds=5.0)
        m.record("src_a", event_time=1000.0, applied_time=1001.0)
        m.record("src_b", event_time=1000.0, applied_time=1008.0)
        report = m.report()
        assert "src_a" in report
        assert "src_b" in report
        assert report["src_a"]["status"] == "ok"
        assert report["src_b"]["status"] == "breached"

    def test_report_sample_count(self):
        m = LagMonitor(slo_seconds=5.0)
        for i in range(7):
            m.record("src", event_time=float(i), applied_time=float(i) + 1.0)
        assert m.report()["src"]["sample_count"] == 7

    def test_slo_boundary_just_over(self):
        m = LagMonitor(slo_seconds=5.0)
        m.record("src", event_time=1000.0, applied_time=1005.0001)
        assert m.is_breached("src")

    def test_negative_lag_not_breached(self):
        # Clock skew: applied_time < event_time -> lag < 0, not a breach
        m = LagMonitor(slo_seconds=5.0)
        m.record("src", event_time=1010.0, applied_time=1005.0)
        assert not m.is_breached("src")


# ---------------------------------------------------------------------------
# End-to-end integration tests
# ---------------------------------------------------------------------------

class TestEndToEnd:
    def test_produce_consume_apply_full_cycle(self, tmp_db):
        """Full round-trip: produce -> read from topic -> apply -> verify corpus."""
        from kafka_sim import ConsumerGroup
        topic = Topic("docs", num_partitions=4)
        group = ConsumerGroup(topic, num_consumers=2)

        events = [
            insert_evt(f"doc_{i:03d}", body=f"body for doc {i}",
                       event_id=f"evt_e2e_{i}")
            for i in range(8)
        ]
        cdc_source(events, topic)

        # Each consumer polls its partitions and applies
        for cid in range(2):
            records = group.poll(cid)
            for rec in records:
                apply_event(rec.value, tmp_db,
                            corpus_version="corpus_v20260622",
                            now_ts="2026-06-22 00:00:00")
            group.commit(cid)

        conn = sqlite3.connect(tmp_db)
        count = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
        conn.close()
        assert count == 8, f"Expected 8 docs in corpus, got {count}"

        # All consumers fully caught up (lag == 0)
        from kafka_sim import ConsumerGroup as CG
        lags = group.lag()
        assert all(v == 0 for v in lags.values()), f"Expected zero lag, got {lags}"

    def test_at_least_once_replay_idempotent(self, tmp_db):
        """Replaying all events (seek to 0) must not create duplicate versions."""
        from kafka_sim import ConsumerGroup
        topic = Topic("docs", num_partitions=1)
        group = ConsumerGroup(topic, num_consumers=1)

        evt = insert_evt("doc_idem", body="idempotent body", event_id="evt_idem_stable")
        cdc_source([evt], topic)

        # First consumption + apply (no commit)
        for rec in group.poll(0):
            apply_event(rec.value, tmp_db, now_ts="2026-01-01 00:00:00")

        # Seek to 0 and replay
        group.seek(0, 0)
        for rec in group.poll(0):
            apply_event(rec.value, tmp_db, now_ts="2026-01-01 00:00:01")

        conn = sqlite3.connect(tmp_db)
        count = conn.execute(
            "SELECT COUNT(*) FROM source_documents WHERE doc_id='doc_idem'"
        ).fetchone()[0]
        conn.close()
        assert count == 1, "Replay must not create duplicate versions"

    def test_lag_monitor_integrated_with_pipeline(self, tmp_db):
        """Lag monitor records lag correctly for events applied via apply_event."""
        monitor = LagMonitor(slo_seconds=5.0)
        topic = Topic("docs", num_partitions=4)

        # Event emitted at t=1000, applied at t=1002 -> lag=2s
        evt = insert_evt("doc_lag_test", body="lag test body", event_time=1000.0,
                         event_id="evt_lag_1")
        cdc_source([evt], topic)
        apply_event(evt, tmp_db, now_ts="2026-01-01 00:00:00")
        monitor.record("corpus_cdc",
                       event_time=evt["event_time"],
                       applied_time=1002.0)

        assert monitor.status("corpus_cdc") == "ok"
        assert not monitor.is_breached("corpus_cdc")

        # Now a stalled event: applied at t=1015 -> lag=15s -> breach
        evt2 = insert_evt("doc_lag_slow", body="slow body", event_time=1000.0,
                          event_id="evt_lag_2")
        cdc_source([evt2], topic)
        apply_event(evt2, tmp_db, now_ts="2026-01-01 00:00:01")
        monitor.record("corpus_cdc",
                       event_time=evt2["event_time"],
                       applied_time=1015.0)

        assert monitor.is_breached("corpus_cdc")
        assert monitor.status("corpus_cdc") == "breached"
