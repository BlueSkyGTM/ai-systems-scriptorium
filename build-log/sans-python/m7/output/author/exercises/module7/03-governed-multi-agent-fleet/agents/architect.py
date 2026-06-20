"""Architect node — decomposes a feature request into an ordered build plan.

The architect is the manager in the supervisor-worker shape (M4 lesson 03),
governed. It reasons once about the feature request and emits a typed plan: an
ordered list of slices, one per coder. The plan is an A2A artifact, not a string
— the coders receive typed work, not a paragraph to interpret.

Its authority is high (tier F2 — it plans autonomously), but its plan is still
gated downstream: a coder verifies, a reviewer gates, and the merge waits for a
human. Planning autonomy is not merge autonomy.
"""

from __future__ import annotations

from a2a import A2AResult, A2ATask
from context import FleetContext
from governance.fleet_budget import BudgetBreach


def run(task: A2ATask, ctx: FleetContext, agent_id: str, model) -> A2AResult:
    """Plan the feature into slices. One governed model call, one typed plan."""
    task.validate(accepted_skills={"plan_feature"})

    if ctx.kill_switch.tripped():
        return A2AResult.failed(task, agent_id, "halted: kill switch engaged")

    try:
        ctx.budget.charge(agent_id, model.respond([]).cost_usd)
    except BudgetBreach as exc:
        return A2AResult.failed(task, agent_id, f"budget breach: {exc}")

    feature = task.input.get("feature", "the requested feature")
    # The plan: one slice per coder. Deterministic for the smoke run; a real
    # model would derive the slices from the feature description.
    plan = [
        {"slice": "implement-core", "assign_role": "coder",
         "instruction": f"Implement {feature}: fix calculator.add and pass the suite."},
        {"slice": "verify-edges", "assign_role": "coder",
         "instruction": f"Verify {feature} against the edge-case tests."},
    ]
    ctx.emit("plan", agent=agent_id, slices=[s["slice"] for s in plan])
    ctx.audit.record(
        correlation_id=ctx.correlation_id, agent=agent_id,
        authority=ctx.policy.authority(agent_id),
        task=task.skill, evidence=f"plan: {len(plan)} slices for {feature!r}",
    )
    return A2AResult.completed(task, agent_id, plan=plan, feature=feature)
