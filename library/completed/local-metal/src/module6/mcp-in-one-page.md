# MCP in One Page

Before you build the server, know the protocol. It is smaller than its reputation, and understanding it up front means you can read a raw JSON trace and tell exactly where a handshake went wrong.

## Step 1: What MCP Is

The Model Context Protocol is a standard that lets an AI client connect to servers that expose tools, discover what those tools do, and call them. Claude Code is an MCP client. When it connects to your server, it finds `ask_local`, learns its input shape, and calls it mid-session without you doing anything. The client side is already built; your job is to build the server side.

The wire format is JSON-RPC 2.0. If you have seen a language server or a debug adapter, the structure is familiar: a thin envelope carrying a method name and params, a matching reply carrying a result or an error. Everything else in MCP is built on top of that envelope.

## Step 2: The stdio Transport

A local MCP server is a process. It reads JSON-RPC messages from stdin and writes responses to stdout. Messages are newline-delimited: one JSON object per line, and a single message must not contain an embedded newline. That is the complete transport for a local server. No sockets, no HTTP, no port to bind, no TLS to configure: stdin goes in, stdout comes out, newlines keep the framing straight.

The simplicity is deliberate. The same server process that Claude Code launches on your machine could, in principle, speak the same protocol over a different transport for remote use. But for the local case, stdio is all you need, and its constraints eliminate an entire class of setup problems.

## Step 3: The Three Methods That Matter

MCP defines more methods than you need for a minimal server. For `ask_local`, three are enough.

**`initialize`** opens the session. The client sends:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "clientInfo": { "name": "claude-code", "version": "1.0" }
  }
}
```

The server replies with its own `protocolVersion`, `capabilities`, and `serverInfo`. After that, the client sends a `notifications/initialized` notification (see Step 4) and the session is open.

**`tools/list`** lets the client discover what the server offers. The server returns:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "ask_local",
        "description": "Delegate a prompt to the local inference rig (routed local vs cloud by policy).",
        "inputSchema": {
          "type": "object",
          "properties": {
            "prompt": { "type": "string" }
          },
          "required": ["prompt"]
        }
      }
    ]
  }
}
```

Each tool entry carries a name, a description, and an `inputSchema`: a JSON Schema object describing the arguments the tool accepts. Claude Code uses that schema to decide whether and how to call the tool.

**`tools/call`** runs the tool. The client sends:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "ask_local",
    "arguments": { "prompt": "Summarize this log file." }
  }
}
```

The server replies with a content array:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      { "type": "text", "text": "The log shows three failed retries between 14:02 and 14:05." }
    ],
    "isError": false
  }
}
```

The content is always an array, even when there is only one item. `isError` is `false` on success and `true` when the tool itself encountered an error (as opposed to a protocol-level error). The current protocol version string for all of these exchanges is `2025-11-25`.

## Step 4: Requests vs Notifications

JSON-RPC distinguishes two message kinds: requests and notifications. A request carries an `id` field and expects a response. A notification has no `id` and gets no response.

In the MCP lifecycle, `initialize` is a request (it carries `"id": 1`), and `notifications/initialized` is a notification (no `id`). This matters in practice: if you send a response to a notification, the client's message loop will not know what to do with it, and the handshake hangs. If you fail to respond to a request, it hangs for the opposite reason. Getting the `id` presence right is the mechanical test that keeps the session alive.

`tools/list` and `tools/call` are both requests and both need responses.

Knowing which is which means you can read a raw JSON trace and spot the problem in seconds: a hanging initialize almost always means the server sent a response to `notifications/initialized`, or never replied to `initialize` itself.

## Core Concepts

- MCP is JSON-RPC 2.0: every message is a thin envelope carrying a method name, params, and either an id (request) or no id (notification).
- The stdio transport for a local server is newline-delimited JSON on stdin and stdout; no sockets, no HTTP.
- Three methods cover a minimal server: `initialize` opens the session, `tools/list` publishes the tool catalog, and `tools/call` runs a tool and returns a content array.
- Requests carry an `id` and require a response; notifications carry no `id` and must not receive one; mixing these up is the most common cause of a hanging handshake.

<div class="claude-handoff" data-exercise="exercises/module6/mcp-in-one-page/">

**Build It in Claude Code**: Write out the JSON-RPC messages of a minimal MCP handshake by hand: the initialize request and response, the initialized notification, and a tools/list and tools/call exchange; mark which messages carry an id and which do not.

</div>

<!-- SOURCES: https://modelcontextprotocol.io/specification/2025-11-25/basic | https://modelcontextprotocol.io/specification/draft/basic/transports/stdio | https://modelcontextprotocol.io/specification/2025-11-25/server/tools -->
