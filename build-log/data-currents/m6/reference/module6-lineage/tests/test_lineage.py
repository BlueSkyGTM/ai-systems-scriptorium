"""
tests/test_lineage.py
pytest CI suite for module6-lineage.

Run with:
    python -m pytest tests/ -v

All tests use in-memory SQLite with foreign keys ON.
No external dependencies; deterministic and offline.
"""

from __future__ import annotations

import hashlib
import sqlite3

import pytest

# Make the module importable from tests/
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import init_schema
from lineage import (
    LineageCapture,
    find_lineage_gaps,
    impact_of_version,
    simulate_rag_run,
    trace_answer_to_sources,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def conn():
    """Fresh in-memory SQLite connection with lineage schema and FK enforcement."""
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys = ON")
    init_schema(c)
    yield c
    c.close()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# ---------------------------------------------------------------------------
# 1. Complete capture
# ---------------------------------------------------------------------------

class TestCompleteCapture:
    def test_all_tables_populated(self, conn):
        aid = simulate_rag_run(conn, answer_id="ans-1")

        assert conn.execute(
            "SELECT 1 FROM source_documents WHERE doc_id='doc-1' AND version_id='v1'"
        ).fetchone()
        assert conn.execute(
            "SELECT 1 FROM chunks WHERE chunk_id='chunk-1'"
        ).fetchone()
        assert conn.execute(
            "SELECT 1 FROM embeddings WHERE embedding_id='emb-1'"
        ).fetchone()
        assert conn.execute(
            "SELECT 1 FROM answers WHERE answer_id=?", (aid,)
        ).fetchone()
        assert conn.execute(
            "SELECT 1 FROM retrievals WHERE answer_id=?", (aid,)
        ).fetchone()
        assert conn.execute(
            "SELECT 1 FROM eval_verdicts WHERE answer_id=?", (aid,)
        ).fetchone()

    def test_embedding_content_hash_matches_chunk_text(self, conn):
        chunk_text = "Paris is the capital of France."
        simulate_rag_run(
            conn,
            answer_id="ans-hash",
            chunk_text=chunk_text,
        )
        row = conn.execute(
            "SELECT content_hash FROM embeddings WHERE embedding_id='emb-1'"
        ).fetchone()
        assert row is not None
        assert row[0] == _sha256(chunk_text)

    def test_simulate_returns_answer_id(self, conn):
        aid = simulate_rag_run(conn, answer_id="ans-ret")
        assert aid == "ans-ret"

    def test_simulate_autogenerates_answer_id(self, conn):
        aid = simulate_rag_run(conn)
        assert isinstance(aid, str) and len(aid) > 0


# ---------------------------------------------------------------------------
# 2. Backward query
# ---------------------------------------------------------------------------

class TestBackwardQuery:
    def test_returns_correct_source_doc(self, conn):
        chunk_text = "The Louvre is in Paris."
        simulate_rag_run(
            conn,
            answer_id="ans-bw",
            doc_id="doc-louvre",
            version_id="v3",
            chunk_text=chunk_text,
        )
        rows = trace_answer_to_sources(conn, "ans-bw")
        assert len(rows) > 0
        row = rows[0]
        assert row["source_doc_id"] == "doc-louvre"
        assert row["source_doc_version"] == "v3"
        assert row["content_hash"] == _sha256(chunk_text)

    def test_includes_eval_verdict(self, conn):
        simulate_rag_run(
            conn,
            answer_id="ans-verdict",
            verdict="pass",
            criterion="faithfulness",
        )
        rows = trace_answer_to_sources(conn, "ans-verdict")
        assert any(r["verdict"] == "pass" for r in rows)
        assert any(r["criterion"] == "faithfulness" for r in rows)

    def test_multiple_retrieved_chunks(self, conn):
        """An answer that retrieved two chunks should have two rows (one per chunk)."""
        cap = LineageCapture(conn)
        cap.record_source("doc-multi", "v1", _sha256("text-a"))
        cap.record_chunk("chunk-ma", "doc-multi", "v1", "text-a")
        cap.record_chunk("chunk-mb", "doc-multi", "v1", "text-b")
        cap.record_embedding("emb-ma", "chunk-ma", "model@v1")
        cap.record_embedding("emb-mb", "chunk-mb", "model@v1")
        aid = cap.record_answer("multi query", "multi answer", answer_id="ans-multi")
        cap.record_retrieval(aid, "chunk-ma", rank=1, score=0.9)
        cap.record_retrieval(aid, "chunk-mb", rank=2, score=0.85)
        cap.record_verdict(aid, "groundedness", "pass", 0.88)

        rows = trace_answer_to_sources(conn, "ans-multi")
        chunk_ids = {r["chunk_id"] for r in rows}
        assert "chunk-ma" in chunk_ids
        assert "chunk-mb" in chunk_ids


# ---------------------------------------------------------------------------
# 3. Forward query
# ---------------------------------------------------------------------------

class TestForwardQuery:
    def test_returns_all_affected_answers(self, conn):
        simulate_rag_run(
            conn, answer_id="ans-fa", doc_id="doc-fw", version_id="v1",
            chunk_id="chunk-fa", chunk_text="text a", embedding_id="emb-fa",
        )
        simulate_rag_run(
            conn, answer_id="ans-fb", doc_id="doc-fw", version_id="v1",
            chunk_id="chunk-fb", chunk_text="text b", embedding_id="emb-fb",
        )
        affected = impact_of_version(conn, "doc-fw", "v1")
        ids = {r["answer_id"] for r in affected}
        assert ids == {"ans-fa", "ans-fb"}

    def test_excludes_other_doc_answers(self, conn):
        simulate_rag_run(
            conn, answer_id="ans-fw-target", doc_id="doc-target", version_id="v1",
            chunk_id="chunk-target", chunk_text="target text", embedding_id="emb-target",
        )
        simulate_rag_run(
            conn, answer_id="ans-fw-other", doc_id="doc-other", version_id="v1",
            chunk_id="chunk-other", chunk_text="other text", embedding_id="emb-other",
        )
        affected = impact_of_version(conn, "doc-target", "v1")
        ids = {r["answer_id"] for r in affected}
        assert "ans-fw-target" in ids
        assert "ans-fw-other" not in ids

    def test_excludes_different_version(self, conn):
        simulate_rag_run(
            conn, answer_id="ans-v1", doc_id="doc-ver", version_id="v1",
            chunk_id="chunk-v1", chunk_text="v1 text", embedding_id="emb-v1",
        )
        simulate_rag_run(
            conn, answer_id="ans-v2", doc_id="doc-ver", version_id="v2",
            chunk_id="chunk-v2", chunk_text="v2 text", embedding_id="emb-v2",
        )
        # Impact of v1 only: should NOT include the v2 answer
        affected_v1 = impact_of_version(conn, "doc-ver", "v1")
        ids_v1 = {r["answer_id"] for r in affected_v1}
        assert "ans-v1" in ids_v1
        assert "ans-v2" not in ids_v1


# ---------------------------------------------------------------------------
# 4. Regression trace
# ---------------------------------------------------------------------------

class TestRegressionTrace:
    def test_fail_verdict_surfaces_in_backward_trace(self, conn):
        original_text = "The speed of light is 3e8 m/s."
        simulate_rag_run(
            conn,
            answer_id="ans-fail",
            doc_id="doc-physics",
            version_id="v1",
            content_hash=_sha256(original_text),
            chunk_id="chunk-phys",
            chunk_text=original_text,
            embedding_id="emb-phys",
            verdict="fail",
            verdict_score=0.2,
        )
        rows = trace_answer_to_sources(conn, "ans-fail")
        assert any(r["verdict"] == "fail" for r in rows)

    def test_cited_hash_differs_from_updated_version(self, conn):
        original_text = "The speed of light is 3e8 m/s."
        updated_text = "The speed of light is ~3e8 m/s in vacuum."
        original_hash = _sha256(original_text)
        updated_hash = _sha256(updated_text)
        assert original_hash != updated_hash  # sanity

        simulate_rag_run(
            conn,
            answer_id="ans-changed",
            doc_id="doc-phy2",
            version_id="v1",
            content_hash=original_hash,
            chunk_id="chunk-phy2",
            chunk_text=original_text,
            embedding_id="emb-phy2",
            verdict="fail",
        )
        # Register v2 with updated hash
        cap = LineageCapture(conn)
        cap.record_source("doc-phy2", "v2", updated_hash)

        rows = trace_answer_to_sources(conn, "ans-changed")
        assert rows
        cited_hash = rows[0]["content_hash"]
        cited_version = rows[0]["source_doc_version"]
        assert cited_version == "v1"
        assert cited_hash == original_hash
        assert cited_hash != updated_hash


# ---------------------------------------------------------------------------
# 5. Lineage gap detection
# ---------------------------------------------------------------------------

class TestLineageGapDetection:
    def test_complete_chain_has_no_gap(self, conn):
        simulate_rag_run(conn, answer_id="ans-ok")
        gaps = find_lineage_gaps(conn)
        gap_ids = {g.answer_id for g in gaps}
        assert "ans-ok" not in gap_ids

    def test_answer_missing_retrieval_is_flagged(self, conn):
        conn.execute(
            "INSERT INTO answers (answer_id, query, answer_text, created_at) "
            "VALUES ('ans-no-ret', 'q', 'a', '2024-01-01T00:00:00+00:00')"
        )
        conn.commit()
        gaps = find_lineage_gaps(conn)
        gap = next((g for g in gaps if g.answer_id == "ans-no-ret"), None)
        assert gap is not None
        assert "no_retrieval" in gap.missing_links

    def test_answer_missing_verdict_is_flagged(self, conn):
        cap = LineageCapture(conn)
        cap.record_source("doc-gv", "v1", _sha256("gap verdict text"))
        cap.record_chunk("chunk-gv", "doc-gv", "v1", "gap verdict text")
        cap.record_embedding("emb-gv", "chunk-gv", "model@v1")
        aid = cap.record_answer("query", "answer", answer_id="ans-no-verdict")
        cap.record_retrieval(aid, "chunk-gv", rank=1, score=0.8)
        # Deliberately skip record_verdict

        gaps = find_lineage_gaps(conn)
        gap = next((g for g in gaps if g.answer_id == "ans-no-verdict"), None)
        assert gap is not None
        assert "no_verdict" in gap.missing_links

    def test_find_gaps_returns_empty_when_all_complete(self, conn):
        simulate_rag_run(conn, answer_id="ans-a1", chunk_id="c1", embedding_id="e1",
                         chunk_text="text 1", doc_id="d1", version_id="v1")
        simulate_rag_run(conn, answer_id="ans-a2", chunk_id="c2", embedding_id="e2",
                         chunk_text="text 2", doc_id="d2", version_id="v1")
        gaps = find_lineage_gaps(conn)
        assert gaps == []


# ---------------------------------------------------------------------------
# 6. Negatives
# ---------------------------------------------------------------------------

class TestNegatives:
    def test_trace_nonexistent_answer_returns_empty(self, conn):
        result = trace_answer_to_sources(conn, "ghost-answer-id")
        assert result == []

    def test_impact_unknown_version_returns_empty(self, conn):
        result = impact_of_version(conn, "ghost-doc", "v99")
        assert result == []

    def test_invalid_verdict_raises_value_error(self, conn):
        cap = LineageCapture(conn)
        with pytest.raises(ValueError, match="pass.*fail|fail.*pass"):
            cap.record_verdict("any", "groundedness", "maybe", 0.5)

    def test_embedding_unknown_chunk_raises_value_error(self, conn):
        cap = LineageCapture(conn)
        with pytest.raises(ValueError, match="chunk_id"):
            cap.record_embedding("emb-x", "chunk-does-not-exist", "model@v1")

    def test_duplicate_source_record_is_idempotent(self, conn):
        """record_source with same (doc_id, version_id) twice should not raise."""
        cap = LineageCapture(conn)
        cap.record_source("doc-dup", "v1", _sha256("text"))
        cap.record_source("doc-dup", "v1", _sha256("text"))  # must not raise
        count = conn.execute(
            "SELECT COUNT(*) FROM source_documents WHERE doc_id='doc-dup'"
        ).fetchone()[0]
        assert count == 1

    def test_verdict_value_pass_accepted(self, conn):
        simulate_rag_run(conn, answer_id="ans-pass-val", verdict="pass")
        row = conn.execute(
            "SELECT verdict FROM eval_verdicts WHERE answer_id='ans-pass-val'"
        ).fetchone()
        assert row is not None and row[0] == "pass"

    def test_verdict_value_fail_accepted(self, conn):
        simulate_rag_run(conn, answer_id="ans-fail-val", verdict="fail")
        row = conn.execute(
            "SELECT verdict FROM eval_verdicts WHERE answer_id='ans-fail-val'"
        ).fetchone()
        assert row is not None and row[0] == "fail"
