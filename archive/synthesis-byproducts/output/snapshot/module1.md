# Module 1 — Prerequisite Snapshot

> **Renumber map (8-module, 2026-06-18).** This file's prose retains the original 5-module analysis
> tags; the machine-readable edge list at the bottom is renumbered to the 8-module structure. Mapping:
> old M1→M1, M2→M2, M3 agent-foundations refs (tool-contracts, MCP, tool-use, agent-eval, memory)→M3,
> M3 multi-agent/concurrent refs→M4, M4 Deploy→M5, M5 capstones→M6/M7/M8. Validated by
> `step2-flow-audit.md` (no backward edges). Module 1 numbering is unchanged.

Module 1 is **foundations**: the environment, the two writing-stack languages (Rust, TypeScript),
and the transformer-forward NLP that everything LLM-related assumes. Four parallel tracks. Only
some have hard internal ordering; the cross-track and cross-module edges are where the audit bites.

Source files: `aefs-module1-setup-tooling`, `aefs-module1-nlp-transformer-forward`,
`rust-module1-rust-book-structure`, `rust-module1-rust-exercises-by-topic`, `ts-module1-typescript-topics`.

---

## Track A — Setup & Tooling (aefs, 12 lessons)

Bottom-up four-layer stack. **This track is a prerequisite for every hands-on lesson in the course.**

Nodes: dev-environment, git, gpu-setup, **apis-and-keys**, jupyter, python-envs, docker, editor, data-management, terminal-shell, linux, debugging-profiling.

Internal edges (install order — each layer needs the one below):
```
system-foundation → package-managers → language-runtimes → ai-ml-libraries
dev-environment → gpu-setup → docker
dev-environment → python-envs → data-management
dev-environment → debugging-profiling
```

Outbound (cross-module):
- `apis-and-keys → [M2] llm-engineering` — first LLM API call is taught here deliberately so Module 2+ can assume it.
- `docker, linux, terminal-shell → [M4] infrastructure/inference-serving` — ops substrate for deployment.
- `data-management → [M2] retrieval-systems` — dataset loading/streaming underpins RAG corpora.

Inbound assumptions: none (this is day one).

---

## Track B — Rust (rust, 8 topics / 98 exercises)

**Strictly linear** — the single cleanest prerequisite chain in the whole library. Each topic compiles only if the prior is understood.

```
intro → basic-calculator → ticket-v1(ownership) → traits → ticket-v2(enums/errors)
      → ticket-management(collections/iterators/lifetimes) → threads → futures(async)
```

Key internal hinge: `ticket-v1(ownership/borrowing)` gates everything after it — ownership is the Rust prerequisite. `traits` gates generics/error-handling. `threads` gates `futures`.

Outbound (cross-module):
- `futures(async/tokio) → [M3] concurrent-agent-tasks` and `→ [M4] serving-layer` — async Rust is the serving/concurrency substrate.
- `threads, ticket-v2(Result/error) → [M4] serving-layer` — fearless concurrency + typed errors for production services.

Inbound assumptions: `[A] dev-environment` (rustup/cargo installed).

---

## Track C — TypeScript (ts, 15 topics)

Product-layer language. Looser ordering, but one clear spine: the type system grounds everything, generics/interfaces ground the agent-tooling payoff.

```
the-type-system → unions-and-literals → objects → interfaces → functions
the-type-system → classes
interfaces, functions → generics → type-operations
generics → declaration-files
```

Seam nodes (flagged in source): `from-javascript-to-typescript` (LLM tooling is JS-first), `generics` (type-safe tool defs / MCP contracts), `declaration-files` (typing untyped npm packages).

Outbound (cross-module):
- `generics, interfaces, type-operations → [M3] agent-tool-contracts / MCP-schemas` — the `Tool<TInput,TOutput>` and MCP contract payoff.
- `declaration-files → [M3] integrating-js-first-tooling`.

Inbound assumptions: `[A] dev-environment` (node/pnpm installed).

---

## Track D — NLP Transformer-Forward (aefs, ~22 lessons, start at lesson 10)

The conceptual pivot is **attention**. Everything else in the track assumes it. Note: a large RAG/eval cluster here is really the *foundations half* of Module 2 material and throws strong forward edges.

Pivot + internal edges:
```
attention(10) → machine-translation(11), summarization(12), qa(13), information-retrieval(14)
attention(10) → subword-tokenization(19) → embedding-models(22) → chunking-for-rag(23)
qa(13), information-retrieval(14), embeddings(22), chunking(23) → [cluster] RAG-foundations
nli(21) → llm-evaluation-ragas(27)
embeddings/long-context(28) → llm-evaluation(27)
structured-outputs(20) → dialogue-state-tracking(29)
```

Antilibrary (recorded, not extracted): lessons 01–09, 16–17 (pre-attention NLP). The **09→10 seam** (seq2seq failure → attention) is the most important cut in the phase.

Hybrid `[CHECK]` nodes (classical+modern, audit may demote): topic-modeling(15), coreference(24), entity-linking(25), relation-extraction(26), dialogue-state-tracking(29).

Outbound (cross-module) — **strong**:
- `qa(13), information-retrieval(14), embedding-models(22), chunking-for-rag(23) → [M2] retrieval-systems` — these five ARE the Phase-05 half of Module 2's RAG.
- `nli(21), llm-evaluation(27), long-context-eval(28) → [M2] eval-guides` and `→ [M3] agent-eval` — the eval thread originates here.
- `structured-outputs/constrained-decoding(20) → [M3] tool-use, dialogue-state-tracking` — structured output is the backbone of reliable tool calls.

Inbound assumptions: `[A] apis-and-keys` (for API-based lessons); basic Python literacy.

---

## Module 1 — flow observations (feed Step 2)

1. **Setup is the universal root.** Every Build lesson everywhere depends on Track A. Trivially satisfied if Module 1 is first; flag only if a later module assumes a tool never installed.
2. **Rust is a clean linear spine** — low audit risk internally; its only forward dependency is async → serving (M3/M4), which is correctly ordered.
3. **The NLP track is half-in-the-wrong-module.** The RAG cluster (13,14,22,23,27) and eval thread (21,27,28) are *prerequisites consumed in Module 2*. Two valid readings: (a) keep them in M1 as "transformer-forward foundations" feeding M2, or (b) they belong in M2 proper. **This is the first real sequencing question for the audit** — surface at Step 2.
4. **TypeScript generics/interfaces are a forward dependency for Module 3** agent tooling — ordered correctly (M1 before M3), no violation.
5. No backward edges detected within Module 1 (nothing depends on a later module). Clean so far.

## Edge list (machine-readable, for topological check)
```
# track A
dev-environment -> gpu-setup
dev-environment -> docker
dev-environment -> python-envs
python-envs -> data-management
dev-environment -> debugging-profiling
apis-and-keys -> M2:llm-engineering
data-management -> M2:retrieval-systems
docker -> M5:inference-serving
linux -> M5:inference-serving
# track B
rust:intro -> rust:basic-calculator
rust:basic-calculator -> rust:ticket-v1
rust:ticket-v1 -> rust:traits
rust:traits -> rust:ticket-v2
rust:ticket-v2 -> rust:ticket-management
rust:ticket-management -> rust:threads
rust:threads -> rust:futures
rust:futures -> M4:concurrent-agent-tasks
rust:futures -> M5:serving-layer
rust:ticket-v2 -> M5:serving-layer
# track C
ts:type-system -> ts:unions-literals
ts:type-system -> ts:classes
ts:unions-literals -> ts:objects
ts:objects -> ts:interfaces
ts:interfaces -> ts:functions
ts:functions -> ts:generics
ts:generics -> ts:type-operations
ts:generics -> ts:declaration-files
ts:generics -> M3:agent-tool-contracts
ts:interfaces -> M3:mcp-schemas
ts:declaration-files -> M3:integrating-js-first-tooling
# track D
nlp:attention -> nlp:machine-translation
nlp:attention -> nlp:summarization
nlp:attention -> nlp:qa
nlp:attention -> nlp:information-retrieval
nlp:attention -> nlp:subword-tokenization
nlp:subword-tokenization -> nlp:embedding-models
nlp:embedding-models -> nlp:chunking-for-rag
nlp:nli -> nlp:llm-evaluation
nlp:long-context-eval -> nlp:llm-evaluation
nlp:structured-outputs -> nlp:dialogue-state-tracking
nlp:qa -> M2:retrieval-systems
nlp:information-retrieval -> M2:retrieval-systems
nlp:embedding-models -> M2:retrieval-systems
nlp:chunking-for-rag -> M2:retrieval-systems
nlp:nli -> M2:eval-guides
nlp:llm-evaluation -> M2:eval-guides
nlp:long-context-eval -> M2:eval-guides
nlp:structured-outputs -> M3:tool-use
```
