# Record the Baseline

You measured latency in the last lesson. Now make it a record. The module closes the way Module 3
did: record what you have, then gate the record with a validator that will not let you move on
with a gap.

## Step 1: Run the Comparison

Run `bench.py` on two models, the 14B that fits entirely on-card and the 32B that splits onto
system RAM. Use the same prompt for both so the numbers compare cleanly:

```bash
python exercises/module4/measure-latency/bench.py "write a haiku about latency"
python exercises/module4/measure-latency/bench.py --model qwen2.5-coder:32b "write a haiku about latency"
```

Record both outputs before continuing. Representative results on the RTX 4060 Ti 16GB (label
representative; your numbers will differ by prompt and thermals):

| Model | Split | TTFT (ms) | Tokens/sec |
|-------|-------|-----------|------------|
| qwen2.5-coder:14b | 100% GPU | 210.0 | 32.0 |
| qwen2.5-coder:32b | 52% GPU / 48% CPU | 1100.0 | 3.0 |

The point lands itself: the bigger model is an order of magnitude slower once it spills. The 14B
answers at 32 tok/s with 210 ms before the first word. The 32B answers at 3 tok/s with over a
second of silence first. That is not a style difference; it is a constraint on what the model can
do in a live interaction.

## Step 2: The Complete LATENCY.md

Open `exercises/module4/record-the-baseline/LATENCY.md` and fill in both rows. The complete file:

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

Readers with the rig: paste your real `bench.py` output for each model. Readers pre-hardware: the
representative figures above satisfy every invariant the validator enforces.

## Step 3: Ship the Validator

Create `check_latency.py` in the same directory as `LATENCY.md`:
`exercises/module4/record-the-baseline/check_latency.py`.

Here is what it enforces, in order:

- Both sections present (`## Test Conditions`, `## Measurements`).
- Every key-value field filled: `Prompt` and `Hardware` in the test conditions.
- No placeholder tokens (`TODO`, `TBD`, `xxx`, angle brackets, ellipses).
- At least one measurement row with all five columns: Model, Quantization, Split, TTFT (ms),
  Tokens/sec. Every cell filled.
- The key gate: TTFT and Tokens/sec must be positive numbers. A zero or a blank is not a
  measurement; it is a placeholder. The validator names the offending model and exits 1.

The complete validator:

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

One regex detail worth knowing: `[^\S\n]` matches horizontal whitespace only (spaces and tabs). It
does not span the newline. A field line with nothing after the colon correctly fails the non-empty
check because the pattern cannot reach the next line's content.

## Step 4: The Live-vs-Expected Rule

The validator checks completeness and that every number is real and positive, not the exact values
themselves. That distinction matters: readers with the rig paste their real `bench.py` figures;
readers without it paste the representative figures from Step 1. Either way, the validator passes
as long as both sections are present, every field is filled, every row has five columns, and every
TTFT and Tokens/sec is a number greater than zero. The reference build satisfies all of it.

Run it to confirm:

```bash
python exercises/module4/record-the-baseline/check_latency.py
```

You should see `LATENCY.md complete` and exit 0. Then test the gate directly: temporarily set one
row's Tokens/sec to `0` and run the validator again. It exits 1 and names the offending model.
Restore the original value before continuing.

The gate is not a style check. A zero means the measurement never ran; a positive number means
it did. The validator holds that line because a baseline that contains a zero is not a baseline;
it is a placeholder that looks like one.

The rig now has a measured baseline: HARDWARE.md describes the metal, SETUP.md describes the
runtime, MODELS.md describes the stack, and LATENCY.md describes its speed. The four files together
are the performance record Module 7 tunes against; every optimization you make there is measured
against what is recorded here.

## Core Concepts

- A baseline is a comparison point you record before you tune: without it, an optimization is
  a claim; with it, it is a measurement.
- The positive-measurement gate is the real acceptance check: a Tokens/sec of zero means the
  benchmark never completed, and a validator that lets it through would let a gap masquerade as data.
- Tokens per second and TTFT are different axes: throughput tells you how fast a model generates;
  time to first token tells you how long the user waits before anything arrives.
- The fourth portfolio file completes the performance record: LATENCY.md joins HARDWARE.md,
  SETUP.md, and MODELS.md as a validator-backed artifact anyone reading the repo can trust.

<div class="claude-handoff" data-exercise="exercises/module4/record-the-baseline/">

**Build It in Claude Code**: Create `exercises/module4/record-the-baseline/LATENCY.md` with your bench.py numbers for an on-card model and a model that splits, then create `check_latency.py` beside it so it exits 0 only when both sections are complete and every row's TTFT and Tokens/sec are real positive numbers.

</div>

<!-- SOURCES: https://github.com/ollama/ollama/blob/main/docs/api.md | https://modelfit.io/gpu/rtx-4060-ti/ -->
