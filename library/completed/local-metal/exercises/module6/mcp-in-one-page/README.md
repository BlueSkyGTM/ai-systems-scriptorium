# Exercise: Trace the Handshake

## Goal

Internalize the MCP protocol by writing out its messages by hand. Not by running code, not by reading a library's output: by composing each JSON object yourself, in order, the way the protocol actually flows.

## Why

When the server you build in the next lesson misbehaves, you will debug it by reading raw JSON on stdin and stdout. A developer who has written these messages once knows immediately whether a hanging handshake is a missing response or a stray extra one. Writing the protocol by hand first means the trace is readable to you, not just to a debugger.

## Steps

Write each of the following messages as valid JSON. Mark each one with either **request** (carries an `id`) or **notification** (no `id`, no response expected). You may write them in a plain text file, a Markdown file, or on paper; the format does not matter. The content does.

1. An `initialize` request from the client (use `"id": 1` and protocol version `2025-11-25`).
2. An `initialize` response from the server (include `protocolVersion`, `capabilities`, and `serverInfo`).
3. A `notifications/initialized` notification from the client.
4. A `tools/list` request from the client (use `"id": 2`).
5. A `tools/list` response from the server listing one tool: a made-up tool of your choice with a name, description, and a minimal `inputSchema`.
6. A `tools/call` request from the client (use `"id": 3`) calling the tool you defined above, with a plausible set of arguments.
7. A `tools/call` response from the server returning a `content` array with one text item and `"isError": false`.

To get you started, here is the initialize request and its response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "clientInfo": { "name": "my-client", "version": "1.0" }
  }
}
```

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "serverInfo": { "name": "my-server", "version": "0.1" }
  }
}
```

Write the remaining five messages yourself.

## Done When

You can answer these three questions cold, without looking at the lesson:

- Which of the seven messages are requests, and which is the notification?
- What does `tools/list` return?
- What does a successful `tools/call` response contain?

## Stretch

Write an eighth message: the `tools/call` response for a call to a tool that does not exist. In JSON-RPC 2.0, an error response uses an `error` object instead of a `result`. The shape is:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

Note the difference: no `result` key, no `content` array, and the `code` field follows the JSON-RPC spec's reserved error code range. A server that returns this correctly, rather than hanging or crashing, is one you can trust.
