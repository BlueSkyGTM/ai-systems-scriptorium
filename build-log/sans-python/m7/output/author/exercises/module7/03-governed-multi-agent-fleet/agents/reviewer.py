"""Reviewer node — reads the coders' diffs and the tester's verdict, then gates.

The reviewer is the conflict-resolution and gate role from the supervisor-worker
pattern (M4 lesson 13 hierarchical-delegation): it takes the coders' typed
results and the tester's verdict and decides whether the work is ready to
*propose* for merge. Its verdict is advisory — tier F1 — because the merge itself
is a human gate, not the reviewer's call.

The reviewer's rule is simple and deterministic for the smoke run: approve only
if the tester accepted AND every coder reported a passing self-test. A coder that
self-tested REJECT, or a tester that rejected, blocks the proposal here — before
it ever reaches the human inbox. The reviewer reads, it does not write
(``tools: [read_file]``); it cannot merge.
"""

from __future__ import annotations

from a2a import A2AResult, A2ATask
from context import FleetContext
from governance.fleet_budget import BudgetBreach


def run(task: A2ATask, ctx: FleetContext, agent_id: str, model) -> A2AResult:
    """Gate the team's work. Returns ``approve_merge`` true only on clean evidence."""
    task.validate(accepted_skills={"review_changes"})

    if ctx.kill_switch.tripped():
        return A2AResult.failed(task, agent_id, "halted: kill switch engaged")

    try:
        ctx.budget.charge(agent_id, model.respond([]).cost_usd)
    except BudgetBreach as exc:
        return A2AResult.failed(task, agent_id, f"budget breach: {exc}")

    coder_results = task.input.get("coder_results", [])
    tester_accepted = task.input.get("tester_accepted", False)
    coders_clean = all(c.get("accepted") for c in coder_results) and bool(coder_results)
    approve = tester_accepted and coders_clean

    reason = (
        "tester ACCEPT and all coder self-tests pass"
        if approve else
        "blocked: " + ("tester REJECT" if not tester_accepted else "a coder self-test failed")
    )
    ctx.emit("review", agent=agent_id, approve_merge=approve, reason=reason)
    ctx.audit.record(
        correlation_id=ctx.correlation_id, agent=agent_id,
        authority=ctx.policy.authority(agent_id),
        task=task.skill, evidence=f"review {'APPROVE' if approve else 'BLOCK'}: {reason}",
    )
    return A2AResult.completed(task, agent_id, approve_merge=approve, reason=reason)
