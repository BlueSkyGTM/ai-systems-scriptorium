# Northstar

The thesis behind Sans Python. Return to this when anything drifts.

---

## The Problem

The standard AI Engineering curriculum is broken by sequencing, not content.

It forces a 6-month Python grind through a language you'll barely write, in an IDE you'll
eventually delete, to reach a skill set so generic it immediately needs triage. Agents are
introduced late — after the wall — which is backwards, because proper orchestration collapses
the wall. Students learn bad habits: IDE-dependent, library-first, agent-last.

The prescribed path:
1. Learn Python from scratch because it's easy and universal
2. Work through the libraries
3. Apply to AI engineering tools
4. Master hundreds of hours of Python material without AI
5. Learn to do it with AI
6. Then mostly abandon it — AI engineering is moving agent-first, away from the IDE-centric workflow
7. Learn Rust and TypeScript from scratch for performance and runtime
8. Start over

## The Thesis

The problem isn't Python. The problem is sequencing — and the gatekeeping that sequencing
enforces.

The conventional curriculum gatekeeps the high-leverage work — orchestration, agents, platform
engineering — behind months of prerequisites: Python first, then libraries, then ML fundamentals,
*then* you're allowed near the interesting material. **That gate is now false.** Agentic
orchestration handles ~85% of what the Python grind was supposed to teach, so a technical
limitation is no longer a reason to defer the advanced topic. The real 15% — the material that
actually matters — is accessible from day one once you stop burying it under prerequisite busywork.

**Get started without Python.** The course inverts the conventional order: start at the
high-leverage work, pull the technical pieces in at point-of-use. The principle generalizes past
Python — it runs through the whole course. Agents before you've "earned" them. Performance
engineering without the ML-math grind. Fleet governance framed as the destination, not a far-off
elective. A technical limitation is not a reason to wait.

**The orchestration layer is where leverage lives.** Decomposing problems, designing tool and
agent systems, knowing when *not* to add an agent, writing specs and evals — that is the skill the
course leads with. It is expressed in natural language, but the competency is orchestration, not
prose.

### Remove false gates, keep real dependencies

The inversion attacks the *artificial* gate (Python-first), never the *structural* one. A concept
that genuinely needs another still comes after it — the curriculum's flow audit confirmed zero
backward edges. This is the line between "we removed the barrier" and "we skipped the fundamentals."
We remove the false gate. We respect the real dependency.

### The stack

Rust and TypeScript are the writing stack, threaded to point-of-use (TypeScript from Module 3, Rust
from Module 5). Python is literacy you read to understand what's under the hood — plus a narrow,
deliberate **"Python you will write"** track (reading and debugging others' code, pytest, packaging,
FastAPI serving glue, eval scripts, notebook-to-service) introduced late, once you're past the false
gate. Python is never the *starting point*; it is never absent either.

## The Approach

- Lead with agency. Orchestration from day one, not syntax from day one.
- Agent-first environment. Understand from the inside — a repo plus a CLI agent, with VS Code or a hosted sandbox as the shell, not VS Code + 100 extensions you'll never configure.
- Compress the wall. The 6-month Python prerequisite is a false gate.
- Focus. One clear path. No generic skill set that immediately needs triage.

Writing principles from *On Writing Well* applied throughout: unite, simplify, shorten
without reducing effectiveness.

The end result: a course that combines the best available material, teaches your actual
day-to-day from day one, and doesn't compromise on quality.

## The Three Archetypes

The AI/ML job market produces three distinct roles. The roadmap treats them as separate
paths to pick and chase. That framing is the second problem — it produces engineers who
don't understand the seam between their role and the one next to it. Synergy is the actual
differentiator. The people who command top-of-band compensation understand the handoffs.

**Build — AI Engineer / Applied AI / GenAI**
Turns foundation models into functional applications. RAG pipelines, agents, LLM
integrations, user-facing AI features. The product layer. Largest volume of new openings
in 2026. Median $206K; agents/GenAI specialists hitting $175K–$250K+.

**Deploy — MLOps / AI Infrastructure Engineer**
The reason AI systems don't collapse in production. Training pipelines, model registries,
data versioning, drift monitoring, A/B testing infrastructure. Most undervalued
specialization in 2026. Median $175K–$220K; bottleneck talent commands a premium.

**Optimize — Machine Learning Engineer**
Trains, fine-tunes, and improves models at scale. Bridges data science experimentation
and robust software delivery. The depth layer. Median $187.5K; senior $240K+.

### Language Fit by Archetype

|  | TypeScript | Rust | Python |
|---|---|---|---|
| Build | Primary — product layer, agents, APIs | Edge cases (WASM, performance) | Replaceable — literacy enough |
| Deploy | Tooling layer — CI/CD, IaC, dashboards | Serving layer, CLIs, pipelines | Literacy required, writing optional |
| Optimize | Evaluation harnesses, UIs | Primary — inference, tokenizers, numerics | Non-negotiable — training ecosystem is Python |

Python is never the starting point. By the time a student reaches Optimize, they've built
and deployed real systems. Python as a specialist tool at that point is a different ask
than Python as the prerequisite to everything.

### Synergy

Build engineers who understand Deploy write code that's actually deployable.
Deploy engineers who understand Optimize know what's worth monitoring.
Optimize engineers who understand Build know what the model is actually for.

Sans Python sequences the three — Build first, Deploy second, Optimize third — so synergies
are visible and earned, not accidentally discovered years into a siloed career.

### Source Material by Archetype

| Sub-Repo | Primary | Role |
|---|---|---|
| ai-engineering-from-scratch | All three | Full arc — the spine of the curriculum |
| made-with-ml | Deploy | MLOps in practice; Optimize as substrate |
| loop-engineering | Deploy | Agentic operations and automation patterns |
| fleet-engineering | Deploy | Agentic governance at scale (3+ loops, 5+ agents) |
| 100-exercises-to-learn-rust | Build + Deploy | Language foundation |
| typescript-projects | Build | Product layer tooling |
| ai-performance-engineering | Deploy / Optimize | Inference-serving performance (inference subset; training/CUDA → Antilibrary) |
| ai-system-design-guide | All three | Staff-level production reference — the AI Platform Engineering spine |
| loop-engineering-orange-book | Deploy | Loop-engineering reference (the complete engineering manual) |

---

## The Target

Sans Python does not target Build engineers or Deploy engineers. It targets the discipline that lives where both tracks converge: **AI Platform Engineering**.

This is not a blend of two roles. It's its own thing — the infrastructure-centric layer that makes AI systems actually work at scale. MLOps is model-centric: model lifecycle, data prep, retraining. AI Platform Engineering is infrastructure-centric: the platform MLOps engineers and application developers USE — GPU clusters, cost controls, API gateways, orchestration layer, observability. The `ai-system-design-guide` — a staff-level production reference used in real engineering interviews — organizes itself around exactly this discipline. The seam was always pointing at something that already had a name.

JD audit (2026-06-17): the title exists, the skills map to the seam, and it's niche enough to be indispensable. Core hypothesis, reframed: **inference-platform engineering > model training** — the seam owns serving, cost, observability, and governance, not model internals. (Evidence is a first-pass audit; a wider JD sample is an open validation task — see AUTOPLAN-REVIEW.md.) Graduates still need a **minimum ML-literacy floor**: what training, fine-tuning, and eval metrics mean and when they matter — enough to read and reason about them, not to implement from scratch.

A perfect fit to Build = a product engineer who can't get to production.
A perfect fit to Deploy = an infrastructure engineer who doesn't understand what they're running.
A perfect fit to either = a commodity hire.

The AI Platform Engineer speaks both languages fluently and neither one perfectly. At a startup, a Series B company, or any team hiring one person to own the full stack, that's the profile they can't find. The apparent weakness in a course catalog is indispensability in the job.

What AI Platform Engineering owns:
- Evaluation and observability — Build creates evals, Deploy monitors them. Same problem, one owner.
- Agent infrastructure — building agents IS deploying them. The seam collapses here.
- Versioning — code, prompts, models — shared concern with no established Python-first solution.
- Testing non-deterministic systems — unsolved problem neither track owns cleanly.
- Cost management — tokens and compute — Build ignores it, Deploy obsesses over it. Reality requires both.
- The fine-tune vs. prompt decision — Build makes it, Deploy lives with it.
- System architecture — how all of the above connects into something that holds under production load.

The goal is not a complete course. The goal is a career. The person who can navigate the full system — from the first API call to the monitoring dashboard — is the one who becomes indispensable.

---

## What This Is Not

- Not "no Python ever"
- Not a replacement for understanding what Python does
- Not a shortcut that skips hard concepts — it reorders them

## Course Name

Sans Python

## Status

Thesis locked. Curriculum structure follows after repo extraction.
