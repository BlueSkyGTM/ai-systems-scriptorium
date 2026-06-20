# MCP fundamentals

The typed tools from lessons 04–06 live inside your process. MCP moves them outside it — and that's where the language bridge becomes real.

## What MCP solves

In-process tools are fast and simple, but they don't compose. Claude Desktop can't call your TypeScript tool. Another team's Python agent can't call it. Claude Code can't call it. Every consumer writes its own integration.

The Model Context Protocol fixes this with a standard: one server exposes your tools over a defined wire format; any MCP client — Claude Desktop, Claude Code, your Python harness, a colleague's agent — connects and calls them without renegotiation. One implementation, many hosts. That is the compounding value.

MCP is JSON-RPC 2.0, nothing more exotic. The spec defines what messages flow, in what order, over what transports. Learning the protocol is learning seven message types and a lifecycle.

## The protocol shape

MCP has three phases: **initialize**, **operation**, shutdown.

In `initialize`, the client announces its capabilities; the server announces its own. Both sides agree on the protocol version and what features are in play.

In `operation`, the client sends requests (`tools/list`, `tools/call`, `resources/read`, `prompts/get`) and the server responds. The server can also send notifications to the client without a pending request.

`shutdown` is a graceful close — the client sends a notification, the server drains, the transport closes.

The wire shape of a `tools/list` round trip:

```json
// client → server
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}

// server → client
{"jsonrpc":"2.0","id":1,"result":{"tools":[
  {
    "name": "search",
    "description": "Search for information on a topic.",
    "inputSchema": {
      "type": "object",
      "properties": {"query": {"type":"string"}},
      "required": ["query"]
    }
  }
]}}
```

And a `tools/call`:

```json
// client → server
{"jsonrpc":"2.0","id":2,"method":"tools/call",
 "params":{"name":"search","arguments":{"query":"MCP transports"}}}

// server → client
{"jsonrpc":"2.0","id":2,"result":{"content":[
  {"type":"text","text":"[result] MCP uses stdio and Streamable HTTP..."}
]}}
```

The schema your TypeScript tool already carries (`name`, `description`, `parameters`) maps directly to the `tools/list` response. No reshaping needed — the TypeScript `ToolDefinition` from lesson 05 is the MCP server manifest.

## Transports

MCP defines two transports: **stdio** and **Streamable HTTP**.

**stdio** runs the server as a child process. The client writes newline-delimited JSON to stdin; the server writes responses to stdout. Local tools, Claude Code extensions, and development setups use stdio. It is dead simple — no ports, no auth, no firewall rules.

**Streamable HTTP** sends all MCP traffic over a single HTTP endpoint (`POST /mcp`). The server assigns a session ID; the client includes it on subsequent requests. Long-running connections use Server-Sent Events for server-to-client notifications. Remote, shared, and production servers use this transport.

Azure API Management natively supports the MCP server remote mode: it can expose any managed REST API or an existing MCP server as a Streamable HTTP endpoint, applying auth, rate limiting, and audit logging at the gateway layer. (learn.microsoft.com/azure/api-management/mcp-server-overview)

## Building the TypeScript MCP server

The TypeScript MCP SDK (`@modelcontextprotocol/sdk`) wraps the protocol. The server exposes the tools already typed in `module3-agent/tools/`:

```typescript
// module3-agent/mcp-server/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { searchTool } from "../tools/search.js";
import { z } from "zod";

const server = new McpServer({
  name: "module3-agent-tools",
  version: "1.0.0",
});

// Register the typed tool from lesson 05
server.tool(
  searchTool.name,
  searchTool.description,
  { query: z.string().describe("The search query.") },
  async ({ query }) => ({
    content: [{ type: "text", text: await searchTool.execute({ query }) }],
  })
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

The tool registered here is the same `searchTool` from `module3-agent/tools/search.ts`. The MCP server is a thin transport wrapper around the typed implementation — no duplication, no reshaping.

Azure AI Foundry Agent Service supports the MCP tool primitive directly: you point an agent at a server URL, and it discovers and calls your tools over the same `tools/list` / `tools/call` round trip shown above. The TypeScript MCP SDK (`@modelcontextprotocol/sdk`) is the same SDK consumed by Foundry when it connects to an MCP tool endpoint. (learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol)

## Connecting the Python loop as an MCP client

This is the bridge. The Python agent harness — the loop, planner, and reflexion layers from lessons 01–03 — connects to the TypeScript MCP server as an MCP client over stdio. Python's MCP SDK handles the protocol:

```python
# module3-agent/harness/mcp_client.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def connect_to_ts_tools():
    params = StdioServerParameters(
        command="node",
        args=["module3-agent/mcp-server/dist/index.js"],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            # tools.tools is a list of Tool objects matching tools/list
            return tools.tools

async def call_tool(name: str, arguments: dict) -> str:
    params = StdioServerParameters(
        command="node",
        args=["module3-agent/mcp-server/dist/index.js"],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
            return result.content[0].text
```

The Python loop calls `call_tool("search", {"query": "..."})` instead of `tools.execute("search", {...})`. The protocol is the bridge — the TypeScript tool runs in its own Node.js process; the Python harness talks to it over stdio JSON-RPC.

The snippet above reconnects per call to keep the illustration simple. In production the Python harness should hold a single persistent `ClientSession` for the loop's lifetime and call tools through it — spawning a new subprocess and re-running `initialize` on every tool call adds latency and process overhead that compounds fast in a multi-turn agent loop.

The language seam is now explicit: TypeScript owns the tool implementations and the MCP server; Python owns the agent harness, the planning loop, and the client connection. MCP is the language boundary.

The Python `mcp` package provides `ClientSession`, `StdioServerParameters`, and `stdio_client` — the three imports shown above. These are the canonical names in the published `mcp` package; verify the installed version matches the server SDK version to avoid protocol-version mismatches. (learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol)

## Decoupling as the payoff

The TypeScript tools now run wherever Node.js runs. Connect Claude Desktop's MCP host to the same server — it calls your tools. Connect Claude Code — same. Connect a colleague's LangGraph agent with its own MCP client — same tools, same implementation, zero duplication.

One more consequence: you can swap the Python harness for a different client without touching the TypeScript tools. You can update the tool implementation without touching the client. The protocol is the only shared contract.

Azure API Center fills the registry role in Azure environments: register your MCP servers as managed API assets, expose a discovery portal to internal consumers, and synchronize with API Management automatically. (learn.microsoft.com/azure/api-center/register-discover-mcp-server)

Write the tool once. The protocol handles the rest — that is the whole point.

## Core concepts

- MCP is JSON-RPC 2.0 with a defined lifecycle (initialize → operation → shutdown) and two transports: stdio for local child-process tools, Streamable HTTP for remote shared servers.
- The TypeScript `ToolDefinition` from lesson 05 maps directly to the MCP `tools/list` response — the MCP server is a transport wrapper, not a new implementation.
- The Python agent harness connects as an MCP client over stdio, making MCP the language bridge: TypeScript typed tools server-side, Python control-flow client-side.
- One MCP server serves any MCP host — Claude Desktop, Claude Code, your Python loop — without per-consumer integration work.

<div class="claude-handoff" data-exercise="exercises/module3/07-mcp-fundamentals/">

**Build it in Claude Code** — expose `module3-agent/tools/` as a runnable MCP server (`module3-agent/mcp-server/index.ts`) over stdio using the TypeScript MCP SDK, then connect the Python harness as an MCP client (`module3-agent/harness/mcp_client.py`). The end-to-end test: the Python loop calls `search` via `session.call_tool()`, receives a result, and prints the JSON-RPC round trip. Open the repo and run the exercise for this lesson.

</div>
