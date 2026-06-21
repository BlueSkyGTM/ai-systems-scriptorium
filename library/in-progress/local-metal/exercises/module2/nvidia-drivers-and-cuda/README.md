# Exercise: NVIDIA Drivers and CUDA

**Goal:** Add the `## GPU Driver and CUDA` section to
`exercises/module2/choosing-and-installing-linux/SETUP.md`, then extend `check_setup.py` with a
`check_gpu_driver_and_cuda` function that validates all three fields are filled.

**Why:** The software baseline is not complete until the driver and toolkit versions are on record.
The validator that exits 0 only when every section is filled is the machine-checkable gate for
Module 2's throughline artifact.

**Note for readers without the machine yet:** Record the driver branch and CUDA toolkit version the
lesson cites (nvidia-driver-550 and CUDA 12.x or 13.x, as appropriate). Update the fields after
you install. The validator checks that the fields are non-empty and placeholder-free, not that they
match a specific value.

---

## Files You Are Editing

Both live under the existing throughline:

```
exercises/module2/choosing-and-installing-linux/SETUP.md       <- add ## GPU Driver and CUDA here
exercises/module2/choosing-and-installing-linux/check_setup.py <- extend the validator here
```

Do not move or rename these files. Lesson 4 reads them from this location and adds its own section.

---

## Step 1: Add `## GPU Driver and CUDA` to SETUP.md

Open `exercises/module2/choosing-and-installing-linux/SETUP.md`. After the `## Operating System`
section, add the following block exactly. The section name and field labels must match this
skeleton: the validator parses them by name.

```markdown
## GPU Driver and CUDA

NVIDIA driver version: 
CUDA toolkit version: 
Install method: 
```

Fill each field:

- **NVIDIA driver version:** the branch you installed, for example `550` or `550.90.07`. If you
  have not installed yet, write the branch the lesson recommends (`550`); update it after
  installation.
- **CUDA toolkit version:** the version `nvcc --version` reports after installation, for example
  `12.4` or `13.3`. If pre-install, write the version the lesson targets.
- **Install method:** `apt (ubuntu-drivers + cuda-keyring)` if you followed the lesson's apt path,
  or `runfile` if you used the `.run` installer.

The completed section should look like this (your values will differ):

```markdown
## GPU Driver and CUDA

NVIDIA driver version: 550
CUDA toolkit version: 12.4
Install method: apt (ubuntu-drivers + cuda-keyring)
```

---

## Step 2: Extend `check_setup.py`

Open `exercises/module2/choosing-and-installing-linux/check_setup.py`. Add the function below
after the existing `check_fields` function and before `main`. Then wire it into `main` after the
operating-system field check.

### The new function

```python
def check_gpu_driver_and_cuda(text: str) -> None:
    if "## GPU Driver and CUDA" not in text:
        print("SETUP.md incomplete: section '## GPU Driver and CUDA' missing")
        sys.exit(1)

    gpu_match = re.search(r"## GPU Driver and CUDA\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not gpu_match:
        print("SETUP.md incomplete: '## GPU Driver and CUDA' section has no content")
        sys.exit(1)
    section = gpu_match.group(1)

    fields = [
        "NVIDIA driver version",
        "CUDA toolkit version",
        "Install method",
    ]
    for field in fields:
        match = re.search(
            rf"{re.escape(field)}[^\S\n]*:[^\S\n]*([^\n]+)",
            section,
        )
        if not match or not match.group(1).strip():
            print(f"SETUP.md incomplete: '{field}' is empty or missing")
            sys.exit(1)
        value = match.group(1).strip().lower()
        placeholders = {"todo", "tbd", "xxx", "...", "<fill in>", "fill in"}
        if any(p in value for p in placeholders):
            print(f"SETUP.md incomplete: '{field}' still contains a placeholder")
            sys.exit(1)
```

### Wire it into main

Find the `main` function. After the call to `check_fields(text)`, add `check_gpu_driver_and_cuda(text)`.
The updated `main` should look like this:

```python
def main() -> None:
    text = load_setup()
    check_placeholders(text)
    check_section(text)
    check_fields(text)
    check_gpu_driver_and_cuda(text)
    print("SETUP.md complete")
    sys.exit(0)
```

---

## Step 3: Run the Validator

From the `choosing-and-installing-linux/` directory:

```bash
python check_setup.py
```

It should print `SETUP.md complete` and exit 0.

If it exits 1, the message names the field that failed. Fix that field and re-run.

---

## Done When

`python check_setup.py` exits 0 and prints `SETUP.md complete` when run against a fully filled
`SETUP.md`. It exits 1 and names the specific field when any driver or CUDA field is blank or
contains a placeholder.

Expected output on success:

```
SETUP.md complete
```

Expected output on a missing field (example):

```
SETUP.md incomplete: 'CUDA toolkit version' is empty or missing
```

Test both paths: run against your complete `SETUP.md` (exit 0), then blank one field and confirm
exit 1 names it.

---

## Stretch

Add a version-format check: after confirming `NVIDIA driver version` is non-empty, assert that it
contains at least one digit. Use `re.search(r"\d", value)` and fail with a descriptive message if
no digit is found. This catches entries like `latest` or `stable` that pass the placeholder check
but carry no real version signal.
