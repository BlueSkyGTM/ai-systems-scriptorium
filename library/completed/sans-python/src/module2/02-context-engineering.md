# Context engineering

The context window is not a suggestion box — it's a fixed budget, and every token you put in displaces something else. Managing it poorly is the fastest path from a working prototype to a hallucinating production system.

## The window budget

Every model call allocates a finite token budget across four categories: the system prompt, tool definitions, retrieved documents, and conversation history. The numbers are large enough that beginners ignore the constraint, and small enough that production agents hit it constantly.

Token cost is not the only concern. **Lost-in-the-middle** is an attention failure: models read the beginning and end of a long context reliably, and degrade on material buried in the middle. If you retrieve ten documents and place the answer-bearing passage at position five, the model may miss it. The fix is deliberate ordering — highest-signal content at the start or end of the window, not the middle.

## Context rot

In multi-turn agent loops, the window accumulates. A conversation that fits in turn two doesn't fit in turn twenty. **Context rot** is the name for what happens: accuracy degrades as token counts grow, not because the model forgets, but because the signal-to-noise ratio collapses as low-value history crowds out high-value instructions.

Five techniques slow the rot:

1. **Compaction** — summarize older conversation turns into dense notes and drop the raw exchange.
2. **Just-in-time loading** — don't inject a document until the agent needs it. Most system prompts pre-load everything; most of that is wasted tokens.
3. **Structured note-taking** — maintain a typed, schema-bound memory object (not free text) so the model reads a compact, queryable store instead of a rambling transcript.
4. **Sub-agent isolation** — spawn a fresh agent for each sub-task. It starts with a clean window and hands back only its output, not its whole context.
5. **System prompt calibration** — audit your system prompt after every major change. Dead instructions are expensive tokens.

## Prompt caching

Provider-side prefix caching reads a warm KV-cache for token-identical prefixes, cutting input cost by fifty to ninety percent and first-token latency by forty to eighty-five percent. Anthropic makes you opt in with a `cache_control` marker — on individual blocks, or one top-level marker that auto-caches the longest stable prefix; OpenAI caches automatically with no markers. The economics favor any prompt with a long, stable prefix — a large system prompt, a reference document, a tool schema list — that stays constant across requests while only the user message changes.

Cache-friendly layout: put the stable content first (system prompt, reference material, tool definitions), put the dynamic content last (the user query). Invert that order and you invalidate the cache on every call.

**Contextual compression (RAD-L)** takes this further: for massive prompts, prune reasoning-irrelevant tokens before they enter the window at all. The result is a shorter, denser prompt that fits the cache boundary and costs less to process.

## Prompt-injection defense

The context window is attackable. Prompt injection is the LLM-era SQL injection: OWASP LLM Top 10, risk number one. Direct injection comes from a malicious user query. Indirect injection comes from content the agent retrieves — a web page, a document, a database record — that contains instructions designed to hijack the model.

Architectural defenses, not prompt-writing, are the answer:

- **Dual-LLM proxy** — a small guard model filters input before it reaches the frontier model. Suspicious instructions get blocked at the gate, not by the model under attack.
- **XML input isolation** — tag untrusted data explicitly (`<untrusted_content>`) and weight those sections lower in the instruction hierarchy (H-Rank training). The model treats flagged content as data, not instructions.
- **Canary tokens** — embed a known string in your system prompt. If it appears in the model's output, you have a system-prompt leak. Alert and rotate.
- **Least-privilege tool scopes** — agents should not have tools they don't need for the current task. Privilege escalation via injection is possible only if the scope is already too wide.

Treat every retrieved RAG chunk as untrusted. Run it through a separate analyzer pass before it reaches the generation call.

Context is a scarce, attackable resource — budgeting and defending it is platform work, not prompt work.

## Core concepts

- The context window is a fixed token budget; lost-in-the-middle attention failure means position inside the window determines whether content gets read.
- Context rot — accuracy collapse in long agent loops — is slowed by compaction, just-in-time loading, structured note-taking, sub-agent isolation, and system-prompt audits.
- Provider-side prefix caching cuts input cost fifty to ninety percent; cache-friendly layout puts stable content first and dynamic content last.
- Prompt injection is an architectural threat, not a prompt-writing problem — defend with a dual-LLM proxy, XML input isolation, canary tokens, and least-privilege tool scopes.

<div class="claude-handoff" data-exercise="exercises/module2/02-context-engineering/">

**Build It in Claude Code** — build a token-budget manager that enforces a context ceiling, compacts conversation history when it approaches the limit, and reports cache hit/miss cost savings.

</div>
