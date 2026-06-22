# Exercise: Build the MCP Server

## Goal

Create `mcp_server.py`: a stdlib MCP stdio server that exposes the local rig to Claude Code via
a single tool, `ask_local`. Its pure `dispatch()` function handles the three core JSON-RPC methods
offline; the live path routes through the Module 5 router and calls the Module 3 client.

## Why

This is the bridge artifact. Once registered with Claude Code in the next lesson, `mcp_server.py`
is what Claude Code calls when it delegates to your rig. The entire stack you built, the model
runtime, the benchmark, the routing policy, runs behind this file. Without it, your rig is
unreachable from your daily tooling; with it, Claude Code can pull the lever mid-session.

## Files You Are Editing

`exercises/module6/build-the-mcp-server/mcp_server.py`

Do not move or rename this file. The next lesson's registration step points to this exact path.

## Steps

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

## Note

`--selftest` runs entirely offline with a fake responder: it imports nothing from your rig and
makes no network calls. The live path (serving real requests) needs `route.py` from Module 5 and
`ollama_client.py` from Module 3 on the Python path, plus the Ollama runtime running on your rig.
For this exercise, the selftest is sufficient.

## Done When

- `python mcp_server.py --selftest` exits 0 and prints the dispatch line.
- Piping a real `initialize`, `notifications/initialized`, `tools/list`, and `tools/call` over
  stdin returns valid JSON-RPC responses for the requests and silence for the notification.

## Expected Output Shape

Running the selftest:

```
selftest passed: initialize, tools/list, tools/call dispatch correctly
```

A representative `tools/list` response (the server writes it on one line; formatted here for
readability):

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
            "prompt": {"type": "string", "description": "the prompt to delegate"}
          },
          "required": ["prompt"]
        }
      }
    ]
  }
}
```

`result.tools[0].name` is `"ask_local"`. That is what Claude Code reads to discover the tool.

## Stretch

Add a second tool, `route_only`, that takes the same `prompt` argument but returns only the
routing decision string (e.g., `"local: routine request fits the local window and is
cost-sensitive"`) without calling the model. Advertise it in `tools/list` alongside `ask_local`
and handle it in the `tools/call` branch. This lets you test the router's decisions from inside
Claude Code without spending tokens on inference.
