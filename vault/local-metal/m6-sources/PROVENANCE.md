# Local Metal — Module 6 Source Provenance

Cited-resource record for Module 6 ("Wire to Claude Code"). Per the authoring directive, every external
resource a lesson cites is captured here as tracked ore: the URL, what it grounds, the source type,
and the retrieval date. The shipped book cites the URLs; this manifest preserves the underlying fact
against link rot. Retrieved 2026-06-21 by the M6 source-fetch tier (two Haiku fetchers) and the
authoring fleet (Sonnet workers + conductor), grounded via the official Model Context Protocol spec
and the official Claude Code MCP docs.

## The MCP protocol (Lessons 1-2: mcp-in-one-page, build-the-mcp-server)

| Fact grounded | Source | Type |
|---|---|---|
| MCP uses JSON-RPC 2.0 as its message format | https://modelcontextprotocol.io/specification/2025-11-25/basic | MCP spec (authoritative) |
| stdio transport: server reads stdin / writes stdout; newline-delimited JSON, no embedded newlines | https://modelcontextprotocol.io/specification/draft/basic/transports/stdio | MCP spec (transports) |
| Lifecycle: `initialize` (protocolVersion/capabilities/clientInfo -> protocolVersion/capabilities/serverInfo), then client `notifications/initialized` (no id, no response) | https://modelcontextprotocol.io/specification/2025-11-25/basic | MCP spec (lifecycle) |
| `tools/list` -> `{tools:[{name, description, inputSchema}]}`; `tools/call` params `{name, arguments}` -> `{content:[{type:"text", text}], isError}` | https://modelcontextprotocol.io/specification/2025-11-25/server/tools | MCP spec (tools) |
| Current stable protocol version string `2025-11-25` | https://modelcontextprotocol.io/specification/2025-11-25/basic | MCP spec |

## Registering with Claude Code (Lessons 3-4: register-with-claude-code, log-the-delegation)

| Fact grounded | Source | Type |
|---|---|---|
| `claude mcp add --scope project <name> -- <command> <args>` registers a local stdio server | https://code.claude.com/docs/en/mcp-quickstart | Claude Code docs (authoritative) |
| `.mcp.json` at the repo root: `mcpServers` -> `{type:"stdio", command, args, env}`; project scope is committed/shared | https://code.claude.com/docs/en/mcp-quickstart , https://code.claude.com/docs/en/mcp | Claude Code docs |
| MCP scopes: local (default, private), project (shared via `.mcp.json`), user (private, all projects) | https://code.claude.com/docs/en/mcp | Claude Code docs |
| Claude Code is an MCP client: discovers tools via `tools/list`, invokes via `tools/call`; first call needs user approval; `/mcp` panel shows status | https://code.claude.com/docs/en/mcp-quickstart , https://code.claude.com/docs/en/mcp | Claude Code docs |

## The compounding spine (the artifact a reviewer traces)

M6 completes the runnable spine: `ollama_client.py` (M3) calls the model; `route.py` (M5) decides when
to; `mcp_server.py` (M6) lets Claude Code pull the lever via the `ask_local` tool. The stdlib MCP
server reports protocolVersion `2025-11-25`, advertises one tool (`ask_local`), and was verified by the
conductor both via `--selftest` (offline dispatch of initialize/tools/list/tools/call) and by piping a
real JSON-RPC handshake over stdio. The official `mcp` Python SDK is named as the production path; the
stdlib server is the readable, testable teaching artifact. No cloud key or network is required to
complete the module; the cloud arm stays a stub and the server binds nothing network-facing (stdio
only).
