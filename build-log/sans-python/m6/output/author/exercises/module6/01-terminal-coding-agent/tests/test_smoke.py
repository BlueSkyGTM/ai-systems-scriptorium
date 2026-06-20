"""BUILD->TEST gate — the smoke run and the operator surfaces.

Standard library + pytest only. No network, no API key, no Docker. Run with:

    python -m pytest tests/

Each test pins one claim the chapter makes:
  - the smoke run fixes the fixture (the agent works end to end);
  - a budget breach stops the run before the next action;
  - the kill switch halts the loop before the next action;
  - the verify gate REJECTS a bad patch even when the model says "done".
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile

import pytest

# Make the artifact root importable when pytest is invoked from anywhere.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import agent  # noqa: E402
import verify_gate  # noqa: E402
from budget import Budget  # noqa: E402
from killswitch import KillSwitch, OperatorKillSwitch  # noqa: E402
from mock_llm import BadPatchMockLLM, MockLLM, StuckMockLLM  # noqa: E402

FIXTURE = os.path.join(ROOT, "fixture")


@pytest.fixture()
def work_dir():
    """A fresh copy of the broken fixture for each test."""
    work = tempfile.mkdtemp(prefix="agent-test-")
    for name in os.listdir(FIXTURE):
        if name.endswith(".py"):
            shutil.copy(os.path.join(FIXTURE, name), os.path.join(work, name))
    yield work
    shutil.rmtree(work, ignore_errors=True)


def test_smoke_run_fixes_the_fixture(work_dir):
    """The happy path: the agent reads, fixes, tests, and the gate ACCEPTs."""
    result = agent.run_agent(
        goal="Fix the failing test.",
        project_root=work_dir,
        model=MockLLM(),
        budget=Budget(max_usd=1.00, max_turns=10),
        kill_switch=KillSwitch(os.path.join(work_dir, ".KILL")),
    )
    assert result.status == "verified"
    assert result.verdict == "ACCEPT"
    # And the fixture really was fixed on disk.
    assert verify_gate.verify(work_dir).accepted


def test_budget_breach_stops_the_run(work_dir):
    """A stuck model that never finishes hits the iteration cap and stops."""
    result = agent.run_agent(
        goal="Fix the failing test.",
        project_root=work_dir,
        model=StuckMockLLM(),
        budget=Budget(max_usd=100.0, max_turns=3),  # generous dollars, tight turns
        kill_switch=KillSwitch(os.path.join(work_dir, ".KILL")),
    )
    assert result.status == "budget_breach"
    assert result.budget["turns"] <= result.budget["max_turns"] + 1
    assert "iteration cap" in result.detail


def test_budget_dollar_ceiling_stops_the_run(work_dir):
    """A tight dollar ceiling stops a stuck run on spend, independent of turns."""
    result = agent.run_agent(
        goal="Fix the failing test.",
        project_root=work_dir,
        model=StuckMockLLM(),
        budget=Budget(max_usd=0.025, max_turns=100),  # ~2 calls of headroom
        kill_switch=KillSwitch(os.path.join(work_dir, ".KILL")),
    )
    assert result.status == "budget_breach"
    assert "per-task budget" in result.detail


def test_kill_switch_halts_before_next_action(work_dir):
    """A tripped switch stops the loop before the next action — and the agent
    cannot clear it (it holds the read-only handle)."""
    kill_path = os.path.join(work_dir, ".KILL")
    operator = OperatorKillSwitch(kill_path)
    operator.engage("operator halt for test")

    agent_view = KillSwitch(kill_path)  # what the loop is handed
    assert not hasattr(agent_view, "engage")  # read-only — no write path

    result = agent.run_agent(
        goal="Fix the failing test.",
        project_root=work_dir,
        model=MockLLM(),
        budget=Budget(max_usd=1.00, max_turns=10),
        kill_switch=agent_view,
    )
    assert result.status == "halted"
    assert result.budget["turns"] == 0  # halted before any action


def test_verify_gate_rejects_a_bad_patch(work_dir):
    """The model writes a patch that does NOT fix the bug and declares success.
    The gate runs the tests and REJECTS anyway."""
    result = agent.run_agent(
        goal="Fix the failing test.",
        project_root=work_dir,
        model=BadPatchMockLLM(),
        budget=Budget(max_usd=1.00, max_turns=10),
        kill_switch=KillSwitch(os.path.join(work_dir, ".KILL")),
    )
    assert result.status == "rejected"
    assert result.verdict == "REJECT"


def test_verify_gate_default_rejects_unfixed_fixture(work_dir):
    """Sanity: the untouched fixture fails the gate (default REJECT)."""
    assert not verify_gate.verify(work_dir).accepted
