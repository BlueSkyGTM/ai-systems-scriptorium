# Exercise: Log the Delegation

**Goal:** Record a real Claude Code delegation session in `DELEGATION.md` and gate it with
`check_delegation.py`. The validator exits 0 only when both sections are filled, the Route is a
real local-or-cloud routing decision, and the Session block holds a non-empty model reply.

**Why:** Five modules of metal, runtime, and routing have no weight without a record of the whole
stack firing. `DELEGATION.md` is that record: the prompt, the route the router chose, the model
that answered, and the reply it gave. With a passing `check_delegation.py` beside it, the record
becomes a portfolio artifact, not just a note.

**Note for readers without hardware yet:** Run a live Claude Code session and capture your real
delegation when you have the rig registered. For now, paste the reference session from the lesson.
The validator checks that the log is complete and the routing decision is real; it does not compare
your text to the reference, so it passes against the reference build.

---

## Files You Are Editing

Both files live at:

```
exercises/module6/log-the-delegation/DELEGATION.md       <- create the delegation log here
exercises/module6/log-the-delegation/check_delegation.py <- create the validator here
```

Do not move or rename either file. The validator resolves `DELEGATION.md` relative to itself;
later exercises assume these locations are stable.

---

## Step 1: Create DELEGATION.md

Create `exercises/module6/log-the-delegation/DELEGATION.md`. The complete file is shown below,
wrapped in a four-backtick outer fence so the inner triple-backtick reply block renders correctly:

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

Fill in:

- **Prompt:** the exact string you sent to Claude Code.
- **Route:** a real routing decision starting with `local` or `cloud`, with a reason (e.g., `local
  (routine request fits the local window and is cost-sensitive)`).
- **Model:** the model tag that handled the request.
- **The fenced block:** your real reply if you have the rig; the reference reply above if not.

If you have the rig, run a live session and capture exactly what happened. The log is more useful
when it is yours.

---

## Step 2: Ship check_delegation.py

Create `exercises/module6/log-the-delegation/check_delegation.py` with this complete validator:

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

`[^\S\n]` matches horizontal whitespace only (spaces and tabs), not newlines. A `Route:` line with
nothing after the colon correctly fails the non-empty check because the pattern cannot reach the
next line's content.

---

## Done When

Run from any directory (the script resolves paths relative to itself):

```bash
python exercises/module6/log-the-delegation/check_delegation.py
```

- Exits 0 and prints `DELEGATION.md complete` when both sections are present, every field is
  filled, the Route starts with `local` or `cloud`, and the Session block holds a non-empty reply.
- Exits 1 and names the first gap when anything is missing or incomplete.

Test both paths. First: run it against your completed `DELEGATION.md` and confirm exit 0. Then:
temporarily change the `Route` line to something that does not start with `local` or `cloud` (for
example, `Route: maybe`) and run it again. Confirm it exits 1 and names the bad route value.
Restore the original value before continuing.

---

## Stretch

Add a commented-out idea to `check_delegation.py`: assert that the logged `Model` field matches
the local model named in `ROUTING.md`, making the delegation log and the routing policy cross-check
each other. Write the function signature and a docstring describing the invariant, then leave the
body stubbed and the call in `main()` commented out. This is the kind of cross-file consistency
check that turns two separate records into a single coherent system claim.
