#!/usr/bin/env python3
"""
calibrate.py -- the self-review rubric, as code, for the Answer Engineering prep dossier.

Good calibration is not a feeling; it is a count. This script reads your deliberate-practice
log and prints a scorecard: how many reps you have logged per signal category, how your four
Algorithm steps score across those reps, which step is your weakest, which categories are
under-practiced, and a single readiness verdict.

The rubric IS this file. The scoring dimensions (the four Algorithm steps), the scale
(strong / partial / weak), the category set, and the readiness thresholds are all defined
here as code. The lessons teach you to feed it and read its output; the schema lives here.

Usage:
  python calibrate.py             Score deliberate-practice.md and print the scorecard.
  python calibrate.py --selftest  Run the built-in self-test on synthetic reps (exit 0 on pass).
  python calibrate.py --help      Show this help text.

Exit code (normal run):
  0  READY: every category has at least the minimum reps and its most recent rep has no weak step.
  1  NOT READY (or the log is missing/empty): the verdict lists exactly what to drill.

deliberate-practice.md format
-----------------------------
Each rep is headed by:  ### DP<n>   (e.g. ### DP1, ### DP7)
Required fields per rep (one per line, in any order):
  **Question:**
  **Signal category:**   one of: ownership, conflict, failure, influence, systems-design
  **Decompose:**         strong | partial | weak
  **Signal:**            strong | partial | weak
  **Construct:**         strong | partial | weak
  **Stress-test:**       strong | partial | weak
  **Verdict:**
"""

import argparse
import re
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PRACTICE_LOG = SCRIPT_DIR / "deliberate-practice.md"

# --- The rubric schema (this is the spec, in code) ---------------------------

CATEGORIES = ["ownership", "conflict", "failure", "influence", "systems-design"]
STEPS = ["Decompose", "Signal", "Construct", "Stress-test"]
SCALE = {"strong": 2, "partial": 1, "weak": 0}
MIN_REPS_PER_CATEGORY = 3

DP_ENTRY_RE = re.compile(r"^###\s+DP(\d+)$")


# --- Parsing helpers ---------------------------------------------------------


def split_into_entries(text, heading_pattern):
    """Split text into (heading, lines) sections starting at each heading match."""
    entries = []
    heading = None
    lines = []
    for line in text.splitlines():
        if heading_pattern.match(line.strip()):
            if heading is not None:
                entries.append((heading, lines))
            heading = line.strip()
            lines = []
        elif heading is not None:
            lines.append(line)
    if heading is not None:
        entries.append((heading, lines))
    return entries


def field_value(lines, prefix):
    """Return the text after a '**Field:**' line, lowercased and stripped, or None."""
    plo = prefix.lower()
    for line in lines:
        s = line.strip()
        if s.lower().startswith(plo):
            return s[len(prefix):].strip()
    return None


def parse_reps(text):
    """Parse the log into a list of rep dicts: {category, scores: {step: value}}.

    Only reps with a valid category and all four step scores valid are counted; the
    scorecard reports how many reps were skipped as malformed.
    """
    reps = []
    skipped = 0
    for _heading, lines in split_into_entries(text, DP_ENTRY_RE):
        category = field_value(lines, "**Signal category:**")
        category = category.lower() if category else None
        scores = {}
        ok = category in CATEGORIES
        for step in STEPS:
            raw = field_value(lines, f"**{step}:**")
            val = raw.lower() if raw else None
            if val not in SCALE:
                ok = False
            scores[step] = val
        if ok:
            reps.append({"category": category, "scores": scores})
        else:
            skipped += 1
    return reps, skipped


# --- Scoring -----------------------------------------------------------------


def calibrate(reps):
    """Compute the calibration report structure from a list of rep dicts."""
    per_category = {c: [] for c in CATEGORIES}
    for rep in reps:
        per_category[rep["category"]].append(rep)

    step_dist = {step: {"strong": 0, "partial": 0, "weak": 0} for step in STEPS}
    for rep in reps:
        for step in STEPS:
            step_dist[step][rep["scores"][step]] += 1

    # Weakest step: most weak marks, then fewest strong marks as the tiebreak.
    def step_rank(step):
        d = step_dist[step]
        return (-d["weak"], d["strong"])
    weakest_step = min(STEPS, key=step_rank) if reps else None

    category_status = {}
    for c in CATEGORIES:
        creps = per_category[c]
        count = len(creps)
        latest_has_weak = bool(creps) and any(
            creps[-1]["scores"][s] == "weak" for s in STEPS
        )
        ready = count >= MIN_REPS_PER_CATEGORY and not latest_has_weak
        category_status[c] = {
            "count": count,
            "latest_has_weak": latest_has_weak,
            "ready": ready,
        }

    all_ready = bool(reps) and all(category_status[c]["ready"] for c in CATEGORIES)
    return {
        "total": len(reps),
        "per_category": per_category,
        "step_dist": step_dist,
        "weakest_step": weakest_step,
        "category_status": category_status,
        "ready": all_ready,
    }


def format_scorecard(report, skipped=0):
    """Render the calibration report as the printed scorecard (a list of lines)."""
    out = []
    out.append("Answer Engineering Calibration Scorecard")
    out.append("=" * 40)
    out.append("")
    out.append(f"Reps logged: {report['total']} across {len(CATEGORIES)} categories")
    if skipped:
        out.append(f"  ({skipped} malformed rep(s) skipped: check the field names and scores.)")
    out.append("")

    out.append(f"Per-category reps (need >= {MIN_REPS_PER_CATEGORY} each):")
    for c in CATEGORIES:
        st = report["category_status"][c]
        mark = "ok " if st["count"] >= MIN_REPS_PER_CATEGORY else "GAP"
        need = ""
        if st["count"] < MIN_REPS_PER_CATEGORY:
            need = f"  need {MIN_REPS_PER_CATEGORY - st['count']} more"
        out.append(f"  {c:<16}{st['count']:>2}  {mark}{need}")
    out.append("")

    out.append("Step calibration (across all reps):")
    for step in STEPS:
        d = report["step_dist"][step]
        flag = "  <- weakest step" if step == report["weakest_step"] and report["total"] else ""
        out.append(
            f"  {step:<12} strong {d['strong']:<3} partial {d['partial']:<3} weak {d['weak']:<3}{flag}"
        )
    out.append("")

    out.append("Readiness by category (latest rep must have no weak step):")
    for c in CATEGORIES:
        st = report["category_status"][c]
        if st["ready"]:
            label = "READY"
        elif st["count"] < MIN_REPS_PER_CATEGORY:
            label = f"NOT READY (need {MIN_REPS_PER_CATEGORY - st['count']} more rep(s))"
        elif st["latest_has_weak"]:
            label = "NOT READY (latest rep has a weak step)"
        else:
            label = "NOT READY"
        out.append(f"  {c:<16}{label}")
    out.append("")

    if report["ready"]:
        out.append("VERDICT: READY. Every category is practiced and its latest rep is clean.")
    else:
        drill = []
        for c in CATEGORIES:
            st = report["category_status"][c]
            if st["count"] < MIN_REPS_PER_CATEGORY:
                drill.append(f"{c} (reps)")
            elif st["latest_has_weak"]:
                drill.append(f"{c} (clean rep)")
        if report["weakest_step"] and report["total"]:
            wd = report["step_dist"][report["weakest_step"]]
            if wd["weak"]:
                drill.append(f"{report['weakest_step']} step across the bank")
        drill_str = "; ".join(drill) if drill else "log more reps"
        out.append(f"VERDICT: NOT READY. Drill: {drill_str}.")
    return out


# --- Self-test ---------------------------------------------------------------


def _synthetic_log():
    """A synthetic log exercising: an under-practiced category, a category whose latest
    rep has a weak step, a clear weakest step (Stress-test), and one malformed rep."""
    blocks = []

    def rep(n, cat, d, s, c, t):
        return (
            f"### DP{n}\n"
            f"**Question:** practice question {n}\n"
            f"**Signal category:** {cat}\n"
            f"**Decompose:** {d}\n**Signal:** {s}\n**Construct:** {c}\n**Stress-test:** {t}\n"
            f"**Verdict:** noted\n"
        )

    # ownership: 3 reps, latest clean -> READY
    blocks += [rep(1, "ownership", "strong", "strong", "strong", "partial"),
               rep(2, "ownership", "strong", "partial", "strong", "partial"),
               rep(3, "ownership", "strong", "strong", "strong", "strong")]
    # conflict: 3 reps, latest has a weak step -> NOT READY
    blocks += [rep(4, "conflict", "strong", "strong", "partial", "weak"),
               rep(5, "conflict", "partial", "partial", "partial", "weak"),
               rep(6, "conflict", "strong", "partial", "partial", "weak")]
    # failure: 1 rep -> under-practiced
    blocks += [rep(7, "failure", "partial", "weak", "partial", "weak")]
    # influence: 0 reps
    # systems-design: 3 reps, latest clean -> READY
    blocks += [rep(8, "systems-design", "strong", "strong", "strong", "partial"),
               rep(9, "systems-design", "strong", "strong", "partial", "partial"),
               rep(10, "systems-design", "strong", "strong", "strong", "strong")]
    # one malformed rep (bad score) -> skipped
    blocks.append(
        "### DP11\n**Question:** bad\n**Signal category:** ownership\n"
        "**Decompose:** great\n**Signal:** strong\n**Construct:** strong\n"
        "**Stress-test:** strong\n**Verdict:** x\n"
    )
    return "\n".join(blocks)


def selftest():
    text = _synthetic_log()
    reps, skipped = parse_reps(text)
    assert skipped == 1, f"expected 1 malformed rep skipped, got {skipped}"
    assert len(reps) == 10, f"expected 10 valid reps, got {len(reps)}"

    report = calibrate(reps)
    cs = report["category_status"]
    assert cs["ownership"]["ready"] is True, "ownership should be READY"
    assert cs["conflict"]["ready"] is False and cs["conflict"]["latest_has_weak"], \
        "conflict latest rep has a weak step -> NOT READY"
    assert cs["failure"]["count"] == 1 and cs["failure"]["ready"] is False, \
        "failure is under-practiced"
    assert cs["influence"]["count"] == 0 and cs["influence"]["ready"] is False, \
        "influence has no reps"
    assert cs["systems-design"]["ready"] is True, "systems-design should be READY"
    assert report["weakest_step"] == "Stress-test", \
        f"Stress-test should be weakest, got {report['weakest_step']}"
    assert report["ready"] is False, "overall should be NOT READY"

    # Round-trip through a real temp file to prove file reading works too.
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "deliberate-practice.md"
        p.write_text(text, encoding="utf-8")
        reps2, skipped2 = parse_reps(p.read_text(encoding="utf-8"))
        assert len(reps2) == 10 and skipped2 == 1

    # An all-ready log must verdict READY and the formatter must say so.
    ready_text = "\n".join(
        f"### DP{i}\n**Question:** q{i}\n**Signal category:** {c}\n"
        f"**Decompose:** strong\n**Signal:** strong\n**Construct:** strong\n"
        f"**Stress-test:** strong\n**Verdict:** ok\n"
        for i, c in enumerate(CATEGORIES * MIN_REPS_PER_CATEGORY, start=1)
    )
    rready, _ = parse_reps(ready_text)
    assert calibrate(rready)["ready"] is True, "a full clean log should be READY"

    print("calibrate.py self-test: PASS")
    return 0


# --- Main --------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        prog="calibrate.py",
        description="Score the deliberate-practice log and print a calibration scorecard.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--selftest", action="store_true",
        help="Run the built-in self-test on synthetic reps and exit.",
    )
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    if not PRACTICE_LOG.exists():
        print("No practice logged yet.")
        print(f"  Create {PRACTICE_LOG.name} (copy deliberate-practice.template.md) and log your reps.")
        return 1

    text = PRACTICE_LOG.read_text(encoding="utf-8")
    reps, skipped = parse_reps(text)
    report = calibrate(reps)
    for line in format_scorecard(report, skipped):
        print(line)
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
