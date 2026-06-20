"""End-to-end smoke run — a governed 5-agent SWE team ships a feature, offline.

Drives the full composition with deterministic mocks: a feature request ->
architect plans -> two coder nodes implement (the M6 loop) -> tester runs the
suite -> reviewer gates -> the merge is PROPOSED to the shared HITL inbox ->
a human approves through the inbox -> the merge commits, and the audit answers
all four accountability clauses for every action — all under the fleet budget.

No network, no API key, no Docker — standard library only. This is the
BUILD->TEST gate's happy path:

    python smoke.py

The team never auto-merges: the run suspends at the inbox until the (simulated)
human approval lands. A real model run is one import away (client_llm.py +
.env.example); this file stays on the mocks so the gate is deterministic.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile

from fleet import load_fleet

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixture")


def copy_fixture() -> str:
    work = tempfile.mkdtemp(prefix="swe-fleet-")
    for name in os.listdir(FIXTURE):
        if name.endswith(".py"):
            shutil.copy(os.path.join(FIXTURE, name), os.path.join(work, name))
    return work


def print_event(rec: dict) -> None:
    e = rec["event"]
    if e == "plan":
        print(f"  [architect] plan: {rec['slices']}")
    elif e == "act":
        print(f"  [{rec['agent']}] act: {rec['tool']}")
    elif e == "coder_verdict":
        print(f"  [{rec['agent']}] self-test {rec['verdict']}: {rec['detail']}")
    elif e == "tester_verdict":
        print(f"  [{rec['agent']}] acceptance {rec['verdict']}: {rec['detail']}")
    elif e == "review":
        print(f"  [reviewer] approve_merge={rec['approve_merge']} ({rec['reason']})")
    elif e == "merge_proposed":
        print(f"  [inbox] merge PROPOSED -> {rec['inbox_id']} (awaiting human; no auto-merge)")
    elif e == "merged":
        print(f"  [inbox] merge COMMITTED by {rec['by']} ({rec['inbox_id']})")
    elif e in ("blocked", "stop"):
        print(f"  [stop] {rec.get('status', 'blocked')}: {rec.get('reason', '')}")


def main() -> int:
    work = copy_fixture()
    kill_path = os.path.join(work, ".FLEET_KILL")  # never tripped on the happy path
    print(f"Governed SWE fleet — smoke run on {work}")
    print("=" * 68)

    fleet = load_fleet(kill_switch_path=kill_path, on_event=print_event)
    print(f"Registry: {fleet.registry['fleet']} v{fleet.registry['version']} — "
          f"{len(fleet.registry['agents'])} agents, team cap ${fleet.registry['team_daily_usd']}")
    print("-" * 68)

    run = fleet.ship_feature("addition operator", project_root=work)
    print("-" * 68)
    print(f"status (pre-approval): {run.status}  ->  {run.detail}")

    # The HITL gate: nothing merged yet. A human works the inbox.
    pending = fleet.inbox.pending()
    print(f"\nHITL inbox — {len(pending)} proposal(s) awaiting a human:")
    for p in pending:
        print(f"  {p.inbox_id}: {p.summary}")

    # Simulate the operator approving the merge through the inbox (by id).
    if run.merge_inbox_id:
        fleet.inbox.approve(run.merge_inbox_id, by="operator@platform-team",
                            reason="diff reviewed; tests green")
        run = fleet.commit_merge(run, approver="operator@platform-team")
    print(f"\nstatus (post-approval): {run.status}  ->  {run.detail}")

    # The accountability test: which / authority / task / evidence, for the run.
    print("\n" + "=" * 68)
    print("ACCOUNTABILITY — the four clauses for this task:")
    clauses = fleet.audit.answers_four_clauses(run.correlation_id)
    print(f"  which agents      : {clauses['which_agents']}")
    print(f"  under authority   : {len(clauses['under_what_authority'])} authority records")
    print(f"  against task      : {clauses['against_what_task']}")
    print(f"  evidenced by      : {len(clauses['evidenced_by_what'])} evidence records")
    print(f"  COMPLETE (all 4)  : {clauses['complete']}")
    print(f"\nFleet budget: ${run.budget['team_spent_usd']} / ${run.budget['team_daily_usd']} "
          f"team cap  |  by agent: {run.budget['by_agent']}")

    shutil.rmtree(work, ignore_errors=True)
    return 0 if (run.status == "merged" and clauses["complete"]) else 1


if __name__ == "__main__":
    sys.exit(main())
