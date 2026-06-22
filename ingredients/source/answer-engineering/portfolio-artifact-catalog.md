# Portfolio Artifact Catalog — M6 Reference Ingredient

Distilled from the **Sans Python completed book's runnable portfolio artifacts** (the "resume" this
book teaches the reader to interview on):
- `library/completed/sans-python/src/module6/01-terminal-coding-agent.md` + its `exercises/module6/01-terminal-coding-agent/` code
- `library/completed/sans-python/src/module6/02-production-rag-chatbot.md` + its `exercises/module6/02-production-rag-chatbot/` code
- the other portfolio lessons in `src/module6`, `src/module7`, `src/module8` (indexed below)

Distillation date: 2026-06-21. Scope: portfolio-narration ore for Answer Engineering M6. Dense; no
prose polish. Everything traces to a real Sans Python lesson + its code; no invented projects or
decisions. Each decision is given as: the decision / the alternative rejected / the tradeoff accepted /
the failure mode guarded, plus a short quoted rationale from the source lesson where one exists.

The lessons teach the reader to **narrate the reasoning behind an artifact, not read the code**. This
catalog supplies the decision layer for the two featured walkthroughs and a one-line hook for the rest
of the bank.

---

## Artifact A: The Terminal Coding Agent

**Purpose:** a plan/act/observe loop that reads a failing file, writes a fix, runs tests in a subprocess
sandbox, and stops only when a deterministic verification gate accepts the result, bounded by a cost
ceiling and an operator-held kill switch.

**Architecture in brief:** a state-machine loop (`agent.py`) calls `model.respond(messages)` at a seam,
dispatches schema-validated tool calls (read/write/test) through a registry scoped to the project root,
runs tests in a subprocess sandbox (`sandbox.py`) with a wall-clock timeout, charges each model call to a
`Budget`, checks a read-only `KillSwitch` before every action, and hands the final call to a
deterministic `verify_gate` that runs the suite and defaults to REJECT. A mock model drives the offline
smoke test; a live model swaps in behind the same seam.

**Load-bearing decisions:**

1. **The model seam (`respond`).** Decision: abstract the model behind one method returning a tool call
   or a final answer plus cost. Rejected: hardcoding a vendor SDK into the loop. Tradeoff: one layer of
   indirection. Failure mode guarded: vendor lock-in; the mock runs offline, any vendor swaps in with
   zero loop changes. Rationale: "Hold that line and the agent outlives the stack you built it on."

2. ★ **The verification gate (deterministic, defaults to REJECT).** Decision: "done" is a fact from
   running the real tests, not a claim from the model. Rejected: trusting the model's self-assessment.
   Tradeoff: the agent runs the full suite every time. Failure mode guarded: the agent declaring victory
   on a broken fix. Rationale: "An agent that decides it is finished is not done; it is optimistic. The
   gate is the antidote... The default is REJECT."

3. ★ **The kill switch (read-only from the agent).** Decision: the switch is a file the operator owns;
   the agent can only read `tripped()`, never write. Rejected: a flag in the agent's reachable state.
   Tradeoff: an external file check. Failure mode guarded: the agent disabling its own off switch.
   Rationale: "if the off switch lives in the agent's reachable state, the agent can disable its own kill
   switch, and you have a kill switch in name only."

4. ★ **The budget with two caps (dollars + iterations), checked before each call.** Decision: deterministic
   pre-call checks stop the loop before paying for one more action. Rejected: asking the model to track
   spend; checking only after the call. Tradeoff: tight loop/budget coupling. Failure mode guarded:
   "Denial of Wallet", a runaway loop billing forever. Rationale: "a budget you ask a model to enforce
   is a budget the model can talk its way out of."

5. **The tool registry with path jailing.** Decision: validate tool args against a schema before dispatch
   and scope every tool to the project root (refuse `../` escapes). Rejected: passing raw args, no
   validation. Tradeoff: schema must track the handler contract. Failure mode guarded: malformed calls
   return as observations the model corrects (not crashes); path-traversal is structurally blocked.

**Lead with:** the verification gate that defaults to REJECT and runs the real tests. It shows the
candidate understands the hard part of a coding agent is not the model, it is the harness that makes the
model's output trustworthy.

---

## Artifact B: The Production RAG Chatbot

**Purpose:** a citation-enforced, guardrailed RAG system for regulated verticals; it retrieves from a
corpus, grounds answers in retrieved chunks with explicit citations, screens input/output against
hardcoded prohibitions, monitors quality drift against an SLO, and gates acceptance on retrieval
precision and answer faithfulness, runnable offline on stdlib alone.

**Architecture in brief:** documents ingest into a `Chunk` contract (text + citation handle); chunks load
into a `VectorIndex` (pure-Python default, Azure AI Search opt-in); a `Retriever` wraps the index with a
relevance floor (refuse when nothing clears it); the `Chatbot` chains input guardrail -> retrieval ->
generation (mock or real model) -> output guardrail, returning an `Answer` with citations; a
`DriftMonitor` samples quality over a rolling window; an `eval` gate scores precision + faithfulness and
defaults to FAIL.

**Load-bearing decisions:**

1. ★ **The `Chunk` contract (text + citation handle).** Decision: everything downstream binds to `Chunk`
   (doc_id, section, text), never to "a PDF". Rejected: passing raw document objects through the pipeline.
   Tradeoff: ingest must map every format onto one shape. Failure mode guarded: a parser/format change
   rippling through every layer. Rationale: "Swap a scanned contract for a native PDF and the chunk your
   index sees is the same shape; the parser changed, the contract didn't."

2. ★ **The `VectorIndex` protocol seam.** Decision: a two-method interface (`add`, `search`) that both the
   in-memory index and Azure AI Search satisfy. Rejected: hard-coding one backend. Tradeoff: the default
   embedding is intentionally simple (hashed bag-of-words). Failure mode guarded: a cloud migration that
   touches every layer. Rationale: "Azure AI Search <-> local index is a change of one constructor call."

3. **The deterministic mock LLM at the generation seam.** Decision: ground the answer in the top chunk
   and append its citation, reproducibly, offline. Rejected: stubbing the generator; citations as an
   afterthought. Tradeoff: the mock is deliberately dumb. Failure mode guarded: shipping untested citation
   infrastructure. Rationale: "the interesting parts, retrieval, citation, refusal, the gate, are exactly
   the parts that don't need a live model to prove out."

4. ★ **The guardrail with a hardcoded-prohibitions floor.** Decision: split rules into un-lowerable
   hardcoded prohibitions (prompt injection, PII exfiltration) and operator-tunable defaults (topical
   scope, style). Rejected: making all guardrails operator-configurable. Tradeoff: the operator can tune
   scope but not disable the security floor. Failure mode guarded: a misconfigured or pressured operator
   lowering the security floor. Rationale: "operator config cannot lower them... bounded by that floor."

5. ★ **The relevance floor (CRAG-style refusal).** Decision: return no hits if the top-k all fall below
   `min_score`, forcing a refusal instead of fabrication. Rejected: always returning top-k. Tradeoff:
   some valid questions get "I don't have a source for that." Failure mode guarded: hallucinated citations
   grounded in low-relevance chunks. Rationale: "the answerer should refuse rather than fabricate from
   low-relevance context."

6. **The drift monitor (rolling window + SLO breach flag).** Decision: sample answer quality over a
   window, flag a breach when the mean drops below tolerance. Rejected: monitoring only latency/error
   rates. Tradeoff: needs a quality-score definition; signals lag. Failure mode guarded: silent quality
   rot while infra metrics stay green. Rationale: "The corpus shifted, the model updated, and no
   infrastructure metric moves."

7. ★ **The eval gate (precision + faithfulness, deterministic, defaults to FAIL).** Decision: score
   retrieval precision and answer faithfulness offline without an LLM judge. Rejected: an LLM judge; manual
   post-deploy eval. Tradeoff: simple metrics miss sophisticated hallucinations. Failure mode guarded: a
   degraded build shipping; the test injects a bad answerer and watches the gate reject it. Rationale:
   "deterministic, no LLM judge needed offline, so the gate runs in CI and means the same thing every time."

**Lead with:** the citation-and-refusal contract (`Chunk` + guardrail + eval gate). It shows the candidate
understands that regulated RAG is not a chatbot with citations tacked on; it is a citation-and-refusal
machine that uses retrieval.

---

## The Rest of the Portfolio Bank (the reader's full set; one hook each)

- **Real-Time Voice Assistant** (`src/module6/03`): streaming VAD -> STT -> LLM -> TTS under a hard
  ~450-600ms budget; headline decision = treat latency as a finite budget, stream fragments on arrival,
  handle barge-in by stopping synthesis on interrupt.
- **Issue-to-PR Agent** (`src/module6/04`): GitHub-triggered autonomous coder; headline decision = the
  hard boundary "agent proposes, human merges", enforced by scoped credentials (one repo, `agent/*`
  branches only) that structurally prevent writes to main.
- **Autonomous Research Agent** (`src/module7/01`): supervisor + parallel sub-agents + verifier under a
  shared budget and kill switch; headline decision = reuse the M6 agent loop unchanged (composition over
  new code).
- **DevOps K8s Agent** (`src/module7/02`): on-call diagnostic loop that stops at a human gate; headline
  decision = asymmetric authority (read anything to diagnose, change nothing without approval).
- **Governed Multi-Agent Fleet** (`src/module7/03`): five-agent software factory; headline decision = the
  fleet is the governance frame composing five M6 loops, with a shared budget and a human-in-the-loop
  inbox.
- **The Integrated Exam** (`src/module8/01`): replicate a real reference architecture at a scope you can
  build and operate; headline decision = not blank-page architecture but operating a known seam at smaller
  scale, judged by a rubric in code.

---

## Notes for Lesson Authors (role-tailoring angles)

For L3 (tailoring to the role), the same artifact narrates differently by role:
- **Applied-AI / product engineer:** foreground the user-facing reliability decisions (the RAG refusal
  floor, the citation contract, the guardrail) and the eval/drift story (does it stay good in production?).
- **ML-platform / infra engineer:** foreground the seams and operability (the model seam, the
  `VectorIndex` protocol, the budget/kill-switch governance, the deterministic gates that run in CI).
- **Research-adjacent / applied-science:** foreground the eval rigor (precision/faithfulness metrics,
  the deterministic gate, drift detection) and the principled refusal behavior.
The decision set does not change; the emphasis and the lead bend to what the role values. That is the
anti-memorization thesis applied to the portfolio walkthrough.
