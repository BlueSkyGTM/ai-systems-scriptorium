#!/usr/bin/env python3
"""
check_prep.py -- Validator for the Answer Engineering prep dossier.

Validates two logs in the same directory as this script:
  decomposition-log.md  (exercise 1: ten question decompositions)
  answers-log.md        (exercise 2: five full Algorithm runs)

Exits 0 only when both logs are complete and free of placeholder text.
Exits 1 otherwise, with a clear per-file report.

Usage:
  python check_prep.py           Run validation and print report.
  python check_prep.py --help    Show this help text.

Section markers the validator expects
--------------------------------------
decomposition-log.md:
  Each entry is headed by:  ## Q<n>   (e.g. ## Q1, ## Q7)
  Required fields (one per entry, on their own line):
    **Literal parse:**
    **Signal category:**
    **Primary hypothesis:**
  Calibration section headed by:  ## Calibration
    (must exist and must not contain only placeholder text)

answers-log.md:
  Each entry is headed by:  ## A<n>   (e.g. ## A1, ## A5)
  Required sections within each entry (headings, any level):
    ### Step 1: Decompose
    ### Step 2: Identify the Signal
    ### Step 3: Construct the Answer
    ### Step 4: Stress-Test
  Required score lines (on their own line, in any order):
    **Specificity:**
    **Structure:**
    **Completeness:**
  Score values must be one of: strong, partial, weak
  (case-insensitive; must not be TODO or other placeholder)
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent

DECOMP_LOG = SCRIPT_DIR / "decomposition-log.md"
ANSWERS_LOG = SCRIPT_DIR / "answers-log.md"

# Placeholder text patterns: any required field containing these fails.
PLACEHOLDER_PATTERNS = re.compile(
    r"\bTODO\b|XXX|<fill|\.\.\.",
    re.IGNORECASE,
)

# Valid score values for the answers log.
VALID_SCORES = {"strong", "partial", "weak"}

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def is_placeholder(text: str) -> bool:
    """Return True if the text contains placeholder markers."""
    return bool(PLACEHOLDER_PATTERNS.search(text))


def extract_field_value(lines: list[str], field_prefix: str) -> str | None:
    """
    Find the first line starting with `field_prefix` (after stripping whitespace)
    and return the text after the colon, stripped.
    Returns None if the field is not found.
    """
    prefix_lower = field_prefix.lower()
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith(prefix_lower):
            after_colon = stripped[len(field_prefix):].strip()
            return after_colon
    return None


def split_into_entries(text: str, heading_pattern: re.Pattern) -> list[tuple[str, list[str]]]:
    """
    Split `text` into sections, each starting with a heading matching
    `heading_pattern`. Returns a list of (heading_text, lines_in_section) tuples.
    Sections before the first matching heading are discarded.
    """
    entries = []
    current_heading = None
    current_lines: list[str] = []

    for line in text.splitlines():
        m = heading_pattern.match(line.strip())
        if m:
            if current_heading is not None:
                entries.append((current_heading, current_lines))
            current_heading = line.strip()
            current_lines = []
        else:
            if current_heading is not None:
                current_lines.append(line)

    if current_heading is not None:
        entries.append((current_heading, current_lines))

    return entries


# ---------------------------------------------------------------------------
# Decomposition log validator
# ---------------------------------------------------------------------------

# Heading pattern: ## Q<digits>  (exactly, case-sensitive)
DECOMP_ENTRY_RE = re.compile(r"^##\s+Q(\d+)$")
# Calibration section heading
CALIBRATION_RE = re.compile(r"^##\s+Calibration$", re.IGNORECASE)

DECOMP_REQUIRED_FIELDS = [
    "**Literal parse:**",
    "**Signal category:**",
    "**Primary hypothesis:**",
]

MIN_DECOMP_ENTRIES = 10


def validate_decomposition_log(path: Path) -> tuple[bool, list[str]]:
    """
    Validate decomposition-log.md.
    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append("  Copy decomposition-log.template.md to decomposition-log.md and complete it.")
        return False, messages

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    passed = True

    # --- Check for entry headings ---
    all_entries = split_into_entries(text, DECOMP_ENTRY_RE)
    found_count = len(all_entries)

    if found_count < MIN_DECOMP_ENTRIES:
        messages.append(
            f"FAIL: Found {found_count} question entries (## Q<n> headings); "
            f"need at least {MIN_DECOMP_ENTRIES}."
        )
        passed = False
    else:
        messages.append(f"OK:   {found_count} question entries found.")

    # --- Check each entry for required fields ---
    for heading, entry_lines in all_entries:
        entry_label = heading  # e.g. "## Q1"
        for field in DECOMP_REQUIRED_FIELDS:
            value = extract_field_value(entry_lines, field)
            if value is None:
                messages.append(f"FAIL: {entry_label}: missing field '{field}'.")
                passed = False
            elif not value:
                messages.append(f"FAIL: {entry_label}: field '{field}' is empty.")
                passed = False
            elif is_placeholder(value):
                messages.append(
                    f"FAIL: {entry_label}: field '{field}' contains placeholder text: {value!r}"
                )
                passed = False

    # --- Check calibration section ---
    calibration_present = False
    calibration_text: list[str] = []
    in_calibration = False

    for line in lines:
        if CALIBRATION_RE.match(line.strip()):
            calibration_present = True
            in_calibration = True
            continue
        # Stop collecting calibration text at the next ## heading
        if in_calibration and line.strip().startswith("## "):
            in_calibration = False
        if in_calibration:
            calibration_text.append(line)

    if not calibration_present:
        messages.append("FAIL: Missing '## Calibration' section.")
        passed = False
    else:
        # Collapse to non-empty, non-comment lines
        content_lines = [
            l for l in calibration_text
            if l.strip() and not l.strip().startswith("<!--")
        ]
        calibration_body = " ".join(content_lines)
        if not content_lines:
            messages.append("FAIL: '## Calibration' section is empty.")
            passed = False
        elif is_placeholder(calibration_body):
            messages.append(
                "FAIL: '## Calibration' section contains placeholder text. "
                "Write your actual calibration."
            )
            passed = False
        else:
            messages.append("OK:   Calibration section is present and filled in.")

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Answers log validator
# ---------------------------------------------------------------------------

# Heading pattern: ## A<digits>
ANSWERS_ENTRY_RE = re.compile(r"^##\s+A(\d+)$")

# Step headings expected inside each entry (case-insensitive substring match
# because the learner may write "### Step 1: Decompose" or "### Step 1: decompose")
STEP_HEADINGS = [
    "### Step 1:",
    "### Step 2:",
    "### Step 3:",
    "### Step 4:",
]

SCORE_FIELDS = [
    "**Specificity:**",
    "**Structure:**",
    "**Completeness:**",
]

MIN_ANSWERS_ENTRIES = 5


def validate_answers_log(path: Path) -> tuple[bool, list[str]]:
    """
    Validate answers-log.md.
    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append("  Copy answers-log.template.md to answers-log.md and complete it.")
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    # --- Check for entry headings ---
    all_entries = split_into_entries(text, ANSWERS_ENTRY_RE)
    found_count = len(all_entries)

    if found_count < MIN_ANSWERS_ENTRIES:
        messages.append(
            f"FAIL: Found {found_count} answer entries (## A<n> headings); "
            f"need at least {MIN_ANSWERS_ENTRIES}."
        )
        passed = False
    else:
        messages.append(f"OK:   {found_count} answer entries found.")

    # --- Check each entry ---
    for heading, entry_lines in all_entries:
        entry_label = heading  # e.g. "## A1"
        entry_text = "\n".join(entry_lines)

        # Check that all four step headings appear
        for step in STEP_HEADINGS:
            if step.lower() not in entry_text.lower():
                messages.append(f"FAIL: {entry_label}: missing section '{step}'.")
                passed = False

        # Check score fields: present, non-placeholder, valid value
        for field in SCORE_FIELDS:
            value = extract_field_value(entry_lines, field)
            if value is None:
                messages.append(f"FAIL: {entry_label}: missing score field '{field}'.")
                passed = False
            elif not value:
                messages.append(f"FAIL: {entry_label}: score field '{field}' is empty.")
                passed = False
            elif is_placeholder(value):
                messages.append(
                    f"FAIL: {entry_label}: score field '{field}' contains placeholder text: {value!r}"
                )
                passed = False
            elif value.lower() not in VALID_SCORES:
                messages.append(
                    f"FAIL: {entry_label}: score field '{field}' value {value!r} is not "
                    f"one of: strong, partial, weak."
                )
                passed = False

        # Spot-check that Step 3 (the answer body) has some real content:
        # find the block between ### Step 3 and the next ### heading.
        step3_body = extract_step_body(entry_text, "### Step 3:")
        if step3_body is not None:
            if is_placeholder(step3_body) or not step3_body.strip():
                messages.append(
                    f"FAIL: {entry_label}: Step 3 answer body is empty or contains placeholder text."
                )
                passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


def extract_step_body(entry_text: str, step_prefix: str) -> str | None:
    """
    Return the text between `step_prefix` heading and the next ### heading,
    or None if the step heading is not found.
    """
    lines = entry_text.splitlines()
    in_step = False
    body_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith(step_prefix.lower()):
            in_step = True
            continue
        if in_step:
            # Stop at any heading of level ### or higher
            if stripped.startswith("### ") or stripped.startswith("## "):
                break
            body_lines.append(line)

    if not in_step:
        return None
    # Filter out HTML comment lines before checking content
    content = "\n".join(
        l for l in body_lines if not l.strip().startswith("<!--")
    )
    return content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_prep.py",
        description=(
            "Validate the Answer Engineering prep dossier. "
            "Checks decomposition-log.md and answers-log.md for completeness. "
            "Exits 0 when both logs are complete; exits 1 otherwise."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Run from exercises/prep/ or any directory; paths resolve relative to this script.\n\n"
            "Expected files:\n"
            "  decomposition-log.md  -- ten question decompositions + calibration section\n"
            "  answers-log.md        -- five full Algorithm runs with scores\n"
        ),
    )
    return parser


def main() -> int:
    parser = build_parser()
    parser.parse_args()  # --help is handled here; no positional args expected

    print("Answer Engineering Prep Dossier Validator")
    print("=" * 44)
    print()

    decomp_passed, decomp_messages = validate_decomposition_log(DECOMP_LOG)
    answers_passed, answers_messages = validate_answers_log(ANSWERS_LOG)

    print(f"--- {DECOMP_LOG.name} ---")
    for msg in decomp_messages:
        print(" ", msg)
    print()

    print(f"--- {ANSWERS_LOG.name} ---")
    for msg in answers_messages:
        print(" ", msg)
    print()

    if decomp_passed and answers_passed:
        print("RESULT: Both logs are complete. Dossier passes.")
        return 0
    else:
        failed = []
        if not decomp_passed:
            failed.append(DECOMP_LOG.name)
        if not answers_passed:
            failed.append(ANSWERS_LOG.name)
        print(f"RESULT: Incomplete. Fix the issues above in: {', '.join(failed)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
