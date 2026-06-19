# VERIFY verdict — Lesson 02: Communication Protocols (MCP / A2A / ACP / ANP)

**Lesson:** `build-stages/m4/output/author/02-communication-protocols.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch01 Multi-Agent & Swarms)
**Date:** 2026-06-19

## Markers resolved (3 of 3)

| Marker | Source checked | Result |
|---|---|---|
| `[MCP-spec: tools/list, tools/call]` (line 13) | MCP spec (course M3 prior art; method names are stable spec primitives) | **PASS → removed.** `tools/list` and `tools/call` are the correct MCP JSON-RPC methods; woven into prose. |
| `[A2A-spec: Agent Card, Task lifecycle]` (line 15) | WebFetch: a2a-protocol.org/latest/specification + WebSearch (a2a-protocol.org v0.2/v0.3) | **FIXED → removed.** See defects below: Agent Card well-known path made concrete; lifecycle confirmed (subset) with `input-required` added; the code-block RPC method name corrected. |
| `[verify: FIPA-ACL — IEEE FIPA00037 specification]` (line 27) | WebSearch (FIPA SC00037J, fipa.org) — fipa.org site itself ECONNREFUSED, corroborated via multiple secondary refs | **FIXED → removed.** Two factual errors corrected (count and year/attribution). |

## Claim ledger

| Claim | Source consulted | Verdict |
|---|---|---|
| Four-layer stack: MCP (agent↔tool), A2A (agent↔agent), ACP (audit/trajectory), ANP (identity/trust/DID) | asdg §03 key concepts (MCP/A2A/ACP) + protocol-survey framing (arXiv 2505.02279) | PASS |
| MCP: connect server, list tools, read schemas, invoke over JSON-RPC | MCP spec; asdg §03 "JSON-RPC… dynamic discovery" | PASS |
| A2A: Agent Card for discovery at a well-known URL | A2A spec — Agent Card retrieved at `GET /.well-known/agent-card.json` | **FIXED** (made the path concrete) |
| A2A Task lifecycle `submitted → working → completed / failed / canceled` | A2A spec TaskState enum: submitted, working, completed, failed, canceled, input-required, rejected, auth-required, (unspecified) | **FIXED** — draft showed a valid happy-path subset; added `input-required` so the simplification is honest. (Full enum noted; not all states needed pedagogically.) |
| Results are typed Artifacts | A2A spec: "Results SHOULD BE returned using Artifacts associated with a Task" | PASS |
| Code-block A2A send method | A2A spec current RPC is **`message/send`** (and `message/stream`); early drafts used `tasks/send` | **FIXED** — renamed `method: "tasks/send"` → `"message/send"` (renamed-API defect). |
| FIPA-ACL performative count | FIPA Communicative Act Library SC00037J = **22** performatives | **FIXED** — "twenty" → "twenty-two." |
| FIPA-ACL year / standardization body | FIPA specs published **2002-12**; **IEEE Computer Society inherited FIPA in 2005** | **FIXED** — "In 2000 the IEEE ratified FIPA-ACL" was wrong on year and body. Now: "In 2002 the FIPA standards bodies published FIPA-ACL… (the IEEE Computer Society later took FIPA over in 2005)." |
| KQML ~1993, speech-act theory heritage | FIPA followed KQML (early 1990s) per ACL histories | PASS (kept "early 1990s") |
| Reference platforms JADE / JACK | JADE is the canonical FIPA-compliant platform; JACK is a BDI agent platform, not a FIPA reference impl | **FIXED** — dropped JACK; kept JADE only (defensible). |
| Contract-net for task delegation | FIPA Contract Net Interaction Protocol (real) | PASS |
| Old failure modes return: ambiguous performatives, deadlock, ontology mismatch | Editorial; consistent with classic ACL critique | PASS |
| Raw-string failure trio: misinterpretation, deadlock, scale | Editorial; sound | PASS |
| Reuse M3 TS MCP wire types; type the A2A wire the same way | PLAN line 79–80 (TS contracts reuse M3 MCP work) | PASS |

## STYLE result — PASS

- H1 single; second person, present tense, one voice. ✓
- Seam-framed lead (line 3): the lying-strings problem → why a wire contract; no throat-clearing. ✓
- Acronyms in title (MCP/A2A/ACP/ANP) all expanded on first use in body. ✓
- One `## Core concepts` block (3 propositions); handoff div well-formed. ✓
- Ending (line 69): "the agents talk, and you can prove what they said" — consequence shape, not the banned template. ✓
- Code block earns its place (typed wire contract the prose can't carry). ✓

## Overall verdict: **FIX-APPLIED** (3 markers resolved, 4 defects corrected — 22 vs 20 performatives, 2002/2005 vs 2000, `message/send` vs `tasks/send`, JADE-only — plus 1 honesty add (`input-required`). 0 FLAGGED). Ship-ready.

### Note for Opus
The A2A Task-lifecycle subset is intentionally simplified for teaching; the full enum (input-required, rejected, auth-required, unspecified) is verified and noted here if you want the lesson to gesture at the complete set.
