#!/usr/bin/env python3
"""
grade_dossier.py -- Capstone grader for the Answer Engineering prep dossier.

Composes check_prep and calibrate to grade the reader's whole prep dossier
against the five interview-loop stages and produce a single readiness verdict.

Usage:
  python grade_dossier.py            Grade the dossier and print the report.
  python grade_dossier.py --selftest Run the built-in self-test (exit 0 on pass).
  python grade_dossier.py --help     Show this help text.

Exit code:
  0  VERDICT: READY -- every stage is ready.
  1  VERDICT: NOT READY -- at least one stage has a gap (or dossier files are missing).

Stage map:
  recruiter-screen     validators: portfolio_narrative, answers
  hiring-manager       validators: behavioral_bank            categories: ownership, influence
  systems-design-round validators: systems_design_log         categories: systems-design
  portfolio-deep-dive  validators: portfolio_narrative
  panel                validators: behavioral_bank, portfolio_narrative   categories: conflict, failure

Readiness rule (per stage):
  READY iff all validators passed AND all categories ready AND the stage is planned in loop-plan.md.
  Otherwise GAP, listing which validators failed, which categories are not ready, and whether the plan
  entry is missing.
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Sibling-module imports (resolved relative to this script's directory)
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent

# Add the prep directory to sys.path so sibling imports work from any cwd.
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import check_prep  # noqa: E402
import calibrate   # noqa: E402

# ---------------------------------------------------------------------------
# Stage map
# ---------------------------------------------------------------------------

STAGE_MAP = {
    "recruiter-screen": {
        "validators": ["portfolio_narrative", "answers"],
        "categories": [],
    },
    "hiring-manager": {
        "validators": ["behavioral_bank"],
        "categories": ["ownership", "influence"],
    },
    "systems-design-round": {
        "validators": ["systems_design_log"],
        "categories": ["systems-design"],
    },
    "portfolio-deep-dive": {
        "validators": ["portfolio_narrative"],
        "categories": [],
    },
    "panel": {
        "validators": ["behavioral_bank", "portfolio_narrative"],
        "categories": ["conflict", "failure"],
    },
}

# Ordered list so the report prints in interview-sequence order.
STAGE_ORDER = [
    "recruiter-screen",
    "hiring-manager",
    "systems-design-round",
    "portfolio-deep-dive",
    "panel",
]

# ---------------------------------------------------------------------------
# Validator dispatch
# ---------------------------------------------------------------------------

# Maps validator key -> (function, path_constant)
_VALIDATOR_MAP = {
    "behavioral_bank":    (check_prep.validate_behavioral_bank,    check_prep.BEHAVIORAL_BANK),
    "systems_design_log": (check_prep.validate_systems_design_log,  check_prep.SYSTEMS_DESIGN_LOG),
    "portfolio_narrative":(check_prep.validate_portfolio_narrative, check_prep.PORTFOLIO_NARRATIVE),
    "answers":            (check_prep.validate_answers_log,         check_prep.ANSWERS_LOG),
}


def run_validators() -> dict[str, bool]:
    """Run each validator once and return {key: passed_bool}."""
    results = {}
    for key, (fn, path) in _VALIDATOR_MAP.items():
        passed, _msgs = fn(path)
        results[key] = passed
    return results


# ---------------------------------------------------------------------------
# Loop-plan parsing
# ---------------------------------------------------------------------------

LOOP_PLAN_PATH = _HERE / "loop-plan.md"

# Match "### Stage <name>" headings (case-insensitive).
_STAGE_HEADING_RE = re.compile(r"^###\s+Stage\s+(.+)$", re.IGNORECASE)
# Placeholder patterns mirroring check_prep.PLACEHOLDER_PATTERNS.
_PLACEHOLDER_RE = re.compile(r"\bTODO\b|XXX|<fill|\.\.\.", re.IGNORECASE)


def parse_planned_stages() -> set[str]:
    """
    Read loop-plan.md and return the set of stage names that have a non-empty,
    non-placeholder **Plan:** field.

    Returns an empty set if loop-plan.md does not exist.
    """
    if not LOOP_PLAN_PATH.exists():
        return set()

    text = LOOP_PLAN_PATH.read_text(encoding="utf-8")
    planned: set[str] = set()

    current_stage: str | None = None
    current_lines: list[str] = []

    def _check_stage(stage: str, lines: list[str]) -> None:
        """Inspect the lines of a stage block for a filled-in **Plan:** field."""
        for line in lines:
            stripped = line.strip()
            if stripped.lower().startswith("**plan:**"):
                value = stripped[len("**plan:**"):].strip()
                # Non-empty and not a placeholder -> planned.
                if value and not _PLACEHOLDER_RE.search(value):
                    planned.add(stage)
                return
        # **Plan:** field not found -> not planned.

    for raw_line in text.splitlines():
        m = _STAGE_HEADING_RE.match(raw_line.strip())
        if m:
            # Flush the previous stage block.
            if current_stage is not None:
                _check_stage(current_stage, current_lines)
            current_stage = m.group(1).strip()
            current_lines = []
        else:
            if current_stage is not None:
                current_lines.append(raw_line)

    # Flush the last stage block.
    if current_stage is not None:
        _check_stage(current_stage, current_lines)

    return planned


# ---------------------------------------------------------------------------
# Category readiness from calibrate
# ---------------------------------------------------------------------------

def get_category_readiness() -> dict[str, bool]:
    """
    Return {category: ready_bool} for all calibrate.CATEGORIES.

    Reads calibrate.PRACTICE_LOG; if it is missing or empty, every category
    is not ready.
    """
    if not calibrate.PRACTICE_LOG.exists():
        return {c: False for c in calibrate.CATEGORIES}

    text = calibrate.PRACTICE_LOG.read_text(encoding="utf-8")
    reps, _skipped = calibrate.parse_reps(text)
    report = calibrate.calibrate(reps)
    return {c: report["category_status"][c]["ready"] for c in calibrate.CATEGORIES}


# ---------------------------------------------------------------------------
# Pure grading function (no I/O -- testable with synthetic data)
# ---------------------------------------------------------------------------

def grade_stages(
    validator_pass: dict[str, bool],
    category_ready: dict[str, bool],
    planned: set[str],
) -> dict[str, dict]:
    """
    Grade each stage in STAGE_ORDER against validator results, category readiness,
    and the planned-stage set.

    Returns:
      {
        stage_name: {
          "ready": bool,
          "reasons": list[str],  # empty when ready
        },
        ...
        "_overall": bool,
      }
    """
    results: dict[str, dict] = {}

    for stage in STAGE_ORDER:
        spec = STAGE_MAP[stage]
        reasons: list[str] = []

        # Check validators.
        for v_key in spec["validators"]:
            if not validator_pass.get(v_key, False):
                reasons.append(f"validator {v_key} failed")

        # Check categories.
        for cat in spec["categories"]:
            if not category_ready.get(cat, False):
                reasons.append(f"category '{cat}' not ready")

        # Check plan.
        if stage not in planned:
            reasons.append("loop-plan entry missing or empty")

        results[stage] = {
            "ready": len(reasons) == 0,
            "reasons": reasons,
        }

    overall = all(results[s]["ready"] for s in STAGE_ORDER)
    results["_overall"] = overall  # type: ignore[assignment]
    return results


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

def print_report(grade: dict) -> None:
    print("Answer Engineering Dossier Readiness Report")
    print("=" * 44)
    print()
    for stage in STAGE_ORDER:
        info = grade[stage]
        if info["ready"]:
            print(f"  {stage:<24} READY")
        else:
            reasons_str = ", ".join(info["reasons"])
            print(f"  {stage:<24} GAP: {reasons_str}")
    print()

    overall: bool = grade["_overall"]
    if overall:
        print("VERDICT: READY. All interview stages are prepared.")
    else:
        gaps = [s for s in STAGE_ORDER if not grade[s]["ready"]]
        print(f"VERDICT: NOT READY. Close: {', '.join(gaps)}.")


# ---------------------------------------------------------------------------
# Self-test (pure function only -- no file I/O)
# ---------------------------------------------------------------------------

def selftest() -> int:
    """Test grade_stages on two synthetic cases. Exits 0 on pass, raises on fail."""

    # --- Case 1: fully ready ---
    all_validators_pass = {k: True for k in _VALIDATOR_MAP}
    all_cats_ready = {c: True for c in calibrate.CATEGORIES}
    all_planned = set(STAGE_ORDER)

    g1 = grade_stages(all_validators_pass, all_cats_ready, all_planned)

    assert g1["_overall"] is True, "Case 1: expected overall READY"
    for stage in STAGE_ORDER:
        assert g1[stage]["ready"] is True, f"Case 1: expected {stage} READY, got GAP: {g1[stage]['reasons']}"

    # --- Case 2: mixed gaps ---
    # systems_design_log fails, systems-design category not ready, panel not planned.
    mixed_validators = {k: True for k in _VALIDATOR_MAP}
    mixed_validators["systems_design_log"] = False

    mixed_cats = {c: True for c in calibrate.CATEGORIES}
    mixed_cats["systems-design"] = False

    mixed_planned = set(STAGE_ORDER) - {"panel"}

    g2 = grade_stages(mixed_validators, mixed_cats, mixed_planned)

    assert g2["_overall"] is False, "Case 2: expected overall NOT READY"

    # recruiter-screen: no categories, validators pass, planned -> READY
    assert g2["recruiter-screen"]["ready"] is True, \
        f"Case 2: recruiter-screen should be READY, got: {g2['recruiter-screen']['reasons']}"

    # systems-design-round: validator fails, category not ready -> GAP
    sd = g2["systems-design-round"]
    assert sd["ready"] is False, "Case 2: systems-design-round should be GAP"
    assert any("systems_design_log" in r for r in sd["reasons"]), \
        f"Case 2: systems_design_log missing from reasons: {sd['reasons']}"
    assert any("systems-design" in r for r in sd["reasons"]), \
        f"Case 2: category 'systems-design' missing from reasons: {sd['reasons']}"

    # panel: not planned -> GAP
    panel = g2["panel"]
    assert panel["ready"] is False, "Case 2: panel should be GAP"
    assert any("loop-plan" in r for r in panel["reasons"]), \
        f"Case 2: loop-plan reason missing: {panel['reasons']}"

    # hiring-manager: validators pass, ownership+influence ready, planned -> READY
    assert g2["hiring-manager"]["ready"] is True, \
        f"Case 2: hiring-manager should be READY, got: {g2['hiring-manager']['reasons']}"

    # portfolio-deep-dive: validator passes, no categories, planned -> READY
    assert g2["portfolio-deep-dive"]["ready"] is True, \
        f"Case 2: portfolio-deep-dive should be READY, got: {g2['portfolio-deep-dive']['reasons']}"

    print("grade_dossier.py self-test: PASS")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="grade_dossier.py",
        description=(
            "Grade the Answer Engineering prep dossier against all five interview-loop stages "
            "and print a readiness verdict. "
            "Exits 0 when every stage is READY; exits 1 otherwise."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Run from any directory; all paths resolve relative to this script.\n\n"
            "A stage is READY when:\n"
            "  - All required dossier validators pass for that stage.\n"
            "  - All required signal categories are calibrated-ready (>= 3 reps, latest rep clean).\n"
            "  - A non-placeholder '**Plan:**' field exists under '### Stage <name>' in loop-plan.md.\n"
        ),
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run the built-in self-test on synthetic data and exit 0 on pass.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    # Gather inputs (all file I/O happens here).
    try:
        validator_pass = run_validators()
        category_ready = get_category_readiness()
        planned = parse_planned_stages()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not read dossier files: {exc}", file=sys.stderr)
        return 1

    grade = grade_stages(validator_pass, category_ready, planned)
    print_report(grade)
    return 0 if grade["_overall"] else 1


if __name__ == "__main__":
    sys.exit(main())
