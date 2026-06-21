# Record the Policy

You wrote the policy and built the router. Now make the policy a checked artifact. The module
closes the way Modules 3 and 4 did: gate the record with a validator that will not let it go
stale, and the module's done-when is the validator passing.

## Step 1: The Complete ROUTING.md

Before running the validator, confirm your file matches the reference exactly. The lesson on
signals and thresholds created this file; this lesson does not change it. It only gates it.

The complete `exercises/module5/signals-and-thresholds/ROUTING.md`:

```markdown
# Routing Policy

How requests are routed between the local rig and the cloud. Read by check_routing.py.

## Signals

| Signal | Threshold | Routes To |
|--------|-----------|-----------|
| Context size | over 8192 tokens | cloud |
| Latency budget | under 2000 ms, fits local | local |
| Sensitivity | private / on-machine | local |
| Stakes | high-stakes one-off | cloud |

## Targets

Local model: qwen2.5-coder:14b (8K practical context)
Cloud model: claude (frontier, 1M-token context)

## Policy

Route to local when the request fits the local context window and is cost-sensitive,
latency-tolerant, or privacy-sensitive. Escalate to cloud when the context exceeds the local
window or the task is high-stakes and wants the best answer regardless of cost. Sensitive data
never leaves the machine.
```

Check your copy against this line by line before moving on. The validator is unforgiving about
missing sections and placeholder text.

## Step 2: Ship the Validator

Create `check_routing.py` beside `ROUTING.md` at
`exercises/module5/signals-and-thresholds/check_routing.py`.

Here is what it enforces, in order:

- All three sections present: `## Signals`, `## Targets`, `## Policy`.
- No placeholder tokens, including angle brackets. The thresholds are written with the words
  "over" and "under" rather than the `<` and `>` symbols precisely because the validator treats
  those symbols as unfilled placeholders. A policy with `< 2000 ms` in it would fail; "under 2000
  ms" passes.
- The Signals table has at least three rows, each with all three cells filled: Signal, Threshold,
  and Routes To.
- The Targets section names both a local model and a cloud model, each with a non-empty value on
  the same line as the field name.
- The Policy section holds a real written policy of at least 40 characters, not a stub.

The complete validator:

```python
#!/usr/bin/env python3
"""
check_routing.py: validate ROUTING.md for the Local Metal module-5 throughline.

Usage: python check_routing.py [path/to/ROUTING.md]
Exits 0 when the policy is complete (signals with thresholds, targets, a written
policy); exits 1 and names the first gap found.
"""

import re
import sys
from pathlib import Path

ROUTING_PATH = Path(__file__).parent / "ROUTING.md"

REQUIRED_SECTIONS = ["## Signals", "## Targets", "## Policy"]
TARGET_FIELDS = ["Local model", "Cloud model"]
MIN_SIGNALS = 3
MIN_POLICY_CHARS = 40

PLACEHOLDERS = {"TODO", "TBD", "xxx", "fill in", "<", ">", "..."}


def fail(message: str) -> None:
    print(f"ROUTING.md incomplete: {message}")
    sys.exit(1)


def load(path: Path) -> str:
    if not path.exists():
        fail(f"{path} not found")
    return path.read_text(encoding="utf-8")


def check_sections(text: str) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f'section "{section}" missing from ROUTING.md')


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


def check_signals_table(section_text: str) -> None:
    rows = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if any("---" in c for c in cells):
            continue  # separator row
        if "Signal" in cells and "Routes To" in cells:
            continue  # header row
        rows.append(cells)
    if len(rows) < MIN_SIGNALS:
        fail(f'"## Signals" needs at least {MIN_SIGNALS} signal rows; found {len(rows)}')
    for cells in rows:
        if len(cells) < 3:
            fail(f'signal row "{" | ".join(cells)}" needs three columns (Signal, Threshold, Routes To)')
        if any(not c for c in cells[:3]):
            fail(f'signal row "{" | ".join(cells)}" has an empty cell; every signal needs a threshold and a target')


def check_policy(section_text: str) -> None:
    if len(section_text.strip()) < MIN_POLICY_CHARS:
        fail("the \"## Policy\" section needs a written policy, not a stub")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROUTING_PATH
    text = load(path)
    check_sections(text)
    check_no_placeholders(text)
    check_signals_table(extract_section(text, "## Signals"))
    check_fields(extract_section(text, "## Targets"), TARGET_FIELDS, "## Targets")
    check_policy(extract_section(text, "## Policy"))
    print("ROUTING.md complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

One regex detail worth knowing: `[^\S\n]` matches horizontal whitespace only (spaces and tabs).
It does not span the newline. A field line with nothing after the colon correctly fails the
non-empty check because the pattern cannot reach the next line's content.

## Step 3: The Live-vs-Expected Rule

The validator checks that the policy is complete and well-formed, not that its thresholds are
"right" for your rig. The 8192-token context limit and the 2000 ms latency budget reflect the
reference card; tune them to your own hardware and keep the structure. What the validator holds
constant is the three-section contract: signals with thresholds, named targets, a written
rationale. It passes against the reference policy above.

Run it to confirm:

```bash
python exercises/module5/signals-and-thresholds/check_routing.py
```

You should see `ROUTING.md complete` and exit 0. Then test the gate: temporarily delete a signal
row so only two remain and run the validator again. It exits 1 and names the shortfall. Restore
the row before continuing.

Five portfolio files now describe the metal, the runtime, the stack, the speed, and the decision
layer. `route.py` is built and waiting. Module 6 wires it into Claude Code, and the delegation
starts happening without you thinking about it.

## Core Concepts

- A policy is a portfolio artifact only when a validator can confirm it is complete: the file
  alone is prose, the file plus the passing validator is a checked record.
- The three-section contract enforces structure: signals declare the triggers, targets name the
  endpoints, and the policy states the rationale in plain language.
- Thresholds are written with words rather than angle-bracket symbols because the validator treats
  `<` and `>` as unfilled placeholder tokens; a policy that uses the words "over" and "under"
  passes; one that uses the comparison symbols does not.
- The routing layer completes the hybrid system: local for what fits the window, is
  cost-sensitive, or is private; cloud for what exceeds it or demands the best answer regardless
  of cost.

<div class="claude-handoff" data-exercise="exercises/module5/record-the-policy/">

**Build It in Claude Code**: Create `check_routing.py` beside your `ROUTING.md` so it exits 0 only when all three sections are present, the Signals table has at least three complete rows, the Targets name a local and a cloud model, and the Policy section holds a real written policy.

</div>

<!-- SOURCES: https://docs.litellm.ai/docs/routing -->
