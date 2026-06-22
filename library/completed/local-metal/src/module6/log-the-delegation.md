# Log the Delegation

The server is registered. Now use it, and record the proof. A `DELEGATION.md` sitting in the
repository is what turns six modules of metal, runtime, and routing into a portfolio that a
reviewer can actually run.

## Step 1: Run a Delegation

Open a Claude Code session with the local-rig server registered. Ask it to delegate a routine task to
the local model. Claude Code will surface an approval prompt showing it intends to call `ask_local`;
approve it, and let the call go through.

What to capture before you close the session:

- The exact prompt you sent.
- The route the request took (did the router send it local or cloud, and why?).
- The model tag that answered.
- The reply the model returned.

These four pieces are what `DELEGATION.md` records.

## Step 2: Record DELEGATION.md

Create `exercises/module6/log-the-delegation/DELEGATION.md`. The complete file, shown wrapped in a
four-backtick outer fence so the inner triple-backtick reply block renders:

````markdown
# Delegation Log

A session where Claude Code delegated work to the local rig through the MCP server.
Read by check_delegation.py.

## Setup

MCP server: local-rig (mcp_server.py)
Registered via: .mcp.json (project scope)
Tool exposed: ask_local

## Session

Prompt: reformat this loop into a list comprehension
Route: local (routine request fits the local window and is cost-sensitive)
Model: qwen2.5-coder:14b

```
Rewritten as a list comprehension:

    return [row.strip() for row in lines if row]
```
````

The `Route` line is a real decision, not a label. Start it with `local` or `cloud` and say why: the
router's logic belongs in the record because that is the claim the validator enforces.

## Step 3: Ship the Validator

Create `exercises/module6/log-the-delegation/check_delegation.py` beside `DELEGATION.md`.

What it enforces, in order:

- Both sections present (`## Setup` and `## Session`).
- Setup fields filled: `MCP server` and `Tool exposed`.
- Session fields filled: `Prompt`, `Route`, and `Model`.
- No placeholder tokens (including angle brackets, `TODO`, `TBD`, ellipses).
- The `Route` value is a real routing decision: it must start with `local` or `cloud`.
- A non-empty fenced reply block in `## Session` (at least ten characters).

The `[^\S\n]` regex detail (horizontal whitespace only, same as the M2-M5 validators) keeps a blank
field from grabbing the next line's value and falsely passing the check.

The complete validator:

```python
#!/usr/bin/env python3
"""
check_delegation.py: validate DELEGATION.md for the Local Metal module-6 throughline.

Usage: python check_delegation.py [path/to/DELEGATION.md]
Exits 0 when the delegation log is complete (setup, a routed session, and a
captured reply); exits 1 and names the first gap found.
"""

import re
import sys
from pathlib import Path

DELEGATION_PATH = Path(__file__).parent / "DELEGATION.md"

REQUIRED_SECTIONS = ["## Setup", "## Session"]
SETUP_FIELDS = ["MCP server", "Tool exposed"]
SESSION_FIELDS = ["Prompt", "Route", "Model"]

PLACEHOLDERS = {"TODO", "TBD", "xxx", "fill in", "<", ">", "..."}


def fail(message: str) -> None:
    print(f"DELEGATION.md incomplete: {message}")
    sys.exit(1)


def load(path: Path) -> str:
    if not path.exists():
        fail(f"{path} not found")
    return path.read_text(encoding="utf-8")


def check_sections(text: str) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f'section "{section}" missing from DELEGATION.md')


def check_no_placeholders(text: str) -> None:
    for token in PLACEHOLDERS:
        if token in text:
            fail(f'placeholder token "{token}" still present; fill in the real value')


def extract_section(text: str, heading: str) -> str:
    match = re.search(rf"{re.escape(heading)}\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        fail(f'"{heading}" section has no content')
    return match.group(1)


def check_fields(section_text: str, fields: list, section_name: str) -> None:
    for field in fields:
        # [^\S\n] is horizontal whitespace only: it must not span the newline,
        # or a blank field would capture the next line's value.
        match = re.search(rf"{re.escape(field)}[^\S\n]*:[^\S\n]*([^\n]+)", section_text)
        if not match:
            fail(f'field "{field}" not found in {section_name}')
        if not match.group(1).strip():
            fail(f'field "{field}" in {section_name} is empty')


def check_route_decision(section_text: str) -> None:
    match = re.search(r"Route[^\S\n]*:[^\S\n]*([^\n]+)", section_text)
    if not match:
        fail('field "Route" not found in ## Session')
    value = match.group(1).strip().lower()
    if not (value.startswith("local") or value.startswith("cloud")):
        fail(f'Route must be a real decision starting with "local" or "cloud"; got "{match.group(1).strip()}"')


def check_reply_block(section_text: str) -> None:
    blocks = re.findall(r"```[^\n]*\n(.*?)```", section_text, re.DOTALL)
    if not blocks:
        fail('"## Session" has no fenced reply block; paste the ask_local reply in a ``` block')
    if not any(len(block.strip()) >= 10 for block in blocks):
        fail('the fenced reply block in "## Session" is empty; paste the model reply')


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DELEGATION_PATH
    text = load(path)
    check_sections(text)
    check_no_placeholders(text)
    check_fields(extract_section(text, "## Setup"), SETUP_FIELDS, "## Setup")
    session = extract_section(text, "## Session")
    check_fields(session, SESSION_FIELDS, "## Session")
    check_route_decision(session)
    check_reply_block(session)
    print("DELEGATION.md complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

## Step 4: The Live-vs-Expected Rule

With the rig and Claude Code, run a real session and log what actually happened. Without them, paste
the reference session from Step 2. The validator checks that the log is complete and well-formed: a
real routing decision, a real reply. It does not compare your text to the reference, so either path
exits 0 when the record is honest.

Six portfolio files now describe the metal, the runtime, the stack, its speed, the routing policy,
and the bridge into Claude Code. The runnable spine reads end to end: `ollama_client.py` calls the
model, `route.py` decides when to, `mcp_server.py` lets Claude Code pull the lever, and
`DELEGATION.md` is the receipt that proves it happened. The spine is the artifact a reviewer traces;
Module 7 makes it faster.

## Core Concepts

- The delegation log is the end-to-end proof: a `DELEGATION.md` with a real route and a real reply
  shows the whole stack firing in sequence, not just each piece in isolation.
- The validator gates a real routing decision: `Route` must start with `local` or `cloud` because
  a vague label is not evidence and a passing check on a label is not a gate.
- The six-file portfolio tells a complete story: hardware, runtime, model stack, benchmark, routing
  policy, and the Claude Code bridge cover every layer from the card to the tool.
- The compounding spine is the artifact a reviewer traces: `ollama_client.py` -> `route.py` ->
  `mcp_server.py` is a chain any interviewer can clone and run, and `DELEGATION.md` is the logged
  proof it ran.

<div class="claude-handoff" data-exercise="exercises/module6/log-the-delegation/">

**Build It in Claude Code**: Record a real delegation in `exercises/module6/log-the-delegation/DELEGATION.md` (the prompt, the route it took, the model, and the reply), then create `check_delegation.py` beside it so it exits 0 only when the log has both sections filled, a real local-or-cloud route, and a non-empty reply.

</div>

<!-- SOURCES: https://code.claude.com/docs/en/mcp -->
