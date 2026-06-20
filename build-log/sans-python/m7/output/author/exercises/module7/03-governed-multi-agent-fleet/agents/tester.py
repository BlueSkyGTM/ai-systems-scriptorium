"""Tester node — runs the suite in the sandbox and returns one deterministic verdict.

The tester is the verification interface (M6) as a team member. It does not read
the diff or reason about it; it runs the project's tests through the same
deterministic verify gate the coder used and returns ACCEPT or REJECT. No model
judgment decides whether the feature works — running code does.

This is the antidote to optimistic agents. An agent that decides it is finished
is not finished; the tester is the deterministic third party that turns "I think
it works" into a verdict the reviewer and the human can trust.
"""

from __future__ import annotations

import verify_gate
from a2a import A2AResult, A2ATask
from context import FleetContext
from governance.fleet_budget import BudgetBreach


def run(task: A2ATask, ctx: FleetContext, agent_id: str, model, project_root: str) -> A2AResult:
    """Run the suite and return the verdict. The tester's authority is to run
    tests only (``tools: [run_tests]``); it cannot write code or merge."""
    task.validate(accepted_skills={"run_acceptance"})

    if ctx.kill_switch.tripped():
        return A2AResult.failed(task, agent_id, "halted: kill switch engaged")

    try:
        ctx.budget.charge(agent_id, model.respond([]).cost_usd)
    except BudgetBreach as exc:
        return A2AResult.failed(task, agent_id, f"budget breach: {exc}")

    ctx.policy.authorize_tool(agent_id, "run_tests")
    verdict = verify_gate.verify(project_root)
    ctx.emit("tester_verdict", agent=agent_id, verdict=verdict.label, detail=verdict.detail)
    ctx.audit.record(
        correlation_id=ctx.correlation_id, agent=agent_id,
        authority=ctx.policy.authority(agent_id),
        task=task.skill, evidence=f"acceptance {verdict.label}: {verdict.detail}",
    )
    return A2AResult.completed(
        task, agent_id, verdict=verdict.label, accepted=verdict.accepted, detail=verdict.detail,
    )
