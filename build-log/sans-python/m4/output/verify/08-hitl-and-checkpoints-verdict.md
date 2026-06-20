# VERIFY verdict — Lesson 08: HITL Propose-Then-Commit + Checkpoints/Rollback

**Lesson:** `build-stages/m4/output/author/08-hitl-and-checkpoints.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch02 Op-Safety, safety-critical)
**Date:** 2026-06-19

## Markers resolved (4 of 4)

| Marker | Source checked | Result |
|---|---|---|
| `[verify: LangGraph — interrupt() / human-in-the-loop]` | WebFetch docs.langchain.com (persistence + add-human-in-the-loop) | **PASS → removed.** `interrupt()` suspends a graph at a node and resumes from the checkpoint on response; requires a checkpointer. Added the "needs a checkpointer" precision. |
| `[verify: Cloudflare Agents — waitForApproval()]` | WebSearch Cloudflare Agents/Workflows docs | **PASS (with precision) → removed.** `waitForApproval()` is the HITL approval gate on the Cloudflare platform; it can wait hours/days/weeks. NOTE: strictly it is a **Cloudflare Workflows** method that integrates with Agents (which run on Durable Objects); the draft's old "does the same on a Durable Object" was slightly imprecise. Reworded to "Cloudflare Agents run on Durable Objects and pause for approval with a `waitForApproval()` gate" — accurate without overclaiming the host object. |
| `[MS-Learn: Microsoft Agent Framework RequestInfoEvent / human-in-the-loop]` | MS Learn connector: "Agent Framework Workflows — Human-in-the-loop (HITL)", "Events", "Sequential orchestration with HITL" | **PASS → removed.** An approval-required tool call pauses the workflow and emits `RequestInfoEvent` (carrying `ToolApprovalRequestContent`); the response routes back and execution continues. Reworded to MS's exact mechanism (pause approval-required tool call → emit event → route response back). |
| `[verify: EU AI Act Article 14 — human oversight requirements]` | WebFetch artificialintelligenceact.eu/article/14 | **PASS (reframed) → removed.** Article 14 requires effective human oversight: interpret output, intervene/interrupt with a stop control, and disregard/override/reverse the output. It does NOT literally say "queryable checkpoints" or "rehearsed rollback." See FLAGGED below — softened to separate statute from engineering reading. |

## Claim ledger

| Claim | Source | Verdict |
|---|---|---|
| Propose-then-commit, persisted with idempotency key, surface intent/lineage/blast-radius/rollback, commit on positive ack, verify after | Ph15 L15 verbatim (the 2026 HITL consensus enumeration) | PASS |
| Two naive-HITL failures: lost approval on crash + reviewer fatigue | Ph15 L15 (rubber-stamp); durable-pause from L12/L16 | PASS |
| Three frameworks: LangGraph `interrupt()`+Postgres / MS Agent Framework `RequestInfoEvent` / Cloudflare `waitForApproval()` | Ph15 L15 verbatim trio; each confirmed live (above) | PASS |
| Rubber-stamp is the canonical HITL failure; mitigate with challenge-and-response checklist | Ph15 L15 verbatim ("canonical failure is the rubber-stamp… mitigated by challenge-and-response with an explicit checklist") | PASS |
| Double-execute bug: crash after action runs but before record → naive retry re-executes | Ph15 L16 ("without all four a retry after a transient failure can double-execute an approved action") | PASS |
| Four-piece fix: idempotency key + precondition check + post-action verify + rollback-on-fail | Ph15 L16 verbatim (all four) | PASS |
| EU AI Act Article 14 = effective human oversight mandatory for high-risk systems | Ph15 L16 ("EU AI Act Article 14 makes queryable checkpoints/rehearsed rollbacks mandatory") + Article 14 text (oversight capabilities) | PASS (reframed — see FLAGGED) |
| Fleet scale = shared inbox applies the same protocol; references L08, does not re-teach | PLAN de-dup rule (HITL defined L08, `shared-inbox-HITL` applies it in L13) | PASS |
| `propose.py` code (idempotency key, pending→committed/rejected, idempotent return-prior-result) | Self-consistent; correctly implements the four-piece contract | PASS |

## FLAGGED (softened)

- **EU AI Act Article 14 framing.** The source extract (Ph15 L16) phrases Article 14 as making "queryable checkpoints/rehearsed rollbacks mandatory." The statute itself speaks in *capabilities* (interpret, intervene, interrupt/stop, override, reverse), not those engineering terms. I rewrote the section heading ("For high-risk systems, oversight is now law") and body to state what the Article literally requires, then explicitly frame queryable-proposal + tested-rollback as the *engineering reading* that satisfies it ("The Article speaks in those capabilities, not in implementation terms — but read against this protocol, they are exactly what propose-then-commit gives you"). The compliance claim is preserved but is now anchored to the oversight bar, not to verbatim statutory language. Confidence: HIGH that this is accurate and no longer overstates the statute.

## STYLE result — PASS

- Single H1, present tense, 2nd person, one voice. ✓
- Seam lead: "the agent decided to is not an answer you want to give an auditor" — irreversible-action problem; cusp implicit (audit/compliance = MLOps governance over AI capability). HITL expanded at first use. ✓
- One `## Core concepts` block, 4 testable propositions (Article 14 bullet updated to match reframe). ✓
- Handoff div well-formed. ✓
- Ending ("Build it as a popup over a tool call and you have a rubber stamp with extra steps"): contrast/warning shape, not the banned template; varied vs. siblings. ✓
- Acronyms: HITL expanded at first use; RAM standard. ✓
- De-dup: durable pause referenced to L05; fleet shared-inbox deferred to L13 ("define HITL once, here"). ✓

## Antilibrary fence — PASS
No frontier-safety/policy material. ✓

## Overall verdict: **PASS** (4 markers resolved, 1 framing defect FIXED [Cloudflare host object], 1 FLAGGED+softened [Article 14 statute vs engineering reading]). Ship-ready.
