# Exercise: Verify the GPU Is Visible

**Goal:** Finalize the module-2 software-baseline record. Add the `## Verification` section to
`exercises/module2/choosing-and-installing-linux/SETUP.md`, then finalize `check_setup.py` so
it exits 0 only when all three sections are complete and the captured `nvidia-smi` output
contains both `CUDA Version` and `NVIDIA`.

**Why:** The module's machine-checkable done-when is a complete `SETUP.md`: the software
baseline that records the distro, the driver, the CUDA version, and the verification readout
proving the stack is live. Without the Verification section, the record is unfinished and
`check_setup.py` will say so. With it, every future module can trust the runtime layer is real.

**Note for readers without hardware yet:** Run the commands against your machine when you have
it. For now, paste the expected reference-build readout from the lesson (driver 550.90.12,
CUDA 12.4, `NVIDIA GeForce RTX 4060 Ti`) and record the expected CUDA version. The validator
checks completeness and that the block contains real content, not live truth; it will still
pass against the reference output.

---

## Files You Are Editing

Both files live under the existing throughline:

```
exercises/module2/choosing-and-installing-linux/SETUP.md       <- add ## Verification here
exercises/module2/choosing-and-installing-linux/check_setup.py <- finalize the validator here
```

Do not move or rename these files. Module 3 and later will read them from this location.

---

## Step 1: Add `## Verification` to SETUP.md

Open `exercises/module2/choosing-and-installing-linux/SETUP.md`. After the `## GPU Driver and
CUDA` section, add:

```markdown
## Verification

GPU detected (yes/no):
CUDA version reported:

```
<paste your nvidia-smi output here>
```
```

Fill in the two key: value lines:

- **GPU detected (yes/no):** `yes` if `nvidia-smi` listed your GPU, `no` if it reported no
  devices or failed.
- **CUDA version reported:** the CUDA Version shown in the `nvidia-smi` header line (e.g.,
  `12.4`). This is the driver's capability ceiling, not necessarily the toolkit version on disk.

Then paste your actual `nvidia-smi` output inside the fenced block. On the reference build it
looks like this:

```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.90.12              Driver Version: 550.90.12      CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4060 Ti     Off |   00000000:08:00.0 Off |                  N/A |
|  0%   45C    P0             32W / 165W  |     582MiB / 16380MiB  |      0%      Default |
+-----------------------------------------------------------------------------------------+
```

If you have the machine: run `nvidia-smi` in your terminal and paste the real output.
If you are pre-hardware: paste the reference-build output above so the validator can confirm
the record is complete.

---

## Step 2: Finalize `check_setup.py`

Replace `check_setup.py` with this complete final version. It folds in the Operating System
check from `choosing-and-installing-linux` and the driver check from `nvidia-drivers-and-cuda`,
then adds the Verification checks: all three sections present, every field filled, no placeholder
tokens anywhere, and a fenced `nvidia-smi` block that contains both `CUDA Version` and `NVIDIA`.

```python
#!/usr/bin/env python3
"""
check_setup.py: validate SETUP.md for the Local Metal module-2 throughline.

Usage: python check_setup.py [path/to/SETUP.md]
Exits 0 when the record is complete; exits 1 and names the first gap found.
"""

import re
import sys
from pathlib import Path

SETUP_PATH = Path(__file__).parent / "SETUP.md"

REQUIRED_SECTIONS = [
    "## Operating System",
    "## GPU Driver and CUDA",
    "## Verification",
]

OS_FIELDS = ["Distro", "Version", "Kernel", "Disk layout"]
DRIVER_FIELDS = ["NVIDIA driver version", "CUDA toolkit version", "Install method"]
VERIFICATION_FIELDS = ["GPU detected (yes/no)", "CUDA version reported"]

PLACEHOLDERS = {"TODO", "TBD", "xxx", "fill in", "<", ">", "..."}


def fail(message: str) -> None:
    print(f"SETUP.md incomplete: {message}")
    sys.exit(1)


def load(path: Path) -> str:
    if not path.exists():
        fail(f"{path} not found")
    return path.read_text(encoding="utf-8")


def check_sections(text: str) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f'section "{section}" missing from SETUP.md')


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


def check_verification_fenced_block(section_text: str) -> None:
    blocks = re.findall(r"```[^\n]*\n(.*?)```", section_text, re.DOTALL)
    if not blocks:
        fail('"## Verification" has no fenced code block; paste your nvidia-smi output in a ``` block')
    for block in blocks:
        if "CUDA Version" in block and "NVIDIA" in block:
            return
    fail('the fenced block in "## Verification" must contain both "CUDA Version" and "NVIDIA" '
         "(a real nvidia-smi capture)")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else SETUP_PATH
    text = load(path)
    check_sections(text)
    check_no_placeholders(text)
    check_fields(extract_section(text, "## Operating System"), OS_FIELDS, "## Operating System")
    check_fields(extract_section(text, "## GPU Driver and CUDA"), DRIVER_FIELDS, "## GPU Driver and CUDA")
    verification = extract_section(text, "## Verification")
    check_fields(verification, VERIFICATION_FIELDS, "## Verification")
    check_verification_fenced_block(verification)
    print("SETUP.md complete")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

`[^\S\n]` matches horizontal whitespace only (spaces and tabs), not newlines, so a `field:` line
with nothing after the colon correctly fails the non-empty check.

---

## Done When

Run from any directory (the script resolves paths relative to itself):

```bash
python exercises/module2/choosing-and-installing-linux/check_setup.py
```

- Exits 0 and prints `SETUP.md complete` when every section is present, every field is filled,
  and the Verification block contains a real `nvidia-smi` capture.
- Exits 1 and names the first gap (missing section, empty field, placeholder token, or missing
  fenced block) when anything is incomplete.

Test both paths: run it against your completed `SETUP.md` and confirm exit 0; then temporarily
blank `CUDA version reported:` and confirm exit 1 names that field.

---

## Stretch

Enable the cross-field consistency check in `check_setup.py`. In `main()`, uncomment the line:

```python
# check_cuda_version_consistency(text)
```

This asserts that the CUDA version string in the `nvidia-smi` fenced block matches the
`CUDA toolkit version` field in `## GPU Driver and CUDA`. If the two diverge (for example,
the driver supports CUDA 12.4 but you installed the CUDA 12.2 toolkit), the validator names
the mismatch. It is the kind of cross-field consistency gate a real acceptance check runs.
