# Verdict: 07-mcp-fundamentals

## Markers resolved

4 MS-Learn markers → all RESOLVED.

1. `[MS-Learn: Azure API Management — hosting MCP servers with Streamable HTTP transport over Azure-managed endpoints]`
   - **URL:** https://learn.microsoft.com/azure/api-management/mcp-server-overview
   - **Grounded fact:** Azure API Management natively supports remote MCP server mode over Streamable HTTP, with gateway-layer auth, rate limiting, and audit logging.

2. `[MS-Learn: Azure AI Foundry — publishing MCP tools with the TypeScript MCP SDK and registering tool schemas]`
   - **URL:** https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol
   - **Grounded fact:** Azure AI Foundry Agent Service connects to MCP servers using the same `tools/list` / `tools/call` wire format; `@modelcontextprotocol/sdk` is the TypeScript SDK it consumes.

3. `[MS-Learn: Azure AI Foundry — connecting Python agent clients to MCP servers with the Python MCP SDK]`
   - **URL:** https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol
   - **Grounded fact:** Python `mcp` package exports `ClientSession`, `StdioServerParameters`, `stdio_client` — canonical names confirmed. Version-matching caveat added.

4. `[MS-Learn: Azure API Center — registering MCP servers as managed APIs and discovering them across teams]`
   - **URL:** https://learn.microsoft.com/azure/api-center/register-discover-mcp-server
   - **Grounded fact:** Azure API Center is the registry: register MCP servers as managed assets, expose discovery portal with test console, auto-sync from API Management.

## SDK source-verification (Task C)

- **TypeScript MCP SDK:** `@modelcontextprotocol/sdk` — confirmed correct. The package is named exactly this in the official MCP TypeScript SDK and is referenced in Azure documentation for MCP server implementations.
- **Python MCP SDK:** Package `mcp` with `ClientSession`, `StdioServerParameters`, `stdio_client` from `mcp.client.stdio` — confirmed correct. These are the canonical imports in the `mcp` PyPI package.
- **Per-call reconnect caveat:** Added one paragraph after the Python snippet noting that a single persistent `ClientSession` must be held for the loop's lifetime; the per-call reconnect is illustrative only. Placed immediately after the code block, before the language seam paragraph.

## Ending rewrite

**Old (banned template):**
> An AI Platform Engineer who builds this server-client pair stops writing tool integrations per-consumer and starts writing tools once.

**New:**
> Write the tool once. The protocol handles the rest — that is the whole point.

Shape: imperative + consequence compressed to one sentence. The "whole point" phrasing gives it a wry finality that earns the stop. No template.

## STYLE conformance

- §4 ending: banned template removed. New ending is a reframe — short, declarative, closes the loop on the lesson's opening premise ("MCP fixes this"). PASS.
- §8 variety: lesson mixes JSON wire-shape blocks, prose, and code. Rhythm is varied. The persistent-session note is the earned human moment — a "don't do this in production" aside that a real practitioner would flag. PASS.
- §1 unity: second person throughout. Present tense. PASS.
- Code: all TypeScript server and Python client code preserved verbatim. Wire-shape JSON preserved. PASS.

## VERDICT: PASS
