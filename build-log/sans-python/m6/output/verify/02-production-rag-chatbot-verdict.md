# VERIFY verdict — 02 Production RAG Chatbot

Artifact: `build-stages/m6/output/author/02-production-rag-chatbot.md`
Scaffold: `build-stages/m6/output/author/exercises/module6/02-production-rag-chatbot/`
Gate: guide-prose correctness (claims + STYLE + guide-matches-scaffold). Code already passed BUILD→TEST.
Verdict: **PASS (fixes applied in place)**

## Markers resolved

| Marker (location) | Resolution | Source |
|---|---|---|
| `[MS-Learn: Azure AI Search vector + hybrid retrieval]` (Capability bullet) | Verified + rewritten to clean prose: "executes a BM25 keyword query and a vector query in parallel, then merges with Reciprocal Rank Fusion." | MS Learn — learn.microsoft.com/azure/search/hybrid-search-overview ("Hybrid search combines results from both full-text and vector queries… BM25 for text, HNSW… for vectors. An RRF algorithm merges the results.") |
| `[verify: Anthropic Messages API system-prompt grounding]` (Generation bullet) | Verified + rewritten: "prompted through the Messages API with a system prompt that says answer only from the retrieved context and cite each claim or refuse." Matches `chatbot.py:anthropic_llm` (uses `client.messages.create(system=…, messages=[…])` with a cite-or-refuse system prompt). | scaffold `chatbot.py`; Anthropic Messages API shape. |

Zero markers remain in the guide (grep clean for `[verify:` / `[MS-Learn:`).

## Claim ledger

- **Docling parses PDF/DOCX/PPTX into a `DoclingDocument`, chunks structure-aware** — VERIFIED. WebFetch github.com/docling-project/docling: `DocumentConverter` → `DoclingDocument`, supports PDF/DOCX/PPTX/XLSX/HTML/etc. `HybridChunker` (importable from `docling.chunking`) does tokenization-aware refinement on top of document-based hierarchical chunking. Matches scaffold `ingest.py` (`from docling.chunking import HybridChunker`) and the M5 lesson-11 grounding (LF AI & Data, MIT — confirmed).
- **Azure AI Search hybrid (BM25 + vector) retrieval, RRF merge** — VERIFIED via MS Learn (above).
- **Anthropic model id not hardcoded; read from env** — CONSISTENT. Scaffold `chatbot.py` reads `os.environ["ANTHROPIC_MODEL"]`; `.env.example` documents it. Guide does not name a model id. Honors the build-progress gotcha (current model `claude-opus-4-8`, never hardcode from memory).
- **Two-interface seam (`Chunk` + `VectorIndex`); Azure AI Search ↔ local index is one constructor call** — VERIFIED against scaffold. `index.py` defines `VectorIndex(Protocol)` with `add`/`search`; `InMemoryVectorIndex` (stdlib, hashed bag-of-words cosine, no numpy/FAISS) is the default; `build_azure_search_index` and `build_faiss_index` are guarded opt-in backends satisfying the same interface. The guide's seam code block matches the Protocol signature exactly.
- **Relevance floor / CRAG-style refusal** — VERIFIED. `retriever.py` `min_score` floor; `chatbot.py` returns a no-context refusal when nothing clears it.
- **Three operator surfaces (guardrail / drift / eval gate), all real** — VERIFIED. `guardrail.py` (hardcoded `_PROHIBITED` floor + operator-adjustable `_OFF_TOPIC_DEFAULT`), `drift.py` (rolling window vs SLO floor), `eval.py` (retrieval precision + answer faithfulness, deterministic, `passes()` gate).
- **BUILD→TEST: `smoke.py` exit 0; `pytest tests/` 5/5; low-faithfulness build fails the gate** — VERIFIED by reading `smoke.py` (6 steps, exit 0 only if all surfaces behave) and `tests/test_smoke.py` (exactly 5 tests incl. `test_low_faithfulness_answer_fails_the_acceptance_gate`). Matches build-progress "pytest 5/5".

## Guide-matches-scaffold

Confirmed: file names (`ingest/index/retriever/chatbot/guardrail/drift/eval/smoke`), the `VectorIndex` Protocol + `Chunk` contract, the Azure-AI-Search-swaps-for-local-index seam claim, the mock-LLM generation seam, the three operator surfaces, and the offline stdlib-only smoke gate all match the scaffold. No drift found in this guide.

## STYLE (full read)

- H1 present; seam-style two-paragraph lead (problem + why a seam engineer needs it); `## What you build` + `## Core concepts` immediately precede the handoff; `<div class="claude-handoff">` present with correct `data-exercise` path.
- Second person, present tense, one confident voice throughout. No banned template ending ("An AI Platform Engineer who…"); section endings vary (reframe, consequence, warning).
- Fix applied: expanded **SLO** → "service-level-objective (SLO)" on first use (build sequence step 6). Other acronyms (PII, BM25, DOCX/PPTX, CRAG, OpenTelemetry) are domain-standard for the audience and consistent with shipped M5; left as-is.
- No qualifier/passive defects found warranting edit.

## FLAGGED (non-blocking)

- None blocking. The guide's mention of Azure OpenAI as an alternate generator is accurate (scaffold notes Azure OpenAI as an opt-in swap in the README) though only the Anthropic path is implemented in `chatbot.py`; the guide says "Azure OpenAI or Anthropic," which the README backs.
