# Exercise: The Micro Center Run

**Goal:** Record your purchase and assembly result in `HARDWARE.md`, then extend
`check_hardware.py` to assert the section is present and all fields are filled.

**Why:** A build record is only useful if it captures what actually happened at the counter,
not what the spec planned. The validator makes "I filled it out" machine-checkable.

## Before You Start

Open `exercises/module1/why-each-part/HARDWARE.md` and read its current state. The `## Bill
of Materials` section is already there from the previous exercise, and so is the v1
`check_hardware.py` you wrote beside it. You are extending both, not replacing them.

## Steps

**Step 1 - Add the `## Purchase and Assembly` section to `HARDWARE.md`.**

Open `exercises/module1/why-each-part/HARDWARE.md` and append the following section after
`## Bill of Materials`:

```markdown
## Purchase and Assembly

Store: Tustin Micro Center
Express ProBuild (yes/no): yes
Stress test (pass/fail): pass
Duration: 10 minutes
Peak CPU temp: 78C
Peak GPU temp: 64C
```

Replace each value with your own. If you have not bought yet, record your plan: the store
you intend to use, whether you plan the ProBuild (yes/no), and a real planned stress result
(`pass` is the target). The validator accepts any real value; it rejects blank fields and
tokens like `TODO` or `TBD`.

**Step 2 - Extend `check_hardware.py` with a Purchase and Assembly check.**

Your `check_hardware.py` from the previous exercise validates the Bill of Materials. Add the
function below, which reuses the `fail` and `has_placeholder` helpers already in the file, then
call it from `main` after the BOM check:

```python
def check_purchase_and_assembly(content: str) -> None:
    if "## Purchase and Assembly" not in content:
        fail("'## Purchase and Assembly' section not found in HARDWARE.md")

    pa_start = content.index("## Purchase and Assembly")
    pa_section = content[pa_start:]

    required_fields = [
        "Store",
        "Express ProBuild (yes/no)",
        "Stress test (pass/fail)",
        "Duration",
        "Peak CPU temp",
        "Peak GPU temp",
    ]
    for field in required_fields:
        # [^\S\n] is horizontal whitespace only: it must not span the newline,
        # or a blank field would capture the next line's value.
        match = re.search(rf"{re.escape(field)}[^\S\n]*:[^\S\n]*([^\n]+)", pa_section)
        if not match or not match.group(1).strip():
            fail(f"'{field}' is empty or missing in Purchase and Assembly")
        if has_placeholder(match.group(1)):
            fail(f"'{field}' contains a placeholder")
```

Then wire it into `main`, right after the BOM validation runs:

```python
    # ... existing Bill of Materials checks above ...
    check_purchase_and_assembly(content)
```

The function asserts six fields: Store; Express ProBuild; Stress test; Duration; Peak CPU
temp; Peak GPU temp. It fails on any blank or placeholder value and prints the specific field
name.

**Step 3 - Run the validator.**

From the `exercises/module1/why-each-part/` directory:

```
python check_hardware.py
```

A clean run prints:

```
HARDWARE.md complete
```

and exits 0. A failing run prints the specific missing or unfilled field and exits 1. Fix
the field it names and re-run until you get exit 0.

**Step 4 - Test the failure case.**

Temporarily blank a field in `HARDWARE.md`, run the validator again, and confirm it exits 1
and names the field you blanked. Then restore the value and confirm exit 0.

## Done When

`python check_hardware.py` exits 0 against a filled `## Purchase and Assembly` section. The
validator is the gate: a real value in every field, no placeholder tokens.

`python check_hardware.py` exits 1, naming the specific field, when any field in
`## Purchase and Assembly` is blank or contains a placeholder.

## Note on Values

Your numbers come from your machine and your receipt, not from this page. The values in
Step 1 are an example from the reference build; treat them as the target shape, not numbers
to copy. The validator checks that you recorded real values, not that they match the example.

## Stretch

Run the full OCCT CPU:OCCT test for one hour after the machine is home. Record the peak
CPU temp that OCCT reports and update the `Peak CPU temp` field. Re-run the validator to
confirm the update is accepted.
