# Exercise: Record the Stack

**Goal:** Complete the module-3 throughline by adding the `## Sample Response` section to
`MODELS.md` and shipping `check_models.py` beside it. The validator exits 0 only when all three
sections are present, every field is filled, the model fits on-card, and the Sample Response block
holds a real reply.

**Why:** `HARDWARE.md` documented the metal. `SETUP.md` documented the runtime. `MODELS.md`
completes the stack record, but only once it carries a sample response that proves the model
answers. Without that section, the record is a configuration file; with it and a passing
`check_models.py`, it is a portfolio artifact a validator can stand behind.

**Note for readers without hardware yet:** Run `ollama_client.py` and capture your real reply when
you have the rig. For now, paste the reference reply from the lesson. The validator checks
completeness and the fits-on-card invariant, not live truth; it passes against the reference build.

---

## Files You Are Editing

Both files live at the throughline location established in the previous lesson:

```
exercises/module3/a-14b-model-on-card/MODELS.md        <- add ## Sample Response here
exercises/module3/a-14b-model-on-card/check_models.py  <- create the validator here
```

Do not move or rename either file. Module 5 reads `MODELS.md` from this path and `ollama_client.py`
sits beside it; later modules assume these locations are stable.

---

## Step 1: Add `## Sample Response` to MODELS.md

Open `exercises/module3/a-14b-model-on-card/MODELS.md`. After the `## Models` table, add the
following (shown wrapped in a four-backtick outer fence so the inner triple-backtick reply block
renders):

````markdown
## Sample Response

Prompt: explain a Python decorator in one sentence
Model: qwen2.5-coder:14b

```
A decorator is a function that takes another function and extends its behavior
without modifying the original function's source code.
```
````

Fill in:

- **Prompt:** the exact string you passed to `ollama_client.py`.
- **Model:** the model tag you ran (e.g., `qwen2.5-coder:14b`).
- **The fenced block:** your real reply if you have the rig; the reference reply above if not.

The complete finished `MODELS.md` (all three sections together) looks like this. Note: the
`## Sample Response` section contains a triple-backtick fenced block inside the file, shown here
wrapped in a four-backtick outer fence so it renders correctly:

````markdown
# Model Stack

The serving layer and the models on the rig, with their VRAM footprint. Read by check_models.py.

## Serving Layer

Ollama version: 0.30.10
Docker version: 27.3.1
Endpoint: http://localhost:11434

## Models

| Model | Quantization | Size on Disk | VRAM Used | VRAM Total |
|-------|--------------|--------------|-----------|------------|
| qwen2.5-coder:14b | Q4_K_M | 9.0 GB | 11.0 GB | 16.0 GB |

## Sample Response

Prompt: explain a Python decorator in one sentence
Model: qwen2.5-coder:14b

```
A decorator is a function that takes another function and extends its behavior
without modifying the original function's source code.
```
````

---

## Step 2: Finalize `check_models.py`

Create `exercises/module3/a-14b-model-on-card/check_models.py` with this complete final version:

```python
#!/usr/bin/env python3
"""
check_models.py: validate MODELS.md for the Local Metal module-3 throughline.

Usage: python check_models.py [path/to/MODELS.md]
Exits 0 when the record is complete and the model fits on-card; exits 1 and names
the first gap found.
"""

import re
import sys
from pathlib import Path

MODELS_PATH = Path(__file__).parent / "MODELS.md"

REQUIRED_SECTIONS = [
    "## Serving Layer",
    "## Models",
    "## Sample Response",
]

SERVING_FIELDS = ["Ollama version", "Docker version", "Endpoint"]
SAMPLE_FIELDS = ["Prompt", "Model"]

PLACEHOLDERS = {"TODO", "TBD", "xxx", "fill in", "<", ">", "..."}


def fail(message: str) -> None:
    print(f"MODELS.md incomplete: {message}")
    sys.exit(1)


def load(path: Path) -> str:
    if not path.exists():
        fail(f"{path} not found")
    return path.read_text(encoding="utf-8")


def check_sections(text: str) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f'section "{section}" missing from MODELS.md')


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


def parse_gb(cell: str):
    """Extract a float number of GB from a table cell like '10.8 GB'."""
    match = re.search(r"([\d.]+)", cell)
    if not match:
        return None
    return float(match.group(1))


def check_models_table(section_text: str) -> None:
    rows = []
    for line in section_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if any("---" in c for c in cells):
            continue  # separator row
        if "Model" in cells and "Quantization" in cells:
            continue  # header row
        rows.append(cells)
    if not rows:
        fail('"## Models" has no model rows; add at least one model to the table')
    for cells in rows:
        if len(cells) < 5:
            fail(f'model row "{" | ".join(cells)}" is missing columns '
                 "(need Model, Quantization, Size on Disk, VRAM Used, VRAM Total)")
        if any(not c for c in cells[:5]):
            fail(f'model row "{" | ".join(cells)}" has an empty cell; fill every column')
        used = parse_gb(cells[3])
        total = parse_gb(cells[4])
        if used is None or total is None:
            fail(f'model row "{cells[0]}" has a non-numeric VRAM value; use figures like "10.8 GB"')
        if used > total:
            fail(f'model "{cells[0]}" overflows VRAM: {used} GB used > {total} GB total. '
                 "Pick a smaller model or a tighter quantization so it fits on-card.")


def check_sample_response(section_text: str) -> None:
    blocks = re.findall(r"```[^\n]*\n(.*?)```", section_text, re.DOTALL)
    if not blocks:
        fail('"## Sample Response" has no fenced code block; paste the model reply in a ``` block')
    if not any(len(block.strip()) >= 10 for block in blocks):
        fail('the fenced block in "## Sample Response" is empty; paste a real model reply')


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else MODELS_PATH
    text = load(path)
    check_sections(text)
    check_no_placeholders(text)
    check_fields(extract_section(text, "## Serving Layer"), SERVING_FIELDS, "## Serving Layer")
    check_models_table(extract_section(text, "## Models"))
    sample = extract_section(text, "## Sample Response")
    check_fields(sample, SAMPLE_FIELDS, "## Sample Response")
    check_sample_response(sample)
    print("MODELS.md complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

`[^\S\n]` matches horizontal whitespace only (spaces and tabs), not newlines. A `field:` line with
nothing after the colon correctly fails the non-empty check because the pattern cannot reach the
next line's content.

---

## Done When

Run from any directory (the script resolves paths relative to itself):

```bash
python exercises/module3/a-14b-model-on-card/check_models.py
```

- Exits 0 and prints `MODELS.md complete` when every section is present, every field is filled, the
  model table has at least one complete row, and the Sample Response block holds a real reply.
- Exits 1 and names the first gap when anything is missing or incomplete.

Test both paths. First: run it against your completed `MODELS.md` and confirm exit 0. Then:
temporarily set VRAM Used above VRAM Total in the table (for example, change `11.0 GB` to
`17.0 GB`) and run it again. Confirm it exits 1 and names the overflowing model. Restore the
original value before continuing.

---

## Stretch

Add a commented-out `check_vram_headroom` idea to `check_models.py`. The function would assert that
VRAM Total minus VRAM Used is at or above a configurable threshold (say, 2.0 GB), flagging rows
where the model is packed so tightly that a longer context window would push it over. Write the
function signature and a docstring describing the invariant, then leave the body stubbed and the
call in `main()` commented out, the way `check_setup.py` handled the cross-field consistency check.
This is the kind of capacity headroom assertion a real serving SLO enforces: not just "fits on
card" but "fits on card with room to breathe."
