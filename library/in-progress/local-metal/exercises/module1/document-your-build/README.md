# Exercise: Document Your Build

**Goal:** Finalize `HARDWARE.md` by adding the `## First Boot` section, then finalize
`check_hardware.py` so it validates the complete record: all three sections present, every field
filled, no placeholder text anywhere.

**Why:** A build record is not a portfolio artifact until it is complete. The Bill of Materials
and the purchase record you captured in earlier exercises document the decision and the cost;
the first-boot identity proves the machine is real and reports what you bought. The validator that
exits 0 only when all three are in place is the machine-checkable gate for Module 1.

**Note for readers without hardware yet:** Record the identity you expect from your BOM (the
CPU model name, GPU and VRAM, RAM total, and drive you ordered) and update each field when the
machine is in your hands. The validator checks completeness, not live truth; it rejects blank
fields and placeholder tokens, so write a real expected value rather than a `TODO`.

---

## Files You Are Editing

Both live under the existing throughline:

```
exercises/module1/why-each-part/HARDWARE.md       <- add ## First Boot here
exercises/module1/why-each-part/check_hardware.py <- finalize the validator here
```

Do not move or rename these files. Later modules read them from this location.

---

## Step 1: Add `## First Boot` to HARDWARE.md

Open `exercises/module1/why-each-part/HARDWARE.md`. After the `## Purchase and Assembly`
section, add:

```markdown
## First Boot

| Field | Value |
|-------|-------|
| CPU | |
| GPU and VRAM | |
| Total RAM | |
| Disk | |
| POST result | |
```

Fill each field with the identity your machine reports:

- **CPU:** the full model string (`AMD Ryzen 7 7700X 8-Core Processor` on the reference build;
  read from the BIOS screen at first power-on, or later from `lscpu | grep "Model name"`).
- **GPU and VRAM:** GPU name and VRAM total as the driver reports it (`NVIDIA GeForce RTX 4060 Ti,
  16380 MiB` on the reference build; read from `nvidia-smi` once Linux and drivers are up in
  Module 2). The RTX 4060 Ti 16GB reports `16380MiB`, not `16384MiB`; the difference is a small
  driver reservation, not a defective card.
- **Total RAM:** what the OS sees (`62 GiB` for 64 GB of DDR5 installed; read from
  `free -h | grep Mem`).
- **Disk:** the drive model and capacity you installed.
- **POST result:** `clean` if the machine booted without error codes, or the beep/error code it
  showed.

---

## Step 2: Finalize `check_hardware.py`

Open `exercises/module1/why-each-part/check_hardware.py`. Replace it with the complete validator
below. It asserts all three sections are present, the BOM has seven complete rows (a Price Paid
and a Why for each), every Purchase and First Boot field is filled, and no placeholder tokens
remain anywhere. The Bill of Materials table is the five-column layout you created in
`why-each-part`: `Component | Part | Est. Price | Price Paid | Why`.

```python
#!/usr/bin/env python3
"""
check_hardware.py: validate HARDWARE.md for the Local Metal throughline.

Usage: python check_hardware.py [path/to/HARDWARE.md]
Exits 0 on a complete record; exits 1 and names the first gap found.
"""

import sys
import re
from pathlib import Path

HARDWARE_PATH = Path(__file__).parent / "HARDWARE.md"
PLACEHOLDER_TOKENS = {"TODO", "TBD", "xxx", "fill in", "<", ">", "..."}

REQUIRED_SECTIONS = [
    "## Bill of Materials",
    "## Purchase and Assembly",
    "## First Boot",
]

PURCHASE_FIELDS = [
    "Store",
    "Express ProBuild (yes/no)",
    "Stress test (pass/fail)",
    "Duration",
    "Peak CPU temp",
    "Peak GPU temp",
]

FIRST_BOOT_FIELDS = [
    "CPU",
    "GPU and VRAM",
    "Total RAM",
    "Disk",
    "POST result",
]

BOM_ROW_COUNT = 7  # the seven lines of the reference-build BOM


def fail(message: str) -> None:
    print(f"HARDWARE.md incomplete: {message}")
    sys.exit(1)


def load(path: Path) -> str:
    if not path.exists():
        fail(f"{path} not found")
    return path.read_text(encoding="utf-8")


def check_sections(text: str) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f'section "{section}" missing from HARDWARE.md')


def check_no_placeholders(text: str) -> None:
    for token in PLACEHOLDER_TOKENS:
        if token in text:
            fail(f'placeholder token "{token}" still present; fill in the real value')


def check_bom(text: str) -> None:
    bom_match = re.search(r"## Bill of Materials\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not bom_match:
        fail('"## Bill of Materials" section has no content')
    bom_block = bom_match.group(1)
    rows = [
        line for line in bom_block.splitlines()
        if line.strip().startswith("|")
        and not re.match(r"^\s*\|[-| :]+\|\s*$", line)            # separator row
        and not re.match(r"^\s*\|[^|]*Component[^|]*\|", line)    # header row
    ]
    if len(rows) < BOM_ROW_COUNT:
        fail(f"Bill of Materials has {len(rows)} data row(s); expected {BOM_ROW_COUNT}.")
    for i, row in enumerate(rows, start=1):
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 5:
            fail(f"BOM row {i} has fewer than 5 columns; expected "
                 "Component | Part | Est. Price | Price Paid | Why")
        price_paid = cells[3]   # column 4: Price Paid
        why = cells[4]          # column 5: Why
        if price_paid in ("", "-"):
            fail(f"BOM row {i} ({cells[0]}) is missing a Price Paid value")
        if why in ("", "-"):
            fail(f"BOM row {i} ({cells[0]}) is missing a Why value")


def check_purchase_and_assembly(text: str) -> None:
    pa_match = re.search(r"## Purchase and Assembly\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not pa_match:
        fail('"## Purchase and Assembly" section has no content')
    pa_block = pa_match.group(1)
    for field in PURCHASE_FIELDS:
        pattern = rf"{re.escape(field)}[^\S\n]*:[^\S\n]*([^\n]+)"
        match = re.search(pattern, pa_block, re.IGNORECASE)
        if not match:
            fail(f'Purchase and Assembly field "{field}" not found')
        if not match.group(1).strip():
            fail(f'Purchase and Assembly field "{field}" is empty')


def check_first_boot(text: str) -> None:
    boot_match = re.search(r"## First Boot\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not boot_match:
        fail('"## First Boot" section has no content')
    boot_block = boot_match.group(1)
    for field in FIRST_BOOT_FIELDS:
        pattern = re.compile(rf"\|\s*{re.escape(field)}\s*\|\s*([^|\n]+?)\s*\|", re.IGNORECASE)
        match = pattern.search(boot_block)
        if not match:
            fail(f'First Boot field "{field}" not found or not in a table row')
        if not match.group(1).strip():
            fail(f'First Boot field "{field}" is empty')


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HARDWARE_PATH
    text = load(path)
    check_sections(text)
    check_no_placeholders(text)
    check_bom(text)
    check_purchase_and_assembly(text)
    check_first_boot(text)
    print("HARDWARE.md complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

---

## Done When

Run from the `why-each-part/` directory:

```bash
python check_hardware.py
```

- Exits 0 and prints `HARDWARE.md complete` when every section is filled and clean.
- Exits 1 and names the first gap (missing section, empty field, or placeholder token) when
  anything is incomplete.

Test both paths before you call this done: run it against your complete `HARDWARE.md` and confirm
exit 0; then temporarily blank one field and confirm exit 1 names it.

---

## Stretch

Have the validator confirm that the GPU VRAM entry in `## First Boot` is consistent with the GPU
row in `## Bill of Materials`. Parse the BOM GPU row for a VRAM hint (`16GB` or `16380 MiB`) and
the First Boot `GPU and VRAM` field for the same marker, and fail with a descriptive message if
they contradict each other. This is the kind of cross-field consistency check a real acceptance
gate runs.
