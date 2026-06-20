"""The terminal coding agent — plan/act/observe, under three operator surfaces.

This is the M3 agent loop (Observe -> Think -> Act) pointed at a code-fixing
task and wrapped in the controls a platform engineer answers for:

- a **budget** that charges every model call and stops the run on breach,
- a **kill switch** the agent reads before each action but cannot write,
- a **verify gate** that decides "done" from the test result, not the model's
  say-so.

The model is a coprocessor wired in at one seam (``model.respond(messages)``).
Swap the deterministic mock for a real Anthropic client and nothing else in
this file changes — that is the portable seam the chapter sells.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import tools
import verify_gate
from budget import Budget, BudgetBreach
from killswitch import Halted, KillSwitch


@dataclass
class RunResult:
    status: str  # "verified" | "rejected" | "budget_breach" | "halted"
    detail: str
    trace: list = field(default_factory=list)
    budget: dict = field(default_factory=dict)
    verdict: str | None = None


SYSTEM_PROMPT = (
    "You are a terminal coding agent. Read the failing file, fix the bug, run "
    "the tests, and stop when they pass. Use the read_file, write_file, and "
    "run_tests tools."
)


def run_agent(
    goal: str,
    project_root: str,
    model,
    budget: Budget,
    kill_switch: KillSwitch,
    on_trace=None,
) -> RunResult:
    """Drive the plan/act/observe loop to a verified fix or a stop.

    The loop terminates four ways: the model emits a final answer (then the
    verify gate has the last word), the budget breaches, the kill switch trips,
    or the turn budget is exhausted. There is no path where the agent declares
    itself done and the harness simply believes it.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]
    trace: list = []

    def emit(event: str, **data):
        record = {"event": event, **data}
        trace.append(record)
        if on_trace:
            on_trace(record)

    while True:
        # Kill switch is checked before every action — it cannot be written by
        # anything in this process the agent can reach.
        if kill_switch.tripped():
            emit("halted", reason="kill switch engaged")
            return RunResult("halted", "kill switch engaged before next action",
                             trace, budget.summary())

        # Check the budget BEFORE the model call: a run already over budget
        # stops here, before paying for one more action.
        try:
            budget.check()
        except BudgetBreach as exc:
            emit("budget_breach", detail=str(exc))
            return RunResult("budget_breach", str(exc), trace, budget.summary())

        response = model.respond(messages)

        # Charge this turn. The charge increments the turn counter and the spend,
        # then enforces both caps — so a runaway loop hits the iteration wall and
        # a slow grind hits the dollar wall.
        try:
            budget.charge(response.cost_usd, label="model_call")
        except BudgetBreach as exc:
            emit("budget_breach", detail=str(exc))
            return RunResult("budget_breach", str(exc), trace, budget.summary())

        if response.is_final:
            emit("final_answer", text=response.text)
            # The agent does not mark its own work done — the gate does.
            verdict = verify_gate.verify(project_root)
            emit("verify", verdict=verdict.label, detail=verdict.detail)
            status = "verified" if verdict.accepted else "rejected"
            return RunResult(status, verdict.detail, trace, budget.summary(), verdict.label)

        # Act: execute the tool through the registry (validated, scoped).
        emit("act", tool=response.tool_name, args=response.tool_args)
        observation = tools.dispatch(response.tool_name, response.tool_args, project_root)
        emit("observe", tool=response.tool_name, observation=_clip(observation))

        # Append the act + observation to the buffer so the next Think step
        # sees what happened. The mock counts these to advance its plan.
        messages.append({"role": "tool_call", "name": response.tool_name,
                         "args": response.tool_args})
        messages.append({"role": "tool_result", "name": response.tool_name,
                         "content": observation})


def _clip(text: str, limit: int = 400) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + " …[clipped]"
