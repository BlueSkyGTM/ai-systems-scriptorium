# Exercise 07 — MCP Fundamentals

## Goal

Expose `module3-agent/tools/` as a runnable MCP server over stdio, then connect the Python harness as an MCP client — making the Python-loop ↔ TypeScript-tools bridge concrete and testable.

## Why

In-process tools don't compose across hosts. The MCP server turns typed TypeScript tools into a standard interface any MCP client can call — including the Python harness, Claude Code, and Claude Desktop — without per-consumer integration work.

## Steps

1. Install `@modelcontextprotocol/sdk` (npm). Add `module3-agent/mcp-server/index.ts` and a matching `tsconfig.json` that emits to `mcp-server/dist/`.
2. Create an `McpServer` with name `module3-agent-tools` and version `1.0.0`.
3. Register the `searchTool` from `module3-agent/tools/search.ts` using `server.tool()`. Use `zod` (`z.string()`) for the parameter schema — the compiled Zod schema is what the SDK sends in `tools/list`.
4. Connect a `StdioServerTransport` and call `server.connect(transport)`. Compile with `npx tsc`.
5. Smoke-test the server manually: run `node mcp-server/dist/index.js`, pipe in the `initialize` + `tools/list` JSON-RPC messages by hand, and confirm the response lists the `search` tool.
6. Add `module3-agent/harness/mcp_client.py`. Install the Python MCP SDK (`pip install mcp`). Implement `connect_to_ts_tools()` using `StdioServerParameters` pointing to `node mcp-server/dist/index.js` and `ClientSession`.
7. Implement `call_tool(name, arguments)` in `mcp_client.py` — open a session, call `session.call_tool()`, return the first text content item.
8. Update the Python agent harness so its `tools.execute(name, args)` delegates to `call_tool()` from `mcp_client.py`. Remove the direct TypeScript registry call from lesson 06.
9. Run the full loop end-to-end: the Python harness calls `search` through the MCP session; the TypeScript server handles it; the result comes back as an observation in the Python loop.

## Done when

- `node mcp-server/dist/index.js` starts without errors and responds to `tools/list` with the `search` tool.
- `python harness/mcp_client.py` prints the JSON-RPC round trip: the `tools/list` response and the `tools/call` result for `search`.
- The Python agent loop completes a toy goal — any goal that triggers `search` — with the tool call routed through MCP. The loop's output includes the observation text returned by the TypeScript server.
- `npx tsc --noEmit` passes in both `module3-agent/` and `module3-agent/mcp-server/`.

## Stretch

Connect Claude Desktop to the same MCP server: add a `claude_desktop_config.json` snippet pointing to `node mcp-server/dist/index.js` and verify that Claude Desktop lists the `search` tool in its tool picker.
