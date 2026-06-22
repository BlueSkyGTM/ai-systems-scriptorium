#!/usr/bin/env python3
"""
check_prep.py -- Validator for the Answer Engineering prep dossier.

Validates the logs in the same directory as this script. Module 1 established
the two core logs; Module 2 adds four more; Module 3 adds the behavioral bank;
Module 4 adds the coding-screen log (sibling branch, not a prerequisite for M5-M8);
Module 5 adds the systems-design log; Module 6 adds the portfolio narrative;
Module 7 adds the deliberate-practice log; Module 8 adds the loop plan.
The --module flag controls which artifacts are required for the exit code.

  decomposition-log.md       (M1: ten question decompositions + calibration)
                             (M2 extension: Hard Cases section with >=3 HC entries)
  answers-log.md             (M1: five full Algorithm runs with scores)
  signal-map.md              (M2: three questions mapped across two company contexts)
  practice-log.md            (M2: two answers recorded and self-scored)
  audit-log.md               (M2: two answers run through the pitfalls audit)
  behavioral-bank.md         (M3: four STAR-L stories covering all four categories,
                                  each with an audit verdict; no placeholders)
  coding-screen-log.md       (M4: three or more coding-screen reps, each with all six
                                  fields filled; no placeholders. M4 is a sibling gate:
                                  --module 4 requires M1+M2+M3+coding-screen-log.
                                  --module 5/6/7/8 do NOT require coding-screen-log.)
  systems-design-log.md      (M5: one complete design entry with all eight fields;
                                  no placeholders)
  portfolio-narrative.md     (M6: one complete artifact entry with all seven fields;
                                  no placeholders)
  deliberate-practice.md     (M7: five practice reps across all five signal categories;
                                  step scores strong|partial|weak; no placeholders)
  loop-plan.md               (M8: five stage entries covering all five loop stages,
                                  Readiness ready|gap, Plan filled; no placeholders)

Exits 0 only when the required logs for the selected module are complete and
free of placeholder text. Exits 1 otherwise, with a clear per-file report.

Usage:
  python check_prep.py              Run all checks; report per-artifact status.
  python check_prep.py --module 1   Require only M1 artifacts complete.
  python check_prep.py --module 2   Require M1 + all M2 artifacts complete.
  python check_prep.py --module 3   Require M1 + M2 + behavioral-bank.md complete.
  python check_prep.py --module 4   Require M1 + M2 + M3 + coding-screen-log.md complete.
                                    (M4 is a sibling gate; M5-M8 do not require it.)
  python check_prep.py --module 5   Require M1 + M2 + M3 + systems-design-log.md complete.
  python check_prep.py --module 6   Require M1 + M2 + M3 + M5 + portfolio-narrative.md complete.
  python check_prep.py --module 7   Require M1 + M2 + M3 + M5 + M6 + deliberate-practice.md complete.
  python check_prep.py --module 8   Require M1 + M2 + M3 + M5 + M6 + M7 + loop-plan.md complete.
  python check_prep.py --module all Same as the default (all artifacts, including M4 and M8).
  python check_prep.py --help       Show this help text.

Note: --module 4 is a sibling gate (M1+M2+M3+coding-screen-log). --module 5/6/7/8
do not require coding-screen-log.md. --module all DOES require coding-screen-log.md.

Section markers the validator expects
--------------------------------------
decomposition-log.md (M1 checks):
  Each entry is headed by:  ## Q<n>   (e.g. ## Q1, ## Q7)
  Required fields (one per entry, on their own line):
    **Literal parse:**
    **Signal category:**
    **Primary hypothesis:**
  Calibration section headed by:  ## Calibration
    (must exist and must not contain only placeholder text)

decomposition-log.md (M2 Hard Cases extension):
  Hard Cases section headed by:  ## Hard Cases
  Each entry is headed by:       ### HC<n>   (e.g. ### HC1, ### HC3)
  Required fields per entry:
    **Senior reading:**
    **Primary hypothesis (senior):**
    **Staff reading:**
    **Primary hypothesis (staff):**
    **How the hypothesis shifts:**

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

signal-map.md:
  Each entry is headed by:  ### SM<n>   (e.g. ### SM1, ### SM3)
  Required fields per entry:
    **Stated signal:**
    **Latent signal:**
    **Frontier lab context:**
    **Enterprise context:**

practice-log.md:
  Each entry is headed by:  ### PL<n>   (e.g. ### PL1, ### PL2)
  Required fields per entry:
    **2-minute version:**
    **30-second version:**
    **Delivery self-score:**

audit-log.md:
  Each entry is headed by:  ### AL<n>   (e.g. ### AL1, ### AL2)
  Required fields per entry:
    **Pitfalls present:**
    **Basic bar verdict:**
    **Staff bar verdict:**
    **Revised sentence:**

behavioral-bank.md (M3):
  Each entry is headed by:  ## Story <n>   (e.g. ## Story 1, ## Story 4)
  Required fields per entry:
    **Category:**   (must be one of: ownership, conflict, failure, influence)
    **Situation:**
    **Task:**
    **Action:**
    **Result:**
    **Learning:**
    **Audit verdict:**
  All four categories must appear across the entries.
  Minimum four entries. No placeholder text in any field.

coding-screen-log.md (M4):
  Each entry is headed by:  ## Screen <n>   (e.g. ## Screen 1, ## Screen 3)
  Required fields per entry:
    **Task:**
    **Clarifying questions:**
    **Approach narration:**
    **Stuck and recovery:**
    **Test cases:**
    **Verdict:**
  Minimum three entries. No placeholder text in any field.

systems-design-log.md (M5):
  Each entry is headed by:  ## Design <n>   (e.g. ## Design 1)
  Required fields per entry:
    **Prompt:**
    **Scope:**
    **Design:**
    **Cost:**
    **Latency:**
    **Reliability:**
    **Evaluation:**
    **Audit verdict:**
  Minimum one entry. No placeholder text in any field.

portfolio-narrative.md (M6):
  Each entry is headed by:  ## Artifact <n>   (e.g. ## Artifact 1)
  Required fields per entry:
    **Artifact:**
    **Overview:**
    **Key decisions:**
    **Tradeoffs:**
    **Failure modes handled:**
    **Role tailoring:**
    **Audit verdict:**
  Minimum one entry. No placeholder text in any field.

deliberate-practice.md (M7):
  Each entry is headed by:  ### DP<n>   (e.g. ### DP1, ### DP7)
  Required fields per entry:
    **Question:**
    **Signal category:**   (must be one of: ownership, conflict, failure, influence, systems-design)
    **Decompose:**         (must be one of: strong, partial, weak)
    **Signal:**            (must be one of: strong, partial, weak)
    **Construct:**         (must be one of: strong, partial, weak)
    **Stress-test:**       (must be one of: strong, partial, weak)
    **Verdict:**
  All five signal categories must appear across the entries.
  Minimum five entries. No placeholder text in any field.

loop-plan.md (M8):
  Each entry is headed by:  ### Stage <name>   (e.g. ### Stage recruiter-screen)
  Required fields per entry:
    **Dossier pieces:**
    **Readiness:**   (must be one of: ready, gap)
    **Plan:**
  All five stage names must appear:
    recruiter-screen, hiring-manager, systems-design-round, portfolio-deep-dive, panel
  Minimum five entries. No placeholder text in any field.
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
SIGNAL_MAP = SCRIPT_DIR / "signal-map.md"
PRACTICE_LOG = SCRIPT_DIR / "practice-log.md"
AUDIT_LOG = SCRIPT_DIR / "audit-log.md"
BEHAVIORAL_BANK = SCRIPT_DIR / "behavioral-bank.md"
CODING_SCREEN_LOG = SCRIPT_DIR / "coding-screen-log.md"
SYSTEMS_DESIGN_LOG = SCRIPT_DIR / "systems-design-log.md"
PORTFOLIO_NARRATIVE = SCRIPT_DIR / "portfolio-narrative.md"
DELIBERATE_PRACTICE = SCRIPT_DIR / "deliberate-practice.md"
LOOP_PLAN = SCRIPT_DIR / "loop-plan.md"

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


def validate_entries(
    entries: list[tuple[str, list[str]]],
    required_fields: list[str],
    min_count: int,
    artifact_name: str,
    messages: list[str],
) -> bool:
    """
    Shared entry-validation logic: check count and required fields for a set
    of entries. Appends messages and returns True if all checks pass.

    `artifact_name` appears in error messages to identify the artifact (e.g.
    "signal-map.md" or "Hard Cases section").
    """
    passed = True
    found_count = len(entries)

    if found_count < min_count:
        messages.append(
            f"FAIL: {artifact_name}: found {found_count} entries; "
            f"need at least {min_count}."
        )
        passed = False
    else:
        messages.append(f"OK:   {artifact_name}: {found_count} entries found.")

    for heading, entry_lines in entries:
        entry_label = heading
        for field in required_fields:
            value = extract_field_value(entry_lines, field)
            if value is None:
                messages.append(f"FAIL: {entry_label}: missing field '{field}'.")
                passed = False
            elif not value:
                messages.append(f"FAIL: {entry_label}: field '{field}' is empty.")
                passed = False
            elif is_placeholder(value):
                messages.append(
                    f"FAIL: {entry_label}: field '{field}' contains placeholder "
                    f"text: {value!r}"
                )
                passed = False

    return passed


# ---------------------------------------------------------------------------
# Decomposition log validator (M1 core)
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

# Hard Cases (M2 extension within decomposition-log.md)
HC_ENTRY_RE = re.compile(r"^###\s+HC(\d+)$")
HARD_CASES_RE = re.compile(r"^##\s+Hard Cases$", re.IGNORECASE)

HC_REQUIRED_FIELDS = [
    "**Senior reading:**",
    "**Primary hypothesis (senior):**",
    "**Staff reading:**",
    "**Primary hypothesis (staff):**",
    "**How the hypothesis shifts:**",
]

MIN_HC_ENTRIES = 3


def validate_decomposition_log(path: Path, check_hard_cases: bool = False) -> tuple[bool, list[str]]:
    """
    Validate decomposition-log.md.

    When `check_hard_cases` is True (M2 mode), also validates the ## Hard Cases
    extension. When False (M1 mode), only the core M1 checks run.

    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append(
            "  Copy decomposition-log.template.md to decomposition-log.md and complete it."
        )
        return False, messages

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    passed = True

    # --- M1: Check for Q-entry headings ---
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

    # --- M1: Check each Q-entry for required fields ---
    for heading, entry_lines in all_entries:
        entry_label = heading
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

    # --- M1: Check calibration section ---
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

    # --- M2 extension: Hard Cases section ---
    if check_hard_cases:
        hard_cases_present = False
        hard_cases_text: list[str] = []
        in_hc_section = False

        for line in lines:
            if HARD_CASES_RE.match(line.strip()):
                hard_cases_present = True
                in_hc_section = True
                continue
            # Stop collecting at any sibling ## heading (but NOT ### headings)
            if in_hc_section and re.match(r"^##\s+(?!#)", line.strip()):
                in_hc_section = False
            if in_hc_section:
                hard_cases_text.append(line)

        if not hard_cases_present:
            messages.append(
                "FAIL: Missing '## Hard Cases' section in decomposition-log.md. "
                "Append it and complete at least three ### HC<n> entries."
            )
            passed = False
        else:
            hc_section_text = "\n".join(hard_cases_text)
            hc_entries = split_into_entries(hc_section_text, HC_ENTRY_RE)
            hc_passed = validate_entries(
                hc_entries, HC_REQUIRED_FIELDS, MIN_HC_ENTRIES,
                "Hard Cases section", messages,
            )
            if not hc_passed:
                passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Answers log validator (M1)
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
        entry_label = heading
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
# Signal map validator (M2)
# ---------------------------------------------------------------------------

SM_ENTRY_RE = re.compile(r"^###\s+SM(\d+)$")

SM_REQUIRED_FIELDS = [
    "**Stated signal:**",
    "**Latent signal:**",
    "**Frontier lab context:**",
    "**Enterprise context:**",
]

MIN_SM_ENTRIES = 3


def validate_signal_map(path: Path) -> tuple[bool, list[str]]:
    """
    Validate signal-map.md.
    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append("  Copy signal-map.template.md to signal-map.md and complete it.")
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    entries = split_into_entries(text, SM_ENTRY_RE)
    entry_passed = validate_entries(
        entries, SM_REQUIRED_FIELDS, MIN_SM_ENTRIES, path.name, messages,
    )
    if not entry_passed:
        passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Practice log validator (M2)
# ---------------------------------------------------------------------------

PL_ENTRY_RE = re.compile(r"^###\s+PL(\d+)$")

PL_REQUIRED_FIELDS = [
    "**2-minute version:**",
    "**30-second version:**",
    "**Delivery self-score:**",
]

MIN_PL_ENTRIES = 2


def validate_practice_log(path: Path) -> tuple[bool, list[str]]:
    """
    Validate practice-log.md.
    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append("  Copy practice-log.template.md to practice-log.md and complete it.")
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    entries = split_into_entries(text, PL_ENTRY_RE)
    entry_passed = validate_entries(
        entries, PL_REQUIRED_FIELDS, MIN_PL_ENTRIES, path.name, messages,
    )
    if not entry_passed:
        passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Audit log validator (M2)
# ---------------------------------------------------------------------------

AL_ENTRY_RE = re.compile(r"^###\s+AL(\d+)$")

AL_REQUIRED_FIELDS = [
    "**Pitfalls present:**",
    "**Basic bar verdict:**",
    "**Staff bar verdict:**",
    "**Revised sentence:**",
]

MIN_AL_ENTRIES = 2


def validate_audit_log(path: Path) -> tuple[bool, list[str]]:
    """
    Validate audit-log.md.
    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append("  Copy audit-log.template.md to audit-log.md and complete it.")
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    entries = split_into_entries(text, AL_ENTRY_RE)
    entry_passed = validate_entries(
        entries, AL_REQUIRED_FIELDS, MIN_AL_ENTRIES, path.name, messages,
    )
    if not entry_passed:
        passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Behavioral bank validator (M3)
# ---------------------------------------------------------------------------

# Heading pattern: ## Story <digits>
BB_ENTRY_RE = re.compile(r"^##\s+Story\s+(\d+)$")

BB_REQUIRED_FIELDS = [
    "**Category:**",
    "**Situation:**",
    "**Task:**",
    "**Action:**",
    "**Result:**",
    "**Learning:**",
    "**Audit verdict:**",
]

# Valid category values (case-insensitive).
VALID_BB_CATEGORIES = {"ownership", "conflict", "failure", "influence"}

MIN_BB_ENTRIES = 4


def validate_behavioral_bank(path: Path) -> tuple[bool, list[str]]:
    """
    Validate behavioral-bank.md.

    Checks that the file has at least four ## Story <n> entries, each with
    all seven required fields filled in and free of placeholder text, and that
    all four categories (ownership, conflict, failure, influence) appear across
    the entries.

    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append(
            "  Copy behavioral-bank.template.md to behavioral-bank.md and complete it."
        )
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    entries = split_into_entries(text, BB_ENTRY_RE)

    # --- Count check ---
    entry_passed = validate_entries(
        entries, BB_REQUIRED_FIELDS, MIN_BB_ENTRIES, path.name, messages,
    )
    if not entry_passed:
        passed = False

    # --- Category check: all four must appear ---
    categories_found: set[str] = set()
    for heading, entry_lines in entries:
        raw = extract_field_value(entry_lines, "**Category:**")
        if raw:
            categories_found.add(raw.strip().lower())

    missing_categories = VALID_BB_CATEGORIES - categories_found
    if missing_categories:
        missing_sorted = sorted(missing_categories)
        messages.append(
            f"FAIL: {path.name}: missing categories: "
            + ", ".join(missing_sorted)
            + ". Each of ownership, conflict, failure, influence must appear."
        )
        passed = False
    else:
        messages.append(
            f"OK:   {path.name}: all four categories present "
            f"({', '.join(sorted(categories_found))})."
        )

    # --- Per-entry category value check ---
    for heading, entry_lines in entries:
        raw = extract_field_value(entry_lines, "**Category:**")
        if raw and not is_placeholder(raw):
            cat = raw.strip().lower()
            if cat not in VALID_BB_CATEGORIES:
                messages.append(
                    f"FAIL: {heading}: **Category:** value {raw!r} is not one of: "
                    + ", ".join(sorted(VALID_BB_CATEGORIES)) + "."
                )
                passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Coding screen log validator (M4)
# ---------------------------------------------------------------------------

# Heading pattern: ## Screen <digits>
CS_ENTRY_RE = re.compile(r"^##\s+Screen\s+(\d+)$")

CS_REQUIRED_FIELDS = [
    "**Task:**",
    "**Clarifying questions:**",
    "**Approach narration:**",
    "**Stuck and recovery:**",
    "**Test cases:**",
    "**Verdict:**",
]

MIN_CS_ENTRIES = 3


def validate_coding_screen_log(path: Path) -> tuple[bool, list[str]]:
    """
    Validate coding-screen-log.md.

    Checks that the file has at least three ## Screen <n> entries, each with
    all six required fields filled in and free of placeholder text.

    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append(
            "  Copy coding-screen-log.template.md to coding-screen-log.md and complete it."
        )
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    entries = split_into_entries(text, CS_ENTRY_RE)
    entry_passed = validate_entries(
        entries, CS_REQUIRED_FIELDS, MIN_CS_ENTRIES, path.name, messages,
    )
    if not entry_passed:
        passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Systems design log validator (M5)
# ---------------------------------------------------------------------------

# Heading pattern: ## Design <digits>
SD_ENTRY_RE = re.compile(r"^##\s+Design\s+(\d+)$")

SD_REQUIRED_FIELDS = [
    "**Prompt:**",
    "**Scope:**",
    "**Design:**",
    "**Cost:**",
    "**Latency:**",
    "**Reliability:**",
    "**Evaluation:**",
    "**Audit verdict:**",
]

MIN_SD_ENTRIES = 1


def validate_systems_design_log(path: Path) -> tuple[bool, list[str]]:
    """
    Validate systems-design-log.md.

    Checks that the file has at least one ## Design <n> entry with all eight
    required fields filled in and free of placeholder text.

    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append(
            "  Copy systems-design-log.template.md to systems-design-log.md and complete it."
        )
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    entries = split_into_entries(text, SD_ENTRY_RE)
    entry_passed = validate_entries(
        entries, SD_REQUIRED_FIELDS, MIN_SD_ENTRIES, path.name, messages,
    )
    if not entry_passed:
        passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Portfolio narrative validator (M6)
# ---------------------------------------------------------------------------

# Heading pattern: ## Artifact <digits>
PN_ENTRY_RE = re.compile(r"^##\s+Artifact\s+(\d+)$")

PN_REQUIRED_FIELDS = [
    "**Artifact:**",
    "**Overview:**",
    "**Key decisions:**",
    "**Tradeoffs:**",
    "**Failure modes handled:**",
    "**Role tailoring:**",
    "**Audit verdict:**",
]

MIN_PN_ENTRIES = 1


def validate_portfolio_narrative(path: Path) -> tuple[bool, list[str]]:
    """
    Validate portfolio-narrative.md.

    Checks that the file has at least one ## Artifact <n> entry with all seven
    required fields filled in and free of placeholder text.

    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append(
            "  Copy portfolio-narrative.template.md to portfolio-narrative.md and complete it."
        )
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    entries = split_into_entries(text, PN_ENTRY_RE)
    entry_passed = validate_entries(
        entries, PN_REQUIRED_FIELDS, MIN_PN_ENTRIES, path.name, messages,
    )
    if not entry_passed:
        passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Deliberate practice log validator (M7)
# ---------------------------------------------------------------------------

# Heading pattern: ### DP<digits>
DP_ENTRY_RE = re.compile(r"^###\s+DP(\d+)$")

DP_REQUIRED_FIELDS = [
    "**Question:**",
    "**Signal category:**",
    "**Decompose:**",
    "**Signal:**",
    "**Construct:**",
    "**Stress-test:**",
    "**Verdict:**",
]

# Valid signal categories for the deliberate practice log.
VALID_DP_CATEGORIES = {"ownership", "conflict", "failure", "influence", "systems-design"}

# Step fields that must hold strong|partial|weak values.
DP_STEP_FIELDS = ["**Decompose:**", "**Signal:**", "**Construct:**", "**Stress-test:**"]

MIN_DP_ENTRIES = 5


def validate_deliberate_practice(path: Path) -> tuple[bool, list[str]]:
    """
    Validate deliberate-practice.md.

    Checks that the file has at least five ### DP<n> entries, each with all seven
    required fields filled in and free of placeholder text; that all five signal
    categories (ownership, conflict, failure, influence, systems-design) appear across
    the entries; and that each of the four step fields (Decompose, Signal, Construct,
    Stress-test) holds one of: strong, partial, weak.

    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append(
            "  Copy deliberate-practice.template.md to deliberate-practice.md and complete it."
        )
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    entries = split_into_entries(text, DP_ENTRY_RE)

    # --- Count and field checks ---
    entry_passed = validate_entries(
        entries, DP_REQUIRED_FIELDS, MIN_DP_ENTRIES, path.name, messages,
    )
    if not entry_passed:
        passed = False

    # --- Category check: all five must appear ---
    categories_found: set[str] = set()
    for heading, entry_lines in entries:
        raw = extract_field_value(entry_lines, "**Signal category:**")
        if raw:
            categories_found.add(raw.strip().lower())

    missing_categories = VALID_DP_CATEGORIES - categories_found
    if missing_categories:
        missing_sorted = sorted(missing_categories)
        messages.append(
            f"FAIL: {path.name}: missing signal categories: "
            + ", ".join(missing_sorted)
            + ". Each of ownership, conflict, failure, influence, systems-design must appear."
        )
        passed = False
    else:
        messages.append(
            f"OK:   {path.name}: all five signal categories present "
            f"({', '.join(sorted(categories_found))})."
        )

    # --- Per-entry category value check ---
    for heading, entry_lines in entries:
        raw = extract_field_value(entry_lines, "**Signal category:**")
        if raw and not is_placeholder(raw):
            cat = raw.strip().lower()
            if cat not in VALID_DP_CATEGORIES:
                messages.append(
                    f"FAIL: {heading}: **Signal category:** value {raw!r} is not one of: "
                    + ", ".join(sorted(VALID_DP_CATEGORIES)) + "."
                )
                passed = False

    # --- Step score value check: each must be strong|partial|weak ---
    for heading, entry_lines in entries:
        for field in DP_STEP_FIELDS:
            value = extract_field_value(entry_lines, field)
            if value is not None and not is_placeholder(value) and value:
                if value.lower() not in VALID_SCORES:
                    messages.append(
                        f"FAIL: {heading}: {field} value {value!r} is not "
                        f"one of: strong, partial, weak."
                    )
                    passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Loop plan validator (M8)
# ---------------------------------------------------------------------------

# Heading pattern: ### Stage <name>
LP_ENTRY_RE = re.compile(r"^###\s+Stage\s+(.+)$")

LP_REQUIRED_FIELDS = [
    "**Dossier pieces:**",
    "**Readiness:**",
    "**Plan:**",
]

# Valid stage names (must match grade_dossier.py STAGE_ORDER exactly).
VALID_LOOP_STAGES = {
    "recruiter-screen",
    "hiring-manager",
    "systems-design-round",
    "portfolio-deep-dive",
    "panel",
}

# Valid readiness values (case-insensitive).
VALID_READINESS = {"ready", "gap"}

MIN_LP_ENTRIES = 5


def validate_loop_plan(path: Path) -> tuple[bool, list[str]]:
    """
    Validate loop-plan.md.

    Checks that the file has at least five ### Stage <name> entries, each with
    all three required fields filled in and free of placeholder text; that all
    five stage names (recruiter-screen, hiring-manager, systems-design-round,
    portfolio-deep-dive, panel) appear; and that each **Readiness:** value is
    one of: ready, gap.

    Returns (passed: bool, messages: list[str]).
    """
    messages: list[str] = []

    if not path.exists():
        messages.append(f"NOT STARTED: {path.name} does not exist yet.")
        messages.append(
            "  Copy loop-plan.template.md to loop-plan.md and complete it."
        )
        return False, messages

    text = path.read_text(encoding="utf-8")
    passed = True

    entries = split_into_entries(text, LP_ENTRY_RE)

    # --- Count and field checks ---
    entry_passed = validate_entries(
        entries, LP_REQUIRED_FIELDS, MIN_LP_ENTRIES, path.name, messages,
    )
    if not entry_passed:
        passed = False

    # --- Stage name check: all five must appear ---
    stages_found: set[str] = set()
    for heading, entry_lines in entries:
        # Heading is "### Stage <name>"; extract the stage name.
        m = LP_ENTRY_RE.match(heading)
        if m:
            stage_name = m.group(1).strip()
            stages_found.add(stage_name.lower())

    missing_stages = VALID_LOOP_STAGES - stages_found
    if missing_stages:
        missing_sorted = sorted(missing_stages)
        messages.append(
            f"FAIL: {path.name}: missing stage entries: "
            + ", ".join(missing_sorted)
            + ". Each of recruiter-screen, hiring-manager, systems-design-round, "
            "portfolio-deep-dive, panel must appear."
        )
        passed = False
    else:
        messages.append(
            f"OK:   {path.name}: all five stages present "
            f"({', '.join(sorted(stages_found))})."
        )

    # --- Per-entry stage name validity check ---
    for heading, entry_lines in entries:
        m = LP_ENTRY_RE.match(heading)
        if m:
            stage_name = m.group(1).strip().lower()
            if stage_name not in VALID_LOOP_STAGES:
                messages.append(
                    f"FAIL: {heading}: stage name {stage_name!r} is not one of: "
                    + ", ".join(sorted(VALID_LOOP_STAGES)) + "."
                )
                passed = False

    # --- Per-entry Readiness value check ---
    for heading, entry_lines in entries:
        raw = extract_field_value(entry_lines, "**Readiness:**")
        if raw and not is_placeholder(raw):
            readiness = raw.strip().lower()
            if readiness not in VALID_READINESS:
                messages.append(
                    f"FAIL: {heading}: **Readiness:** value {raw!r} is not one of: "
                    "ready, gap."
                )
                passed = False

    if passed:
        messages.append(f"PASS: {path.name} is complete.")

    return passed, messages


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check_prep.py",
        description=(
            "Validate the Answer Engineering prep dossier. "
            "Checks logs for completeness and placeholder-free content. "
            "Exits 0 when the required logs for the selected module are complete; "
            "exits 1 otherwise."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Run from exercises/prep/ or any directory; paths resolve relative to this script.\n\n"
            "Module levels:\n"
            "  --module 1   Require decomposition-log.md + answers-log.md complete (M1 gate).\n"
            "  --module 2   Require M1 artifacts + Hard Cases + signal-map.md +\n"
            "               practice-log.md + audit-log.md complete (M2 gate).\n"
            "  --module 3   Require M1 + M2 artifacts + behavioral-bank.md complete (M3 gate).\n"
            "  --module 4   Require M1 + M2 + M3 artifacts + coding-screen-log.md complete\n"
            "               (M4 gate). coding-screen-log.md must have >= 3 Screen entries,\n"
            "               each with all six fields filled and free of placeholder text.\n"
            "               M4 is a SIBLING gate: --module 5/6/7/8 do NOT require it.\n"
            "               --module all DOES require coding-screen-log.md.\n"
            "  --module 5   Require M1 + M2 + M3 artifacts + systems-design-log.md complete (M5 gate).\n"
            "  --module 6   Require M1 + M2 + M3 + M5 artifacts + portfolio-narrative.md complete\n"
            "               (M6 gate).\n"
            "  --module 7   Require M1 + M2 + M3 + M5 + M6 artifacts + deliberate-practice.md\n"
            "               complete (M7 gate). deliberate-practice.md must have >= 5 reps\n"
            "               covering all five signal categories with valid step scores.\n"
            "  --module 8   Require M1 + M2 + M3 + M5 + M6 + M7 artifacts + loop-plan.md\n"
            "               complete (M8 gate). loop-plan.md must have all five stage entries\n"
            "               (recruiter-screen, hiring-manager, systems-design-round,\n"
            "               portfolio-deep-dive, panel) with Readiness ready|gap and Plan filled.\n"
            "  --module all Same as omitting the flag: report all artifacts including M4 and M8.\n\n"
            "Status values per artifact: PASS / INCOMPLETE / NOT STARTED\n"
        ),
    )
    parser.add_argument(
        "--module",
        choices=["1", "2", "3", "4", "5", "6", "7", "8", "all"],
        default="all",
        help=(
            "Module gate to enforce. '1' requires only M1 artifacts. "
            "'2' requires M1 + M2 artifacts. '3' requires M1 + M2 + M3 artifacts. "
            "'4' requires M1 + M2 + M3 + coding-screen-log.md (sibling gate; "
            "M5-M8 do not require coding-screen-log). "
            "'5' requires M1 + M2 + M3 + systems-design-log.md. "
            "'6' requires M1 + M2 + M3 + M5 + portfolio-narrative.md. "
            "'7' requires M1 + M2 + M3 + M5 + M6 + deliberate-practice.md. "
            "'8' requires M1 + M2 + M3 + M5 + M6 + M7 + loop-plan.md. "
            "'all' requires all artifacts including coding-screen-log.md and loop-plan.md. "
            "Default: all."
        ),
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    module = args.module  # "1", "2", "3", "4", "5", "6", "7", "8", or "all"
    require_m2 = module in ("2", "3", "4", "5", "6", "7", "8", "all")
    require_m3 = module in ("3", "4", "5", "6", "7", "8", "all")
    require_m4 = module in ("4", "all")
    require_m5 = module in ("5", "6", "7", "8", "all")
    require_m6 = module in ("6", "7", "8", "all")
    require_m7 = module in ("7", "8", "all")
    require_m8 = module in ("8", "all")

    print("Answer Engineering Prep Dossier Validator")
    print("=" * 44)
    print()

    # Run all validators, collecting results.
    # M1 artifacts are always checked; M2 artifacts are checked when require_m2;
    # M3 artifacts are checked when require_m3.

    check_hard_cases = require_m2

    decomp_passed, decomp_messages = validate_decomposition_log(
        DECOMP_LOG, check_hard_cases=check_hard_cases
    )
    answers_passed, answers_messages = validate_answers_log(ANSWERS_LOG)

    print(f"--- {DECOMP_LOG.name} ---")
    for msg in decomp_messages:
        print(" ", msg)
    print()

    print(f"--- {ANSWERS_LOG.name} ---")
    for msg in answers_messages:
        print(" ", msg)
    print()

    if require_m2:
        sm_passed, sm_messages = validate_signal_map(SIGNAL_MAP)
        pl_passed, pl_messages = validate_practice_log(PRACTICE_LOG)
        al_passed, al_messages = validate_audit_log(AUDIT_LOG)

        print(f"--- {SIGNAL_MAP.name} ---")
        for msg in sm_messages:
            print(" ", msg)
        print()

        print(f"--- {PRACTICE_LOG.name} ---")
        for msg in pl_messages:
            print(" ", msg)
        print()

        print(f"--- {AUDIT_LOG.name} ---")
        for msg in al_messages:
            print(" ", msg)
        print()

    if require_m3:
        bb_passed, bb_messages = validate_behavioral_bank(BEHAVIORAL_BANK)

        print(f"--- {BEHAVIORAL_BANK.name} ---")
        for msg in bb_messages:
            print(" ", msg)
        print()

    if require_m4:
        cs_passed, cs_messages = validate_coding_screen_log(CODING_SCREEN_LOG)

        print(f"--- {CODING_SCREEN_LOG.name} ---")
        for msg in cs_messages:
            print(" ", msg)
        print()

    if require_m5:
        sd_passed, sd_messages = validate_systems_design_log(SYSTEMS_DESIGN_LOG)

        print(f"--- {SYSTEMS_DESIGN_LOG.name} ---")
        for msg in sd_messages:
            print(" ", msg)
        print()

    if require_m6:
        pn_passed, pn_messages = validate_portfolio_narrative(PORTFOLIO_NARRATIVE)

        print(f"--- {PORTFOLIO_NARRATIVE.name} ---")
        for msg in pn_messages:
            print(" ", msg)
        print()

    if require_m7:
        dp_passed, dp_messages = validate_deliberate_practice(DELIBERATE_PRACTICE)

        print(f"--- {DELIBERATE_PRACTICE.name} ---")
        for msg in dp_messages:
            print(" ", msg)
        print()

    if require_m8:
        lp_passed, lp_messages = validate_loop_plan(LOOP_PLAN)

        print(f"--- {LOOP_PLAN.name} ---")
        for msg in lp_messages:
            print(" ", msg)
        print()

    # Build the required artifact lists and results based on module level.
    # Gating is cumulative within each branch.
    # M4 is a sibling to M5-M8: --module 4 requires M1+M2+M3+coding-screen-log
    # but does NOT require M5-M8 artifacts. --module 5/6/7/8 do NOT require
    # coding-screen-log. --module all requires both M4 and M8 chains.
    if require_m8 and require_m4:
        # --module all: requires M1+M2+M3+M4(coding-screen-log)+M5+M6+M7+M8.
        all_passed = (
            decomp_passed and answers_passed
            and sm_passed and pl_passed and al_passed
            and bb_passed and cs_passed and sd_passed and pn_passed
            and dp_passed and lp_passed
        )
        required_names = [
            DECOMP_LOG.name, ANSWERS_LOG.name,
            SIGNAL_MAP.name, PRACTICE_LOG.name, AUDIT_LOG.name,
            BEHAVIORAL_BANK.name, CODING_SCREEN_LOG.name,
            SYSTEMS_DESIGN_LOG.name,
            PORTFOLIO_NARRATIVE.name, DELIBERATE_PRACTICE.name,
            LOOP_PLAN.name,
        ]
        results = [
            decomp_passed, answers_passed,
            sm_passed, pl_passed, al_passed,
            bb_passed, cs_passed, sd_passed, pn_passed, dp_passed,
            lp_passed,
        ]
    elif require_m8:
        # --module 8: requires M1+M2+M3+M5+M6+M7+loop-plan (no coding-screen-log).
        all_passed = (
            decomp_passed and answers_passed
            and sm_passed and pl_passed and al_passed
            and bb_passed and sd_passed and pn_passed
            and dp_passed and lp_passed
        )
        required_names = [
            DECOMP_LOG.name, ANSWERS_LOG.name,
            SIGNAL_MAP.name, PRACTICE_LOG.name, AUDIT_LOG.name,
            BEHAVIORAL_BANK.name, SYSTEMS_DESIGN_LOG.name,
            PORTFOLIO_NARRATIVE.name, DELIBERATE_PRACTICE.name,
            LOOP_PLAN.name,
        ]
        results = [
            decomp_passed, answers_passed,
            sm_passed, pl_passed, al_passed,
            bb_passed, sd_passed, pn_passed, dp_passed,
            lp_passed,
        ]
    elif require_m7:
        all_passed = (
            decomp_passed and answers_passed
            and sm_passed and pl_passed and al_passed
            and bb_passed and sd_passed and pn_passed
            and dp_passed
        )
        required_names = [
            DECOMP_LOG.name, ANSWERS_LOG.name,
            SIGNAL_MAP.name, PRACTICE_LOG.name, AUDIT_LOG.name,
            BEHAVIORAL_BANK.name, SYSTEMS_DESIGN_LOG.name,
            PORTFOLIO_NARRATIVE.name, DELIBERATE_PRACTICE.name,
        ]
        results = [
            decomp_passed, answers_passed,
            sm_passed, pl_passed, al_passed,
            bb_passed, sd_passed, pn_passed, dp_passed,
        ]
    elif require_m6:
        all_passed = (
            decomp_passed and answers_passed
            and sm_passed and pl_passed and al_passed
            and bb_passed and sd_passed and pn_passed
        )
        required_names = [
            DECOMP_LOG.name, ANSWERS_LOG.name,
            SIGNAL_MAP.name, PRACTICE_LOG.name, AUDIT_LOG.name,
            BEHAVIORAL_BANK.name, SYSTEMS_DESIGN_LOG.name,
            PORTFOLIO_NARRATIVE.name,
        ]
        results = [
            decomp_passed, answers_passed,
            sm_passed, pl_passed, al_passed,
            bb_passed, sd_passed, pn_passed,
        ]
    elif require_m5:
        all_passed = (
            decomp_passed and answers_passed
            and sm_passed and pl_passed and al_passed
            and bb_passed and sd_passed
        )
        required_names = [
            DECOMP_LOG.name, ANSWERS_LOG.name,
            SIGNAL_MAP.name, PRACTICE_LOG.name, AUDIT_LOG.name,
            BEHAVIORAL_BANK.name, SYSTEMS_DESIGN_LOG.name,
        ]
        results = [
            decomp_passed, answers_passed,
            sm_passed, pl_passed, al_passed,
            bb_passed, sd_passed,
        ]
    elif require_m4:
        # M4 sibling gate: requires M1+M2+M3+coding-screen-log only.
        all_passed = (
            decomp_passed and answers_passed
            and sm_passed and pl_passed and al_passed
            and bb_passed and cs_passed
        )
        required_names = [
            DECOMP_LOG.name, ANSWERS_LOG.name,
            SIGNAL_MAP.name, PRACTICE_LOG.name, AUDIT_LOG.name,
            BEHAVIORAL_BANK.name, CODING_SCREEN_LOG.name,
        ]
        results = [
            decomp_passed, answers_passed,
            sm_passed, pl_passed, al_passed,
            bb_passed, cs_passed,
        ]
    elif require_m3:
        all_passed = (
            decomp_passed and answers_passed
            and sm_passed and pl_passed and al_passed
            and bb_passed
        )
        required_names = [
            DECOMP_LOG.name, ANSWERS_LOG.name,
            SIGNAL_MAP.name, PRACTICE_LOG.name, AUDIT_LOG.name,
            BEHAVIORAL_BANK.name,
        ]
        results = [
            decomp_passed, answers_passed,
            sm_passed, pl_passed, al_passed,
            bb_passed,
        ]
    elif require_m2:
        all_passed = decomp_passed and answers_passed and sm_passed and pl_passed and al_passed
        required_names = [
            DECOMP_LOG.name, ANSWERS_LOG.name,
            SIGNAL_MAP.name, PRACTICE_LOG.name, AUDIT_LOG.name,
        ]
        results = [decomp_passed, answers_passed, sm_passed, pl_passed, al_passed]
    else:
        all_passed = decomp_passed and answers_passed
        required_names = [DECOMP_LOG.name, ANSWERS_LOG.name]
        results = [decomp_passed, answers_passed]

    if all_passed:
        print(f"RESULT: All required logs are complete. Dossier passes (--module {module}).")
        return 0
    else:
        failed = [name for name, ok in zip(required_names, results) if not ok]
        print(
            f"RESULT: Incomplete (--module {module}). "
            f"Fix the issues above in: {', '.join(failed)}"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
