# Module 6: Wire to Claude Code

Five modules in, you have a rig that serves a model, a benchmark that proves what it costs, and a
router that decides when to use it. What you do not have is a reason to open any of it during a normal
workday. Infrastructure you have to remember to reach for is infrastructure you stop reaching for.
This module closes that gap by putting the rig inside the tool you already live in.

The mechanism is the Model Context Protocol. Claude Code is an MCP client: it can connect to small
servers that expose tools, discover what those tools do, and call them mid-session. You will build one
of those servers. It exposes a single tool, `ask_local`, and when Claude Code calls it, the request
runs through the router you built in Module 5, which sends it to the local model you built in Module 3.
Claude Code stays the driver; the rig becomes a place it can delegate to.

That delegation is the point. The routine, high-volume, privacy-sensitive work that does not need a
frontier model can go to the rig you already paid for, while Claude handles the rest. The decision is
the router's; your job in this module is to give Claude Code a clean way to ask.

The server is deliberately small and built from the standard library. The Model Context Protocol is
JSON-RPC 2.0 over stdio: a handful of methods, plain JSON in and out. You will implement the three
that matter, `initialize`, `tools/list`, and `tools/call`, with a dispatch function pure enough to
self-test offline, no editor and no rig required. The production path uses the official MCP SDK; the
stdlib server you build here is the one you can read end to end and prove correct.

You leave this module with a sixth file in the portfolio repository: `DELEGATION.md`, a logged session
of Claude Code handing real work to the local rig and getting an answer back. The metal, the runtime,
the stack, its speed, and the routing policy were documented across the first five modules; now the
bridge into your daily tooling is too. The runnable spine reads end to end: `ollama_client.py` calls
the model, `route.py` decides when to, and `mcp_server.py` lets Claude Code pull the lever. Module 7
is the last one: making all of it faster.
