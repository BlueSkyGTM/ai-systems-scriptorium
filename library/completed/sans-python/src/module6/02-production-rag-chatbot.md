# Production RAG chatbot (regulated vertical)

A bank's compliance team answers the same policy questions all day, by hand, with no record of who said what. You can replace that with a chatbot — but the moment the domain is regulated, an answer without a source is not a feature, it is a liability someone signs their name under. This is the most-shipped production AI shape of 2026, and it is the one where the hard parts are the parts a demo skips: the citation, the guardrail, the gate that says ship or don't.

You have built the pieces already. Module 2 gave you the RAG spine and the evaluation triad; Module 5 gave you the Docling front door and quality-drift observability; Module 4 gave you guardrails. This artifact assembles them into one system a regulator could audit, and it makes the seams real enough to reuse.

## The business problem

Strip the romance off and the job is narrow. A compliance team owns a corpus of policy documents — retention schedules, access-control rules, incident-response timelines — and a stream of questions that already have answers buried in those documents. Today a person finds the answer, or guesses it, and nobody can reconstruct later why the answer was what it was.

A regulated vertical changes the acceptance bar in two specific ways, and both are non-negotiable. First, **every claim must cite its source.** "Records are kept seven years" is worthless; "Records are kept seven years [Data Retention Policy, Section 2]" is an auditable statement. Second, **the system must refuse before it misbehaves** — refuse to answer from a document it didn't retrieve, refuse a prompt-injection attempt, refuse to leak PII — because in this domain a confident wrong answer costs more than no answer at all. Citations and guardrails are the reason the system is allowed to exist, not polish on top of one that already works.

That reframes the build. You are not building a chatbot that happens to cite; you are building a citation-and-refusal machine that happens to use retrieval to do it.

## Capability and one stack

The capability is RAG with three things bolted on that a toy RAG omits: **citations**, **guardrails**, and **drift observability**. The reference stack, one concrete choice end to end:

- **Ingestion** — Docling parses PDF/DOCX/PPTX into a `DoclingDocument` and chunks it structure-aware (Module 5's front door).
- **Index** — Azure AI Search holds the vectors and runs hybrid retrieval: it executes a BM25 keyword query and a vector query in parallel, then merges the two ranked lists with Reciprocal Rank Fusion.
- **Generation** — Azure OpenAI or Anthropic, prompted through the Messages API with a system prompt that says answer only from the retrieved context and cite each claim or refuse.
- **Guardrail** — an input/output content screen (Module 4's pattern), anchored to hardcoded prohibitions.
- **Observability** — OpenTelemetry GenAI spans and a sampled quality check (Module 5's outer loop).

One stack, named, so the choices are honest. But the stack is not the lesson. The seam is.

## The portable seam

Two interfaces carry this whole system, and getting them right is what lets you swap a cloud service for a laptop without touching the rest.

The first is the **`Chunk` contract**, inherited from Module 5's `DoclingDocument`. A chunk is text plus its citation handle — the document it came from and the section within it. Everything downstream binds to `Chunk`, never to "a PDF" or "a DOCX." Swap a scanned contract for a native PDF and the chunk your index sees is the same shape; the parser changed, the contract didn't.

The second is the **retriever interface** — a `VectorIndex` with two methods, `add` and `search`:

```python
class VectorIndex(Protocol):
    def add(self, chunks: List[Chunk]) -> None: ...
    def search(self, query: str, k: int = 4) -> List[Tuple[Chunk, float]]: ...
```

The default backend is a pure-Python in-memory index: hashed bag-of-words embeddings scored by cosine, no numpy, no FAISS, no service. Azure AI Search is a second class that satisfies the same interface and reads its endpoint from the environment. The chatbot above the interface cannot tell which one it is talking to. That is the swap: **Azure AI Search ↔ local index** is a change of one constructor call, because the chatbot, the guardrail, the eval gate, and the drift monitor all bind to `VectorIndex` and `Chunk`, not to a backend.

This is the same swappable-engine stance the serving stack took and the same one Docling's seam took. You are not learning a new idea here; you are watching it pay off a third time.

## The build sequence

Build it in the order the dependencies force, each step runnable before the next:

1. **Ingest** — corpus to `Chunk`s. Docling for real documents; a stdlib markdown splitter for the offline path. Section headers ride along as metadata — the source-anchoring context that lifts recall.
2. **Index** — load the chunks into the pure-Python `VectorIndex`. This is the seam; prove it works locally before any cloud call exists.
3. **Retrieve** — wrap the index in the retriever interface, with a relevance floor. Below the floor, return nothing — the CRAG-style move that stops the model fabricating from junk.
4. **Answer with citations** — retrieve, then generate. On the smoke path the generator is a deterministic mock LLM that grounds the answer in the top chunk and appends its citation, so the output is reproducible and the citation is real. A real model plugs in at the same `generate` signature.
5. **Guardrail** — screen input and output. Block the unsafe query before retrieval; block the unsafe answer before it returns.
6. **Drift** — record a rolling quality reading against a service-level-objective (SLO) floor.
7. **Eval** — score retrieval precision and answer faithfulness against a labeled set. This is the gate.

The mock LLM is doing real work, not papering over a gap. A deterministic policy at the generation seam is what makes the whole pipeline testable in CI; the interesting parts — retrieval, citation, refusal, the gate — are exactly the parts that don't need a live model to prove out.

## The operator surfaces

Module 8 hands the student the operator's chair: set the thresholds, watch the signals, hold the go/no-go. So this artifact exposes three surfaces the student will drive, and they are real, not decorative.

**The guardrail gate.** The input/output screen carries two classes of rule, straight from Module 4. **Hardcoded prohibitions** — prompt-injection patterns, "dump all customer PII," "disable the audit log" — are the floor; operator config cannot lower them. **Operator-adjustable defaults** — topical scope, response style — are the knobs, bounded by that floor. The honest caveat from Module 4 still holds: a classifier is a layer, not a wall. It catches the careless; it does not stop a motivated adversary. That is why the hard prohibitions sit underneath it and don't bend.

**The drift metric.** A serving stack can be green — latency nominal, errors zero — while the answers quietly rot. The corpus shifted, the model updated, and no infrastructure metric moves. The drift monitor samples a quality score over a rolling window and flags a breach when the mean falls below the SLO floor. It is Module 5's outer loop, shrunk to one operator surface.

**The acceptance gate.** Eval scores two metrics from the RAG triad against a labeled evalset: **retrieval precision** (did the top chunk come from the document that holds the answer?) and **answer faithfulness** (does the answer contain the expected facts, drawn from a cited source?). The gate is a threshold on each. A build below it does not ship. Both checks are deterministic — no LLM judge needed offline — so the gate runs in CI and means the same thing every time.

## The BUILD→TEST gate

The whole artifact runs on the Python standard library alone, no cloud, no network, no GPU. `python smoke.py` ingests the corpus, builds the index, answers a real question with a correct citation, blocks an unsafe query at the guardrail, records a drift reading, and runs the eval gate — exiting zero only if every surface behaves. `python -m pytest tests/` asserts the surfaces hold: an answer cites a real source chunk, the guardrail blocks the unsafe query, eval returns scores, and a deliberately degraded low-faithfulness answer **fails** the gate — proving the gate has teeth.

Every third-party import — Docling, FAISS, Azure, Anthropic — is guarded behind `try/except ImportError` with a stdlib fallback on the smoke path. Real services are opt-in through `.env`. The gate you can run on a plane is the gate that runs in CI.

## Strong-project done-when

This clears the hireability bar: a real entry point you run from a shell, not a notebook; a README that frames the business problem before the code; evaluation with metrics and a pass/fail gate; tests covering the smoke path and every operator surface; a clean, versioned layout; and a shipped `outputs/skill-production-rag-chatbot.md`. Done means the smoke gate is green and a stranger can read the README, run two commands, and see a cited answer and a blocked attack.

## What Module 7 reuses

This artifact is the **knowledge/retrieval service**. In Module 7 the `Retriever` stops being something a person queries and becomes a tool a governed agent fleet calls. The citation contract travels with it — an agent that retrieves through this service inherits cited answers for free — and so does the eval gate, which becomes one of the acceptance checks the fleet's operator runs. You are not rebuilding retrieval in M7; you are wiring this seam into a larger machine. That is the compounding the course promised: the single agent you ship here is a node in the team you ship next.

## What you build

A citation-enforced, guardrailed RAG chatbot for a regulated corpus: Docling-or-stdlib ingestion into a `Chunk` contract, a swappable `VectorIndex` (pure-Python default, Azure AI Search opt-in), a retriever with a relevance floor, a cited-answer path over a mock or real LLM, a Module 4 guardrail, a drift monitor, and an eval acceptance gate — all passing an offline, stdlib-only BUILD→TEST smoke gate.

## Core concepts

- In a regulated vertical, citations and refusal are the acceptance bar, not features: an uncited claim is a liability, so the system is a citation-and-refusal machine that uses retrieval, not a chatbot that happens to cite.
- The portable seam is two interfaces — the `Chunk` citation contract and the `VectorIndex` retriever — so swapping Azure AI Search for a local index is one constructor call and the chatbot, guardrail, eval, and drift code never change.
- A deterministic mock LLM at the generation seam makes the pipeline testable in CI, because the load-bearing parts — retrieval, citation, refusal, the gate — are exactly the parts that don't need a live model to prove out.
- The three operator surfaces are real go/no-go controls: a guardrail gate with un-lowerable hardcoded prohibitions, a rolling drift metric against an SLO floor, and an eval acceptance gate that a low-faithfulness build fails.

<div class="claude-handoff" data-exercise="exercises/module6/02-production-rag-chatbot/">

**Build It in Claude Code** — assemble the production RAG chatbot: ingest a small regulated corpus into the `Chunk` contract, build the pure-Python `VectorIndex`, retrieve with a relevance floor, answer with citations through the mock LLM, screen input and output with the guardrail, log a drift reading, and run the eval acceptance gate. Prove it: `python smoke.py` exits zero with a cited answer and a blocked attack, and `python -m pytest tests/` shows a low-faithfulness build failing the gate. Then swap the local index for Azure AI Search behind the same interface. Open the repo and run the exercise for this lesson.

</div>
