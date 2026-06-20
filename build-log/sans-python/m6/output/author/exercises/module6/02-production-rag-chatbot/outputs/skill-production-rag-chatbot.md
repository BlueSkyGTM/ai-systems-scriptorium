# Skill: Production RAG Chatbot (Regulated Vertical)

A portable recipe for a citation-enforced, guardrailed RAG chatbot you can drop into a
regulated domain. Pure-Python and offline by default; real services swap in behind one
interface.

## What it gives you

- **Ingestion front door** -- documents to a stable `Chunk` contract. Docling parses real
  PDF/DOCX into a `DoclingDocument` then chunks structure-aware; a stdlib markdown splitter
  is the offline fallback. Downstream code never learns the source format.
- **Swappable retriever seam** -- a `VectorIndex` interface with a pure-Python cosine index
  as the default and FAISS / Azure AI Search as opt-in backends. The chatbot above it does
  not change when the engine does.
- **Cited answers** -- every answer carries a `[source: doc :: section]` citation drawn from
  a retrieved chunk. No source, no claim.
- **Guardrail** -- input/output content screen with hardcoded prohibitions an operator
  cannot disable (the M4 layer-soft-on-hard pattern).
- **Drift monitor** -- a rolling quality mean against an SLO floor (the M5 outer loop).
- **Acceptance gate** -- retrieval precision + answer faithfulness scored against a labeled
  evalset; a build below threshold does not ship.

## The interfaces that make it portable

```python
class VectorIndex(Protocol):
    def add(self, chunks: List[Chunk]) -> None: ...
    def search(self, query: str, k: int = 4) -> List[Tuple[Chunk, float]]: ...

# Chunk is the citation handle: doc_id + section point back to the source.
```

Bind to `VectorIndex` and `Chunk`, not to a PDF or a cloud service. That is the whole
reuse story.

## How to run

```bash
python smoke.py            # end-to-end offline gate, exit 0 on pass
python -m pytest tests/    # operator-surface tests
```

## How to go to production

1. **Retriever** -> `index.build_azure_search_index(chunks)` with `AZURE_SEARCH_*` set.
2. **Generator** -> `chatbot.anthropic_llm` (or an Azure OpenAI deployment) with a key.
3. **Ingestion** -> `pip install docling` for real PDFs; the `Chunk` shape is unchanged.

## Reused as

The **knowledge/retrieval service** for the Module 7 agent fleet. The `Retriever` becomes a
tool a governed agent calls; the citation contract and the eval gate travel with it.
