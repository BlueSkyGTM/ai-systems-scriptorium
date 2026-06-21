# Exercise: Record the Baseline

**Goal:** Complete the module-4 throughline by creating `LATENCY.md` with bench.py output for
an on-card model and a split model, then shipping `check_latency.py` beside it. The validator
exits 0 only when both sections are present, every field is filled, and every row's TTFT and
Tokens/sec are real positive numbers.

**Why:** `HARDWARE.md` documented the metal. `SETUP.md` documented the runtime. `MODELS.md`
documented the stack. `LATENCY.md` completes the performance record, but only once it holds
real measurements the validator can stand behind. A file with a zero in the Tokens/sec column
is not a baseline; it is a gap with a table around it.

**Note for readers without hardware yet:** Run `bench.py` and paste your real output when you
have the rig. For now, use the representative figures from the lesson. The validator checks
completeness and that the numbers are real and positive, not their exact values; it passes
against the reference build.

---

## Files You Are Editing

Both files live at the throughline location for this exercise:

```
exercises/module4/record-the-baseline/LATENCY.md        <- create and fill here
exercises/module4/record-the-baseline/check_latency.py  <- create the validator here
```

Do not move or rename either file. Module 7 reads `LATENCY.md` from this path to anchor every
tuning decision; later modules assume this location is stable.

---

## Step 1: Create LATENCY.md

Create `exercises/module4/record-the-baseline/LATENCY.md` with this complete file. Fill in
your real `bench.py` numbers if you have the rig; paste the representative figures below if not:

```markdown
# Latency Baseline

Measured latency for each model on the rig, captured with bench.py. Read by check_latency.py.

## Test Conditions

Prompt: write a haiku about latency
Hardware: RTX 4060 Ti 16GB + 64GB DDR5-6000

## Measurements

| Model | Quantization | Split | TTFT (ms) | Tokens/sec |
|-------|--------------|-------|-----------|------------|
| qwen2.5-coder:14b | Q4_K_M | 100% GPU | 210.0 | 32.0 |
| qwen2.5-coder:32b | Q4_K_M | 52% GPU / 48% CPU | 1100.0 | 3.0 |
```

Fill in:

- **Prompt:** the exact string you passed to `bench.py` for both runs.
- **Hardware:** your GPU and RAM (e.g., `RTX 4060 Ti 16GB + 64GB DDR5-6000`).
- **Each row:** model tag, quantization, split percentage from `ollama ps`, TTFT in ms, and
  Tokens/sec, all from `bench.py` output.

---

## Step 2: Ship check_latency.py

Create `exercises/module4/record-the-baseline/check_latency.py` with this complete validator:

```python
#!/usr/bin/env python3
"""
check_latency.py: validate LATENCY.md for the Local Metal module-4 throughline.

Usage: python check_latency.py [path/to/LATENCY.md]
Exits 0 when the baseline is complete with real positive measurements; exits 1
and names the first gap found.
"""

import re
import sys
from pathlib import Path

LATENCY_PATH = Path(__file__).parent / "LATENCY.md"

REQUIRED_SECTIONS = ["## Test Conditions", "## Measurements"]
CONDITION_FIELDS = ["Prompt", "Hardware"]

PLACEHOLDERS = {"TODO", "TBD", "xxx", "fill in", "<", ">", "..."}


def fail(message: str) -> None:
    print(f"LATENCY.md incomplete: {message}")
    sys.exit(1)


def load(path: Path) -> str:
    if not path.exists():
        fail(f"{path} not found")
    return path.read_text(encoding="utf-8")


def check_sections(text: str) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f'section "{section}" missing from LATENCY.md')


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


def parse_number(cell: str):
    """Extract a leading float from a table cell like '210.0' or '42.0 tok/s'."""
    match = re.search(r"([\d.]+)", cell)
    if not match:
        return None
    return float(match.group(1))


def check_measurements(section_text: str) -> None:
    rows = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if any("---" in c for c in cells):
            continue  # separator row
        if "Model" in cells and "Tokens/sec" in cells:
            continue  # header row
        rows.append(cells)
    if not rows:
        fail('"## Measurements" has no rows; benchmark at least one model with bench.py')
    for cells in rows:
        if len(cells) < 5:
            fail(f'row "{" | ".join(cells)}" is missing columns '
                 "(need Model, Quantization, Split, TTFT (ms), Tokens/sec)")
        if any(not c for c in cells[:5]):
            fail(f'row "{" | ".join(cells)}" has an empty cell; fill every column')
        ttft = parse_number(cells[3])
        toks = parse_number(cells[4])
        if ttft is None or toks is None:
            fail(f'row "{cells[0]}" has a non-numeric TTFT or Tokens/sec; use figures like "210.0"')
        if toks <= 0:
            fail(f'model "{cells[0]}" has Tokens/sec {toks}; a real measurement is greater than 0')
        if ttft <= 0:
            fail(f'model "{cells[0]}" has TTFT {ttft}; a real measurement is greater than 0')


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else LATENCY_PATH
    text = load(path)
    check_sections(text)
    check_no_placeholders(text)
    check_fields(extract_section(text, "## Test Conditions"), CONDITION_FIELDS, "## Test Conditions")
    check_measurements(extract_section(text, "## Measurements"))
    print("LATENCY.md complete")
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
python exercises/module4/record-the-baseline/check_latency.py
```

- Exits 0 and prints `LATENCY.md complete` when both sections are present, every field is filled,
  and every measurement row has a positive TTFT and Tokens/sec.
- Exits 1 and names the first gap when anything is missing, empty, or not a real positive number.

Test both paths. First: run it against your completed `LATENCY.md` and confirm exit 0. Then:
temporarily set one row's Tokens/sec to `0` and run the validator again. Confirm it exits 1 and
names the offending model. Restore the original value before continuing.

---

## Stretch

Add a commented-out idea to `check_latency.py`: a function that asserts the on-card model is at
least some factor N faster than the split model in Tokens/sec. Write the function signature and a
docstring describing the invariant, then leave the body stubbed and the call in `main()` commented
out. This is the kind of regression check a performance SLO runs in CI: not just "both models
returned measurements" but "the on-card model is still meaningfully faster than the split one."
