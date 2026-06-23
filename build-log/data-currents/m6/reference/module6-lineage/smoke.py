"""
smoke.py
End-to-end smoke test for module6-lineage.

Run with:
    python smoke.py

Prints PASS/FAIL per assertion.  Exits non-zero if any assertion fails.
Uses only the standard library; no pytest required.
"""

from __future__ import annotations

import hashlib
import sqlite3
import sys

from schema import init_schema
from lineage import (
    LineageCapture,
    find_lineage_gaps,
    impact_of_version,
    simulate_rag_run,
    trace_answer_to_sources,
)

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------

_RESULTS: list[tuple[str, bool, str]] = []


def _check(name: str, ok: bool, detail: str = "") -> bool:
    _RESULTS.append((name, ok, detail))
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    return ok


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Test helpers: fresh in-memory DB per test group
# ---------------------------------------------------------------------------

def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    init_schema(conn)
    return conn


# ---------------------------------------------------------------------------
# Assertion 1: complete capture
# ---------------------------------------------------------------------------

def test_complete_capture() -> None:
    conn = _db()
    aid = simulate_rag_run(conn, answer_id="ans-1")

    has_source = conn.execute(
        "SELECT 1 FROM source_documents WHERE doc_id='doc-1' AND version_id='v1'"
    ).fetchone()
    has_chunk = conn.execute(
        "SELECT 1 FROM chunks WHERE chunk_id='chunk-1'"
    ).fetchone()
    has_emb = conn.execute(
        "SELECT 1 FROM embeddings WHERE embedding_id='emb-1'"
    ).fetchone()
    has_answer = conn.execute(
        "SELECT 1 FROM answers WHERE answer_id=?", (aid,)
    ).fetchone()
    has_retrieval = conn.execute(
        "SELECT 1 FROM retrievals WHERE answer_id=?", (aid,)
    ).fetchone()
    has_verdict = conn.execute(
        "SELECT 1 FROM eval_verdicts WHERE answer_id=?", (aid,)
    ).fetchone()

    all_present = all([
        has_source, has_chunk, has_emb, has_answer, has_retrieval, has_verdict
    ])
    _check(
        "complete_capture",
        all_present,
        f"source={bool(has_source)} chunk={bool(has_chunk)} emb={bool(has_emb)} "
        f"answer={bool(has_answer)} retrieval={bool(has_retrieval)} verdict={bool(has_verdict)}",
    )
    conn.close()


# ---------------------------------------------------------------------------
# Assertion 2: backward query resolves to correct source + verdict
# ---------------------------------------------------------------------------

def test_backward_query() -> None:
    conn = _db()
    chunk_text = "Paris is the capital of France."
    expected_hash = _sha256(chunk_text)

    aid = simulate_rag_run(
        conn,
        answer_id="ans-2",
        doc_id="doc-A",
        version_id="v2",
        chunk_text=chunk_text,
    )

    rows = trace_answer_to_sources(conn, "ans-2")

    _check(
        "backward_query_nonempty",
        len(rows) > 0,
        f"returned {len(rows)} row(s)",
    )
    if rows:
        row = rows[0]
        _check(
            "backward_query_doc_id",
            row["source_doc_id"] == "doc-A",
            f"got {row['source_doc_id']!r}",
        )
        _check(
            "backward_query_version",
            row["source_doc_version"] == "v2",
            f"got {row['source_doc_version']!r}",
        )
        _check(
            "backward_query_content_hash",
            row["content_hash"] == expected_hash,
            f"got {row['content_hash'][:16]}...",
        )
        _check(
            "backward_query_verdict",
            row["verdict"] == "pass",
            f"got {row['verdict']!r}",
        )
    conn.close()


# ---------------------------------------------------------------------------
# Assertion 3: forward query returns exactly the affected answers
# ---------------------------------------------------------------------------

def test_forward_query() -> None:
    conn = _db()

    # Two answers cite chunks from doc-B v1; one answer cites doc-C v1.
    simulate_rag_run(
        conn,
        answer_id="ans-3a",
        doc_id="doc-B",
        version_id="v1",
        chunk_id="chunk-3a",
        chunk_text="The Eiffel Tower is in Paris.",
        embedding_id="emb-3a",
    )
    simulate_rag_run(
        conn,
        answer_id="ans-3b",
        doc_id="doc-B",
        version_id="v1",
        chunk_id="chunk-3b",
        chunk_text="France is a republic.",
        embedding_id="emb-3b",
    )
    simulate_rag_run(
        conn,
        answer_id="ans-3c",
        doc_id="doc-C",
        version_id="v1",
        chunk_id="chunk-3c",
        chunk_text="Germany borders France.",
        embedding_id="emb-3c",
    )

    affected = impact_of_version(conn, "doc-B", "v1")
    affected_ids = {r["answer_id"] for r in affected}

    _check(
        "forward_query_affected_count",
        len(affected) == 2,
        f"got {len(affected)} answer(s): {affected_ids}",
    )
    _check(
        "forward_query_correct_ids",
        affected_ids == {"ans-3a", "ans-3b"},
        f"got {affected_ids}",
    )
    _check(
        "forward_query_excludes_other_doc",
        "ans-3c" not in affected_ids,
        f"ans-3c present={('ans-3c' in affected_ids)}",
    )
    conn.close()


# ---------------------------------------------------------------------------
# Assertion 4: regression trace — failed verdict + changed source version
# ---------------------------------------------------------------------------

def test_regression_trace() -> None:
    conn = _db()

    # Version v1 of the doc: a specific content_hash
    original_text = "The speed of light is 3 × 10^8 m/s."
    original_hash = _sha256(original_text)

    # Version v2: the doc was updated (different content_hash)
    updated_text = "The speed of light is approximately 3 × 10^8 m/s in a vacuum."
    updated_hash = _sha256(updated_text)

    # Answer was produced against v1 (old hash), verdict = fail
    aid = simulate_rag_run(
        conn,
        answer_id="ans-reg",
        doc_id="doc-physics",
        version_id="v1",
        content_hash=original_hash,
        chunk_id="chunk-physics-v1",
        chunk_text=original_text,
        embedding_id="emb-physics-v1",
        verdict="fail",
        verdict_score=0.3,
        criterion="groundedness",
    )

    # Also record that v2 exists with a different hash (the "change")
    cap = LineageCapture(conn)
    cap.record_source("doc-physics", "v2", updated_hash)

    rows = trace_answer_to_sources(conn, "ans-reg")
    _check(
        "regression_verdict_is_fail",
        any(r["verdict"] == "fail" for r in rows),
        f"verdicts found: {[r['verdict'] for r in rows]}",
    )
    if rows:
        cited_hash = rows[0]["content_hash"]
        cited_version = rows[0]["source_doc_version"]
        _check(
            "regression_cited_version_is_v1",
            cited_version == "v1",
            f"cited version: {cited_version!r}",
        )
        _check(
            "regression_hash_differs_from_v2",
            cited_hash != updated_hash,
            f"cited={cited_hash[:16]}... updated={updated_hash[:16]}...",
        )
        _check(
            "regression_cited_hash_matches_v1",
            cited_hash == original_hash,
            f"cited={cited_hash[:16]}... original={original_hash[:16]}...",
        )
    conn.close()


# ---------------------------------------------------------------------------
# Assertion 5: lineage gap detection
# ---------------------------------------------------------------------------

def test_lineage_gap_detection() -> None:
    conn = _db()

    # Complete answer (should NOT appear as a gap)
    simulate_rag_run(conn, answer_id="ans-complete")

    # Incomplete answer: insert answer row directly, skip retrieval + verdict
    conn.execute(
        "INSERT INTO answers (answer_id, query, answer_text, created_at) "
        "VALUES ('ans-incomplete', 'orphan query', 'orphan answer', '2024-01-01T00:00:00+00:00')"
    )
    conn.commit()

    gaps = find_lineage_gaps(conn)
    gap_ids = {g.answer_id for g in gaps}

    _check(
        "gap_detected_for_incomplete",
        "ans-incomplete" in gap_ids,
        f"gap_ids={gap_ids}",
    )
    _check(
        "no_gap_for_complete",
        "ans-complete" not in gap_ids,
        f"gap_ids={gap_ids}",
    )
    # Verify the gap has the right missing links
    incomplete_gap = next((g for g in gaps if g.answer_id == "ans-incomplete"), None)
    if incomplete_gap:
        _check(
            "gap_reports_no_retrieval",
            "no_retrieval" in incomplete_gap.missing_links,
            f"missing_links={incomplete_gap.missing_links}",
        )
        _check(
            "gap_reports_no_verdict",
            "no_verdict" in incomplete_gap.missing_links,
            f"missing_links={incomplete_gap.missing_links}",
        )
    conn.close()


# ---------------------------------------------------------------------------
# Assertion 6: negatives
# ---------------------------------------------------------------------------

def test_negatives() -> None:
    conn = _db()

    # 6a: trace_answer_to_sources on nonexistent answer_id -> empty list
    result = trace_answer_to_sources(conn, "nonexistent-answer")
    _check(
        "negative_trace_nonexistent_returns_empty",
        result == [],
        f"got {result!r}",
    )

    # 6b: impact_of_version on unknown version -> empty list
    result2 = impact_of_version(conn, "ghost-doc", "v99")
    _check(
        "negative_impact_unknown_version_returns_empty",
        result2 == [],
        f"got {result2!r}",
    )

    # 6c: record_verdict with invalid verdict string -> ValueError
    cap = LineageCapture(conn)
    raised = False
    try:
        cap.record_verdict("any-id", "groundedness", "maybe", 0.5)
    except ValueError:
        raised = True
    _check(
        "negative_invalid_verdict_raises_valueerror",
        raised,
        "ValueError raised as expected" if raised else "no exception raised",
    )

    # 6d: record_embedding with unknown chunk_id -> ValueError
    raised2 = False
    try:
        cap.record_embedding("emb-x", "chunk-ghost", "model@v1")
    except ValueError:
        raised2 = True
    _check(
        "negative_embedding_unknown_chunk_raises_valueerror",
        raised2,
        "ValueError raised as expected" if raised2 else "no exception raised",
    )

    conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 60)
    print("module6-lineage smoke test")
    print("=" * 60)

    test_complete_capture()
    print()
    test_backward_query()
    print()
    test_forward_query()
    print()
    test_regression_trace()
    print()
    test_lineage_gap_detection()
    print()
    test_negatives()

    print()
    print("=" * 60)
    passed = sum(1 for _, ok, _ in _RESULTS if ok)
    failed = sum(1 for _, ok, _ in _RESULTS if not ok)
    print(f"Results: {passed} PASS  {failed} FAIL  (total {len(_RESULTS)})")
    print("=" * 60)

    if failed:
        print("\nFailed assertions:")
        for name, ok, detail in _RESULTS:
            if not ok:
                print(f"  FAIL  {name}  — {detail}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
