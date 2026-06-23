# Module 6 — Lineage: From Document to Eval Verdict — Build Plan (self-locked)

Status: **PLAN SELF-LOCKED 2026-06-21** (straight-through mandate; gates self-cleared). M6 productionizes
the manual lineage walk from M1 into an automated lineage store that records the full provenance chain,
from a source-document version through the embedding and retrieval to the cited answer and its eval
verdict, and answers "why did this answer change" and "what is affected" as graph queries.

## The stage in one line

M1 walked lineage by hand; M5 gave us versioned documents via Delta time-travel; M6 captures the whole
chain automatically and makes it queryable. Seam: when an answer's quality drops, lineage is the chain
that explains exactly which upstream change caused it, end to end.

## Settled decisions

1. **Throughline composes M1 + M5 (and M4's verdicts).** `module6-lineage/` records the chain:
   `source_doc_version -> chunk -> embedding_pin -> retrieved_context -> answer -> eval_verdict`. It
   reuses M1's answer/chunk/source_documents lineage shape and M5's Delta time-travel (a document's
   content_hash at a version) so "what did this answer cite, at which version" resolves exactly.
2. **Capture, do not reconstruct.** The M1 walk reconstructed lineage from existing tables. M6's point
   is automatic capture: a thin wrapper records a lineage link at each pipeline step as the work
   happens (embedding pins the model + content_hash, retrieval logs the chunk ids, the answer logs the
   retrieved context, the eval logs its verdict). Lineage is then complete by construction.
3. **Two queries are the payoff.** Backward: answer -> the exact source-document versions it cited
   (root-cause). Forward: a changed source-document version -> the answers affected (impact analysis).
4. **Purview is the enterprise surface.** Microsoft Purview Unified Catalog + data lineage + column-level
   lineage is the cross-system governance surface; M6 teaches it as the production home for what the
   local store models, grounded in MS-Learn. The local store is the offline-runnable model.

## Proposed M6 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind |
|---|---------------|----------|------|
| 0 | `00-overview` | Lineage is the chain from source document to eval verdict; here is the graph, automatic capture, the two queries, and Purview. | concept |
| 1 | `the-lineage-graph` | Lineage is a graph of provenance links (source-version -> chunk -> embedding -> retrieval -> answer -> verdict); each link is a recorded row. | build |
| 2 | `capturing-lineage-automatically` | A capture wrapper records each link as the pipeline step runs, so lineage is complete by construction, not reconstructed after the fact. | build |
| 3 | `querying-the-lineage-store` | The store answers two questions: backward (answer -> source versions it cited) and forward (changed version -> affected answers / impact analysis). | build |
| 4 | `lineage-as-governance-purview` | Enterprise lineage is a governance surface: Microsoft Purview Unified Catalog + column-level lineage for cross-system audit and impact. Closes the module. | concept/build |

## The artifact + oracle (locked first)

`module6-lineage/`: a lineage store (SQLite) with the chain tables + a `LineageCapture` wrapper whose
methods (`record_embedding`, `record_retrieval`, `record_answer`, `record_verdict`) write links as a
simulated RAG pipeline runs; a `trace_answer_to_sources(answer_id)` (backward) and
`impact_of_version(doc_id, version)` (forward) query; reuse of M5's `get_content_hash_at_version`.
Oracle (`smoke.py` + `pytest`, offline): running the simulated pipeline populates a complete chain for
an answer; the backward query resolves an answer to the exact source-document versions + content_hashes
it cited; the forward query returns the answers affected when a given doc version changes; a regression
(an answer whose eval verdict failed) traces back to the changed source version that explains it.
Negative: an answer with a missing link in the chain is detected (lineage gap), not silently resolved;
querying a non-existent answer raises.

## Fleet plan

- **Haiku fetch (2):** (a) MS-Learn Microsoft Purview data lineage + Unified Catalog + column-level
  lineage + impact analysis, verified URL pack; (b) `ai-engineering-from-scratch` (aefs) survey for the
  eval-verdict / RAG-provenance ore + any lineage-graph modeling worth grounding on.
- **Sonnet artifact-engineer (1):** builds + tests `module6-lineage/`; reuses M1 + M5 shapes; returns
  byte-identical code + a green run.
- **Sonnet authors (4):** L1–L4 around the locked code + grounding.
- **Opus conductor:** overview, schema/oracle lock, review, em-dash sweep + `mdbook build`, ship + push.
