# Exercise: Why Each Part

**Goal:** Create `HARDWARE.md`, the canonical record of the machine this repository runs on, and
`check_hardware.py` v1, the validator that proves the record is complete.

**Why:** `HARDWARE.md` is the throughline artifact for Module 1. Later exercises open it and add
to it: `the-micro-center-run` fills in the prices you actually paid and the stress-test result;
`document-your-build` adds the first-boot identity of the rig and finalizes the validator. You are
starting the record, not finishing it. Every subsequent exercise depends on finding it here, in this
shape, with these section names.

**Note on filling in the table:** You do not have hardware in hand yet. Fill "Price Paid" with your
best estimate (you will update it at the Micro Center counter), and write "Why" in your own words
after reading the lesson. The validator checks that every cell is present and contains no
placeholders; it does not check live hardware. The goal is a complete, reasoned record you can
commit before the machine exists.

## Steps

1. Create `exercises/module1/why-each-part/HARDWARE.md` with the following structure. Copy the
   skeleton exactly, including the header, the section name, and the column labels.

   ```markdown
   # HARDWARE.md

   The machine this repository runs on.

   ## Bill of Materials

   | Component | Part | Est. Price | Price Paid | Why |
   |-----------|------|-----------|------------|-----|
   | CPU + Motherboard | AMD Ryzen 7 7700X + MSI B650I Edge WiFi Mini-ITX | ~$340 | | |
   | GPU | NVIDIA RTX 4060 Ti 16GB | ~$450 | | |
   | RAM | 64GB DDR5-6000 CL30 (2×32GB) | ~$185 | | |
   | Storage | Crucial T500 or Inland Performance Plus 2TB PCIe Gen 4 NVMe | ~$125 | | |
   | Case | Fractal Design Ridge Mini-ITX | ~$155 | | |
   | PSU | Corsair SF750 80+ Platinum SFX | ~$180 | | |
   | Assembly | Micro Center Express ProBuild + stress test | $250 | | |
   ```

   Fill "Price Paid" with your best estimate and write your own rationale in "Why" for each row.
   The lesson explains the inference reason behind each component; put it in your own words.

2. Create `exercises/module1/why-each-part/check_hardware.py` with the following contract (stdlib
   only):

   ```python
   """
   check_hardware.py: v1 BOM validator.

   Reads HARDWARE.md (path relative to this script), asserts the Bill of Materials
   section is present and all 7 component rows are complete. Exits 0 on success,
   exits 1 with a specific message on the first failure it finds.
   """

   import sys
   import re
   from pathlib import Path

   PLACEHOLDERS = {"todo", "tbd", "xxx", "fill in", "...", "<", ">"}

   REQUIRED_COMPONENTS = [
       "CPU",
       "GPU",
       "RAM",
       "Storage",
       "Case",
       "PSU",
       "Assembly",
   ]


   def fail(msg: str) -> None:
       print(f"FAIL: {msg}", file=sys.stderr)
       sys.exit(1)


   def has_placeholder(text: str) -> bool:
       lower = text.lower()
       return any(p in lower for p in PLACEHOLDERS)


   def main() -> None:
       hardware_path = Path(__file__).parent / "HARDWARE.md"
       if not hardware_path.exists():
           fail("HARDWARE.md not found")

       content = hardware_path.read_text(encoding="utf-8")

       # Assert BOM section header is present
       if "## Bill of Materials" not in content:
           fail("'## Bill of Materials' section not found in HARDWARE.md")

       # Extract the BOM section
       bom_start = content.index("## Bill of Materials")
       bom_section = content[bom_start:]

       # Find table rows (lines starting with |, skipping header and separator rows)
       rows = []
       for line in bom_section.splitlines():
           stripped = line.strip()
           if stripped.startswith("|") and not re.match(r"^\|\s*[-:]+", stripped):
               cells = [c.strip() for c in stripped.strip("|").split("|")]
               if len(cells) >= 5 and cells[0].lower() != "component":
                   rows.append(cells)

       # Check all 7 components are present
       found_components = [row[0] for row in rows]
       for required in REQUIRED_COMPONENTS:
           if not any(required.lower() in c.lower() for c in found_components):
               fail(f"Missing component row containing '{required}'")

       if len(rows) < 7:
           fail(f"Expected 7 component rows, found {len(rows)}")

       # Check each row: Price Paid (index 3) and Why (index 4) must be non-empty
       for row in rows:
           component = row[0]
           price_paid = row[3] if len(row) > 3 else ""
           why = row[4] if len(row) > 4 else ""

           if not price_paid:
               fail(f"'Price Paid' is empty for: {component}")
           if not why:
               fail(f"'Why' is empty for: {component}")
           if has_placeholder(price_paid):
               fail(f"'Price Paid' contains a placeholder for: {component}")
           if has_placeholder(why):
               fail(f"'Why' contains a placeholder for: {component}")

       print("HARDWARE.md complete")
       sys.exit(0)


   if __name__ == "__main__":
       main()
   ```

3. Fill every "Price Paid" and "Why" cell in your `HARDWARE.md`. Use the estimates from the BOM
   skeleton as your starting prices; you will update them at the counter. Write "Why" in your own
   words: one sentence per component explaining the inference reason behind that part, using the
   lesson as your source.

4. Run the validator from the exercise directory:

   ```
   python check_hardware.py
   ```

   It should print `HARDWARE.md complete` and exit 0.

5. If it exits 1, the message tells you exactly which field failed. Fix that field and re-run.

## Done When

`python check_hardware.py` exits 0 and prints `HARDWARE.md complete` when run against a fully
filled `HARDWARE.md`. It exits 1 with a specific field message when any cell is blank or contains
a placeholder.

Expected output on success:

```
HARDWARE.md complete
```

Expected output on a placeholder failure (example):

```
FAIL: 'Why' contains a placeholder for: GPU
```

## Stretch

Add a second check: confirm the total estimated cost in `HARDWARE.md` is within a reasonable range
of the reference build ($1,450–$1,685). Parse the "Est. Price" column, strip the `~$` prefix,
sum the values, and assert the total falls between $1,400 and $1,800. Print the parsed total
alongside the `HARDWARE.md complete` message. This makes `check_hardware.py` a live sanity check
on your own BOM if you substitute parts.
