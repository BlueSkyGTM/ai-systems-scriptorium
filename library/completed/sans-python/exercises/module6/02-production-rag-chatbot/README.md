# Production RAG Chatbot -- Regulated Vertical

A retrieval-augmented chatbot for a regulated domain (compliance / legal / clinical),
where an answer without a citation is a liability and an unsafe query must never reach
the model. This is the most-shipped production AI shape of 2026, built the way it has
to be built when a regulator can audit the transcript.

## The business problem

A compliance team is drowning in policy documents. People ask the same questions --
"how long do we keep account records?", "is MFA required for PII?" -- and get answers
from whoever is free, with no source and no audit trail. You replace that with a
chatbot that answers **only** from the approved policy corpus, **cites the exact source
section** for every claim, **refuses** unsafe or out-of-scope queries at the door, and
**logs a quality signal** so you know when its answers start drifting. Citations and
guardrails are not features here. They are the reason the system is allowed to exist.

## Run it (offline, no cloud, no GPU)

```bash
python smoke.py            # ingest -> index -> cited answer -> guardrail -> drift -> eval
python -m pytest tests/    # the operator-surface tests
```

Both run on the Python standard library alone. Every third-party dependency (Docling,
FAISS, Azure AI Search, Anthropic) is a guarded import with a stdlib fallback used on
the smoke path.

## What each file does

| File | Role |
|------|------|
| `ingest.py` | documents -> `Chunk`s. Docling if installed; stdlib markdown splitter otherwise. |
| `index.py` | the **retriever seam** -- a pure-Python cosine vector index by default; FAISS / Azure AI Search opt-in behind the same `VectorIndex` interface. |
| `retriever.py` | the portable retriever interface (where a reranker / hybrid merge slots in). |
| `chatbot.py` | retrieve -> answer **with citations** (deterministic mock LLM; real LLM opt-in). |
| `guardrail.py` | input/output content screen with hardcoded prohibitions (the M4 pattern). |
| `drift.py` | rolling quality metric with an SLO floor (the M5 observability move). |
| `eval.py` | retrieval precision + answer faithfulness -- the **acceptance gate**. |
| `corpus/` | a small sample regulated corpus + `evalset.json` (Q / expected source / expected facts). |
| `smoke.py` | the end-to-end offline gate. Exit 0 only if every operator surface behaves. |

## Operator surfaces (what you drive in M8)

- **Guardrail gate** -- `guardrail.py` blocks an unsafe query before retrieval. Hardcoded
  prohibitions cannot be lowered by config.
- **Drift metric** -- `drift.py` tracks a rolling quality mean against an SLO floor and
  flags a breach.
- **Acceptance gate** -- `eval.py` returns retrieval precision and answer faithfulness; a
  build below threshold does not ship.

## Extend to Azure (the production swap)

The retriever is the seam. To move from the local index to Azure AI Search:

1. `pip install azure-search-documents` and create an index in your Azure AI Search
   service with a vector field alongside the text fields (and an optional semantic
   configuration for reranking) so a single query can run BM25 and vector search in
   parallel and merge them with Reciprocal Rank Fusion.
2. Set `AZURE_SEARCH_ENDPOINT` / `AZURE_SEARCH_KEY` / `AZURE_SEARCH_INDEX` (see `.env.example`).
3. Build the index with `index.build_azure_search_index(chunks)` instead of
   `index.default_index(chunks)` and hand it to the same `Retriever`.

Nothing else changes. The `Chatbot`, the guardrail, the eval gate, and the drift monitor
all bind to the `VectorIndex` interface and the `Chunk` contract, not to any one backend.
The same move swaps the mock LLM for `chatbot.anthropic_llm` (set `ANTHROPIC_API_KEY`) or
an Azure OpenAI deployment.

To ingest real PDFs/DOCX, `pip install docling`; `ingest.py` picks it up automatically
and produces the same `Chunk` shape via the `DoclingDocument` -> `HybridChunker` path.

## Reused in Module 7

This artifact is the **knowledge/retrieval service**. In M7 the `Retriever` becomes a tool
a governed agent fleet calls; the citation contract and the eval gate travel with it.
