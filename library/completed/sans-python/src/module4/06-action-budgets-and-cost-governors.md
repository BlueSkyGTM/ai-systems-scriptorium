# Action budgets & cost governors

A bug in a normal service throws an error and stops. A bug in an agent keeps reasoning, keeps calling tools, and keeps billing — because nothing in the loop was designed to make it stop. The failure has a name: Denial of Wallet, and the only defense is a stack of limits that fire before the invoice does.

## Denial of Wallet is the agent-native outage

Classic denial of service exhausts your CPU or your bandwidth. An agent exhausts your *budget*. Give a loop a goal, a model, and a credit card behind the API key, and a single bad prompt — or a single adversarial input — can send it into a retry spiral that spends thousands of dollars before a human notices. There is no segfault, no 500, no page. Just a metered loop doing exactly what it was told, forever.

This is the failure mode that makes long-horizon agents (lesson 05) financially dangerous. Durability is what keeps a long run alive; budgets are what keep an alive run from bankrupting you. The two are a pair — you do not ship one without the other. This is squarely the MLOps half of the seam: the AI Engineer makes the agent capable, and the platform engineer is the one who has to answer for the bill when capable goes sideways at 3 a.m.

## One cap is not a budget

The instinct is to set a monthly spending cap and call it done. That cap is real, and it is also useless against the failure you actually fear. A monthly limit catches a runaway *after the wallet is already gone* — by the time you hit it, the damage is done. Different failure modes live at different time scales, and a budget worth the name puts a limit at each one.

Think of it as a stack, from the single call up to the calendar:

**`max_tokens` per call.** The floor. Cap the output of any single model call so one response can't balloon. Cheap to set, and it bounds the smallest unit.

**Iteration caps (`max_turns`).** A hard ceiling on loop cycles — the turn budget from Module 3's agent loop, now load-bearing. The stop condition handles the happy path; the iteration cap handles the loop that never decides it's done. Claude Code exposes exactly this pair as first-class controls — `--max-turns` caps the agentic steps and `--max-budget-usd` sets a hard spend ceiling — on its non-interactive runs; hit either and the agent stops and returns a partial result.

**Per-task token and dollar budgets.** Each task gets an allowance. The runner tracks cumulative spend across every call in the task and refuses the next action when the allowance is exhausted. This is the limit that maps to a unit of business value — "this task is worth at most two dollars to me."

**Per-tool caps.** Some tools are cheap (a string lookup); some are expensive (a model-backed sub-search, a paid API). Cap the costly ones independently so one tool can't dominate a task's budget.

**Velocity limits.** The time-derivative limit, and the one that catches the spiral the static caps miss. Watch the *rate* of spend: more than fifty dollars in ten minutes is not a task running hot, it is a task out of control. Trip the velocity limit and cut the run, even if no per-task or monthly cap has been crossed yet. A spiral is recognizable by its slope long before it reaches a ceiling.

**Calendar caps (per-minute / per-day / per-month).** The outer envelope across all tasks and agents. Necessary, but never your first line of defense — they are the backstop, not the trigger.

The lesson is that these are not redundant. Each catches a failure the others let through: `max_tokens` bounds one response, the iteration cap bounds one loop, the per-task budget bounds one job, the velocity limit catches the spiral mid-flight, and the calendar cap bounds everything when all else fails. Pull any layer and a class of runaway walks straight through the gap.

```python
# module4-fleet/governor/budget.py — the per-task governor, control plane in Python
from dataclasses import dataclass, field
import time

@dataclass
class TaskBudget:
    max_usd: float                       # hard per-task allowance
    max_turns: int                       # iteration cap
    velocity_usd: float = 50.0           # spend allowed inside the window...
    velocity_window_s: float = 600.0     # ...a 10-minute window
    spent_usd: float = 0.0
    turns: int = 0
    _ledger: list = field(default_factory=list)   # (timestamp, usd) per charge

    def charge(self, usd: float) -> None:
        """Record a charge or raise BudgetBreach. Callers consult check() first."""
        now = time.time()
        self.spent_usd += usd
        self.turns += 1
        self._ledger.append((now, usd))
        self._enforce(now)

    def _enforce(self, now: float) -> None:
        if self.spent_usd > self.max_usd:
            raise BudgetBreach(f"per-task budget exceeded: ${self.spent_usd:.2f} > ${self.max_usd:.2f}")
        if self.turns > self.max_turns:
            raise BudgetBreach(f"iteration cap exceeded: {self.turns} > {self.max_turns}")
        window = sum(u for t, u in self._ledger if now - t <= self.velocity_window_s)
        if window > self.velocity_usd:
            raise BudgetBreach(f"velocity limit: ${window:.2f} in {self.velocity_window_s/60:.0f}min")

class BudgetBreach(Exception):
    ...
```

The governor is deliberately boring deterministic code — no model, no judgment. A budget you ask a model to enforce is a budget the model can talk its way out of.

## Routing is a budget too

Not every step needs your most expensive model. Tiered routing is cost governance applied to the model choice itself: send the cheap, high-volume work — classification, extraction, a rubric score — to a small fast model, and reserve the expensive reasoning model for the steps that need depth. A reviewer pass on a fixed rubric runs fine on a cheap model; the builder loop that has to reason through a hard task does not. Routing every step to the top model is the most common way teams quietly triple their bill for no accuracy gain.

Prompt caching and context windowing belong in the same conversation: cache the stable prefix so you stop paying to re-send it every turn, and trim the message history so a long run's context doesn't grow without bound. Both are spend control by another name. Azure surfaces these governance levers as first-class platform controls rather than something you bolt on per agent: its Foundry control plane enforces per-project token-per-minute rate limits and total token quotas to cap aggregate spend, and a model router that sends each request to a cheaper or more capable model by the prompt.

## When a limit breaks, cut

A budget that logs a warning and keeps going is not a budget. Every limit in the stack ends the same way: on breach, the governor trips the kill switch and the run stops before the next action executes. The breach is the trigger; the kill switch is the mechanism — and that mechanism is the next lesson. Here the contract is simple: when any cap is crossed, the next action does not run.

This is also where budgets stop being a single-agent concern. When you graduate to a fleet (Module 4's back half), the same governor runs at fleet scale — a shared budget across many agents, with the velocity limit watching aggregate spend. The fleet lessons reference this stack; they do not rebuild it. Define the governor once, here, and the fleet inherits it.

Set the caps too high and they never fire, which is the same as not having them; set them where a healthy task clears them with room and a runaway hits a wall in seconds — that gap, between comfortable and catastrophic, is the budget's entire job.

## Core concepts

- Denial of Wallet is the agent-native failure: a loop with no stop designed in keeps reasoning, calling, and billing — defended only by limits that fire before the invoice, not after.
- A budget is a stack of caps at different time scales — `max_tokens`, iteration caps, per-task token/dollar budgets, per-tool caps, velocity limits, and calendar caps — because each catches a runaway the others let through; a single monthly cap catches it only after the wallet is gone.
- Tiered model routing, prompt caching, and context windowing are cost governance too: send cheap work to a small model and reserve the expensive model for steps that need depth.
- A budget governor is deterministic code that, on any breach, trips the kill switch so the next action never runs — defined here once, inherited unchanged at fleet scale.

<div class="claude-handoff" data-exercise="exercises/module4/06-action-budgets-and-cost-governors/">

**Build It in Claude Code** — add a `budget.py` cost governor to the `_harness/` orchestrator: a per-task dollar budget, an iteration cap, and a velocity limit (spend-per-window). Wrap each agent action so cumulative spend is charged before the next action runs, and prove all three caps independently — a slow grind hits the per-task cap, a stuck loop hits the iteration cap, and a burst hits the velocity limit and cuts mid-run. On any breach, raise the breach and stop the run.

</div>
