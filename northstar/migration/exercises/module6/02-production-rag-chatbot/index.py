"""index.py -- the swappable retriever seam.

The default is a pure-Python in-memory vector index: hashed bag-of-words
embeddings scored by cosine similarity. No numpy, no faiss, no service. It runs on
the standard library alone, which is what makes the offline smoke path work.

FAISS, Chroma, and Azure AI Search are real production backends. Each is an opt-in
class guarded behind a `try/except ImportError`; none is required to run. They all
satisfy the same `VectorIndex` interface, so the chatbot above them never changes
when you swap the engine. That interface is the seam.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Dict, List, Protocol, Tuple

from ingest import Chunk

_TOKEN = re.compile(r"[a-z0-9]+")
EMBED_DIM = 512  # hashing dimension for the pure-Python embedder


def embed(text: str, dim: int = EMBED_DIM) -> List[float]:
    """Deterministic hashed bag-of-words embedding -- pure stdlib.

    Each token is hashed into one of `dim` buckets; the vector is L2-normalized.
    This is a real (if simple) embedding: lexically similar text lands nearby under
    cosine. It stands in for a neural embedder on the offline path and keeps the
    smoke test dependency-free. Swap `embed` for a model call to go to production.
    """
    vec = [0.0] * dim
    for tok in _TOKEN.findall(text.lower()):
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        bucket = h % dim
        sign = 1.0 if (h >> 8) & 1 else -1.0
        vec[bucket] += sign
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


def cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class VectorIndex(Protocol):
    """The contract every backend implements -- the seam.

    `add` ingests chunks; `search` returns (Chunk, score) pairs ranked by relevance.
    The chatbot binds to this Protocol, not to any one engine.
    """

    def add(self, chunks: List[Chunk]) -> None: ...

    def search(self, query: str, k: int = 4) -> List[Tuple[Chunk, float]]: ...


class InMemoryVectorIndex:
    """Default backend: pure-Python cosine over hashed embeddings. Stdlib only."""

    def __init__(self, dim: int = EMBED_DIM) -> None:
        self.dim = dim
        self._chunks: List[Chunk] = []
        self._vecs: List[List[float]] = []

    def add(self, chunks: List[Chunk]) -> None:
        for c in chunks:
            self._chunks.append(c)
            self._vecs.append(embed(c.text, self.dim))

    def search(self, query: str, k: int = 4) -> List[Tuple[Chunk, float]]:
        q = embed(query, self.dim)
        scored = [(c, cosine(q, v)) for c, v in zip(self._chunks, self._vecs)]
        scored.sort(key=lambda t: t[1], reverse=True)
        return scored[:k]

    def __len__(self) -> int:
        return len(self._chunks)


# --- opt-in production backends (guarded; never required on the smoke path) ----


def build_faiss_index(chunks: List[Chunk]):  # pragma: no cover - needs faiss+numpy
    """Opt-in FAISS backend. Requires `faiss` and `numpy`."""
    try:
        import numpy as np  # type: ignore
        import faiss  # type: ignore
    except ImportError as exc:
        raise RuntimeError("FAISS backend needs `pip install faiss-cpu numpy`") from exc

    class _FaissIndex:
        def __init__(self) -> None:
            self._chunks: List[Chunk] = []
            self._index = faiss.IndexFlatIP(EMBED_DIM)

        def add(self, cs: List[Chunk]) -> None:
            mat = np.array([embed(c.text) for c in cs], dtype="float32")
            self._index.add(mat)
            self._chunks.extend(cs)

        def search(self, query: str, k: int = 4):
            q = np.array([embed(query)], dtype="float32")
            scores, idxs = self._index.search(q, k)
            return [(self._chunks[i], float(s)) for s, i in zip(scores[0], idxs[0]) if i >= 0]

    idx = _FaissIndex()
    idx.add(chunks)
    return idx


def build_azure_search_index(chunks: List[Chunk]):  # pragma: no cover - needs azure + creds
    """Opt-in Azure AI Search backend.

    [verify: azure-search-documents SearchClient.upload_documents / search API]
    [MS-Learn: Azure AI Search vector + hybrid (BM25 + vector) retrieval].

    Reads endpoint/key/index from the environment (.env.example documents them).
    Returns an object satisfying the same `VectorIndex` interface. This is the
    production swap: the chatbot does not change, only the index it is handed.
    """
    import os

    try:
        from azure.core.credentials import AzureKeyCredential  # type: ignore
        from azure.search.documents import SearchClient  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Azure backend needs `pip install azure-search-documents`"
        ) from exc

    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_KEY"]
    index_name = os.environ.get("AZURE_SEARCH_INDEX", "regulated-rag")
    client = SearchClient(endpoint, index_name, AzureKeyCredential(key))

    class _AzureIndex:
        def add(self, cs: List[Chunk]) -> None:
            docs = [
                {
                    "id": c.chunk_id.replace("#", "_").replace(" ", "_"),
                    "doc_id": c.doc_id,
                    "section": c.section,
                    "content": c.text,
                    "embedding": embed(c.text),
                }
                for c in cs
            ]
            client.upload_documents(documents=docs)

        def search(self, query: str, k: int = 4):
            results = client.search(search_text=query, top=k)
            out: List[Tuple[Chunk, float]] = []
            for r in results:
                ch = Chunk(
                    chunk_id=r["id"],
                    doc_id=r.get("doc_id", ""),
                    section=r.get("section", ""),
                    text=r.get("content", ""),
                )
                out.append((ch, float(r.get("@search.score", 0.0))))
            return out

    idx = _AzureIndex()
    idx.add(chunks)
    return idx


def default_index(chunks: List[Chunk]) -> InMemoryVectorIndex:
    """Factory for the offline default. Always stdlib-only."""
    idx = InMemoryVectorIndex()
    idx.add(chunks)
    return idx


if __name__ == "__main__":
    import os
    from ingest import ingest_corpus

    here = os.path.dirname(os.path.abspath(__file__))
    idx = default_index(ingest_corpus(os.path.join(here, "corpus")))
    hits = idx.search("how long are account records kept", k=3)
    for c, s in hits:
        print(f"{s:.3f}  [{c.citation()}]  {c.text[:60]!r}")
