# Verdict: 12 — Frameworks and the Four Primitives

## Markers resolved

| Original marker | Status | URL |
|---|---|---|
| `[MS-Learn: Microsoft Agent Framework — graph-based workflow orchestration and checkpoint storage patterns]` | RESOLVED | https://learn.microsoft.com/agent-framework/workflows/ |
| `[MS-Learn: Microsoft Agent Framework — overview, actor model, and migration from AutoGen]` | RESOLVED | https://learn.microsoft.com/agent-framework/migration-guide/from-autogen/ |
| `[MS-Learn: Azure AI Foundry Agent Service — choosing between hosted agents, prompt agents, and bring-your-own framework]` | RESOLVED | https://learn.microsoft.com/azure/foundry/agents/overview#agent-types |

**Markers resolved: 3 / Unresolved: 0**

## Fixes applied

### (C) Claude Agent SDK package rename
- **Before:** `import { query } from "@anthropic-ai/claude-code"`
- **After:** `import { query } from "@anthropic-ai/claude-agent-sdk"`
- The lesson text already called the section "Claude Agent SDK"; the import used the old `claude-code` package name. The package was renamed to `claude-agent-sdk`. The `query()` entry point and the model IDs (`claude-opus-4-8`, `claude-haiku-4-5`) were not contradicted by any source, so both are retained.

### (C) Microsoft Agent Framework — successor language adjusted
- **Before:** "successor to AutoGen v0.4 and Semantic Kernel"
- **After:** "direct successor to both AutoGen and Semantic Kernel, built by the same teams"
- Rationale: MS Learn consistently says Agent Framework is "the next generation of both Semantic Kernel and AutoGen" with no version qualifier on AutoGen. "v0.4" appears nowhere in official documentation. Removed.

### (C) GA timeline claim removed
- The draft said "GA Q2 2026" as a parenthetical for Agent Framework. The MS Learn overview page still ships the C# package with `--prerelease`. No explicit GA announcement appears in Agent Framework docs as of the knowledge cutoff. The release cadence is documented (python-1.3.0 in May 2026) but no GA declaration was found. The GA qualifier was removed; the grounding clause now references the docs directly without asserting GA status.

### (B) STYLE §4 — banned ending rewritten
- **Before:** "An AI Platform Engineer who knows the four knobs can onboard any new framework in an afternoon — because every framework is a different set of bets about the same four questions."
- **After (new ending / seam line):** "The four knobs don't change when you add a hosting layer. What changes is where the orchestrator lives."
- Shape: consequence. Follows naturally from the Azure AI Foundry grounding clause about hosted vs. bring-your-own.

### (A) MS-Learn marker content woven in — lesson 12 Foundry section
The old `[MS-Learn: Azure AI Foundry...]` marker was replaced with a grounding paragraph explaining the hosted agent / prompt agent distinction, tied to the decision-rule section. Light grounding, no vendor pitch.

## STYLE conformance

- §1 Unity: second person and present tense hold throughout. No "we."
- §2 Simplicity: no qualifiers or dead adverbs introduced. Active voice maintained.
- §4 Lead: unchanged — strong, grabs immediately.
- §4 Ending: new ending is a consequence seam line. "An AI Platform Engineer who…" opener eliminated.
- §8 Variety: ending shape differs from adjacent lessons (consequence, not warning or question). One earned human moment already present in the DSPy aside ("It's worth knowing it exists for the moment…").
- Code snippets: all per-framework language assignments preserved (Python for LangGraph/Agent Framework/CrewAI/OpenAI; TypeScript for Claude Agent SDK/Mastra). No language changes made.
- Core concepts: unchanged (4 propositions, one sentence each).

## VERDICT: PASS (conditional on Opus confirming `query` export from `@anthropic-ai/claude-agent-sdk`)

The package rename is source-verified via the lesson's own naming convention and the task brief's explicit instruction. The `query()` function signature could not be independently confirmed via MS Learn or a public API reference reachable from this session. If Opus cannot confirm the exact export, the code comment already softens this ("Claude Code native") and the package name correction stands.
