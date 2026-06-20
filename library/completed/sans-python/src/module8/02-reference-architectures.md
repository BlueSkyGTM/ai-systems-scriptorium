# Reference architectures

You do not invent the system you build for the exam. You replicate one. This chapter is the catalog — twenty production architectures, distilled from Chapter 16 of the systems-design case studies — and your job is to pick one, name the seam you must keep, and scope a version you can ship.

## Why a catalog instead of a prompt

A blank page is a trap. Asked to design a multi-tenant RAG system from nothing, most engineers produce something that works in a demo and falls over the first time two tenants share a shard. The architectures below were not invented in a demo; they were paid for in incidents. Each one carries the design decision that a real version cannot drop — the *seam* — and that seam is what the exam grades. Replicating a known architecture is not a shortcut around the thinking. It is the thinking, done by people who already hit the wall you would otherwise hit yourself.

Read the catalog as a menu of solved problems. Each row names the architecture type, what you replicate, and the seam. Pick the row whose seam you want to prove you can hold.

## The full catalog

| # · Case study | Architecture type | What you replicate | Seam |
|---|---|---|---|
| 01 · Enterprise RAG System | Enterprise RAG | Hybrid retrieval with permission-filtered vector search, reranking, cited generation | Permission filter on retrieval |
| 02 · Customer Support Conversational Agent | Enterprise RAG | A confidence-gated support agent with escalation | The confidence gate to a human |
| 03 · Financial Analysis with Ensemble Verification | Ensemble verification | Equity-research generator with self-consistency, mixture-of-agents, debate, panel-of-judges gating | The verification panel |
| 04 · AI Code Assistant | IDE code-generation service | Real-time completion with context assembly and multi-stage verification | The verification stages |
| 05 · Content Moderation at Scale | Tiered classification + HITL | A multi-tier pipeline: hash filter → ML classifier → LLM review → human queue | The escalation tiers |
| 06 · Real-Time AI Search Engine | Real-time hybrid search | Streaming ingestion with dual-index (vector + full-text) retrieval and cited answers | The dual-index merge |
| 07 · Autonomous Coding Agent | Multi-agent orchestration | Planner–coder–debugger loop with tiered retrieval and sandboxed, test-gated self-correction | The test-gated loop |
| 08 · Multi-Tenant AI SaaS Platform | Multi-tenant RAG | Tiered multi-tenant RAG with defense-in-depth isolation | The isolation boundary |
| 09 · AI-Powered Customer Support | Multi-agent orchestration | Three-tier ticket routing with tool-based auto-resolution and human handoff | The routing + handoff |
| 10 · Document Intelligence Pipeline | Document-intelligence | Parallel specialized field extractors with cross-field validation | Cross-field validation |
| 11 · AI Recommendation Engine | Hybrid retrieval + LLM | Embedding recommender with ANN search, reranker, cached LLM explanations | The explanation cache |
| 12 · Regulatory Compliance Automation | Compliance RAG + audit trail | Claim-extraction + regulation-retrieval + precedent-search reviewer with severity flags and full audit logging | The audit trail |
| 13 · Voice AI for Healthcare | On-prem voice-to-EHR | Clinical-note generation with ASR, diarization, medical NER, FHIR integration | The on-prem boundary |
| 14 · Real-Time Fraud Detection | Real-time ML + rules | Sub-100ms transaction scoring with ML ensemble, business rules, LLM explanation | The latency budget |
| 15 · Enterprise Knowledge Management | Enterprise RAG | A permission-aware multi-source knowledge assistant | Permission-aware sourcing |
| 16 · Production Computer-Use Agent | Computer-use agent | Firecracker-isolated expense-entry agent with tiered human approval | The isolation + approval tiers |
| 17 · Multi-Tenant Fine-Tuning Platform | Multi-tenant LoRA serving | Per-tenant LoRA adapters on a shared base with isolated training and eval-gated promotion | Eval-gated promotion |
| 18 · Eval-Gated CI/CD for an AI Product | Eval-gated CI/CD | Statistical-correction eval pipeline with golden sets and failure-mode taxonomies | The statistical eval gate |
| 19 · Customer-Specific Distillation | Model distillation | Production-trace distillation with eval-gated canary rollout | The eval-gated canary |
| 20 · Enterprise MCP Knowledge Agent | MCP knowledge agent | Multi-system MCP agent with OAuth audience binding, STDIO sandboxing, IPI trust-tagging | The trust boundary |

## Grouped by track

The exam's three tracks each anchor to a handful of these. Start from your track, then pick the row whose seam you want to hold.

**Eval-gated CI/CD** — the seam is a gate that promotes nothing without passing. Anchor case studies: **#18** eval-gated CI/CD (the canonical one: golden sets and a statistical eval gate), **#19** distillation with an eval-gated canary, **#17** multi-tenant LoRA with eval-gated promotion. The version you build proves a change ships only when the eval clears.

**Multi-tenant RAG** — the seam is isolation that holds. Anchor case studies: **#08** multi-tenant SaaS (the canonical one: defense-in-depth isolation), **#01** enterprise RAG, **#12** compliance RAG (where the audit trail is itself the product), **#15** enterprise knowledge management. The version you build proves one tenant's query never reaches another's data.

**Agentic system** — the seam is a governed loop. Anchor case studies: **#07** autonomous coding agent (the one the sample spec replicates), **#09** multi-agent support, **#16** computer-use agent, **#20** MCP knowledge agent. The version you build proves the loop plans, acts, verifies, and stops under a human gate.

The other case studies — fraud detection, voice-to-EHR, recommendation — are real, but they lean on infrastructure outside this fleet's reach (sub-100ms inference, on-prem ASR, an ANN index). Note where they live; reach for the rows your fleet can ship.

## How to choose and scope "a version of"

Choosing is three decisions, in order.

**One: pick the seam, not the demo.** Do not pick the architecture that sounds most impressive. Pick the seam you want on your portfolio — the one design decision you can defend in an interview. If you cannot say in one sentence what makes #08 multi-tenant and not just RAG, pick a different row or learn that one cold first.

**Two: scope down, keep the spine.** A version of #18 is not a full CI/CD platform. It is a single eval gate over a golden set of a dozen cases, wired so a change that regresses the eval does not promote. A version of #07 is not a full autonomous engineer. It is the sample spec: a planner that slices one feature, coders that implement it, a tester that gates, a human who merges. Cut the scale to what the offline fleet can ship in one run. Keep the seam, or you have built a different, weaker thing.

**Three: write it down.** The scope lives in the task spec, not in your head. The spec names the track, the reference architecture, the feature the fleet ships, the business problem, and the acceptance criteria. The business-problem line is where you name the seam you keep and the scope you cut — one sentence that tells a reader you understood the architecture, not just copied its name. The spec is the contract the fleet runs and the rubric grades; a vague spec is a vague grade.

The catalog is twenty answers to "how was this solved already." Choosing one and scoping it honestly is the difference between a portfolio that says *I can design a system* and one that says *I read a real design and shipped a version that holds the line that matters.*

## Core concepts

- The exam replicates a known architecture, never invents one from a blank page; each case study carries a seam — the one design decision a real version cannot drop — and that seam is what the rubric grades.
- The three tracks each anchor to specific case studies: eval-gated CI/CD (#18/#19/#17, seam = the eval gate), multi-tenant RAG (#08/#01/#12/#15, seam = isolation), agentic system (#07/#09/#16/#20, seam = the governed loop).
- Scoping "a version of" is cut the scale, keep the spine: shrink to what the offline fleet ships in one run while keeping the seam intact, and write that scope into the task spec where a reader can check it.
