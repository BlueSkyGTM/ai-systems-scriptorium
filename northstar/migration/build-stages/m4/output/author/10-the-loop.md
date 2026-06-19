# The Loop — A Single Agent-System as Governed Infrastructure

You stop typing the next prompt. Something else discovers the work, hands it to an agent, checks the result, and stops when the money runs out — and the day you build that something, you have crossed from running an agent to operating one.

## Replacing yourself as the prompter

Module 3 built an agent: a loop that observes, thinks, acts, and stops on a condition you defined. You were still the trigger. You opened the session, gave it a goal, watched it run, and read what it produced. The agent was capable; you were the scheduler, the dispatcher, and the verifier, all by hand.

A *loop* — in the sense this lesson means — removes you from that seat. It is one agent system wrapped in the machinery that decides *when* it runs, *what* it works on, *whether* the result is good, and *when* to stop spending. You design the system that discovers work, assigns it, verifies the output, and persists state across runs, instead of being that system yourself. The agent is the worker; the loop is the operation around it.

This is the AI-Engineer ∪ MLOps cusp stated plainly. The AI Engineer makes the agent good at the task. The platform engineer makes the agent *runnable unattended* — on a schedule, against real repositories, with a verdict gate and a kill switch, leaving an audit trail. A capable agent nobody can run safely overnight is a demo. The loop is what turns it into infrastructure.

## The shape: trigger → action → verification → budget/kill-switch

Every loop, whatever it does, has the same four-stage shape. Learn the shape once and you can read any loop pattern in the next lesson at a glance.

**Trigger** — what makes the loop fire. A cron schedule (every weekday at 7 a.m.), an interval (every fifteen minutes during active hours), or an event (CI failed, a PR opened, a dependency alert landed). The trigger is also where the loop earns its keep by *not* running: a no-op early exit when there is nothing to do. A loop that wakes, finds an empty watchlist, and spends fifty thousand tokens deciding it has nothing to do is a loop that bankrupts you on quiet days.

**Action** — the agent does the work. This is the Module 3 loop you already built: observe, think, act, repeat. Discover the failing test, draft the minimal fix, score the issue, draft the release note. The action stage is the only stage where the agent reasons; the other three are governance around it.

**Verification** — a second check that the action is good. The agent does not grade its own work. This is the verification gate carried straight from the Module 3 workbench (lesson 15): an independent verifier — a deterministic check, a separate sub-agent with a different prompt, read-only access — that defaults to REJECT and approves only on evidence. An agent that marks its own work "done" is optimistic, not verified. The loop without this stage is the most expensive way ever invented to merge wrong code on a schedule.

**Budget / kill-switch** — the loop stops. Every run is bounded by the cost governor from lesson 06 (per-task dollar and token caps, an iteration cap, a velocity limit) and the control plane from lesson 07 (a kill switch the agent reads but cannot write, a circuit breaker that trips on repeated failure). On breach, the next action does not run. These were *defined* in those lessons; here they are the loop's fourth stage, applied — you reference them, you do not rebuild them.

```python
# module4-fleet/loop/run_loop.py — the four-stage shape, control plane in Python
def run_loop(pattern, switch, budget):
    if switch.tripped():
        return {"outcome": "halted", "reason": "kill_switch"}

    work = pattern.trigger()                 # 1. trigger — discover work
    if not work:
        return {"outcome": "no-op"}          #    early exit: nothing to do, spend nothing

    result = pattern.action(work, budget)    # 2. action — the M3 agent does the job
                                             #    (budget.charge() per step; breach raises and stops)
    verdict = pattern.verify(result)         # 3. verification — independent checker, defaults REJECT
    if verdict.status != "APPROVE":
        pattern.escalate(work, verdict)      #    REJECT/ESCALATE → hand to a human, do not act
        return {"outcome": "escalated"}

    pattern.commit(result)                   #    APPROVE → act (open PR, apply label)
    pattern.log_run(work, result, verdict)   # 4. budget/audit — append to the run log
    return {"outcome": "acted"}
```

The whole loop is a dozen lines. The judgment lives in `pattern.action`; the safety lives in the three stages around it. Notice what the shape forbids: there is no path from `action` to `commit` that skips `verify`. The verifier is in the wire, not in the agent's good intentions.

## The L1/L2/L3 autonomy ladder

The shape tells you *what* a loop does. The autonomy ladder tells you *how much you let it do* — and the rule is that you climb it, you do not start at the top.

**L1 — Report.** The loop triggers, the agent acts, the verifier checks, and the result is *written to a state file for a human to read*. No PR opened, no label applied, no ticket closed. The loop is a tireless analyst that hands you a prioritized list every morning. Read-only connectors only.

**L2 — Assisted.** The loop acts on the small, safe wins itself — a one-line fix, an allowlisted label, a patch-level dependency bump — but only behind the verifier and only within an explicit path allowlist. Everything outside the allowlist still escalates to a human. This is where most production loops live and stay.

**L3 — Unattended.** The loop runs without anyone watching, auto-merging within tight bounds. Few loops earn this, and the ones that do earn it on a narrow scope after weeks of measured L1 and L2 behavior, never on day one.

The ladder is not a preference; it is a calibration sequence. A loop run at L3 on day one acts on a signal you have not measured — its triage is wrong forty percent of the time and you have no idea, because you skipped the report-only phase where you would have found out. Teams that turned on auto-fix while the verifier still rubber-stamped flaky tests learned this the costly way: one CI sweeper run unattended with no budget caps and a verifier sharing the implementer's session burned eight million tokens and proposed eleven bad PRs in forty-eight hours before anyone killed it. The fix was not a better model. It was L1 first, separate verifier, branch allowlist, daily budget — the ladder, climbed in order. [verify: loop-engineering stories — unattended CI sweeper runaway / L1-first graduation]

Measure before you climb. Graduate L1 → L2 when triage accuracy is high and the verifier has been tested independently; graduate L2 → L3 almost never, and only on a path where a wrong action is cheap to undo.

## A loop is the unit; this is where it already runs

The four-stage loop is not a curriculum abstraction — it is the shape production platforms ship. Microsoft Foundry's *routines* are exactly this: a named automation rule with a trigger (a cron schedule or a one-shot timer) and an action (invoke one agent), where the platform queues the invocation, runs the agent, and stores a run record you inspect later. The trigger fires, Foundry creates a run record, invokes the agent's configured model and tools and identity, and links the run to its trace — trigger → action, with the run log and the project-scoped governance built in. [MS-Learn: Foundry Agent Service — routines (trigger/action, run records, project-scoped governance)]

The same docs draw the exact line this chapter is built on. A routine invokes *one* agent; coordinating *many* agents with branching and shared state is a different construct — a workflow. One loop, one agent, governed on its own. Many loops, coordinated, governed together. That second thing is the fleet, and it is the next half of this chapter. A loop is the unit that lives inside it.

## What you build

You take a stub agent from the seeded `_harness/` and wrap it as a governed loop: a trigger with a no-op early exit, the agent action, an independent verifier that defaults to REJECT, and the budget plus kill-switch from lessons 06 and 07 wired as the stop. You run it at L1 — report to a state file, act on nothing — because that is where every loop starts, and because the rung you skip is the one that bites you.

A loop is the smallest thing you can run unattended and still trust. Build it so the verifier sits in the wire and the off switch sits in your hand, and you have infrastructure; skip either and you have an automated way to be wrong faster than you can read.

## Core concepts

- A loop is one agent system run as governed infrastructure: you build the machinery that triggers it, verifies it, budgets it, and persists its state, instead of being that machinery by hand.
- Every loop has the shape trigger → action → verification → budget/kill-switch; the verification gate (from the M3 workbench, lesson 15) and the budget/kill-switch (from lessons 06–07) are non-negotiable stages, referenced here, not redefined — and no path skips the verifier.
- The L1/L2/L3 autonomy ladder is a calibration sequence, not a preference: report-only first, assisted small wins behind a verifier and allowlist next, unattended almost never — climb it by measuring, because the rung you skip is where the runaway hides.
- A loop governs one agent; a fleet governs many — production platforms (Foundry routines vs. workflows) draw the same line, which is why a loop is the unit that lives inside a fleet.

<div class="claude-handoff" data-exercise="exercises/module4/10-the-loop/">

**Build it in Claude Code** — wrap a `_harness/` stub agent as a governed loop with all four stages: a `trigger()` that discovers work and early-exits to a no-op on an empty watchlist; an `action()` that runs the harness agent under the lesson-06 budget (per-task cap, iteration cap, velocity limit); a `verify()` step — an independent checker that defaults to REJECT and approves only on evidence; and the lesson-07 kill switch checked before every action and on every budget breach. Run it at **L1**: write findings to a state file and act on nothing. Prove the no-op exit spends near zero, a budget breach stops the run, and the kill switch halts before the next action. Open the repo and run the exercise for this lesson.

</div>
