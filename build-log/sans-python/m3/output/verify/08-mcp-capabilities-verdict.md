# Verdict: 08-mcp-capabilities

## Markers resolved

2 MS-Learn markers → all RESOLVED.

1. `[MS-Learn: Azure API Management — surfacing Azure resource metadata as MCP resources for agent context injection]`
   - **URL:** https://learn.microsoft.com/azure/api-management/mcp-server-overview
   - **Grounded fact:** Azure API Management can surface REST API data as MCP tool endpoints; the gateway layer (not MCP resources per se) handles read-only data surfacing. Note: the marker assumed a direct APIM-as-MCP-resources mapping; actual APIM support is at the tool/transport layer. Grounding clause written accurately to what APIM actually does.

2. `[MS-Learn: Azure AI Foundry — implementing human-in-the-loop review for MCP sampling requests in production agents]`
   - **URL:** https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol
   - **Grounded fact:** Foundry Agent Service's `require_approval` field concretizes the human-in-the-loop requirement: when set to `always`, the agent pauses and returns an `mcp_approval_request` output item before execution. Applied to sampling: same principle, server-side model calls without user visibility is the failure mode the spec prevents.

## Ending rewrite

**Old (banned template):**
> An AI Platform Engineer who knows these six primitives and their decision rules can design an MCP server that does exactly what the protocol intended — and can audit one that doesn't.

**New:**
> Six primitives, one decision rule each — get them wrong and the server technically works but does the wrong thing. Get them right and the protocol does the composition for you.

Shape: cost/consequence framing with a payoff inversion. The contrast ("technically works but does the wrong thing" → "protocol does the composition") gives the ending a small click. No template opener.

## STYLE conformance

- §4 ending: banned template removed. New ending is a warning/reframe shape. PASS.
- §8 variety: lesson is a decision-rule lesson — the six-primitive structure is necessarily list-like, but the prose surrounding each primitive uses varied sentence shapes (short commands, longer explanatory clauses, one rhetorical structure in the decision rule block). PASS.
- §1 unity: second person throughout. Present tense. PASS.
- Code: TypeScript `server.resource`, `server.prompt` snippets preserved. JSON roots block preserved. PASS.
- Async tasks/MCP apps one-liner preserved (SEP-1686, SEP-1724 references kept per task spec). PASS.

## VERDICT: PASS
