# Module 1 — Migration Dossier

Ledger for what migrated into `src/module1/`, what was cut, and what threaded out. Source:
`../sub-repos/synthesis/source/module1/`.

## Source files in

| Source file | Verdict | Destination / note |
|-------------|---------|--------------------|
| `aefs-module1-setup-tooling.md` | **KEEP** (whole) | → `src/module1/01-setup-and-tooling.md`. Universal root — every hands-on lesson depends on it. |
| `aefs-module1-nlp-transformer-forward.md` | **KEEP** (transformer-forward subset) | → `src/module1/02-nlp-transformer-forward.md`. Attention-forward only. |
| `rust-module1-rust-book-structure.md` | **THREAD OUT → M5** | Rust ownership on-ramp is taught at Deploy, not M1. M1 only *installs* the toolchain. ([[language-track-threading]]) |
| `rust-module1-rust-exercises-by-topic.md` | **THREAD OUT → M5** | Same — Rust exercises attach at serving-layer point-of-use. |
| `ts-module1-typescript-topics.md` | **THREAD OUT → M3** | TypeScript break-in set is taught at Agent Foundations (first typed tools / MCP), not M1. |

## Cuts → Antilibrary (not migrated; recorded in `src/antilibrary.md`)

From `aefs-module1-nlp-transformer-forward.md`, the pre-attention half (already flagged at source):
- `01-text-processing`, `02-bag-of-words-tfidf`, `03-word-embeddings-word2vec`, `04-glove-fasttext-subword`,
  `05-sentiment-analysis`, `06-named-entity-recognition`, `07-pos-tagging-parsing`, `08-cnns-rnns-for-text`,
  `09-sequence-to-sequence`, `16-text-generation-pre-transformer`, `17-chatbots-rule-to-neural`.
- **The 09→10 seam** (seq2seq failure → attention) is the most important cut: lesson 10 onward assumes
  attention; everything before it is antilibrary. (SYLLABUS antilibrary: "05 — NLP Foundations (pre-transformer half)".)

## Merges / forward-pointers (kept in M1, but feed later modules)

The NLP track carries material that is the *foundations half* of M2 — kept here as transformer-era NLP,
consumed there as systems (the RAG merge ruling, [[curriculum-flow-audit-approach]] confirmed both sides):
- **RAG components** — lessons 13 (QA), 14 (IR), 22 (embeddings), 23 (chunking) → M2 builds the RAG *system*
  on these. M1 teaches the components; M2 = the system (asdg Ch06 canonical spine).
- **Eval thread origin** — lessons 21 (NLI), 27 (RAGAS/LLM-eval), 28 (long-context) → seed Gap-1
  eval-driven development; deepened in M2 eval and M5 observability.
- **Structured outputs** — lesson 20 → backbone of reliable tool calls in M3.

## Lesson-audit flags carried forward (decide during authoring)

Five classical/transformer **hybrids** extracted-and-flagged `[CHECK]`; modern defaults are transformer-era,
so kept, but the lesson-level audit may demote any to antilibrary:
- 15 Topic Modeling (BERTopic), 24 Coreference (span-based e2e), 25 Entity Linking (BLINK/GENRE),
  26 Relation Extraction → KG (LLM + AEVS), 29 Dialogue State Tracking (LLM + Pydantic + constrained decoding).

## Accounted-for check

All 5 source files resolved: 2 kept-and-placed, 3 threaded out. Pre-attention lessons → antilibrary.
Nothing uncatalogued.
