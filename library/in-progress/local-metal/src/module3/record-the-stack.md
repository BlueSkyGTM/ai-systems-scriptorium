# Record the Stack

You have a model on the card and a client that calls it. The stack is real and nothing about it is
written down. This lesson closes Module 3 the same way Module 2 closed: record what you have, then
gate the record with a validator that will not let you move on with a gap.

## Step 1: Capture a Sample Response

Run the client you built in the last lesson:

```bash
python ollama_client.py "explain a Python decorator in one sentence"
```

Copy the reply. Open `exercises/module3/a-14b-model-on-card/MODELS.md` and add a `## Sample Response`
section after the `## Models` table. The section takes two key-value lines and the reply in a fenced
block.

What you should see, on the reference build (shown wrapped in a four-backtick outer fence so the
inner triple-backtick reply block renders):

````markdown
## Sample Response

Prompt: explain a Python decorator in one sentence
Model: qwen2.5-coder:14b

```
A decorator is a function that takes another function and extends its behavior
without modifying the original function's source code.
```
````

Fill in `Prompt:` with your exact prompt and `Model:` with the model tag you ran. If you have the
rig, paste your real reply; if not, paste the reference reply above.

## Step 2: The Complete MODELS.md

Here is the full file with all three sections. Compare yours to it before running the validator.

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

Readers with the rig: fill in your real Ollama and Docker versions, your actual VRAM numbers from
`ollama ps` and `nvidia-smi`, and your real model reply. Readers pre-hardware: the reference figures
above satisfy every invariant the validator enforces.

## Step 3: Ship the Validator

Create `check_models.py` in the same directory as `MODELS.md`:
`exercises/module3/a-14b-model-on-card/check_models.py`.

Here is what it enforces, in order:

- All three sections present (`## Serving Layer`, `## Models`, `## Sample Response`).
- Every key-value field filled: `Ollama version`, `Docker version`, `Endpoint` in the serving
  layer; `Prompt` and `Model` in the sample response.
- No placeholder tokens (`TODO`, `TBD`, `xxx`, angle brackets, ellipses).
- At least one model row with all five columns: Model, Quantization, Size on Disk, VRAM Used,
  VRAM Total. Every cell filled.
- The key invariant: VRAM Used must be less than or equal to VRAM Total. This is not a style
  check; it is the zero-overflow proof, now enforced as code. A model that violates it fails
  immediately and names the offender.
- A non-empty reply in the `## Sample Response` fenced block (at least ten characters).

The complete validator:

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

One regex detail worth knowing: `[^\S\n]` matches horizontal whitespace only (spaces and tabs). It
does not span the newline. A field line with nothing after the colon correctly fails the non-empty
check because the regex cannot reach the next line's content to satisfy itself.

## Step 4: The Live-vs-Expected Rule

The validator checks completeness and the fits-on-card invariant, not live truth. That distinction
matters: readers with the rig paste their real `ollama ps` and `nvidia-smi` figures; readers without
it paste the reference figures from Step 2. Either way, the validator passes as long as every section
is present, every field is filled, the model row has five columns, and VRAM Used sits at or below
VRAM Total. The reference build satisfies all four.

Run it to confirm:

```bash
python exercises/module3/a-14b-model-on-card/check_models.py
```

You should see `MODELS.md complete` and exit 0. Then test the invariant directly: temporarily raise
VRAM Used above VRAM Total in the table and run the validator again. It exits 1 and names the
overflowing model. Restore the original value before continuing.

The validator catches the overflow because it matters: a model that exceeds total VRAM spills onto
the system bus and serves at a fraction of on-card speed. The number in MODELS.md is not decorative;
it is a constraint the validator now holds you to.

The metal got documented in Module 1, the runtime in Module 2, and the model stack now in Module 3.
`ollama_client.py` sits in the same repository, already calling the endpoint; the routing layer in
Module 5 wraps it, and the Claude Code wiring in Module 6 exposes it. What you leave this module
with is not just a working stack: it is a portfolio artifact with a validator that will tell the
next module, and anyone reading the repo, exactly what is on the card and whether it fits.

## Core Concepts

- The completeness gate is the contract: `check_models.py` exits 0 only when all three sections
  exist, every field is filled, and the fenced reply block contains real content.
- The VRAM Used <= VRAM Total invariant is a real acceptance check: a model that violates it exits 1
  and names the offender, because overflow is a performance failure, not a style gap.
- A portfolio artifact is one a validator can verify: a human can skim a Markdown file, but code
  is the gatekeeper that makes the claim stick.
- The throughline now carries a runnable client forward: `ollama_client.py` is not a one-lesson
  artifact; it is the call layer the routing module will wrap.

<div class="claude-handoff" data-exercise="exercises/module3/record-the-stack/">

**Build It in Claude Code**: Add the `## Sample Response` section to `exercises/module3/a-14b-model-on-card/MODELS.md`, then create `check_models.py` beside it so it exits 0 only when all three sections are complete, every field is filled, the model row's VRAM Used is at or below VRAM Total, and the Sample Response holds a real reply.

</div>

<!-- SOURCES: https://ollama.com/library/qwen2.5-coder:14b | https://github.com/ollama/ollama/issues/9704 -->
