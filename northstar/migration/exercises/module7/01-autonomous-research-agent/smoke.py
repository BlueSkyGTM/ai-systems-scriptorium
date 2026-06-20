"""End-to-end smoke run — a team coordinating: plan → dispatch → verify → synthesize.

Runs the autonomous research team on a fixed question with the deterministic mock
model and the fixture corpus, under one shared budget and one kill switch, and
prints the team trace. No network, no API key, no Docker — standard library only.
This is the BUILD->TEST gate's happy path:

    python smoke.py

The trace proves a *team* runs, not one agent: the supervisor plans N
sub-questions, N sub-agents each search their own sandbox and return a cited
finding, the supervisor gates each finding, and the Solver synthesizes only the
verified ones — all charged to a single fleet budget.

A real model run is one import away (see client_llm.py + .env.example); this file
stays on the mock so the gate is deterministic and offline.
"""

from __future__ import annotations

import os
import sys
import tempfile

import supervisor
from budget import FleetBudget
from corpus import CORPUS
from killswitch import KillSwitch
from mock_llm import MockLLM

QUESTION = "What makes a multi-agent system reliable in production?"


def print_trace(record: dict) -> None:
    agent = record.get("agent", "?")
    event = record["event"]
    if event == "plan":
        print(f"  [supervisor] plan -> {len(record['sub_questions'])} sub-questions")
        for q in record["sub_questions"]:
            print(f"               - {q}")
    elif event == "dispatch":
        print(f"  [supervisor] dispatch {record['sub_id']}: {record['question']}")
    elif event == "search":
        print(f"  [{agent}] search({record['query'][:40]}…) -> {record['found']}")
    elif event == "finding":
        print(f"  [{agent}] finding: {record['text']}")
    elif event == "verify":
        print(f"  [supervisor] verify {record['sub_id']}: {record['verdict']} ({record['detail']})")
    elif event == "synthesize":
        print(f"  [supervisor] synthesize: {record['verified']} verified, {record['rejected']} rejected")
    elif event == "budget_breach":
        print(f"  [{agent}] BUDGET BREACH: {record['detail']}")
    elif event == "halted":
        print(f"  [{agent}] HALT: {record['reason']}")


def main() -> int:
    # The kill switch is a file the operator owns; never tripped on the happy path.
    kill_path = os.path.join(tempfile.gettempdir(), "research-team.KILL")
    kill = KillSwitch(kill_path)
    if kill.tripped():  # clean slate for a repeatable run
        os.remove(kill_path)

    budget = FleetBudget(max_usd=1.00, max_calls=20)
    model = MockLLM()

    print(f"Research question: {QUESTION}")
    print("-" * 70)

    result = supervisor.run_team(
        question=QUESTION,
        model=model,
        corpus=CORPUS,
        budget=budget,
        kill_switch=kill,
        on_trace=print_trace,
    )

    print("-" * 70)
    print(f"status : {result.status}")
    print(f"budget : ${result.budget['spent_usd']} over {result.budget['calls']} calls")
    print(f"by agent: {result.budget['by_agent']}")
    print()
    print(result.answer or "(no answer)")

    # Exit 0 only when the team synthesized a cited answer from verified findings.
    ok = result.status == "synthesized" and len(result.verified) >= 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
