# VERIFY verdict — Lesson 01: Why Multi-Agent — the Single-Agent Ceiling

**Lesson:** `build-stages/m4/output/author/01-why-multi-agent.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch01 Multi-Agent & Swarms)
**Date:** 2026-06-19

## Markers resolved (1 of 1)

| Marker | Source checked | Result |
|---|---|---|
| `[verify: Anthropic multi-agent research system — "How we built our multi-agent research system"]` (line 25) | WebFetch: anthropic.com/engineering/multi-agent-research-system | **FIXED → removed.** Confirmed and made precise: the post states the orchestrator + subagent system "outperformed single-agent Claude Opus 4 by **90.2%** on our internal research eval." Draft now reads "beat a single-agent baseline by 90% on their research eval" instead of the vague "by a wide margin." Architecture (orchestrator-worker, subagents in parallel with own contexts) and the fresh-context mechanism both confirmed verbatim. |

## Claim ledger

| Claim | Source consulted | Verdict |
|---|---|---|
| Complexity ladder: model call → workflow → single agent → multi-agent, each rung earns its place | M2/M3 throughline (PLAN line 18, 89); standard course framing | PASS |
| Three walls — context overflow, mixed expertise in one prompt, sequential bottleneck | Editorial synthesis of the multi-agent "when to use" material; consistent with asdg `[GAP 2: complexity ladder]` framing | PASS |
| "More agents, not a bigger agent"; focused fresh-context agents beat one overloaded agent | Anthropic post: subagents in separate context windows are the gain mechanism | PASS |
| Anthropic system beat single-agent baseline by ~90% | WebFetch Anthropic post: "outperformed single-agent Claude Opus 4 by 90.2%" | **FIXED** (was "wide margin" → now "90%") |
| Gain traced to clean per-subagent window, not inherited clutter | Anthropic post: "distributing work across agents with separate context windows" | PASS |
| Token cost: multi-agent ~4× a single agent, ~15× a plain chat | Anthropic post: "agents typically use about 4× more tokens than chat… multi-agent systems use about 15× more tokens than chats" | **FIXED** (was "an order of magnitude more than the single agent it replaced" — overstated; single→multi is ~4×, only chat→multi is ~15×/an order of magnitude. Reworded to the verified figures.) |
| Costs: latency (bounded by slowest worker + planning/synthesis), token cost, debugging-as-graph | Editorial; latency/observability claims are sound and not numeric | PASS |

## STYLE result — PASS

- H1 single; present tense, second person, one blunt confident voice throughout. ✓
- Seam-framed lead (line 3): no throat-clearing; states the problem and why the seam engineer needs it. ✓
- One `## Core concepts` block, 3 testable propositions; aligned to the corrected token figure. ✓
- `claude-handoff` div present and well-formed. ✓
- Ending (line 43): reframe → forward-question shape; not the banned "An AI Platform Engineer who…" template. ✓
- Acronyms: MLOps standard/established in earlier modules. ✓
- Rhythm varied (short declaratives broken by longer breathing sentences). ✓

## Overall verdict: **FIX-APPLIED** (1 marker resolved, 2 false-precision defects corrected, 0 FLAGGED). Ship-ready.

### Defects found + fixed
1. **Vague-where-source-is-precise:** "beat by a wide margin" → "by 90%" (Anthropic reports 90.2%).
2. **False precision / overstatement:** "an order of magnitude more tokens than the single agent it replaced." Anthropic's data makes multi-agent ~4× a single agent and ~15× a plain chat — the order-of-magnitude claim only holds against chat, not against the single agent. Corrected both the body and the Core-concepts line.
