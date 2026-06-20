"""Coder node — the M6 terminal coding agent, reused as a team member.

This is the elevate-don't-author rule made literal. The plan/act/observe loop
here is the M6 coding agent (artifact 01): it reads the failing file, writes a
fix, runs the suite in the subprocess sandbox, and stops. What M7 adds is *not* a
new loop — it is governance wrapped around the existing one:

- every model call charges the **fleet budget** (per-agent + team cap), so a
  runaway coder trips its own wall and the team's;
- the **kill switch** is checked before every action;
- every action is recorded to the **cross-agent audit** under the task's
  correlation id, with the four accountability clauses filled;
- the tools the node may call are gated by the registry's per-agent
  **permissions** (``policy.authorize_tool``).

The coder proposes a diff and a self-test verdict. It does not merge — it has no
authority to (``can_merge: false``). The verdict it hands over is what lets the
reviewer trust it: a fact from running tests, not a promise.
"""

from __future__ import annotations

import tools
import verify_gate
from a2a import A2AResult, A2ATask
from context import FleetContext
from governance.fleet_budget import BudgetBreach
from governance.killswitch import FleetHalted

SYSTEM_PROMPT = (
    "You are a coder node on a software team. Read the failing file, fix the "
    "bug, run the tests, and stop. Use read_file, write_file, run_tests."
)


def run(task: A2ATask, ctx: FleetContext, agent_id: str, model, project_root: str) -> A2AResult:
    """Drive the governed plan/act/observe loop and hand back a typed result.

    Terminates four ways: the model emits a final answer (the verify gate then
    has the last word), the fleet budget breaches, the kill switch trips, or a
    tool is refused by policy. There is no path where the coder declares itself
    done and the fleet simply believes it.
    """
    task.validate(accepted_skills={"implement_slice"})
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task.input.get("instruction", "Fix the failing test.")},
    ]

    while True:
        # Kill switch: checked before every action, read-only to this node.
        if ctx.kill_switch.tripped():
            ctx.emit("halted", agent=agent_id, reason="kill switch engaged")
            return A2AResult.failed(task, agent_id, "halted: kill switch engaged")

        response = model.respond(messages)

        # Charge the call to THIS agent and the team. A breach stops the run.
        try:
            ctx.budget.charge(agent_id, response.cost_usd)
        except BudgetBreach as exc:
            ctx.emit("budget_breach", agent=agent_id, detail=str(exc))
            ctx.audit.record(
                correlation_id=ctx.correlation_id, agent=agent_id,
                authority=ctx.policy.authority(agent_id),
                task=task.skill, evidence=f"budget_breach: {exc}",
            )
            return A2AResult.failed(task, agent_id, f"budget breach: {exc}")

        if response.is_final:
            # The coder does not mark its own work done — the verify gate does.
            verdict = verify_gate.verify(project_root)
            ctx.emit("coder_verdict", agent=agent_id, verdict=verdict.label, detail=verdict.detail)
            ctx.audit.record(
                correlation_id=ctx.correlation_id, agent=agent_id,
                authority=ctx.policy.authority(agent_id),
                task=task.skill,
                evidence=f"self-test {verdict.label}: {verdict.detail}",
            )
            return A2AResult.completed(
                task, agent_id,
                diff_written=True,
                self_test=verdict.label,
                self_test_detail=verdict.detail,
                accepted=verdict.accepted,
            )

        # Act: the tool must be in this node's least-privilege grant.
        ctx.policy.authorize_tool(agent_id, response.tool_name)
        observation = tools.dispatch(response.tool_name, response.tool_args, project_root)
        ctx.emit("act", agent=agent_id, tool=response.tool_name)
        ctx.audit.record(
            correlation_id=ctx.correlation_id, agent=agent_id,
            authority=ctx.policy.authority(agent_id),
            task=f"{task.skill}:{response.tool_name}",
            evidence=_clip(observation),
        )
        messages.append({"role": "tool_call", "name": response.tool_name, "args": response.tool_args})
        messages.append({"role": "tool_result", "name": response.tool_name, "content": observation})


def _clip(text: str, limit: int = 120) -> str:
    text = text.strip().splitlines()[0] if text.strip() else ""
    return text if len(text) <= limit else text[:limit] + " …"
