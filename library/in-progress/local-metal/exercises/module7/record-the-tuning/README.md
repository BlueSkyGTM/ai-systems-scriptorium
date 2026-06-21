# Exercise: Record the Tuning

**Goal:** Complete the module-7 throughline by creating `TUNING.md` with the before-and-after aggregate throughput from `loadbench.py`, then shipping `check_tuning.py` beside it. The validator exits 0 only when all three sections are present, every field is filled, the levers table has at least one complete row, and the tuned aggregate tok/s is at least the baseline.

**Why:** `LATENCY.md` from Module 4 is the comparison point. Every lever you pulled in this module is meaningful only when measured against that starting number. A tuning record without a baseline is a claim; this file makes it a measurement. It is the seventh and final portfolio artifact, and the last thing the book asks you to write.

**Note for readers without hardware yet:** Run `loadbench.py` and paste your real output when you have the rig. For now, use the representative figures from the lesson. The validator checks completeness and that the tuned number is at least the baseline, not the exact values; it passes against the reference build.

---

## Files You Are Editing

Both files live at the throughline location for this exercise:

```
exercises/module7/record-the-tuning/TUNING.md        <- create and fill here
exercises/module7/record-the-tuning/check_tuning.py  <- create the validator here
```

Do not move or rename either file.

---

## Step 1: Create TUNING.md

Create `exercises/module7/record-the-tuning/TUNING.md` with the complete file below. Fill in your real `loadbench.py` figures if you have the rig; paste the representative figures if not:

```markdown
# Tuning Record

Before and after tuning the serving stack, with the levers applied. Read by check_tuning.py.

## Baseline

Aggregate tok/s: 30.0
Source: Module 4 LATENCY.md (single stream, stock settings)

## Tuned

Aggregate tok/s: 64.0
Levers: OLLAMA_NUM_PARALLEL=4, OLLAMA_FLASH_ATTENTION=1, OLLAMA_KV_CACHE_TYPE=q8_0

## Levers Applied

| Lever | Setting | What It Moved |
|-------|---------|---------------|
| OLLAMA_NUM_PARALLEL | 4 | aggregate throughput under load, 30 to 64 tok/s |
| OLLAMA_FLASH_ATTENTION | 1 | modest single-stream speedup, lower attention memory |
| OLLAMA_KV_CACHE_TYPE | q8_0 | smaller KV cache, room for a larger context window |
```

Fill in:

- **Baseline Aggregate tok/s:** the single-stream tok/s from `LATENCY.md` (Module 4).
- **Source:** where the baseline came from (e.g., `Module 4 LATENCY.md (single stream, stock settings)`).
- **Tuned Aggregate tok/s:** the aggregate tok/s from `loadbench.py` after setting the levers.
- **Levers:** the environment variables you set (comma-separated).
- **Each table row:** the lever name, the setting you used, and what number it moved.

---

## Step 2: Ship check_tuning.py

Create `exercises/module7/record-the-tuning/check_tuning.py` with this complete validator:

```python
#!/usr/bin/env python3
"""
check_tuning.py: validate TUNING.md for the Local Metal module-7 throughline.

Usage: python check_tuning.py [path/to/TUNING.md]
Exits 0 when the record is complete and the tuned throughput is at least the
baseline (a proven, non-regressing change); exits 1 and names the first gap.
"""

import re
import sys
from pathlib import Path

TUNING_PATH = Path(__file__).parent / "TUNING.md"

REQUIRED_SECTIONS = ["## Baseline", "## Tuned", "## Levers Applied"]
BASELINE_FIELDS = ["Aggregate tok/s", "Source"]
TUNED_FIELDS = ["Aggregate tok/s", "Levers"]

PLACEHOLDERS = {"TODO", "TBD", "xxx", "fill in", "<", ">", "..."}


def fail(message: str) -> None:
    print(f"TUNING.md incomplete: {message}")
    sys.exit(1)


def load(path: Path) -> str:
    if not path.exists():
        fail(f"{path} not found")
    return path.read_text(encoding="utf-8")


def check_sections(text: str) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f'section "{section}" missing from TUNING.md')


def check_no_placeholders(text: str) -> None:
    for token in PLACEHOLDERS:
        if token in text:
            fail(f'placeholder token "{token}" still present; fill in the real value')


def extract_section(text: str, heading: str) -> str:
    match = re.search(rf"{re.escape(heading)}\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not match:
        fail(f'"{heading}" section has no content')
    return match.group(1)


def field_value(section_text: str, field: str, section_name: str) -> str:
    # [^\S\n] is horizontal whitespace only: it must not span the newline,
    # or a blank field would capture the next line's value.
    match = re.search(rf"{re.escape(field)}[^\S\n]*:[^\S\n]*([^\n]+)", section_text)
    if not match:
        fail(f'field "{field}" not found in {section_name}')
    if not match.group(1).strip():
        fail(f'field "{field}" in {section_name} is empty')
    return match.group(1).strip()


def parse_number(value: str):
    match = re.search(r"([\d.]+)", value)
    return float(match.group(1)) if match else None


def check_levers_table(section_text: str) -> None:
    rows = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if any("---" in c for c in cells):
            continue  # separator row
        if "Lever" in cells and "Setting" in cells:
            continue  # header row
        rows.append(cells)
    if not rows:
        fail('"## Levers Applied" has no rows; record at least one lever you changed')
    for cells in rows:
        if len(cells) < 3 or any(not c for c in cells[:3]):
            fail(f'lever row "{" | ".join(cells)}" needs three filled columns (Lever, Setting, What It Moved)')


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else TUNING_PATH
    text = load(path)
    check_sections(text)
    check_no_placeholders(text)
    baseline = extract_section(text, "## Baseline")
    tuned = extract_section(text, "## Tuned")
    base_value = field_value(baseline, "Aggregate tok/s", "## Baseline")
    field_value(baseline, "Source", "## Baseline")
    tuned_value = field_value(tuned, "Aggregate tok/s", "## Tuned")
    field_value(tuned, "Levers", "## Tuned")
    check_levers_table(extract_section(text, "## Levers Applied"))

    base_tps = parse_number(base_value)
    tuned_tps = parse_number(tuned_value)
    if base_tps is None or tuned_tps is None:
        fail("Aggregate tok/s must be a number in both ## Baseline and ## Tuned")
    if tuned_tps < base_tps:
        fail(f"tuned throughput {tuned_tps} is below baseline {base_tps}; "
             "keep a lever only if it improved the number, then re-record")
    print("TUNING.md complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

`[^\S\n]` matches horizontal whitespace only (spaces and tabs), not newlines. A `field:` line with nothing after the colon correctly fails the non-empty check because the pattern cannot reach the next line's content.

---

## Done When

Run from any directory (the script resolves paths relative to itself):

```bash
python exercises/module7/record-the-tuning/check_tuning.py
```

- Exits 0 and prints `TUNING.md complete` when all three sections are present, every field is filled, the levers table has at least one complete row, and the tuned aggregate tok/s is at least the baseline.
- Exits 1 and names the first gap when anything is missing, empty, or when the tuned number is below the baseline.

Test both paths. First: run it against your completed `TUNING.md` and confirm exit 0. Then: temporarily set the tuned `Aggregate tok/s` below the baseline (for example, change it to `10.0`) and run the validator again. Confirm it exits 1 and names the regression. Restore the original value before continuing.

---

## Stretch

Add a commented-out idea to `check_tuning.py`: a check that asserts the tuned aggregate tok/s is at least 1.5x the baseline, a real performance target rather than mere non-regression. Write the check as a function with a docstring describing the invariant, leave the body implemented but the call in `main()` commented out. This is the shape of a performance SLO in CI: not just "the change did not regress" but "the change hit the target."
