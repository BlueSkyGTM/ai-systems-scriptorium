# Record the Tuning

You profiled the rig, you pulled the levers; now record the before-and-after that proves it was worth it. This is the last file the book asks you to write.

## Step 1: Capture Before and After

The baseline comes from Module 4, single-stream, stock settings. The tuned number comes from `loadbench.py` after setting the levers. The headline lever is `OLLAMA_NUM_PARALLEL`: it raises aggregate throughput under load by letting Ollama serve multiple requests concurrently rather than queuing them.

Representative figures on the RTX 4060 Ti 16GB (label representative; your numbers differ by prompt, model, and thermals):

| Condition | Aggregate tok/s |
|-----------|-----------------|
| Baseline (Module 4, single stream) | 30.0 |
| Tuned (num_parallel=4, flash attention, q8_0 KV cache) | 64.0 |

The 2x+ lift comes primarily from `OLLAMA_NUM_PARALLEL=4`. Flash attention and `OLLAMA_KV_CACHE_TYPE=q8_0` contribute a modest single-stream speedup and a smaller KV footprint; the parallelism setting is what moves the aggregate number.

## Step 2: The Complete TUNING.md

Create `exercises/module7/record-the-tuning/TUNING.md` with your own before-and-after figures. The complete file:

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

## Step 3: Ship the Validator

Create `check_tuning.py` beside `TUNING.md` at `exercises/module7/record-the-tuning/check_tuning.py`.

Here is what it enforces, in order:

- All three sections present: `## Baseline`, `## Tuned`, `## Levers Applied`.
- The `Baseline` section has `Aggregate tok/s` and `Source` filled.
- The `Tuned` section has `Aggregate tok/s` and `Levers` filled.
- No placeholder tokens (`TODO`, `TBD`, `xxx`, angle brackets, ellipses).
- The `## Levers Applied` table has at least one complete row: all three columns filled.
- The key gate: the tuned `Aggregate tok/s` must be at least the baseline. You keep a lever only if it improved the number; if tuning regressed throughput, the validator exits 1 and names the gap.

The complete validator:

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

One regex detail worth knowing: `[^\S\n]` matches horizontal whitespace only (spaces and tabs), not newlines. A `field:` line with nothing after the colon correctly fails the non-empty check because the pattern cannot reach the next line's content.

## Step 4: The Live-vs-Expected Rule

With the rig: run `loadbench.py` before and after setting the levers, and paste your real aggregate tok/s into `TUNING.md`. Without the rig: paste the representative figures above. The validator checks that the record is complete and non-regressing, not the exact values; the reference build satisfies every check.

Seven modules ago this was a parts list at a counter. Now it is a documented, routed, wired, and tuned inference host, with seven portfolio files (HARDWARE.md, SETUP.md, MODELS.md, LATENCY.md, ROUTING.md, DELEGATION.md, TUNING.md) and a runnable spine from `ollama_client.py` through `route.py` to `mcp_server.py` that a reviewer can trace end to end. TUNING.md is not the capstone because it is last; it is the capstone because it forces you to name every decision and show it improved something. That is how engineers sign off a build.

## Core Concepts

- A before-and-after record is the proof tuning worked: a number without a comparison point is a claim, not a result.
- The tuned-at-least-baseline gate catches regressions that feel like progress; you keep a lever only when the number it produced is better than the number you started with.
- Aggregate throughput, not single-stream tokens per second, is the server metric: it measures what happens when the rig has to serve real concurrent load.
- The seven-file portfolio (HARDWARE.md through TUNING.md) is the complete artifact: each file is validator-backed, each records a decision, and together they tell the full story of the build.

<div class="claude-handoff" data-exercise="exercises/module7/record-the-tuning/">

**Build It in Claude Code**: Create `exercises/module7/record-the-tuning/TUNING.md` with your baseline (from Module 4) and tuned aggregate throughput plus the levers you applied, then create `check_tuning.py` beside it so it exits 0 only when the record is complete and the tuned number is at least the baseline.

</div>

<!-- SOURCES: https://github.com/ollama/ollama/blob/main/envconfig/config.go -->
