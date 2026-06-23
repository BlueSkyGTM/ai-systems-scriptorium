# Register with Claude Code

The server runs. Claude Code does not know that yet. This lesson fixes that: you tell Claude Code
where `mcp_server.py` lives, and it handles the rest.

## Step 1: Two Ways to Register

Claude Code discovers MCP servers from two sources: a CLI command and a project config file. Both
produce the same result; pick the one that fits your workflow.

The CLI registers the server immediately and writes the entry into your local project scope (private
to you, not committed):

```bash
claude mcp add --scope project local-rig -- python mcp_server.py
```

The `--` separates Claude Code's own flags from the command it will launch. Everything after `--` is
passed verbatim to the OS: `python mcp_server.py` is the process Claude Code starts when it opens the
server connection. If your Python binary is `python3`, or if `mcp_server.py` lives at a full path,
adjust those tokens accordingly.

The project config file `.mcp.json` at the repo root is the alternative. It travels with the
repository, so anyone who clones it sees the same server entry. Step 2 shows the file format.

Sources: [Claude Code MCP quickstart](https://code.claude.com/docs/en/mcp-quickstart) and
[Claude Code MCP docs](https://code.claude.com/docs/en/mcp)

## Step 2: The .mcp.json File

Create `.mcp.json` at your repo root with this content:

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

Note: `"args": ["mcp_server.py"]` with no directory prefix only resolves if Claude Code is
launched from the exercise directory (`exercises/module6/build-the-mcp-server/`). If you start
Claude Code from the repo root, use the relative or absolute path to the file instead, for
example `"args": ["exercises/module6/build-the-mcp-server/mcp_server.py"]`, to avoid a
`FileNotFoundError` on startup.

The schema is straightforward. `mcpServers` maps a name, here `local-rig`, to a server entry.
`type: "stdio"` tells Claude Code to use the local stdio transport: it launches the process,
writes JSON-RPC messages to its stdin, and reads responses from its stdout. `command` is the
executable; `args` is the argument list. Claude Code assembles these into a subprocess call and
speaks MCP over the resulting pipes.

## Step 3: Scopes

Claude Code has three MCP scopes, and the choice matters for a portfolio repository.

**local** is the default for `claude mcp add`. The entry is private to you in this project and is
not committed to version control. Use it for keys, secrets, or paths that should not travel.

**project** writes to `.mcp.json` at the repo root and is committed. Every collaborator, reviewer,
or recruiter who clones the repo sees the same entry. For a portfolio repository where the server is
part of the story you want to tell, project scope is the right choice.

**user** is also private, but it applies across all your projects, not just this one. Use it for
shared infrastructure you want available everywhere without repeating the config in each repo.

For this book's throughline, project scope fits: the `.mcp.json` entry is evidence that the rig is
integrated into your daily tooling, visible to anyone reading the repo.

## Step 4: What Claude Code Does with It

On startup, Claude Code reads `.mcp.json` and launches each listed server as a child process. It
then sends the MCP `initialize` handshake (the same one you traced in the previous lesson) and
follows with `tools/list` to discover what the server offers. For your server, that response
contains one entry: `ask_local`.

The first time Claude Code wants to call the tool mid-session, it asks you to approve it.
Project-scoped servers appear as pending in the `/mcp` panel until you accept. After approval,
`ask_local` is available for the rest of the session and across future sessions without further
prompting. The `/mcp` panel shows connection status at any time, so you can confirm the server is
up before you try to use it.

Source: [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)

---

The rig is now a first-class citizen of your editor. The next lesson puts that to use: you will run
a real session, log the delegation in `DELEGATION.md`, and close the throughline that started in
Module 3.

## Core Concepts

- Two registration paths exist: `claude mcp add --scope project local-rig -- python mcp_server.py`
  (CLI, immediate) and a `.mcp.json` file at the repo root (config, committed); both produce the
  same server entry.
- The `.mcp.json` schema maps a server name to a `type`, `command`, and `args`; `type: "stdio"`
  tells Claude Code to run the process and speak MCP over its stdin and stdout pipes.
- Three scopes control visibility: local (private to this project), project (committed to the repo,
  travels with it), and user (private, available across all projects); project scope is the right
  choice for a portfolio repository where the integration is part of the record.
- Claude Code discovers tools by calling `tools/list` after the initialize handshake; it asks you
  to approve a project-scoped server before the first `tools/call`, and the `/mcp` panel shows live
  connection status.

<div class="claude-handoff" data-exercise="exercises/module6/register-with-claude-code/">

**Build It in Claude Code**: Create a `.mcp.json` that registers your `mcp_server.py` as a project-scoped stdio MCP server named `local-rig`, or run `claude mcp add --scope project local-rig -- python mcp_server.py`; then confirm Claude Code lists the server.

</div>

<!-- SOURCES: https://code.claude.com/docs/en/mcp-quickstart | https://code.claude.com/docs/en/mcp | https://modelcontextprotocol.io/specification/2025-11-25/server/tools -->
