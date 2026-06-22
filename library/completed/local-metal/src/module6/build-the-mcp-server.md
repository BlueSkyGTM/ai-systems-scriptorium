# Build the MCP Server

You know the protocol; now implement it. `mcp_server.py` is the piece that makes the entire stack
reachable from Claude Code: it translates three JSON-RPC methods into real work and hands the live
path off to the router you built in Module 5.

## Step 1: The Shape

The entry point is `dispatch(message, responder)`. It takes one JSON-RPC message and returns a
response dict, or `None` when the message is a notification that must not receive a reply.

Because `dispatch` has no side effects and no network calls, `--selftest` can assert all three
methods offline with a fake responder. No stdio loop, no rig, no editor. This is the same
offline-core, live-path pattern as `ollama_client.py` and `route.py`: the pure function is the
machine-checkable done-when, and the live path is layered on top.

Two small helpers keep the shape consistent. `result(request_id, payload)` wraps a success
payload in a standard JSON-RPC envelope. `error(request_id, code, message)` wraps a failure.
Every branch of `dispatch` returns one or the other.

## Step 2: The ask_local Tool

`tools/list` advertises a single tool: `ask_local`. Its `inputSchema` requires one field, `prompt`,
typed as a string. That schema is what Claude Code reads to know it can call this tool and what
argument to supply.

`tools/call` runs the tool. It validates the tool name and prompt, then calls `responder(prompt)`
and wraps the return value in a content array with `"isError": false`.

The default `responder` is the compounding payoff: it imports `route()` from the Module 5 router
and `call()` from the Module 3 client, runs the routing decision, and on a local decision calls
the rig directly. When `route.py` is absent, it returns a plain fallback string instead of
crashing. When the rig is unreachable, it returns the routing decision so the caller still knows
what would have happened. `ask_local` is the lever Claude Code pulls; the entire stack you built
sits behind it.

## Step 3: The Serve Loop

`serve()` reads newline-delimited JSON from stdin one line at a time, calls `dispatch`, and writes
the response to stdout followed by a newline and a flush. When `dispatch` returns `None` (a
notification), `serve` skips the write. That is the complete stdio transport: no sockets, no port,
no TLS.

One detail matters in practice: the flush. Without it, the client receives no response until the
buffer drains, and the handshake hangs silently. Every response must flush before the loop
continues.

## Step 4: Build and Run It

Create `exercises/module6/build-the-mcp-server/mcp_server.py` with this exact code:

```python
#!/usr/bin/env python3
"""
mcp_server.py: a minimal Model Context Protocol server exposing the local rig to Claude Code.

Speaks MCP over stdio (JSON-RPC 2.0, newline-delimited): initialize, tools/list,
tools/call. Its one tool, ask_local, routes a prompt through the Module 5 router
and, on a local decision, calls the Module 3 ollama_client. The production path
uses the official `mcp` SDK; this stdlib server is the readable, testable version.

Usage:
  python mcp_server.py             # run as an MCP stdio server (Claude Code launches this)
  python mcp_server.py --selftest  # offline: assert the JSON-RPC dispatch for the 3 core methods
"""

import argparse
import json
import sys

PROTOCOL_VERSION = "2025-11-25"
SERVER_INFO = {"name": "local-rig", "version": "1.0.0"}

ASK_LOCAL_TOOL = {
    "name": "ask_local",
    "description": "Delegate a prompt to the local inference rig (routed local vs cloud by policy).",
    "inputSchema": {
        "type": "object",
        "properties": {"prompt": {"type": "string", "description": "the prompt to delegate"}},
        "required": ["prompt"],
    },
}


def default_responder(prompt):
    """Live path: route the prompt, and on a local decision call the Module 3 client."""
    try:
        from route import route, Request, LOCAL_MODEL
    except ImportError:
        return "router unavailable: put route.py (Module 5) on the path"
    decision = route(Request(prompt_tokens=max(1, len(prompt) // 4)))
    if decision.target == "local":
        try:
            from ollama_client import call
            return call(prompt, model=LOCAL_MODEL)
        except Exception:
            return f"[routed local: {decision.reason}] local server unreachable"
    return f"[routed cloud: {decision.reason}] wire your cloud provider here"


def result(request_id, payload):
    return {"jsonrpc": "2.0", "id": request_id, "result": payload}


def error(request_id, code, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def dispatch(message, responder=default_responder):
    """Pure JSON-RPC dispatch: a message in, a response dict out (None for a notification)."""
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        return result(request_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
        })
    if method == "notifications/initialized":
        return None  # notification: no response
    if method == "tools/list":
        return result(request_id, {"tools": [ASK_LOCAL_TOOL]})
    if method == "tools/call":
        params = message.get("params", {})
        if params.get("name") != "ask_local":
            return error(request_id, -32602, f"unknown tool: {params.get('name')}")
        prompt = params.get("arguments", {}).get("prompt", "")
        if not prompt:
            return error(request_id, -32602, "ask_local requires a 'prompt' argument")
        text = responder(prompt)
        return result(request_id, {"content": [{"type": "text", "text": text}], "isError": False})
    return error(request_id, -32601, f"method not found: {method}")


def serve(stdin=sys.stdin, stdout=sys.stdout):
    """Read newline-delimited JSON-RPC from stdin, write responses to stdout."""
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        message = json.loads(line)
        response = dispatch(message)
        if response is not None:
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()


def selftest():
    """Assert the dispatch for the three core methods offline, with a fake responder."""
    init = dispatch({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert init["result"]["protocolVersion"] == PROTOCOL_VERSION, "initialize protocolVersion wrong"
    assert init["result"]["serverInfo"]["name"] == "local-rig", "serverInfo missing"

    note = dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert note is None, "a notification must not produce a response"

    listed = dispatch({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = [tool["name"] for tool in listed["result"]["tools"]]
    assert "ask_local" in names, "ask_local not advertised by tools/list"

    called = dispatch(
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "ask_local", "arguments": {"prompt": "hello"}}},
        responder=lambda prompt: f"echo: {prompt}",
    )
    content = called["result"]["content"]
    assert content[0]["type"] == "text" and content[0]["text"] == "echo: hello", "tools/call result shape wrong"

    missing = dispatch(
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "ask_local", "arguments": {}}}
    )
    assert "error" in missing, "a tools/call with no prompt should return an error"

    print("selftest passed: initialize, tools/list, tools/call dispatch correctly")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Minimal MCP stdio server for the local rig.")
    parser.add_argument("--selftest", action="store_true", help="assert the JSON-RPC dispatch offline")
    args = parser.parse_args()
    if args.selftest:
        sys.exit(selftest())
    serve()


if __name__ == "__main__":
    main()
```

Walk the pieces before you pipe anything through them.

`PROTOCOL_VERSION` and `SERVER_INFO` are constants at the top. The version string `2025-11-25`
must match what the client sends in `initialize`; mismatches surface as capability negotiation
failures, not clean errors. `SERVER_INFO` is what Claude Code shows in its tool list.

`ASK_LOCAL_TOOL` is a plain dict that gets serialized into the `tools/list` response. The
`inputSchema` is standard JSON Schema: Claude Code reads the `required` array to know the field
is not optional, and reads the property type to know how to fill it. A tool description that says
what the tool does (not what it is) is the difference between Claude picking it and Claude ignoring
it.

`default_responder` defers its imports. The `from route import ...` line inside the function body
means `--selftest` works even when `route.py` is absent: the import is never reached. The same
pattern protects `ollama_client`. The live path fails loudly and descriptively; the test path does
not fail at all.

`dispatch` is a flat if-chain, not a registry. Four branches: `initialize`, the notification,
`tools/list`, `tools/call`. An unknown method falls through to the final `error` return. The
`responder` argument is the injection point that makes the selftest possible: pass a lambda in
tests, leave it defaulted in production.

`selftest` covers five cases. The `initialize` check verifies both the protocol version and the
server name. The notification check verifies `None`. The `tools/list` check verifies `ask_local`
is advertised. The `tools/call` check with a fake responder verifies the content array shape. The
missing-prompt check verifies that a bad call returns an error, not a crash.

## Run It

With no rig and no key, run the selftest:

```bash
python mcp_server.py --selftest
```

What you should see:

```
selftest passed: initialize, tools/list, tools/call dispatch correctly
```

To confirm the wire format by hand, pipe a real handshake through the serve loop. Run the server
in one terminal and send messages from another, or pipe a file of newline-delimited messages
directly:

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","method":"notifications/initialized"}\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n' | python mcp_server.py
```

What you should see (formatted for readability; the server writes each on one line):

```json
{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-11-25", "capabilities": {"tools": {}}, "serverInfo": {"name": "local-rig", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "ask_local", "description": "Delegate a prompt to the local inference rig (routed local vs cloud by policy).", "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string", "description": "the prompt to delegate"}}, "required": ["prompt"]}}]}}
```

Notice: the `notifications/initialized` message produces no line in the output. That silence is
correct. One request in, one response out; one notification in, nothing out.

The next lesson registers `mcp_server.py` with Claude Code and logs a live delegation session,
closing the loop from silicon to AI assistant.

## Core Concepts

- The pure `dispatch` function is testable offline: a message in, a response dict or `None` out,
  with no network calls, so `--selftest` runs anywhere with no rig.
- `ask_local` wraps the entire prior stack: the router decides local vs cloud, the Module 3 client
  handles the local call, and the fallback strings keep the server alive when either is absent.
- The stdio loop is newline-delimited JSON with a flush after every write; without the flush, the
  client's handshake hangs silently.
- Notifications carry no `id` and must not receive a response; sending one anyway is the most
  common cause of a hanging MCP session.

<div class="claude-handoff" data-exercise="exercises/module6/build-the-mcp-server/">

**Build It in Claude Code**: Create `exercises/module6/build-the-mcp-server/mcp_server.py`, a stdlib MCP stdio server whose pure `dispatch()` answers initialize/tools/list/tools/call and whose `ask_local` tool wraps your Module 5 `route.py`, with a `--selftest` mode that asserts the dispatch offline.

</div>

<!-- SOURCES: https://modelcontextprotocol.io/specification/2025-11-25/server/tools | https://modelcontextprotocol.io/specification/2025-11-25/basic -->
