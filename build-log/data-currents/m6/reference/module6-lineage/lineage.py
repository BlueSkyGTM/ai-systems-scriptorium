"""
lineage.py
Automatic lineage capture for a RAG/AI pipeline (M6 — Data Currents).

Design principle: every step in the pipeline calls a record_* method on
LineageCapture BEFORE returning its result.  By construction the full chain
source_doc_version -> chunk -> embedding -> retrieval -> answer -> eval_verdict
exists in the store when an answer is complete — no post-hoc reconstruction needed.

M1 connection  : M1's 08_lineage_walk.sql reconstructed this chain from existing
                 tables by hand.  M6 captures it automatically so the walk is
                 always available and complete.

M5 connection  : In production, content_hash values in source_documents come from
                 M5's lakehouse.get_content_hash_at_version(doc_id, version, delta_path).
                 Here we accept them as parameters so the module is offline/self-contained.
"""

from __future__ import annotations

import hashlib
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _uid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# LineageCapture
# ---------------------------------------------------------------------------

class LineageCapture:
    """
    Wrapper that records a lineage link at each RAG pipeline step.

    Usage pattern::

        cap = LineageCapture(conn)
        cap.record_source("doc-1", "v1", content_hash)
        cap.record_chunk("chunk-1", "doc-1", "v1", text)
        cap.record_embedding("emb-1", "chunk-1", "text-embedding-3-small@2024-03")
        answer_id = cap.record_answer(query, answer_text)
        cap.record_retrieval(answer_id, "chunk-1", rank=1, score=0.92)
        cap.record_verdict(answer_id, "groundedness", "pass", 0.95)
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # Step 1 — source document (versioned)
    # ------------------------------------------------------------------

    def record_source(
        self,
        doc_id: str,
        version_id: str,
        content_hash: str,
    ) -> None:
        """
        Record a versioned source document.

        In production: content_hash = M5's
        lakehouse.get_content_hash_at_version(doc_id, version, delta_path).
        Pass INSERT OR IGNORE so re-runs are idempotent.
        """
        self._conn.execute(
            """
            INSERT OR IGNORE INTO source_documents (doc_id, version_id, content_hash)
            VALUES (?, ?, ?)
            """,
            (doc_id, version_id, content_hash),
        )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Step 2 — chunk anchored to doc version
    # ------------------------------------------------------------------

    def record_chunk(
        self,
        chunk_id: str,
        doc_id: str,
        version_id: str,
        text: str,
    ) -> None:
        """
        Record a chunk produced from a specific source-doc version.

        Anchoring to version_id is the key M6 insight: if the same paragraph
        appears in two doc versions with different content_hashes, the chunks
        are distinct records so lineage never blurs across versions.
        """
        self._conn.execute(
            """
            INSERT OR IGNORE INTO chunks
                (chunk_id, source_doc_id, source_doc_version, text)
            VALUES (?, ?, ?, ?)
            """,
            (chunk_id, doc_id, version_id, text),
        )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Step 3 — embedding pinned to model + content_hash
    # ------------------------------------------------------------------

    def record_embedding(
        self,
        embedding_id: str,
        chunk_id: str,
        model_pin: str,
    ) -> str:
        """
        Record an embedding for a chunk.

        Automatically computes content_hash from the chunk text so the hash
        is deterministic and verifiable without storing the raw vector.

        Returns the content_hash so callers can log it if needed.
        """
        row = self._conn.execute(
            "SELECT text FROM chunks WHERE chunk_id = ?", (chunk_id,)
        ).fetchone()
        if row is None:
            raise ValueError(
                f"record_embedding: chunk_id '{chunk_id}' not found in lineage store. "
                "Call record_chunk before record_embedding."
            )
        content_hash = _sha256(row[0])
        self._conn.execute(
            """
            INSERT OR IGNORE INTO embeddings
                (embedding_id, chunk_id, model_pin, content_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (embedding_id, chunk_id, model_pin, content_hash, _now()),
        )
        self._conn.commit()
        return content_hash

    # ------------------------------------------------------------------
    # Step 4 — answer
    # ------------------------------------------------------------------

    def record_answer(
        self,
        query: str,
        answer_text: str,
        answer_id: str | None = None,
    ) -> str:
        """
        Record a generated answer.  Returns the answer_id (auto-generated if
        not supplied) so callers can wire it into record_retrieval/record_verdict.
        """
        aid = answer_id or _uid()
        self._conn.execute(
            """
            INSERT OR IGNORE INTO answers (answer_id, query, answer_text, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (aid, query, answer_text, _now()),
        )
        self._conn.commit()
        return aid

    # ------------------------------------------------------------------
    # Step 5 — retrieval (which chunks backed this answer)
    # ------------------------------------------------------------------

    def record_retrieval(
        self,
        answer_id: str,
        chunk_id: str,
        rank: int,
        score: float,
    ) -> None:
        """
        Record that chunk_id was retrieved at the given rank/score for answer_id.

        Multiple calls per answer_id are expected (one per retrieved chunk).
        This is the join table M1's ANY(retrieved_chunk_ids) array column
        compressed into; here it is a proper normalized table.
        """
        self._conn.execute(
            """
            INSERT INTO retrievals (answer_id, chunk_id, rank, score)
            VALUES (?, ?, ?, ?)
            """,
            (answer_id, chunk_id, rank, score),
        )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Step 6 — eval verdict (terminal node)
    # ------------------------------------------------------------------

    def record_verdict(
        self,
        answer_id: str,
        criterion: str,
        verdict: str,
        score: float,
    ) -> None:
        """
        Record an eval verdict for an answer.

        verdict must be 'pass' or 'fail'.  Multiple criteria per answer
        are supported (one call per criterion).
        """
        if verdict not in ("pass", "fail"):
            raise ValueError(
                f"record_verdict: verdict must be 'pass' or 'fail', got '{verdict}'"
            )
        self._conn.execute(
            """
            INSERT INTO eval_verdicts
                (answer_id, criterion, verdict, score, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (answer_id, criterion, verdict, score, _now()),
        )
        self._conn.commit()


# ---------------------------------------------------------------------------
# simulate_rag_run — drives a minimal end-to-end chain through LineageCapture
# ---------------------------------------------------------------------------

def simulate_rag_run(
    conn: sqlite3.Connection,
    *,
    doc_id: str = "doc-1",
    version_id: str = "v1",
    content_hash: str | None = None,
    chunk_id: str = "chunk-1",
    chunk_text: str = "Paris is the capital of France.",
    embedding_id: str = "emb-1",
    model_pin: str = "text-embedding-3-small@2024-03",
    query: str = "What is the capital of France?",
    answer_text: str = "The capital of France is Paris.",
    answer_id: str | None = None,
    retrieval_rank: int = 1,
    retrieval_score: float = 0.92,
    criterion: str = "groundedness",
    verdict: str = "pass",
    verdict_score: float = 0.95,
) -> str:
    """
    Drive a complete RAG lineage sequence through LineageCapture.

    Returns the answer_id so tests can use it as a query key.
    All parameters are keyword-only so callers can override any single field.
    """
    if content_hash is None:
        content_hash = _sha256(chunk_text)

    cap = LineageCapture(conn)
    cap.record_source(doc_id, version_id, content_hash)
    cap.record_chunk(chunk_id, doc_id, version_id, chunk_text)
    cap.record_embedding(embedding_id, chunk_id, model_pin)
    aid = cap.record_answer(query, answer_text, answer_id=answer_id)
    cap.record_retrieval(aid, chunk_id, rank=retrieval_rank, score=retrieval_score)
    cap.record_verdict(aid, criterion, verdict, verdict_score)
    return aid


# ---------------------------------------------------------------------------
# Backward query: answer -> sources
# ---------------------------------------------------------------------------

def trace_answer_to_sources(
    conn: sqlite3.Connection,
    answer_id: str,
) -> list[dict[str, Any]]:
    """
    BACKWARD lineage walk (M1's 08_lineage_walk.sql, automated and extended).

    For a given answer_id, follows:
        answers -> retrievals -> chunks -> source_documents -> (content_hash)
    and joins in the eval_verdicts so the caller sees the full terminal state.

    Returns a list of dicts, one per (chunk, source_doc_version, verdict) row.
    Returns [] for unknown answer_id.

    This replaces M1's manual WITH-CTE walk: the lineage store guarantees
    every join resolves (capture-by-construction), so no NULL-checking needed.
    """
    cur = conn.execute(
        """
        SELECT
            a.answer_id,
            a.query,
            a.answer_text,
            r.chunk_id,
            r.rank,
            r.score           AS retrieval_score,
            c.source_doc_id,
            c.source_doc_version,
            sd.content_hash,
            ev.criterion,
            ev.verdict,
            ev.score          AS verdict_score
        FROM answers a
        JOIN retrievals r     ON r.answer_id  = a.answer_id
        JOIN chunks c         ON c.chunk_id   = r.chunk_id
        JOIN source_documents sd
                              ON sd.doc_id    = c.source_doc_id
                             AND sd.version_id= c.source_doc_version
        LEFT JOIN eval_verdicts ev ON ev.answer_id = a.answer_id
        WHERE a.answer_id = ?
        ORDER BY r.rank, ev.criterion
        """,
        (answer_id,),
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# Forward query: source version -> affected answers (impact analysis)
# ---------------------------------------------------------------------------

def impact_of_version(
    conn: sqlite3.Connection,
    doc_id: str,
    version_id: str,
) -> list[dict[str, Any]]:
    """
    FORWARD impact analysis.

    Given a source-doc version, return every answer that cited a chunk from it.
    Use case: "If I update doc-1 v1, which answers are affected?"

    Returns a list of dicts with answer_id, query, answer_text, chunk_id.
    Returns [] if no answers cited any chunk from this version.
    """
    cur = conn.execute(
        """
        SELECT DISTINCT
            a.answer_id,
            a.query,
            a.answer_text,
            c.chunk_id
        FROM source_documents sd
        JOIN chunks c         ON c.source_doc_id      = sd.doc_id
                             AND c.source_doc_version  = sd.version_id
        JOIN retrievals r     ON r.chunk_id            = c.chunk_id
        JOIN answers a        ON a.answer_id           = r.answer_id
        WHERE sd.doc_id = ? AND sd.version_id = ?
        ORDER BY a.answer_id
        """,
        (doc_id, version_id),
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# Lineage gap detection
# ---------------------------------------------------------------------------

@dataclass
class LineageGap:
    answer_id: str
    missing_links: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"LineageGap(answer_id={self.answer_id!r}, missing={self.missing_links})"


def find_lineage_gaps(conn: sqlite3.Connection) -> list[LineageGap]:
    """
    Scan every answer and report any that are missing a required link.

    Required links (in order):
        retrieval  — answer must have >= 1 row in retrievals
        verdict    — answer must have >= 1 row in eval_verdicts
        chunk_src  — every retrieved chunk must resolve to a source_documents row

    An incomplete chain is flagged here so callers can alert/quarantine the
    answer rather than silently serving it.  Returns [] when all chains are complete.
    """
    gaps: list[LineageGap] = []

    answers = conn.execute("SELECT answer_id FROM answers").fetchall()
    for (aid,) in answers:
        missing: list[str] = []

        # Check: at least one retrieval
        n_retrievals = conn.execute(
            "SELECT COUNT(*) FROM retrievals WHERE answer_id = ?", (aid,)
        ).fetchone()[0]
        if n_retrievals == 0:
            missing.append("no_retrieval")

        # Check: at least one eval verdict
        n_verdicts = conn.execute(
            "SELECT COUNT(*) FROM eval_verdicts WHERE answer_id = ?", (aid,)
        ).fetchone()[0]
        if n_verdicts == 0:
            missing.append("no_verdict")

        # Check: every cited chunk resolves to a source_documents row
        unresolved = conn.execute(
            """
            SELECT r.chunk_id
            FROM retrievals r
            LEFT JOIN chunks c ON c.chunk_id = r.chunk_id
            LEFT JOIN source_documents sd
                   ON sd.doc_id     = c.source_doc_id
                  AND sd.version_id = c.source_doc_version
            WHERE r.answer_id = ?
              AND sd.doc_id IS NULL
            """,
            (aid,),
        ).fetchall()
        if unresolved:
            missing.append(f"unresolved_chunks:{[r[0] for r in unresolved]}")

        if missing:
            gaps.append(LineageGap(answer_id=aid, missing_links=missing))

    return gaps
