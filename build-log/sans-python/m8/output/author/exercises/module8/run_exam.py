"""The exam driver — point the shipped M7 fleet at a task spec, under the console.

This is the exam in one file. It does NOT build a system; the governed M7 fleet
does. The driver's whole job is to be the operator:

    1. read a task spec (the chosen track + reference architecture + acceptance
       criteria), written by the student in ``spec_template.md`` form;
    2. load the REAL M7 fleet through the adapter (no rebuild);
    3. point the fleet at the spec's feature, against the produced-system fixture;
    4. work the operator console — suspend at the HITL inbox, approve (or reject)
       the merge by id, hold the kill switch;
    5. capture the produced system + the audit + the budget into an ``ExamRun`` the
       rubric grades.

The result is deterministic on the mock LLM the M7 fleet already ships, so the
exam's BUILD->TEST gate runs offline on the standard library alone. A real model
is a one-line swap on any node (``models={...}``) — the contract does not change.

This file is the bridge between the spec and the grade. The fleet is the
substrate, the spec is the input, your judgment is the grade.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass, field

from fleet_adapter import load_real_fleet, resolve_fleet_dir
from spec import TaskSpec, load_spec


@dataclass
class ExamRun:
    """Everything the rubric needs to grade one exam, captured from a real fleet run.

    This is the operator's record of the run: did the fleet ship the system, was
    the merge human-approved, what does the audit say, did it stay under budget?
    The rubric reads only this — it never re-runs the fleet."""

    spec: TaskSpec
    status: str                       # the FleetRun status: "merged" | "blocked" | ...
    detail: str
    correlation_id: str
    merge_approved_by: str | None     # the human who approved through the inbox, or None
    merge_inbox_id: str | None
    audit_clauses: dict = field(default_factory=dict)  # answers_four_clauses(corr)
    budget: dict = field(default_factory=dict)         # the fleet budget summary
    plan: list = field(default_factory=list)
    halted: bool = False              # the kill switch tripped the run
    events: list = field(default_factory=list)         # the operator's event log


def _produced_system_dir() -> str:
    """Copy the M7 fixture into a throwaway dir — the 'system' the fleet ships.

    The fleet builds *a version of* the reference architecture by working a real
    project: the M7 fixture is a tiny broken project whose acceptance suite the
    fleet must make pass. On a live run this would be your real repo; on the
    offline gate it is the fixture the fleet already knows how to ship."""
    fleet_dir = resolve_fleet_dir()
    fixture = os.path.join(fleet_dir, "fixture")
    work = tempfile.mkdtemp(prefix="exam-system-")
    for name in os.listdir(fixture):
        if name.endswith(".py"):
            shutil.copy(os.path.join(fixture, name), os.path.join(work, name))
    return work


def run_exam(spec_path: str, *, auto_approve: bool = True,
             approver: str = "operator@exam", models: dict | None = None,
             kill_first: bool = False) -> ExamRun:
    """Run one exam: point the real M7 fleet at ``spec_path`` under the console.

    ``auto_approve`` simulates the operator approving the merge through the inbox
    (the HITL gate) so the offline gate is non-interactive; set it False to leave
    the proposal pending (an honest 'awaiting_approval' that the rubric fails).
    ``kill_first`` engages the kill switch before the run, to exercise that
    operator surface. ``models`` swaps a real model onto any node, unchanged.
    """
    spec = load_spec(spec_path)
    system_dir = _produced_system_dir()
    events: list = []

    kill_path = os.path.join(system_dir, ".FLEET_KILL")
    if kill_first:
        # The operator's write path to the kill switch (held outside the fleet).
        with open(kill_path, "w", encoding="utf-8") as f:
            f.write("operator halt before run")

    fleet = load_real_fleet(kill_switch_path=kill_path, on_event=events.append)

    # Point the fleet at the spec's feature. This is `ship_feature` on the REAL
    # orchestrator — architect plans, coders implement (the M6 loop), tester
    # verifies, reviewer gates, merge PROPOSED to the inbox. It never auto-merges.
    run = fleet.ship_feature(spec.feature, project_root=system_dir, models=models)

    merge_approved_by: str | None = None
    if run.status == "awaiting_approval" and auto_approve and run.merge_inbox_id:
        # Work the HITL inbox: approve the merge by id (the only legal path), then
        # commit through the propose-then-commit gate.
        fleet.inbox.approve(run.merge_inbox_id, by=approver,
                            reason="exam: diff reviewed, acceptance suite green")
        run = fleet.commit_merge(run, approver=approver)
        if run.status == "merged":
            merge_approved_by = approver

    clauses = fleet.audit.answers_four_clauses(run.correlation_id)

    exam = ExamRun(
        spec=spec,
        status=run.status,
        detail=run.detail,
        correlation_id=run.correlation_id,
        merge_approved_by=merge_approved_by,
        merge_inbox_id=run.merge_inbox_id,
        audit_clauses=clauses,
        budget=run.budget,
        plan=run.plan,
        halted=(run.status == "halted"),
        events=events,
    )
    shutil.rmtree(system_dir, ignore_errors=True)
    return exam


if __name__ == "__main__":  # pragma: no cover - manual entry point
    import sys
    spec_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "sample_spec.md")
    exam = run_exam(spec_path)
    print(f"track    : {exam.spec.track}")
    print(f"reference: {exam.spec.reference_architecture}")
    print(f"status   : {exam.status} -> {exam.detail}")
    print(f"approved : {exam.merge_approved_by}")
    print(f"audit ok : {exam.audit_clauses.get('complete')}")
    print(f"budget   : ${exam.budget.get('team_spent_usd')} / ${exam.budget.get('team_daily_usd')}")
