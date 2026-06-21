# Module 6 — Wire to Claude Code — Build Plan

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN`).** Self-locked under Ray's "finish the job"
directive (decisions stated for override). Sixth authoring stage for Local Metal (M1-M5 shipped
2026-06-21). M6 is the portfolio capstone: it wires the local rig into Claude Code so the editor can
delegate work to it, turning five modules of infrastructure into a thing you actually use every day.

## The stage in one line

M5 built a router that decides local vs cloud. M6 exposes that router to Claude Code as an MCP tool, so
Claude Code can hand a subtask to the local rig without you leaving the loop. The seam: the whole book
has been building toward offloading routine, private, high-volume work off the metered cloud and onto
the rig you own; M6 is where that offload becomes a single tool call inside your real editor. The
artifact a hiring manager reads here is "this person built an MCP server that bridges a local inference
host into an agentic coding tool," the most senior-sounding line in the book.

## The approach decision (locked: MCP delegation tool)

Three ways to "wire local to Claude Code" were considered:
1. **MCP delegation server (CHOSEN).** A small MCP stdio server exposes an `ask_local` tool; Claude Code
   keeps using Claude but can call the tool to delegate a subtask to the rig (via the M5 router + M3
   client). Best fit for "offload/delegate," keeps Claude as the driver, and is the most credible
   portfolio artifact.
2. Full model swap via an Anthropic-compatible proxy (e.g. LiteLLM) and `ANTHROPIC_BASE_URL`. Rejected
   as the spine: it replaces Claude entirely rather than delegating, and depends on a heavy third-party
   proxy. Named in the lesson as an alternative.
3. Claude Agent SDK custom agent. Rejected as the spine: heavier, less directly "wire into Claude
   Code." Named as a further-reading path.

## Settled decisions

1. **Stage = module.** Same shape as M1-M5; writes `build-log/local-metal/m6/output/{...}`.
2. **Held to the three contracts**; every worker brief carries them + the shipped M1-M5 lessons as the
   locked voice exemplar.
3. **The compounding spine completes here.** The MCP server's `ask_local` handler calls the M5
   `route.py` (decision) which calls the M3 `ollama_client.py` (local call). HARDWARE.md -> SETUP.md ->
   MODELS.md -> LATENCY.md -> ROUTING.md, and now `DELEGATION.md`, the 6th portfolio document (a real
   delegation session log). The runnable spine ollama_client.py -> route.py -> mcp_server.py is the
   through-line a reviewer can trace end to end.
4. **Stdlib-only, offline-testable MCP server.** A minimal MCP stdio server in the standard library
   (JSON-RPC 2.0 over newline-delimited stdio: `initialize`, `tools/list`, `tools/call`), so the
   exercise is machine-checkable with no rig, no cloud key, and no third-party SDK. The official `mcp`
   Python SDK is named as the production path; the stdlib server is the teachable, testable artifact.

## Locked decisions (all accepted; stated for override)

1. **Throughline artifacts: `mcp_server.py` + `.mcp.json` + `DELEGATION.md` + `check_delegation.py`.**
   `mcp_server.py` implements the MCP handshake and an `ask_local` tool; its `dispatch()` is a pure
   function (message in, response out) so `--selftest` asserts the protocol offline (initialize /
   tools/list / tools/call) with an injected fake responder. `.mcp.json` is the Claude Code
   registration snippet. `DELEGATION.md` records a real delegation session; `check_delegation.py` gates
   it (same validator family).
2. **Machine-checkable done-when without rig/Claude Code:** `mcp_server.py --selftest` asserts the
   JSON-RPC dispatch for the three core methods using an injected responder (no stdio, no network);
   `check_delegation.py` gates `DELEGATION.md` completeness. Both offline.
3. **The tool wraps the router, not the model directly.** `ask_local`'s default responder imports
   `route.route()` and, on a local decision, `ollama_client.call()`, with graceful fallback when the
   rig is unreachable. The lesson shows the import chain; selftest injects a fake responder so the
   protocol code tests standalone.
4. **No secrets, private-first.** No cloud key required; the cloud arm stays a stub. The MCP server
   binds nothing network-facing (stdio only), so it is safe to run locally by default.

## Proposed M6 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind |
|---|---------------|----------|------|
| 0 | `00-overview` | Five modules of infrastructure become a tool you use: expose the rig to Claude Code so it can delegate. | concept |
| 1 | `mcp-in-one-page` | What MCP is and the minimum a server must speak: JSON-RPC 2.0 over stdio, `initialize` / `tools/list` / `tools/call`. | concept |
| 2 | `build-the-mcp-server` | Build `mcp_server.py`: the stdio dispatch + an `ask_local` tool that wraps the M5 router; `--selftest` proves the protocol offline. | build |
| 3 | `register-with-claude-code` | Write `.mcp.json` (or `claude mcp add`) to register the server; what Claude Code does with `tools/list` and when it calls `ask_local`. | build |
| 4 | `log-the-delegation` | Record `DELEGATION.md` (a real delegation: prompt, route, reply) and gate it with `check_delegation.py`; the module's done-when. | build |

## Sources (three-source rule)

1. **Ingredient:** the SPEC + the shipped M3/M5 artifacts (`ollama_client.py`, `route.py`).
2. **External grounding:** the Model Context Protocol spec (JSON-RPC methods, stdio transport, tool
   schema), the Claude Code MCP documentation (registering a server, `.mcp.json`, `claude mcp add`,
   scopes); cite real URLs, capture to `vault/local-metal/m6-sources/PROVENANCE.md`. USE THE TOOLS
   (2 Haiku fetchers + the claude-code-guide angle where useful).
3. **Editorial seam framing** in every lead.

## The fleet plan

Conductor-direct, tiered: 2 Haiku source-fetchers (MCP protocol; Claude Code MCP registration) feeding
4 Sonnet lesson authors. Conductor writes the overview, owns + tests `mcp_server.py` +
`check_delegation.py` + the `.mcp.json` (byte-identical to ship), reviews, reconciles, runs the gates.

On ship: VERIFY (voice + grounding), BUILD/TEST (`mdbook build` + `mcp_server.py --selftest` +
`check_delegation.py`), then `GATE-APPROVE-SHIP` (cleared under "finish the job"), commit + push.
