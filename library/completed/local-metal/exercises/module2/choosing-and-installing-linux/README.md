# Exercise: Choosing and Installing Linux

**Goal:** Build `SETUP.md` with its `## Operating System` section filled in, and `check_setup.py` v1 that validates the section is complete and no placeholders remain.

**Why:** Every later lesson in this module opens `SETUP.md` and adds to it. Getting the structure right now means the driver and CUDA sections slot in cleanly in lessons 3 and 4. A validator that exits 0 is the machine-checkable proof that the record is complete.

**Note for readers without the machine yet:** Fill in the expected values from the lesson (`Ubuntu 24.04 LTS`, the 6.8 kernel line) and update the fields after install. The validator checks completeness and the absence of placeholders; it does not probe live system state.

---

## Steps

### Step 1: Create `SETUP.md`

Create the file at `exercises/module2/choosing-and-installing-linux/SETUP.md` with this exact structure:

```markdown
# SETUP.md

The software baseline this machine runs.

## Operating System

Distro: Ubuntu 24.04 LTS
Version: 24.04
Kernel: 6.8.0-xx-generic
Disk layout: 1 TB Linux partition (ext4) alongside 1 TB Windows partition (NTFS)
```

Fill in the `Kernel:` field with the output of `uname -r` from your machine. Fill in `Disk layout:` with your actual partition sizes. If you do not have the machine yet, record the expected values and note them as pre-install estimates; update after first boot.

Do not add the `## GPU Driver and CUDA` or `## Verification` sections; those belong to lessons 3 and 4.

### Step 2: Create `check_setup.py`

Create `exercises/module2/choosing-and-installing-linux/check_setup.py`. The script reads `SETUP.md` (located in the same directory as the script) and validates the `## Operating System` section.

```python
import re
import sys
from pathlib import Path

SETUP_PATH = Path(__file__).parent / "SETUP.md"
PLACEHOLDERS = {"TODO", "TBD", "xxx", "fill in", "<", ">", "..."}
REQUIRED_FIELDS = ["Distro", "Version", "Kernel", "Disk layout"]


def load_setup() -> str:
    if not SETUP_PATH.exists():
        print(f"MISSING: {SETUP_PATH} not found")
        sys.exit(1)
    return SETUP_PATH.read_text(encoding="utf-8")


def check_placeholders(text: str) -> None:
    for marker in PLACEHOLDERS:
        if marker in text:
            print(f"PLACEHOLDER FOUND: '{marker}' still present in SETUP.md")
            sys.exit(1)


def check_section(text: str) -> None:
    if "## Operating System" not in text:
        print("MISSING: ## Operating System section not found")
        sys.exit(1)


def check_fields(text: str) -> None:
    for field in REQUIRED_FIELDS:
        match = re.search(rf"{re.escape(field)}[^\S\n]*:[^\S\n]*([^\n]+)", text)
        if not match or not match.group(1).strip():
            print(f"MISSING OR EMPTY: field '{field}' not found or blank")
            sys.exit(1)


def main() -> None:
    text = load_setup()
    check_placeholders(text)
    check_section(text)
    check_fields(text)
    print("SETUP.md complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

### Step 3: Run the Validator

From the exercise directory:

```bash
python check_setup.py
```

A fully filled `SETUP.md` prints `SETUP.md complete` and exits 0. A missing or empty field prints the field name and exits 1.

---

## Done When

`python check_setup.py` exits 0 against a `SETUP.md` where every field under `## Operating System` is filled and no placeholder marker (`TODO`, `TBD`, `<`, `>`, etc.) appears anywhere in the file.

When one field is blank or missing, the script exits 1 and names the specific field. Test both paths: run the validator against your filled file, then temporarily blank one field and confirm it fails with a clear message.

Expected output (success):

```
SETUP.md complete
```

Expected output (failure, blank Kernel field):

```
MISSING OR EMPTY: field 'Kernel' not found or blank
```

---

## Stretch

Add a check that `## Operating System` contains at least two distinct lines beyond the section heading (not just the heading itself). A section heading with no content below it should fail with a message like `EMPTY SECTION: ## Operating System has no field lines`. This is the pattern that lessons 3 and 4 will use when they add `## GPU Driver and CUDA` and `## Verification`.
