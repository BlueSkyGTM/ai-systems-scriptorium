"""BUILD->TEST gate — the governed SWE fleet and its operator console.

Standard library + pytest only. No network, no API key, no Docker. Run with:

    python -m pytest tests/

Each test pins one claim the finale makes:
  - the team ships a feature end to end (architect -> coders -> tester -> reviewer
    -> human-approved merge);
  - the fleet budget stops a runaway on the PER-AGENT cap AND on the TEAM cap;
  - the shared HITL inbox blocks an unapproved (and off-channel) merge;
  - an off-registry agent is refused before it acts;
  - the cross-agent audit answers all four accountability clauses;
  - the kill switch halts the fleet before the next action.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from a2a import A2AError, A2ATask  # noqa: E402
from fleet import Fleet, load_fleet  # noqa: E402
from governance.fleet_budget import BudgetBreach, FleetBudgetGuard, TaskBudget  # noqa: E402
from governance.inbox import InboxError, SharedInbox  # noqa: E402
from governance.killswitch import KillSwitch, OperatorKillSwitch  # noqa: E402
from mock_llm import CoderMockLLM, StuckCoderMockLLM  # noqa: E402
from policy import FleetPolicy, Unauthorized  # noqa: E402
from schema import RegistryError, load_registry, validate  # noqa: E402

FIXTURE = os.path.join(ROOT, "fixture")


@pytest.fixture()
def work_dir():
    work = tempfile.mkdtemp(prefix="swe-fleet-test-")
    for name in os.listdir(FIXTURE):
        if name.endswith(".py"):
            shutil.copy(os.path.join(FIXTURE, name), os.path.join(work, name))
    yield work
    shutil.rmtree(work, ignore_errors=True)


def make_fleet(work_dir, **kwargs):
    return load_fleet(kill_switch_path=os.path.join(work_dir, ".FLEET_KILL"), **kwargs)


# --- 1) the team ships a feature end to end ------------------------------------

def test_team_ships_a_feature_end_to_end(work_dir):
    """architect -> coders -> tester -> reviewer -> proposal -> human merge."""
    fleet = make_fleet(work_dir)
    run = fleet.ship_feature("addition operator", project_root=work_dir)

    # The run suspends at the inbox — nothing merged without a human.
    assert run.status == "awaiting_approval"
    assert run.merge_inbox_id is not None
    assert len(fleet.inbox.pending()) == 1

    # The human approves through the inbox; the merge commits.
    fleet.inbox.approve(run.merge_inbox_id, by="operator")
    merged = fleet.commit_merge(run, approver="operator")
    assert merged.status == "merged"


# --- 2) the fleet budget stops a runaway: per-agent AND team cap ---------------

def test_fleet_budget_stops_per_agent_runaway(work_dir):
    """A single coder that loops forever trips ITS OWN per-agent cap before the
    team cap — attribution catches the runaway delegation the manager-only cap
    would miss."""
    # Give coder-1 a tiny cap; leave the team cap generous so the per-agent wall
    # is what fires.
    guard = FleetBudgetGuard(
        team_daily_usd=100.0,
        per_agent={a["id"]: TaskBudget(max_usd=(0.025 if a["id"] == "coder-1" else 100.0))
                   for a in load_registry()["agents"]},
    )
    fleet = make_fleet(work_dir)
    fleet.budget = guard
    run = fleet.ship_feature("addition operator", project_root=work_dir,
                             models={"coder-1": StuckCoderMockLLM()})
    assert run.status == "budget_breach"
    assert "coder-1" in run.detail and "per-agent" in run.detail

    # And the unit: a swarm of small agents under one team cap trips the TEAM
    # cap even though no single agent exceeds its own.
    team = FleetBudgetGuard(team_daily_usd=0.05,
                            per_agent={"a": TaskBudget(1.0), "b": TaskBudget(1.0)})
    team.charge("a", 0.03)
    with pytest.raises(BudgetBreach) as exc:
        team.charge("b", 0.03)  # neither agent over its own cap; team cap blown
    assert "team cap" in str(exc.value)


def test_fleet_budget_stops_team_runaway_in_full_run(work_dir):
    """With a tight TEAM cap, the run stops on the team ceiling mid-team."""
    guard = FleetBudgetGuard(
        team_daily_usd=0.05,  # ~5 calls of headroom for the whole team
        per_agent={a["id"]: TaskBudget(max_usd=100.0) for a in load_registry()["agents"]},
    )
    fleet = make_fleet(work_dir)
    fleet.budget = guard
    run = fleet.ship_feature("addition operator", project_root=work_dir)
    assert run.status == "budget_breach"
    assert "team cap" in run.detail


# --- 3) the shared HITL inbox blocks an unapproved / off-channel merge ----------

def test_inbox_blocks_unapproved_merge(work_dir):
    """commit_merge refuses when the proposal has no inbox approval."""
    fleet = make_fleet(work_dir)
    run = fleet.ship_feature("addition operator", project_root=work_dir)
    assert run.status == "awaiting_approval"

    # Try to commit WITHOUT approving — the gate refuses; nothing merges.
    not_merged = fleet.commit_merge(run, approver="sneaky")
    assert not_merged.status == "awaiting_approval"
    assert "no inbox approval" in not_merged.detail
    assert not fleet.inbox.is_approved(run.merge_inbox_id)


def test_inbox_refuses_off_channel_approval():
    """Approval happens only through the inbox, by id. There is no other path,
    and an approval must name a human principal (the evidence clause)."""
    inbox = SharedInbox()
    inbox_id = inbox.submit(agent_id="reviewer-01", correlation_id="corr-x",
                            action="merge", summary="merge X")
    with pytest.raises(InboxError):
        inbox.approve(inbox_id, by="")  # no named principal -> refused
    with pytest.raises(InboxError):
        inbox.approve("inbox-does-not-exist", by="operator")  # no such proposal
    # Legitimate path works, and a proposal cannot be decided twice.
    inbox.approve(inbox_id, by="operator")
    with pytest.raises(InboxError):
        inbox.reject(inbox_id, by="operator")


# --- 4) an off-registry agent is refused before it acts ------------------------

def test_off_registry_agent_is_refused():
    """An agent not on the registry has no identity and no owner — refused."""
    policy = FleetPolicy(load_registry())
    assert policy.known("coder-1")
    assert not policy.known("ghost-agent")
    with pytest.raises(Unauthorized):
        policy.manifest("ghost-agent")
    with pytest.raises(Unauthorized):
        policy.authority("ghost-agent")


def test_tool_outside_grant_is_refused():
    """Least privilege: a reviewer (read-only) may not write code or merge."""
    policy = FleetPolicy(load_registry())
    policy.authorize_tool("reviewer-01", "read_file")  # granted
    with pytest.raises(Unauthorized):
        policy.authorize_tool("reviewer-01", "write_file")  # not granted
    # No agent on this team may merge — the merge is a human gate.
    for a in load_registry()["agents"]:
        with pytest.raises(Unauthorized):
            policy.authorize_merge(a["id"])


# --- 5) the audit answers all four accountability clauses ----------------------

def test_audit_answers_four_clauses(work_dir):
    """which / authority / task / evidence — for every action, end to end."""
    fleet = make_fleet(work_dir)
    run = fleet.ship_feature("addition operator", project_root=work_dir)
    fleet.inbox.approve(run.merge_inbox_id, by="operator")
    fleet.commit_merge(run, approver="operator")

    clauses = fleet.audit.answers_four_clauses(run.correlation_id)
    assert clauses["complete"] is True
    # The chain names every agent that acted, including the human merge.
    agents = set(clauses["which_agents"])
    assert {"architect-01", "coder-1", "coder-2", "tester-01", "reviewer-01", "operator"} <= agents
    # Every record carries all four clauses populated.
    for rec in fleet.audit.by_correlation(run.correlation_id):
        assert rec.agent and rec.authority and rec.task and rec.evidence
    # A correlation id with no records cannot answer the clauses.
    assert fleet.audit.answers_four_clauses("corr-nonexistent")["complete"] is False


# --- 6) the kill switch halts the fleet before the next action -----------------

def test_kill_switch_halts_the_fleet(work_dir):
    """A tripped switch stops the team before its next action — and the agents
    hold a read-only handle, so they cannot clear their own stop."""
    kill_path = os.path.join(work_dir, ".FLEET_KILL")
    operator = OperatorKillSwitch(kill_path)
    operator.engage("operator halt for test")

    agent_view = KillSwitch(kill_path)  # what the fleet's loops are handed
    assert not hasattr(agent_view, "engage")  # read-only — no write path

    fleet = make_fleet(work_dir)
    run = fleet.ship_feature("addition operator", project_root=work_dir)
    assert run.status == "halted"
    # Nothing merged, and the team did no work.
    assert run.budget["team_spent_usd"] == 0.0


# --- supporting gates: schema validation + A2A wire contract -------------------

def test_registry_validates_against_schema():
    """The shipped registry passes its JSON Schema; a malformed one fails."""
    load_registry()  # raises if invalid
    bad = {"fleet": "x", "version": "1", "team_daily_usd": 1.0,
           "agents": [{"id": "a", "role": "wizard", "owner": "o",
                       "autonomy_tier": "F9", "budget_daily_usd": 1.0,
                       "permissions": {"tools": [], "can_write_code": False, "can_merge": False}}]}
    with pytest.raises(RegistryError):
        validate(bad)


def test_a2a_handoff_fails_at_the_boundary():
    """A malformed handoff fails on receipt, not three steps downstream."""
    task = A2ATask("wrong_skill", "architect-01", "coder", "corr-1", {})
    with pytest.raises(A2AError):
        task.validate(accepted_skills={"implement_slice"})
    missing_corr = A2ATask("implement_slice", "architect-01", "coder", "", {})
    with pytest.raises(A2AError):
        missing_corr.validate(accepted_skills={"implement_slice"})


def test_smoke_main_exits_zero(work_dir):
    """The smoke entry point returns 0: team ships and the audit is complete."""
    import smoke
    assert smoke.main() == 0
