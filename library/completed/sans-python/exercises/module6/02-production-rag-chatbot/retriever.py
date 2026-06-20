"""retriever.py -- the portable retriever interface.

The chatbot asks the retriever for context; the retriever asks a VectorIndex for
candidates. Keeping the retriever separate from the index is what lets the index
swap (in-memory -> FAISS -> Azure AI Search) without the chatbot noticing, and it
is where a reranker or a hybrid (dense + BM25) merge slots in later -- one place,
not threaded through the caller.

This interface is what Module 7 reuses as the knowledge/retrieval service.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from index import VectorIndex
from ingest import Chunk


@dataclass
class Retrieved:
    """A retrieved chunk and its relevance score, ready to cite."""

    chunk: Chunk
    score: float

    @property
    def citation(self) -> str:
        return self.chunk.citation()


class Retriever:
    """Wraps any VectorIndex. The stable surface the chatbot binds to."""

    def __init__(self, index: VectorIndex, *, min_score: float = 0.0) -> None:
        self._index = index
        self._min_score = min_score

    def retrieve(self, query: str, k: int = 4) -> List[Retrieved]:
        """Return the top-k chunks above the relevance floor.

        The `min_score` floor is the CRAG-style reliability gate from M2 advanced
        RAG: when nothing clears the floor, the answerer should refuse rather than
        fabricate from low-relevance context.
        """
        hits: List[Tuple[Chunk, float]] = self._index.search(query, k=k)
        return [Retrieved(chunk=c, score=s) for c, s in hits if s >= self._min_score]


if __name__ == "__main__":
    import os
    from index import default_index
    from ingest import ingest_corpus

    here = os.path.dirname(os.path.abspath(__file__))
    r = Retriever(default_index(ingest_corpus(os.path.join(here, "corpus"))))
    for hit in r.retrieve("multi-factor authentication", k=3):
        print(f"{hit.score:.3f}  [{hit.citation}]")
