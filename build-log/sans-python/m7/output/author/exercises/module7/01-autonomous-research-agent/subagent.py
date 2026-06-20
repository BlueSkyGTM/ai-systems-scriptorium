"""Research sub-agent — the M6 worker loop, reused as a team member.

This is the Module 6 agent loop (observe → think → act) pointed at a research
sub-question instead of a bug, and run inside a sandbox. The shape is the M6
worker reused, not rebuilt: a loop under a budget and a kill switch, talking to
the model through one seam, with tool calls scoped to what the sub-agent may
reach. What changes is the job (retrieve evidence, not edit code) and the
governance altitude (the budget is now *shared* across the whole team).

The sub-agent runs in a fresh context with one sub-question — the isolation the
supervisor-worker pattern buys (Module 4): the sub-agent never sees the other
sub-agents, only its own task and its own sandbox. It returns a finding the
supervisor must still send through the verify gate before synthesis; a sub-agent
does not get its answer into the report on its own authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from budget import BudgetBreach, FleetBudget
from killswitch import KillSwitch
from sandbox import ResearchSandbox


@dataclass
class SubResult:
    status: str  # "answered" | "budget_breach" | "halted"
    sub_id: str
    question: str
    finding: str | None = None
    evidence_ids: list = field(default_factory=list)
    trace: list = field(default_factory=list)


def run_subagent(
    sub: dict,
    model,
    sandbox: ResearchSandbox,
    budget: FleetBudget,
    kill_switch: KillSwitch,
    on_trace=None,
) -> SubResult:
    """Drive one sub-agent's loop to a cited finding or a stop.

    ``sub`` is a sub-question record {id, question, query}. The loop terminates
    four ways, the same four as the M6 worker: the model emits a final finding,
    the shared budget breaches, the kill switch trips, or — implicitly — the
    model stops calling tools. The sub-agent never declares its own finding
    verified; that is the supervisor's gate.
    """
    sub_id = sub["id"]
    messages = [
        {"role": "subquestion", "sub": sub},
        {"role": "user", "content": sub["question"]},
    ]
    evidence_ids: list = []
    trace: list = []

    def emit(event: str, **data):
        record = {"event": event, "agent": sub_id, **data}
        trace.append(record)
        if on_trace:
            on_trace(record)

    while True:
        # Kill switch first — every agent reads it before every action, and none
        # of them can write it.
        if kill_switch.tripped():
            emit("halted", reason="kill switch engaged")
            return SubResult("halted", sub_id, sub["question"], trace=trace)

        # Check the shared budget BEFORE the call: a team already over budget
        # stops here, before paying for one more sub-agent action.
        try:
            budget.check()
        except BudgetBreach as exc:
            emit("budget_breach", detail=str(exc))
            return SubResult("budget_breach", sub_id, sub["question"], trace=trace)

        response = model.respond(messages)

        # Charge the shared fleet pool, tagged with this sub-agent's id.
        try:
            budget.charge(response.cost_usd, agent=sub_id, label="model_call")
        except BudgetBreach as exc:
            emit("budget_breach", detail=str(exc))
            return SubResult("budget_breach", sub_id, sub["question"], trace=trace)

        if response.is_final:
            emit("finding", text=response.text)
            return SubResult(
                "answered", sub_id, sub["question"],
                finding=response.text, evidence_ids=evidence_ids, trace=trace,
            )

        # Act: the only tool a research sub-agent has is search, scoped to its
        # own no-egress sandbox.
        if response.tool_name == "search":
            results = sandbox.search(response.tool_args.get("query", ""))
            found_ids = [e.id for e in results]
            for i in found_ids:
                if i not in evidence_ids:
                    evidence_ids.append(i)
            emit("search", query=response.tool_args.get("query", ""), found=found_ids)
            messages.append({"role": "tool_call", "name": "search",
                             "args": response.tool_args})
            messages.append({"role": "tool_result", "name": "search",
                             "evidence_ids": found_ids,
                             "content": "; ".join(f"{e.id}: {e.title}" for e in results)})
        else:
            # Unknown tool becomes an observation, not a crash — the M6 contract.
            emit("observe", note=f"unknown tool: {response.tool_name}")
            messages.append({"role": "tool_call", "name": response.tool_name,
                             "args": response.tool_args})
            messages.append({"role": "tool_result", "name": response.tool_name,
                             "evidence_ids": [],
                             "content": f"[error] unknown tool: {response.tool_name}"})
