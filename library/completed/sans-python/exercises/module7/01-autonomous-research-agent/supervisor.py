"""Supervisor — the M4 supervisor-worker pattern, wired as direct tool calls.

This is the composition the whole artifact exists to prove. The supervisor:

  1. **plans** — decomposes a research question into sub-questions (the M3 ReWOO
     Planner: describe the work before any tool fires);
  2. **dispatches** — runs one sub-agent per sub-question in its own sandbox and
     fresh context (the M4 supervisor-worker fan-out — workers never see each
     other, the supervisor reads only their findings);
  3. **verifies** — sends every sub-result through the verify gate before it may
     enter the answer (the M3 CRITIC / verification gap closed): an ungrounded
     finding is rejected, not synthesized;
  4. **synthesizes** — stitches the *verified* findings into one cited answer
     (the ReWOO Solver).

Supervision is direct tool calls, not a supervisor library (Module 4's 2026
guidance): the control plane is Python, ``run_subagent`` is the tool the
supervisor invokes, and every context boundary is a line written here. The whole
team runs under one shared budget and one kill switch — the operator surfaces a
fleet answers for.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import verify_gate
from budget import BudgetBreach, FleetBudget
from killswitch import KillSwitch
from sandbox import ResearchSandbox
from subagent import run_subagent


@dataclass
class TeamResult:
    status: str  # "synthesized" | "budget_breach" | "halted"
    answer: str | None = None
    plan: list = field(default_factory=list)
    verified: list = field(default_factory=list)   # (sub_id, question, finding)
    rejected: list = field(default_factory=list)    # (sub_id, question, reason)
    trace: list = field(default_factory=list)
    budget: dict = field(default_factory=dict)


def run_team(
    question: str,
    model,
    corpus,
    budget: FleetBudget,
    kill_switch: KillSwitch,
    on_trace=None,
) -> TeamResult:
    """Run the research team end to end: plan → dispatch → verify → synthesize.

    Every sub-agent gets its own ``ResearchSandbox`` over the shared corpus and a
    fresh context. The supervisor reads each finding, gates it, and synthesizes
    only what the gate accepts. The team stops early if the shared budget
    breaches or the kill switch trips — the supervisor checks both at the same
    boundaries a sub-agent does.
    """
    trace: list = []

    def emit(event: str, **data):
        record = {"event": event, "agent": "supervisor", **data}
        trace.append(record)
        if on_trace:
            on_trace(record)

    # Halt / budget check before planning — a team already stopped does no work.
    if kill_switch.tripped():
        emit("halted", reason="kill switch engaged before planning")
        return TeamResult("halted", trace=trace, budget=budget.summary())
    try:
        budget.check()
    except BudgetBreach as exc:
        emit("budget_breach", detail=str(exc))
        return TeamResult("budget_breach", trace=trace, budget=budget.summary())

    # 1. PLAN — the Planner decomposes; charged like any model call.
    plan = model.plan(question)
    try:
        budget.charge(0.0, agent="supervisor", label="plan")
    except BudgetBreach as exc:  # pragma: no cover - plan charge is free here
        emit("budget_breach", detail=str(exc))
        return TeamResult("budget_breach", plan=plan, trace=trace, budget=budget.summary())
    emit("plan", sub_questions=[s["question"] for s in plan])

    verified: list = []
    rejected: list = []

    # 2. DISPATCH — one sub-agent per sub-question, each in its own sandbox.
    for sub in plan:
        if kill_switch.tripped():
            emit("halted", reason="kill switch engaged mid-dispatch")
            return TeamResult("halted", plan=plan, verified=verified,
                              rejected=rejected, trace=trace, budget=budget.summary())

        sandbox = ResearchSandbox(corpus)  # fresh, no-egress sandbox per sub-agent
        emit("dispatch", sub_id=sub["id"], question=sub["question"])
        sub_result = run_subagent(sub, model, sandbox, budget, kill_switch, on_trace)
        trace.extend(sub_result.trace)

        if sub_result.status == "budget_breach":
            emit("budget_breach", detail="sub-agent stopped the team on budget")
            return TeamResult("budget_breach", plan=plan, verified=verified,
                              rejected=rejected, trace=trace, budget=budget.summary())
        if sub_result.status == "halted":
            emit("halted", reason="sub-agent read a tripped kill switch")
            return TeamResult("halted", plan=plan, verified=verified,
                              rejected=rejected, trace=trace, budget=budget.summary())

        # 3. VERIFY — the gate has the last word before a finding can be synthesized.
        verdict = verify_gate.verify(sub_result.finding, sub_result.evidence_ids)
        emit("verify", sub_id=sub["id"], verdict=verdict.label, detail=verdict.detail)
        if verdict.accepted:
            verified.append((sub["id"], sub["question"], sub_result.finding))
        else:
            rejected.append((sub["id"], sub["question"], verdict.detail))

    # 4. SYNTHESIZE — the Solver stitches only the verified findings.
    answer = model.synthesize(question, [(q, f) for _id, q, f in verified])
    emit("synthesize", verified=len(verified), rejected=len(rejected))
    return TeamResult(
        "synthesized", answer=answer, plan=plan,
        verified=verified, rejected=rejected, trace=trace, budget=budget.summary(),
    )
