"""BUILD->TEST gate — the team composition and its operator surfaces.

Standard library + pytest only. No network, no API key, no Docker. Run with:

    python -m pytest tests/

Each test pins one claim the chapter makes:
  - the composition completes — a team (supervisor + N sub-agents) plans,
    verifies, and synthesizes a cited answer (not one agent);
  - an unverified sub-result is REJECTED, not synthesized (the verification gap
    closed — a fabricated citation never reaches the report);
  - a fleet budget breach stops the whole team before the next action;
  - the kill switch halts the team, and no agent can clear it.
"""

from __future__ import annotations

import os
import sys
import tempfile

import pytest

# Make the artifact root importable when pytest is invoked from anywhere.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import supervisor  # noqa: E402
import verify_gate  # noqa: E402
from budget import FleetBudget  # noqa: E402
from corpus import CORPUS  # noqa: E402
from killswitch import KillSwitch, OperatorKillSwitch  # noqa: E402
from mock_llm import FabricatingMockLLM, LoopingMockLLM, MockLLM  # noqa: E402

QUESTION = "What makes a multi-agent system reliable in production?"


@pytest.fixture()
def kill_path():
    path = os.path.join(tempfile.mkdtemp(prefix="research-team-"), ".KILL")
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_composition_completes_as_a_team(kill_path):
    """The happy path: a team plans, every sub-agent answers, the gate accepts,
    the Solver synthesizes. This is more than one agent — assert the team shape."""
    result = supervisor.run_team(
        question=QUESTION,
        model=MockLLM(),
        corpus=CORPUS,
        budget=FleetBudget(max_usd=1.00, max_calls=20),
        kill_switch=KillSwitch(kill_path),
    )
    assert result.status == "synthesized"
    # A team coordinated: a multi-step plan, one sub-agent per sub-question.
    assert len(result.plan) >= 2
    assert len(result.verified) == len(result.plan)
    assert not result.rejected
    # The answer carries citations through from the verified findings.
    assert "[S1]" in result.answer
    # Spend is attributed across multiple agents, not one.
    by_agent = result.budget["by_agent"]
    sub_agents = [a for a in by_agent if a.startswith("sq")]
    assert len(sub_agents) >= 2


def test_unverified_subresult_is_rejected_not_synthesized(kill_path):
    """A sub-agent cites a source it never retrieved. The gate REJECTS the
    finding and it never enters the synthesized answer — the verification gap,
    closed."""
    result = supervisor.run_team(
        question=QUESTION,
        model=FabricatingMockLLM(),
        corpus=CORPUS,
        budget=FleetBudget(max_usd=1.00, max_calls=20),
        kill_switch=KillSwitch(kill_path),
    )
    assert result.status == "synthesized"
    # Every fabricated finding was rejected; nothing was verified.
    assert result.rejected
    assert not result.verified
    # The fabricated citation never reaches the answer.
    assert "[S99]" not in (result.answer or "")


def test_fleet_budget_breach_stops_the_team(kill_path):
    """A looping sub-agent burns the shared call cap; the team stops before the
    next action, and not every planned sub-agent gets to run."""
    result = supervisor.run_team(
        question=QUESTION,
        model=LoopingMockLLM(),
        corpus=CORPUS,
        budget=FleetBudget(max_usd=100.0, max_calls=4),  # generous $, tight calls
        kill_switch=KillSwitch(kill_path),
    )
    assert result.status == "budget_breach"
    assert result.budget["calls"] <= result.budget["max_calls"] + 1
    # The team did not synthesize a full answer — it was stopped.
    assert result.answer is None
    assert len(result.verified) < len(result.plan)


def test_fleet_dollar_ceiling_stops_the_team(kill_path):
    """A tight dollar ceiling stops a looping team on spend, independent of calls."""
    result = supervisor.run_team(
        question=QUESTION,
        model=LoopingMockLLM(),
        corpus=CORPUS,
        budget=FleetBudget(max_usd=0.025, max_calls=1000),  # ~2 calls of headroom
        kill_switch=KillSwitch(kill_path),
    )
    assert result.status == "budget_breach"
    assert "fleet budget" in [r["detail"] for r in result.trace if r["event"] == "budget_breach"][0]


def test_kill_switch_halts_the_team(kill_path):
    """A tripped switch stops the team before any sub-agent acts — and the
    agents cannot clear it (they hold the read-only handle)."""
    operator = OperatorKillSwitch(kill_path)
    operator.engage("operator halt for test")

    agent_view = KillSwitch(kill_path)  # what the supervisor and sub-agents get
    assert not hasattr(agent_view, "engage")  # read-only — no write path

    result = supervisor.run_team(
        question=QUESTION,
        model=MockLLM(),
        corpus=CORPUS,
        budget=FleetBudget(max_usd=1.00, max_calls=20),
        kill_switch=agent_view,
    )
    assert result.status == "halted"
    assert result.budget["calls"] == 0  # halted before any model call


def test_verify_gate_rejects_uncited_and_fabricated_findings():
    """Unit-level: the gate accepts only findings whose every citation is
    grounded in the retrieved evidence."""
    # Grounded — accepted.
    v = verify_gate.verify("clear answer [S1] [S2]", evidence_ids=["S1", "S2", "S3"])
    assert v.accepted and v.label == "ACCEPT"
    # No citation — rejected.
    assert not verify_gate.verify("a confident claim with no source", []).accepted
    # Fabricated citation — rejected.
    assert not verify_gate.verify("answer [S9]", evidence_ids=["S1"]).accepted
    # Empty — rejected.
    assert not verify_gate.verify("", evidence_ids=["S1"]).accepted
