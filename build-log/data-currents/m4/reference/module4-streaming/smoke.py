"""
module4-streaming/smoke.py
Full oracle for the M4 streaming + CDC reference implementation.

Assertions:
  A1  Produce/consume: a produced event is consumed and applied; the corpus
      reflects the change (source_documents has the new version).
  A2  Partitioning: events for the same doc_id always land in the same
      partition; the Topic reports the expected offsets.
  A3  Consumer-group coverage: every partition is assigned to exactly one
      consumer; together the group consumes all produced events exactly once
      under normal delivery.
  A4  At-least-once idempotency: redelivering an already-applied event
      (replay from an uncommitted offset) does NOT create a duplicate
      source_documents version (the MERGE absorbs it).
  A5  Lag monitor — kept-up consumer: low lag (within SLO).
      Lag monitor — stalled consumer: injected lag exceeds SLO => breached.
  N1  Negative: a stalled consumer trips the lag breach as designed.
  N2  Negative: a malformed event (missing doc_id) is rejected with
      ValidationError without corrupting the corpus.

Usage:
  python smoke.py
Exits 0 if all positive assertions PASS and all negatives FAIL as designed.
"""

import os
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from kafka_sim import Topic, ConsumerGroup
from corpus_store import bootstrap_db, content_hash, clean_text
from cdc_pipeline import (
    ValidationError,
    apply_event,
    cdc_source,
    LagMonitor,
)


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


def make_insert_event(doc_id: str, title: str, body: str,
                      event_time: float = 1000.0,
                      event_id: str | None = None) -> dict:
    return {
        "op": "insert",
        "doc_id": doc_id,
        "title": title,
        "body": body,
        "event_time": event_time,
        "event_id": event_id or f"evt_{doc_id}_insert",
    }


def make_update_event(doc_id: str, title: str, body: str,
                      event_time: float = 1001.0,
                      event_id: str | None = None) -> dict:
    return {
        "op": "update",
        "doc_id": doc_id,
        "title": title,
        "body": body,
        "event_time": event_time,
        "event_id": event_id or f"evt_{doc_id}_update",
    }


def make_delete_event(doc_id: str, event_time: float = 1002.0,
                      event_id: str | None = None) -> dict:
    return {
        "op": "delete",
        "doc_id": doc_id,
        "event_time": event_time,
        "event_id": event_id or f"evt_{doc_id}_delete",
    }


# ---------------------------------------------------------------------------
# A1: Produce/consume — corpus reflects the change
# ---------------------------------------------------------------------------

def assert_a1_produce_consume() -> bool:
    print("\n=== A1: Produce/consume ===")
    results = []

    topic = Topic("docs", num_partitions=4)

    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        # Produce one insert event
        event = make_insert_event("doc_alpha", "Alpha Title", "Alpha body text.")
        addresses = cdc_source([event], topic)

        ok = check("A1.1 event produced (one address returned)", len(addresses) == 1,
                   f"addresses={addresses}")
        results.append(ok)

        # Consume from the topic manually (simulate consumer)
        part, offset = addresses[0]
        records = topic.read_from(part, offset)
        ok = check("A1.2 event readable from topic at produced offset",
                   len(records) == 1, f"part={part} offset={offset}")
        results.append(ok)

        # Apply the event
        result = apply_event(event, db_path, corpus_version="corpus_v20260622",
                             now_ts="2026-06-22 10:00:00")
        ok = check("A1.3 apply_event returns success dict",
                   result["op"] == "insert" and result["is_new"],
                   f"result={result}")
        results.append(ok)

        # Verify corpus state
        conn = sqlite3.connect(db_path)
        row = conn.execute(
            "SELECT doc_id, version_id, is_deleted FROM source_documents "
            "WHERE doc_id = 'doc_alpha'"
        ).fetchone()
        conn.close()

        ok = check("A1.4 source_documents has new doc_alpha at v1",
                   row is not None and row[1] == "v1" and row[2] == 0,
                   f"row={row}")
        results.append(ok)

        # Update event
        update_evt = make_update_event(
            "doc_alpha", "Alpha Title", "Alpha body text. UPDATED."
        )
        r2 = apply_event(update_evt, db_path, corpus_version="corpus_v20260622",
                         now_ts="2026-06-22 10:00:01")
        ok = check("A1.5 update creates new version (different body)",
                   r2["is_new"] and r2["version_id"] == "v2", f"r2={r2}")
        results.append(ok)

        # Delete event
        del_evt = make_delete_event("doc_alpha")
        r3 = apply_event(del_evt, db_path, corpus_version="corpus_v20260622",
                         now_ts="2026-06-22 10:00:02")
        ok = check("A1.6 delete marks doc as deleted", not r3["skipped"], f"r3={r3}")
        results.append(ok)

        conn = sqlite3.connect(db_path)
        deleted_count = conn.execute(
            "SELECT COUNT(*) FROM source_documents "
            "WHERE doc_id = 'doc_alpha' AND is_deleted = 1"
        ).fetchone()[0]
        conn.close()
        ok = check("A1.7 all doc_alpha versions are soft-deleted",
                   deleted_count == 2, f"deleted_count={deleted_count}")
        results.append(ok)

    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass

    return all(results)


# ---------------------------------------------------------------------------
# A2: Partitioning — same doc_id always lands in same partition
# ---------------------------------------------------------------------------

def assert_a2_partitioning() -> bool:
    print("\n=== A2: Partitioning (per-key order preserved) ===")
    results = []

    topic = Topic("docs", num_partitions=4)

    # Multiple events for the same doc_id
    events = [
        make_insert_event("doc_beta", "Beta", "v1 body", event_time=1000.0,
                          event_id="evt_beta_1"),
        make_update_event("doc_beta", "Beta", "v2 body", event_time=1001.0,
                          event_id="evt_beta_2"),
        make_update_event("doc_beta", "Beta", "v3 body", event_time=1002.0,
                          event_id="evt_beta_3"),
        # Different doc_id
        make_insert_event("doc_gamma", "Gamma", "gamma body", event_time=1000.0,
                          event_id="evt_gamma_1"),
    ]

    addresses = cdc_source(events, topic)

    # All doc_beta events must be on the same partition
    beta_parts = [addresses[i][0] for i in range(3)]  # first 3 events
    ok = check("A2.1 all doc_beta events on same partition",
               len(set(beta_parts)) == 1,
               f"partitions={beta_parts}")
    results.append(ok)

    # Offsets within that partition are monotonically increasing
    beta_offsets = [addresses[i][1] for i in range(3)]
    ok = check("A2.2 doc_beta offsets monotonically increasing",
               beta_offsets == sorted(beta_offsets) and len(set(beta_offsets)) == 3,
               f"offsets={beta_offsets}")
    results.append(ok)

    # doc_gamma may be on a different partition (hash-based routing)
    gamma_part = addresses[3][0]
    ok = check("A2.3 doc_gamma assigned to a valid partition",
               0 <= gamma_part < topic.num_partitions,
               f"gamma_part={gamma_part}")
    results.append(ok)

    # Topic total record count matches produced count
    ok = check("A2.4 topic total_records == 4",
               topic.total_records() == 4,
               f"total_records={topic.total_records()}")
    results.append(ok)

    # Records on doc_beta's partition appear in order
    beta_part = beta_parts[0]
    records_on_part = topic.read_from(beta_part, 0)
    beta_records = [r for r in records_on_part if r.key == "doc_beta"]
    ok = check("A2.5 doc_beta records appear in insertion order on partition",
               [r.offset for r in beta_records] == sorted(r.offset for r in beta_records),
               f"offsets={[r.offset for r in beta_records]}")
    results.append(ok)

    return all(results)


# ---------------------------------------------------------------------------
# A3: Consumer-group coverage — every partition owned by exactly one consumer
# ---------------------------------------------------------------------------

def assert_a3_consumer_group_coverage() -> bool:
    print("\n=== A3: Consumer-group coverage ===")
    results = []

    topic = Topic("docs", num_partitions=6)
    num_consumers = 3
    group = ConsumerGroup(topic, num_consumers=num_consumers)

    # Verify all_partitions_covered
    ok = check("A3.1 all partitions covered by the group",
               group.all_partitions_covered())
    results.append(ok)

    # Verify no overlap — each partition appears in exactly one assignment
    all_assigned = []
    for cid in range(num_consumers):
        all_assigned.extend(group.assignment(cid))
    ok = check("A3.2 no partition assigned to more than one consumer",
               len(all_assigned) == len(set(all_assigned)),
               f"assigned={sorted(all_assigned)}")
    results.append(ok)

    # Produce events across all partitions; consume once per consumer; each
    # event should be consumed exactly once collectively.
    events = [
        make_insert_event(f"doc_{i:03d}", f"Title {i}", f"Body {i}",
                          event_id=f"evt_a3_{i}")
        for i in range(18)  # 18 events into 6 partitions -> 3 per partition
    ]
    cdc_source(events, topic)

    # Collect all consumed records across all consumers (before any commit)
    consumed: list = []
    for cid in range(num_consumers):
        consumed.extend(group.poll(cid))

    total_produced = topic.total_records()
    ok = check("A3.3 all produced events consumed collectively",
               len(consumed) == total_produced,
               f"consumed={len(consumed)} produced={total_produced}")
    results.append(ok)

    ok = check("A3.4 no duplicates across consumers",
               len({(r.partition, r.offset) for r in consumed}) == len(consumed),
               f"unique={len({(r.partition, r.offset) for r in consumed})} total={len(consumed)}")
    results.append(ok)

    return all(results)


# ---------------------------------------------------------------------------
# A4: At-least-once idempotency — replay does NOT create duplicate versions
# ---------------------------------------------------------------------------

def assert_a4_at_least_once_idempotency() -> bool:
    print("\n=== A4: At-least-once idempotency ===")
    results = []

    # Use 1 consumer so it definitively owns ALL partitions — the at-least-once
    # contract is a property of the consumer, not the partition count.
    topic = Topic("docs", num_partitions=4)
    group = ConsumerGroup(topic, num_consumers=1)

    import tempfile as _tf
    db_fd, db_path = _tf.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        # Produce one event
        event = make_insert_event("doc_delta", "Delta", "Delta body.",
                                  event_id="evt_delta_unique")
        cdc_source([event], topic)

        # Consumer 0 polls and applies but does NOT commit
        records = group.poll(0)
        delta_records = [r for r in records if r.value["doc_id"] == "doc_delta"]
        ok = check("A4.1 consumer 0 polled the event",
                   len(delta_records) >= 1,
                   f"total_polled={len(records)}")
        results.append(ok)

        # Apply each polled record
        for rec in delta_records:
            apply_event(rec.value, db_path, corpus_version="corpus_v20260622",
                        now_ts="2026-06-22 11:00:00")

        conn = sqlite3.connect(db_path)
        v_count_1 = conn.execute(
            "SELECT COUNT(*) FROM source_documents WHERE doc_id='doc_delta'"
        ).fetchone()[0]
        conn.close()

        ok = check("A4.2 after first apply: 1 version in source_documents",
                   v_count_1 == 1, f"v_count={v_count_1}")
        results.append(ok)

        # Simulate at-least-once redelivery: seek back to 0 (uncommitted offset)
        delta_partition = topic._partition_for_key("doc_delta")
        group.seek(delta_partition, 0)

        # Re-poll and re-apply (redelivery)
        redelivered = group.poll(0)
        delta_redelivered = [r for r in redelivered if r.value["doc_id"] == "doc_delta"]
        ok = check("A4.3 redelivery returns the same event",
                   len(delta_redelivered) >= 1,
                   f"total_redelivered={len(redelivered)}")
        results.append(ok)

        for rec in delta_redelivered:
            apply_event(rec.value, db_path, corpus_version="corpus_v20260622",
                        now_ts="2026-06-22 11:00:01")

        conn = sqlite3.connect(db_path)
        v_count_2 = conn.execute(
            "SELECT COUNT(*) FROM source_documents WHERE doc_id='doc_delta'"
        ).fetchone()[0]
        conn.close()

        ok = check("A4.4 after redelivery: STILL only 1 version (MERGE absorbed duplicate)",
                   v_count_2 == 1, f"v_count={v_count_2}")
        results.append(ok)

    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass

    return all(results)


# ---------------------------------------------------------------------------
# A5: Lag monitor — kept-up consumer within SLO; stalled consumer breaches
# ---------------------------------------------------------------------------

def assert_a5_lag_monitor() -> bool:
    print("\n=== A5: Lag monitor (injectable clock) ===")
    results = []

    monitor = LagMonitor(slo_seconds=5.0)

    # Kept-up consumer: event_time=1000, applied_time=1002 -> lag=2s < SLO=5s
    lag1 = monitor.record("corpus_cdc", event_time=1000.0, applied_time=1002.0)
    ok = check("A5.1 kept-up consumer lag is 2s",
               abs(lag1 - 2.0) < 0.001, f"lag={lag1}")
    results.append(ok)

    ok = check("A5.2 kept-up consumer status is 'ok'",
               monitor.status("corpus_cdc") == "ok",
               f"status={monitor.status('corpus_cdc')}")
    results.append(ok)

    ok = check("A5.3 kept-up consumer is not breached",
               not monitor.is_breached("corpus_cdc"))
    results.append(ok)

    # Stalled consumer: event_time=1000, applied_time=1010 -> lag=10s > SLO=5s
    lag2 = monitor.record("corpus_cdc", event_time=1000.0, applied_time=1010.0)
    ok = check("A5.4 stalled consumer lag is 10s",
               abs(lag2 - 10.0) < 0.001, f"lag={lag2}")
    results.append(ok)

    ok = check("A5.5 stalled consumer status is 'breached'",
               monitor.status("corpus_cdc") == "breached",
               f"status={monitor.status('corpus_cdc')}")
    results.append(ok)

    ok = check("A5.6 stalled consumer is_breached() returns True",
               monitor.is_breached("corpus_cdc"))
    results.append(ok)

    # max_lag reports the worst sample
    ok = check("A5.7 max_lag == 10.0",
               abs(monitor.max_lag("corpus_cdc") - 10.0) < 0.001,
               f"max_lag={monitor.max_lag('corpus_cdc')}")
    results.append(ok)

    # Fresh monitor with no data
    m2 = LagMonitor(slo_seconds=5.0)
    ok = check("A5.8 monitor with no data: status='no_data'",
               m2.status("corpus_cdc") == "no_data")
    results.append(ok)

    ok = check("A5.9 monitor with no data: is_breached() is False",
               not m2.is_breached("corpus_cdc"))
    results.append(ok)

    return all(results)


# ---------------------------------------------------------------------------
# N1: Negative — stalled consumer trips lag breach
# ---------------------------------------------------------------------------

def assert_n1_stalled_consumer_breach() -> bool:
    print("\n=== N1: Negative — stalled consumer breaches SLO (expected) ===")

    monitor = LagMonitor(slo_seconds=5.0)

    # Inject a 60-second lag (far past 5s SLO)
    monitor.record("corpus_cdc", event_time=0.0, applied_time=60.0)

    breach = monitor.is_breached("corpus_cdc")
    ok = check("N1 stalled consumer breaches SLO (expected)",
               breach,
               f"lag={monitor.current_lag('corpus_cdc')}s slo=5s")
    return ok


# ---------------------------------------------------------------------------
# N2: Negative — malformed event rejected without corrupting corpus
# ---------------------------------------------------------------------------

def assert_n2_malformed_event_rejected() -> bool:
    print("\n=== N2: Negative — malformed event rejected (expected) ===")
    results = []

    topic = Topic("docs", num_partitions=4)

    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        # First insert a good event so there's baseline corpus state
        good_event = make_insert_event("doc_good", "Good Title", "Good body.",
                                       event_id="evt_good_1")
        cdc_source([good_event], topic)
        apply_event(good_event, db_path, corpus_version="corpus_v20260622",
                    now_ts="2026-06-22 12:00:00")

        conn = sqlite3.connect(db_path)
        good_before = conn.execute(
            "SELECT COUNT(*) FROM source_documents"
        ).fetchone()[0]
        conn.close()

        # Malformed event: missing doc_id
        bad_event_1 = {"op": "insert", "title": "T", "body": "B"}
        rejected_1 = False
        try:
            cdc_source([bad_event_1], topic)
        except ValidationError as exc:
            rejected_1 = True

        ok = check("N2.1 event missing doc_id raises ValidationError",
                   rejected_1)
        results.append(ok)

        # Malformed event: invalid op
        bad_event_2 = {"op": "upsert", "doc_id": "doc_bad", "title": "T", "body": "B"}
        rejected_2 = False
        try:
            cdc_source([bad_event_2], topic)
        except ValidationError:
            rejected_2 = True

        ok = check("N2.2 event with invalid op raises ValidationError", rejected_2)
        results.append(ok)

        # Malformed event: insert missing body — rejected at apply_event too
        bad_event_3 = {"op": "insert", "doc_id": "doc_bad3", "title": "T",
                        "event_time": 1000.0}
        rejected_3 = False
        try:
            apply_event(bad_event_3, db_path)
        except ValidationError:
            rejected_3 = True

        ok = check("N2.3 apply_event rejects insert missing 'body'", rejected_3)
        results.append(ok)

        # Corpus unchanged after all the rejected events
        conn = sqlite3.connect(db_path)
        good_after = conn.execute(
            "SELECT COUNT(*) FROM source_documents"
        ).fetchone()[0]
        conn.close()

        ok = check("N2.4 corpus is uncorrupted after rejected events",
                   good_before == good_after,
                   f"before={good_before} after={good_after}")
        results.append(ok)

    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass

    return all(results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 68)
    print("  module4-streaming smoke runner")
    print("=" * 68)

    results = {
        "A1_produce_consume":      assert_a1_produce_consume(),
        "A2_partitioning":         assert_a2_partitioning(),
        "A3_consumer_group":       assert_a3_consumer_group_coverage(),
        "A4_at_least_once":        assert_a4_at_least_once_idempotency(),
        "A5_lag_monitor":          assert_a5_lag_monitor(),
        "N1_stalled_breach":       assert_n1_stalled_consumer_breach(),
        "N2_malformed_rejected":   assert_n2_malformed_event_rejected(),
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

    print(f"\n  {PASS_COUNT} checks passed, {FAIL_COUNT} checks failed.")
    if all_ok:
        print("All assertions PASSED.")
        sys.exit(0)
    else:
        print("One or more assertions FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
