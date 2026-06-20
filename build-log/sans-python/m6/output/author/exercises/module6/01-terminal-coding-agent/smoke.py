"""End-to-end smoke run — plan -> edit -> test -> verify, under the operator surfaces.

Copies the broken fixture to a throwaway directory, runs the agent with the
deterministic mock model, and prints the trace. No network, no API key, no
Docker — standard library only. This is the BUILD->TEST gate's happy path:

    python smoke.py

A real model run is one import away (see client_llm.py + .env.example); this
file stays on the mock so the gate is deterministic and offline.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile

import agent
from budget import Budget
from killswitch import KillSwitch
from mock_llm import MockLLM

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixture")


def copy_fixture() -> str:
    """Copy the fixture to a temp dir so the run is isolated and repeatable."""
    work = tempfile.mkdtemp(prefix="coding-agent-")
    for name in os.listdir(FIXTURE):
        if name.endswith(".py"):
            shutil.copy(os.path.join(FIXTURE, name), os.path.join(work, name))
    return work


def print_trace(record: dict) -> None:
    event = record["event"]
    if event == "act":
        print(f"  [act]     {record['tool']}({_short_args(record['args'])})")
    elif event == "observe":
        first = record["observation"].splitlines()[0] if record["observation"] else ""
        print(f"  [observe] {record['tool']} -> {first}")
    elif event == "final_answer":
        print(f"  [final]   {record['text']}")
    elif event == "verify":
        print(f"  [verify]  {record['verdict']}: {record['detail']}")
    elif event == "budget_breach":
        print(f"  [budget]  BREACH: {record['detail']}")
    elif event == "halted":
        print(f"  [halt]    {record['reason']}")


def _short_args(args: dict) -> str:
    parts = []
    for k, v in args.items():
        s = str(v)
        parts.append(f"{k}={s[:24]}…" if len(s) > 24 else f"{k}={s}")
    return ", ".join(parts)


def main() -> int:
    work = copy_fixture()
    print(f"Smoke run on copied fixture: {work}")
    print("-" * 60)

    budget = Budget(max_usd=1.00, max_turns=10)
    kill = KillSwitch(os.path.join(work, ".KILL"))  # never tripped on the happy path
    model = MockLLM()

    result = agent.run_agent(
        goal="Fix the failing test in calculator.py.",
        project_root=work,
        model=model,
        budget=budget,
        kill_switch=kill,
        on_trace=print_trace,
    )

    print("-" * 60)
    print(f"status : {result.status}")
    print(f"verdict: {result.verdict}")
    print(f"budget : ${result.budget['spent_usd']} over {result.budget['turns']} turns")

    shutil.rmtree(work, ignore_errors=True)
    return 0 if result.status == "verified" else 1


if __name__ == "__main__":
    sys.exit(main())
