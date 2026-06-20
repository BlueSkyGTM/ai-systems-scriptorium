# Reference Layer — Microsoft Learn (context-fill only)

**Microsoft Learn is the ONLY external reference for this curriculum, used on an as-needed
basis purely to fill context.** It is not a spine, not a source of truth, not curriculum.
(Coursera, the Learning Commons standards graph, and the course-designer skill were
evaluated and scrapped — see SESSION-STATE.md / memory.)

The curriculum is built from our own extracted library (`synthesis/source/`) plus Cowork
editorial framing. Microsoft Learn fills gaps and grounds orchestration patterns where our
material is thin — pull a URL below only when a specific lesson needs that context. Each
entry maps to a module and a teaching purpose.

---

## Module 3 — Orchestration Patterns

### Complexity Ladder (Gap 2 — complexity decision framework)
**Where it goes:** Bridge section at Module 2→3 boundary.
**Purpose:** The decision framework for when to add agents. "Don't add agents between the task and the model call unless the problem requires it."

| Level | Description | When to use |
|-------|-------------|-------------|
| Direct model call | Single LLM call, well-crafted prompt | Classification, summarization, single-step tasks |
| Single agent with tools | One agent, dynamic tool use | Varied queries in a single domain |
| Multi-agent orchestration | Multiple specialized agents | Cross-domain, parallel specialization, security boundaries |

- [AI agent orchestration patterns — Start with the right level of complexity](https://learn.microsoft.com/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Agent system design patterns — Levels of complexity](https://learn.microsoft.com/azure/databricks/agents/agent-system-design-patterns#levels-of-complexity-from-llms-to-agent-systems)

---

### Pattern 1 — Prompt Chaining
**Where it goes:** Module 3, entry pattern (also overlaps Module 2 LLM Engineering).
**Purpose:** Sequential LLM steps with validation gates. Simplest agentic pattern.
**TypeScript:** Available in Azure Durable Task SDK examples.

- [Prompt chaining pattern](https://learn.microsoft.com/azure/durable-task/sdks/durable-agents-patterns#deterministic-workflow-patterns)

---

### Pattern 2 — Routing
**Where it goes:** Module 3 — Tools and Protocols.
**Purpose:** Classify input and dispatch to specialized agents or models.
**TypeScript:** Available in Azure Durable Task SDK examples.

- [Routing pattern](https://learn.microsoft.com/azure/durable-task/sdks/durable-agents-patterns#deterministic-workflow-patterns)

---

### Pattern 3 — Parallelization (Fan-out/Fan-in)
**Where it goes:** Module 3 — Agent Engineering.
**Purpose:** Dispatch independent subtasks in parallel, aggregate results.
**TypeScript:** Available in Azure Durable Task SDK examples.

- [Parallelization pattern](https://learn.microsoft.com/azure/durable-task/sdks/durable-agents-patterns#deterministic-workflow-patterns)

---

### Pattern 4 — Orchestrator-Workers
**Where it goes:** Module 3 — Agent Engineering.
**Purpose:** LLM plans the work at runtime; spawns specialized worker sub-agents dynamically.
**TypeScript:** Available in Azure Durable Task SDK examples.

- [Orchestrator-workers pattern](https://learn.microsoft.com/azure/durable-task/sdks/durable-agents-patterns#deterministic-workflow-patterns)

---

### Pattern 5 — Evaluator-Optimizer
**Where it goes:** Module 3 — Autonomous Systems.
**Purpose:** Generator + evaluator in a refinement loop. Iterates until quality threshold met.
**TypeScript:** Available in Azure Durable Task SDK examples.
**Supplement:** loop-engineering `loop-verifier` skill for production edge cases.

- [Evaluator-optimizer pattern](https://learn.microsoft.com/azure/durable-task/sdks/durable-agents-patterns#deterministic-workflow-patterns)

---

### Pattern 6 — Agent Loops
**Where it goes:** Module 3 — Agent Engineering / Autonomous Systems.
**Purpose:** LLM-directed tool-calling loops. Two variants: orchestration-based and entity-based.
**TypeScript:** Available in Azure Durable Task SDK examples.
**Supplement:** loop-engineering-orange-book for the complete engineering reference.

- [Agent loops — orchestration-based and entity-based](https://learn.microsoft.com/azure/durable-task/sdks/durable-agents-patterns#deterministic-workflow-patterns)
- [Choose an approach (deterministic vs. agent-directed)](https://learn.microsoft.com/azure/durable-task/sdks/durable-agents-patterns#choose-an-approach)

---

### Pattern 7 — Multi-Agent Orchestration
**Where it goes:** Module 3 — Multi-Agent and Swarms.
**Purpose:** Multiple specialized agents coordinating. Orchestrator/peer-based protocols.
**Supplement:** fleet-engineering patterns for production governance (registry, budget guard, HITL).

- [AI agent orchestration patterns (Azure Architecture)](https://learn.microsoft.com/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Multi-agent system design (Databricks)](https://learn.microsoft.com/azure/databricks/agents/agent-system-design-patterns#levels-of-complexity-from-llms-to-agent-systems)

---

## Foundational References (all modules)

### Anthropic — Building Effective Agents
Microsoft's own docs cite this as the source of the pattern taxonomy. Use as conceptual
grounding alongside Microsoft's implementation references.

- [Building Effective Agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)

### Durable Task SDK Overview
The TypeScript/JavaScript runtime for durable orchestration patterns. Production-grade,
checkpointed, distributed.

- [Durable Task SDK overview](https://learn.microsoft.com/azure/durable-task/sdks/durable-task-overview)
- [Durable Functions overview](https://learn.microsoft.com/azure/durable-task/durable-functions/durable-functions-overview)

---

## How Claude Code uses this during Build phase

1. Read the relevant module's pattern entries from this doc
2. Fetch the Microsoft Learn URL via the Microsoft Learn connector for current content
3. Cross-reference with the sub-repo extraction output for exercises and production edge cases
4. Apply seam framing from SPEC.md and SYLLABUS.md
5. Assemble into lesson format per the LearnHouse block spec

This doc grows during Build as new reference gaps are found. Add entries here rather
than embedding URLs in individual lesson files.
