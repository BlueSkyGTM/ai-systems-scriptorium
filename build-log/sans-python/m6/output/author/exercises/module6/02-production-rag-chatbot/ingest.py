"""ingest.py -- the front door: documents -> chunks.

Docling is the production parser (PDF/DOCX/PPTX into a structured DoclingDocument,
then a structure-aware HybridChunker). It is heavy and optional, so the import is
guarded. On the offline smoke path we fall back to a stdlib markdown parser that
splits the sample corpus at section-header boundaries -- the same structure-aware
move Docling makes, executed cheaply for plain text.

The contract downstream code binds to is `Chunk`, never "a PDF". That is the
DoclingDocument seam carried forward: swap the parser, keep the chunk shape.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List

# --- guarded third-party import (production parser) ----------------------------
try:  # pragma: no cover - exercised only when docling is installed
    from docling.document_converter import DocumentConverter  # type: ignore
    from docling.chunking import HybridChunker  # type: ignore

    _HAS_DOCLING = True
except ImportError:
    _HAS_DOCLING = False


@dataclass
class Chunk:
    """The unit the index stores and the retriever returns.

    `doc_id` and `section` are the citation handle: an answer cites a chunk, and
    the chunk points back to its source document and section.
    """

    chunk_id: str
    doc_id: str
    section: str
    text: str
    meta: dict = field(default_factory=dict)

    def citation(self) -> str:
        return f"{self.doc_id} :: {self.section}"


def _split_markdown(doc_id: str, text: str) -> List[Chunk]:
    """Stdlib structure-aware split: one chunk per `##` section.

    Header text rides along as metadata -- the same source-anchoring context that
    lifts retrieval recall (M2 contextual retrieval). No third-party dependency.
    """
    chunks: List[Chunk] = []
    # Title line (single '#') becomes the document heading; '##' starts sections.
    current_section = "Preamble"
    buffer: List[str] = []
    idx = 0

    def flush() -> None:
        nonlocal idx, buffer, current_section
        body = "\n".join(buffer).strip()
        if body:
            chunks.append(
                Chunk(
                    chunk_id=f"{doc_id}#{idx}",
                    doc_id=doc_id,
                    section=current_section,
                    text=body,
                    meta={"source": "stdlib-markdown"},
                )
            )
            idx += 1
        buffer = []

    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            flush()
            current_section = m.group(1).strip()
            continue
        if re.match(r"^#\s+", line):  # document title -- attach to section name
            continue
        buffer.append(line)
    flush()
    return chunks


def _chunk_with_docling(path: str) -> List[Chunk]:  # pragma: no cover - needs docling
    """Production path: parse to a DoclingDocument, then HybridChunker.

    The chunker splits at the document's structural boundaries and sizes chunks to
    an embedding tokenizer. Output is mapped onto the same `Chunk` contract, so the
    index never learns it came from a PDF.
    """
    doc_id = os.path.basename(path)
    converter = DocumentConverter()
    dl_doc = converter.convert(path).document
    chunker = HybridChunker()
    out: List[Chunk] = []
    for i, ch in enumerate(chunker.chunk(dl_doc=dl_doc)):
        headings = getattr(getattr(ch, "meta", None), "headings", None) or []
        section = headings[-1] if headings else "body"
        out.append(
            Chunk(
                chunk_id=f"{doc_id}#{i}",
                doc_id=doc_id,
                section=str(section),
                text=ch.text,
                meta={"source": "docling"},
            )
        )
    return out


def ingest_path(path: str) -> List[Chunk]:
    """Ingest a single file into chunks. Uses Docling if available, else stdlib."""
    if _HAS_DOCLING and path.lower().endswith((".pdf", ".docx", ".pptx", ".xlsx")):
        return _chunk_with_docling(path)
    doc_id = os.path.basename(path)
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    return _split_markdown(doc_id, text)


def ingest_corpus(corpus_dir: str) -> List[Chunk]:
    """Ingest every .md/.txt file in a directory into a flat chunk list."""
    chunks: List[Chunk] = []
    for name in sorted(os.listdir(corpus_dir)):
        if name.lower().endswith((".md", ".txt", ".pdf", ".docx")):
            chunks.extend(ingest_path(os.path.join(corpus_dir, name)))
    return chunks


def docling_available() -> bool:
    return _HAS_DOCLING


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    cs = ingest_corpus(os.path.join(here, "corpus"))
    print(f"docling_available={_HAS_DOCLING}  chunks={len(cs)}")
    for c in cs[:3]:
        print(f"  {c.chunk_id}  [{c.citation()}]  {c.text[:60]!r}")
