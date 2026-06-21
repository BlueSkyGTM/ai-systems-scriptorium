# Exercise: Register with Claude Code

## Goal

Register `mcp_server.py` as a project-scoped stdio MCP server named `local-rig` so Claude Code
can discover and call `ask_local`.

## Why

Claude Code does not know your server exists until you tell it. This exercise produces the
registration artifact, either the `.mcp.json` file or the `claude mcp add` invocation, that
closes the gap between a running server and a usable tool.

## Files You Are Editing

- `.mcp.json` at your **repo root** (or the file in this exercise folder as the deliverable; see
  the Note below).

## Steps

**Option A: CLI registration**

Run this command from your repo root:

```bash
claude mcp add --scope project local-rig -- python mcp_server.py
```

Claude Code writes `.mcp.json` for you and registers the server immediately.

**Option B: Create .mcp.json by hand**

Create `.mcp.json` with this exact content:

```json
{
  "mcpServers": {
    "local-rig": {
      "type": "stdio",
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
```

In a real project this file lives at the **repo root**. The `args` path `mcp_server.py` assumes
`python` is invoked from the directory where `mcp_server.py` lives; adjust to a full absolute
path if you run Claude Code from a different working directory. This exercise folder is the
deliverable location; in production, move or recreate the file at the repo root.

## Note

You do not need the rig running to write the config. To actually test the connection, you need
`mcp_server.py` from the previous lesson and Claude Code installed. Writing the file first and
confirming the JSON is valid is a complete deliverable on its own.

## Done When

- `.mcp.json` is valid JSON containing an `mcpServers.local-rig` entry with `type: "stdio"`,
  `command: "python"`, and `args: ["mcp_server.py"]`.
- Running `claude mcp list` from the project root shows `local-rig`, or opening the `/mcp` panel
  in Claude Code lists the server.

## Stretch

Add an `env` block to the server entry to pass an environment variable to the process. For
example, a model override that `mcp_server.py` reads at startup:

```json
{
  "mcpServers": {
    "local-rig": {
      "type": "stdio",
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "LOCAL_MODEL": "llama3.2:3b"
      }
    }
  }
}
```

Update `mcp_server.py` to read `os.environ.get("LOCAL_MODEL", "llama3.2")` and route accordingly.
