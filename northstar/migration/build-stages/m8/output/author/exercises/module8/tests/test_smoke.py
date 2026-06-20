"""BUILD->TEST gate for the Final Systems Engineering Exam.

Standard library + pytest only. No network, no API key, no Docker. The exam
imports the SHIPPED M7 governed fleet (it does not rebuild one) and grades what the
fleet produces. Run with:

    python -m pytest tests/

Each test pins one exam claim:
  - the exam ships a system via the REAL M7 fleet (not a copy);
  - the rubric PASSES an honest run;
  - the rubric FAILS a deliberately-deficient run (merge unapproved -> R5/R1 fail;
    kill switch tripped -> nothing ships);
  - an operator surface works (the HITL inbox gate and the kill switch).
"""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fleet_adapter import resolve_fleet_dir  # noqa: E402
from rubric import CRITERIA, grade  # noqa: E402
from run_exam import run_exam  # noqa: E402
from spec import SpecError, load_spec, parse_spec  # noqa: E402

SAMPLE = os.path.join(ROOT, "sample_spec.md")


# --- 0) the harness imports the REAL M7 fleet, not a rebuild -------------------

def test_adapter_resolves_the_real_m7_fleet():
    """The exam points at the shipped artifact-03 fleet on disk — its real path,
    with its real fleet.py — never a copy vendored into the exam."""
    fleet_dir = resolve_fleet_dir()
    assert fleet_dir.replace("\\", "/").endswith(
        "exercises/module7/03-governed-multi-agent-fleet"
    )
    assert os.path.isfile(os.path.join(fleet_dir, "fleet.py"))
    # The exam directory does NOT contain its own fleet.py — reuse, not rebuild.
    assert not os.path.isfile(os.path.join(ROOT, "fleet.py"))


# --- 1) the exam ships a system via the M7 fleet ------------------------------

def test_exam_ships_a_system_via_the_m7_fleet():
    """The real fleet plans, implements, tests, gates, and (on approval) merges —
    the produced system ships end to end."""
    exam = run_exam(SAMPLE)
    assert exam.status == "merged"
    assert exam.merge_approved_by == "operator@exam"
    assert exam.merge_inbox_id is not None
    # The fleet actually decomposed and built it (the architect produced a plan).
    assert len(exam.plan) >= 1
    # The audit threaded every agent under one correlation id.
    agents = set(exam.audit_clauses["which_agents"])
    assert {"architect-01", "coder-1", "coder-2", "tester-01", "reviewer-01", "operator"} <= agents


# --- 2) the rubric PASSES the honest run --------------------------------------

def test_rubric_passes_the_honest_run():
    """A clean, governed, in-budget, human-approved run passes all seven criteria."""
    exam = run_exam(SAMPLE)
    report = grade(exam)
    assert report.passed is True
    assert report.failed() == []
    assert len(report.results) == len(CRITERIA) == 7


# --- 3a) the rubric FAILS a deficient run: merge never approved (HITL gate) ----

def test_rubric_fails_when_merge_is_not_human_approved():
    """Leave the merge proposal pending — no human approval through the inbox. The
    fleet refuses to auto-merge, so the system never ships: R5 (HITL) and R1 (runs)
    fail. This is the deliberately-deficient run."""
    exam = run_exam(SAMPLE, auto_approve=False)
    assert exam.status == "awaiting_approval"   # the fleet did NOT auto-merge
    assert exam.merge_approved_by is None

    report = grade(exam)
    assert report.passed is False
    failed_ids = {r.rid for r in report.failed()}
    assert "R5" in failed_ids   # HITL-GOVERNED: no human approval on record
    assert "R1" in failed_ids   # RUNS: the system never shipped


# --- 3b) the rubric FAILS a deficient run: spec missing framing/version --------

def test_rubric_fails_a_spec_missing_framing_and_tests():
    """A spec with a track but no reference architecture, no problem line, no
    version, and no acceptance criteria fails R6 and R7 even if the fleet ships."""
    thin_spec = parse_spec(
        "**Track:** agentic-system\n**Feature:** addition operator\n"
    )
    exam = run_exam(SAMPLE)
    exam.spec = thin_spec   # graft the deficient spec onto an otherwise-clean run

    report = grade(exam)
    assert report.passed is False
    failed_ids = {r.rid for r in report.failed()}
    assert "R6" in failed_ids   # PROBLEM-FRAMED: missing ref arch + problem line
    assert "R7" in failed_ids   # TESTED+VERSIONED: missing criteria + version


# --- 4) an operator surface works: the kill switch halts the fleet ------------

def test_kill_switch_halts_the_fleet_before_it_ships():
    """The operator trips the kill switch before the run; the real fleet halts
    before the next action and ships nothing — and the rubric fails the run."""
    exam = run_exam(SAMPLE, kill_first=True)
    assert exam.halted is True
    assert exam.status == "halted"
    assert exam.merge_approved_by is None
    # No work was done — the team never spent against the budget.
    assert exam.budget.get("team_spent_usd") == 0.0

    report = grade(exam)
    assert report.passed is False


# --- 4b) an operator surface works: the HITL inbox is the only merge path ------

def test_hitl_inbox_is_the_only_path_to_a_merge():
    """An honest run only merges because a human approved through the inbox by id;
    without that approval the same run does not merge. The inbox is the gate."""
    approved = run_exam(SAMPLE, auto_approve=True)
    pending = run_exam(SAMPLE, auto_approve=False)
    assert approved.status == "merged"
    assert pending.status == "awaiting_approval"
    # Same fleet, same spec — the only difference is the human decision in the inbox.
    assert approved.merge_inbox_id is not None
    assert pending.merge_inbox_id is not None


# --- supporting: the spec parser refuses a spec with no valid track -----------

def test_spec_requires_a_valid_track():
    with pytest.raises(SpecError):
        parse_spec("**Feature:** something\n**Version:** 1.0.0\n")
    # The sample spec parses and carries its fields.
    spec = load_spec(SAMPLE)
    assert spec.track == "agentic-system"
    assert spec.version == "1.0.0"
    assert spec.declares_tests()
    assert spec.has_framing()


# --- supporting: the guide rubric == this rubric (the coherence invariant) -----

def test_rubric_has_exactly_the_seven_guide_criteria():
    """The rubric grades exactly the seven criteria the guide documents, in order.
    If the guide and code drift, this catches it at the level of the criterion ids."""
    ids = [rid for rid, _ in CRITERIA]
    assert ids == ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
