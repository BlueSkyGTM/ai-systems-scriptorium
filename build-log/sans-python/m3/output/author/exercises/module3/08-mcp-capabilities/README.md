# Exercise 08 — MCP Capabilities

## Goal

Extend the MCP server from lesson 07 with a resource, a prompt, and roots enforcement — turning a tool-only server into a full-contract MCP server.

## Why

Tools handle computed actions. Resources serve read-only context. Prompts offer reusable interaction templates. Roots scope filesystem access. Building all three makes the MCP contract concrete and teaches the decision rule for which primitive fits which job.

## Steps

1. Add a resource to the MCP server: `config://module3-agent/config`. The resource handler returns the agent's runtime config (`{ model: "claude-opus-4-8", maxTurns: 10, strict: true }`) as `application/json`. Register it with `server.resource()`.
2. Add a prompt to the MCP server: `review-tool-schema`. The prompt takes a `tool_name` string parameter and returns a `messages` array: one `user` role message that includes the named tool's JSON Schema as formatted JSON and a review instruction. Register it with `server.prompt()`.
3. Add roots enforcement to the server. At `initialize`, read the client-declared roots from the session (if present). Add a `checkRoot(filePath: string): boolean` helper that returns `false` if the path falls outside every declared root URI. Apply this check in any tool that accesses the filesystem — return a structured error observation if the path is out of bounds.
4. Rebuild and restart the MCP server (`npx tsc && node mcp-server/dist/index.js`).
5. In `mcp_client.py`, extend the smoke-test script:
   - Call `session.list_resources()` and print the result.
   - Call `session.read_resource("config://module3-agent/config")` and print the JSON content.
   - Call `session.list_prompts()` and print the result.
   - Call `session.get_prompt("review-tool-schema", {"tool_name": "search"})` and print the returned messages.

## Done when

- `session.list_resources()` returns the `config://module3-agent/config` resource.
- `session.read_resource("config://module3-agent/config")` returns the config JSON.
- `session.list_prompts()` returns the `review-tool-schema` prompt.
- `session.get_prompt("review-tool-schema", {"tool_name": "search"})` returns a messages list with one user message containing the search tool's JSON Schema.
- A simulated out-of-roots file path returns a structured error observation (test with a string path outside the declared root, hardcoded for the test).

## Stretch

Add a `notifications/resources/updated` subscription: when the config file on disk changes (use a file watcher), send the notification to any subscribed client. Verify by subscribing in `mcp_client.py` and touching the config file.
