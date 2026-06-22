# Exercise: Record the Policy

**Goal:** Complete the module-5 throughline by shipping `check_routing.py` beside the
`ROUTING.md` you created in the signals-and-thresholds exercise. The validator exits 0 only when
all three sections are present, the Signals table has at least three complete rows, the Targets
section names a local and a cloud model, and the Policy section holds a real written policy.

**Why:** `HARDWARE.md` documented the metal. `SETUP.md` documented the runtime. `MODELS.md`
documented the stack. `LATENCY.md` documented its speed. `ROUTING.md` documents the decision
layer, but only once a validator can stand behind it. A policy file with a stub in the Policy
section or two signals in the table is not a checked artifact; it is a draft with a passing
resemblance to one.

---

## Files You Are Editing

Both files live at the throughline location for this module's signals exercise:

```
exercises/module5/signals-and-thresholds/ROUTING.md        <- confirm and keep; Module 6 reads from here
exercises/module5/signals-and-thresholds/check_routing.py  <- create the validator here
```

Do not move or rename either file. Module 6 reads `ROUTING.md` from this path to drive the
Claude Code wiring; later modules assume this location is stable.

---

## Step 1: Confirm ROUTING.md

Open `exercises/module5/signals-and-thresholds/ROUTING.md` and confirm it matches the reference
exactly. If you edited it during the signals-and-thresholds exercise, update it now. The
complete file:

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

If you are tuning the thresholds to your own card, keep the structure intact: the validator checks
the three-section contract and that every signal row is complete, not the exact numbers.

---

## Step 2: Ship check_routing.py

Create `exercises/module5/signals-and-thresholds/check_routing.py` with this complete validator:

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

`[^\S\n]` matches horizontal whitespace only (spaces and tabs), not newlines. A `field:` line
with nothing after the colon correctly fails the non-empty check because the pattern cannot reach
the next line's content.

---

## Done When

Run from any directory (the script resolves paths relative to itself):

```bash
python exercises/module5/signals-and-thresholds/check_routing.py
```

- Exits 0 and prints `ROUTING.md complete` when all three sections are present, the Signals table
  has at least three complete rows, the Targets name a local and a cloud model, and the Policy
  section holds at least 40 characters of real policy text.
- Exits 1 and names the first gap when anything is missing, empty, or still a stub.

Test both paths. First: run it against your completed `ROUTING.md` and confirm exit 0. Then:
temporarily delete a signal row so only two remain and run the validator again. Confirm it exits 1
and names the shortfall. Restore the row before continuing.

---

## Stretch

Add a commented-out idea to `check_routing.py`: a function that asserts the local and cloud
targets are different model names. Write the function signature and a docstring describing the
invariant, then leave the body stubbed and the call in `main()` commented out. This is the kind
of sanity check that catches a misconfigured policy where someone accidentally set both targets to
the same model, making the routing logic meaningless.
