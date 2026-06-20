# Fleet Patterns & Governance-as-Code

The last lesson named the seven concerns a fleet governs. This one hands you the patterns that implement them — six named shapes you reach for by name, the way you reach for a circuit breaker or a retry. Each one turns a concern into a file you can diff, and together they make a fleet not just describable but *runnable* as code. This is the lesson the M7 finale is built on top of, so it earns the closing slot of the chapter.

## Six Patterns, Each a Concern Made Concrete

A fleet pattern is a concern from lesson 12 with a name, a schema, and a governance rule attached. Naming them matters: "we should track our agents" is a wish, but **team-registry** is a thing you can build, audit, and hand to a teammate. Here are the six.

**Team-registry** is the foundational pattern — a machine-readable registry index plus a per-agent manifest for each entry. The manifest carries the four accountability clauses (which agent, whose authority, what task, what evidence), and a human gate guards the changes that matter: granting an agent new production-data access or swapping its credential model is a reviewed pull request, not a quiet edit. Build this first. Every other pattern reads against it.

**Cross-agent-audit** answers the fourth accountability clause across boundaries. When a task crosses three agents, "evidenced by what?" only has an answer if a single correlation ID threads the whole chain — user request to manager to worker to outcome. The pattern is a read-only audit playbook that queries by time range, agent ID, principal, and tool class, reconstructing what happened from records nobody had to remember to write.

**Fleet-budget-guard** is the lesson 06 governor at fleet scale. The single-agent stack capped one task; the fleet version adds a *team* total and per-agent attribution, with admission control that pauses one agent's scheduler when its cap trips — and requires an inbox approval to raise it. The reason per-agent attribution is not optional has a price tag: a fleet that capped only its manager loop watched that manager spawn twelve retries on a flaky API and absorb eight times the normal spend by morning, because nothing attributed the burn to the runaway workers underneath. Cap the manager and the workers.

**Hierarchical-delegation** routes a task from a manager agent to specialized workers through typed, auditable handoff packets — JSON with authority, constraints, and evidence, never a raw string. Workers start *report-only*: their output is a proposal, not an action, and promotion to write-capable autonomy is a human gate. This is the supervisor-worker pattern from lesson 03, governed — the handoff is now a contract you can validate, and the conflict between two workers' outputs is resolved at a gate, not by whichever wrote last.

**Shared-inbox-HITL** is the lesson 08 propose-then-commit protocol with more proposers. Every agent's proposed action routes to *one* central, trackable inbox; principals approve or reject; nothing destructive auto-executes. The governance rule is strict and learned the hard way: approve only through the inbox, with an `inbox_id` on every approval. A team that let an engineer approve a deploy by DM "just this once" could not answer "evidenced by what?" at the incident review, and compliance flagged it as a bypass. An inbox nobody uses is worse than no inbox: it manufactures false confidence.

**Agent-clone-fork** spreads a proven agent across teams without configuration drift. Cloning is gated by a tiered permission model — `can run`, `can clone`, `can edit` — and every fork registers its lineage (`forked_from`, `owner`) so the registry never loses track of where an agent came from. Promotion of a fork from experimental to production is a human gate. Without this, your registry slowly fills with near-identical agents nobody can tell apart, which is how the duplicate-agent audit horror stories start.

You do not need all six on day one. Team-registry first, then the safety patterns the count forces — budget-guard when spend matters, shared-inbox when an agent can do something irreversible. Reach for each when the fleet's risk earns it.

## Two Patterns, Built by Reference Not from Scratch

Two of the six are the single-agent controls you already built, pointed at the fleet. Showing them at scale is the point of this lesson — and showing that you *do not rebuild them* is the discipline.

**Fleet-budget-guard** reuses the `TaskBudget` governor from lesson 06 unchanged. What the fleet adds is attribution and a team ceiling — the governor itself, the deterministic stack of caps, is the same code:

```python
# module4-fleet/governor/fleet_budget.py — the lesson-06 governor, at fleet scale
from governor.budget import TaskBudget, BudgetBreach   # reused, not redefined

class FleetBudgetGuard:
    """Per-agent TaskBudgets under one team ceiling. The cap logic lives in
    TaskBudget (lesson 06); the fleet only adds attribution and admission control."""
    def __init__(self, team_daily_usd: float, per_agent: dict[str, TaskBudget]):
        self.team_daily_usd = team_daily_usd
        self.per_agent = per_agent          # agent_id -> its own TaskBudget
        self.team_spent = 0.0

    def charge(self, agent_id: str, usd: float) -> None:
        self.per_agent[agent_id].charge(usd)     # raises BudgetBreach per-agent (lesson 06)
        self.team_spent += usd
        if self.team_spent > self.team_daily_usd:
            raise BudgetBreach(f"team cap: ${self.team_spent:.2f} > ${self.team_daily_usd:.2f}")
        # admission control: a tripped cap pauses *this* agent's scheduler;
        # raising it requires an inbox approval (shared-inbox-HITL), not a code edit.
```

The import line is the whole argument. The cap logic is not retyped; the runaway-delegation story is defended by attributing every charge to an agent *and* summing to a team ceiling, so neither a single greedy agent nor a swarm of small ones slips through. Define the governor once in lesson 06; the fleet inherits it.

**Shared-inbox-HITL** reuses the propose-then-commit protocol from lesson 08. The single-agent version persisted one proposal with an idempotency key, surfaced the case, committed only on positive acknowledgement, and verified after. The fleet version is the same protocol with a queue in front:

```python
# module4-fleet/hitl/shared_inbox.py — many proposers, one queue, lesson-08 protocol
from hitl.propose import propose, commit          # the protocol, reused not re-taught

def submit(agent_id: str, action, inbox) -> str:
    """Any agent proposes into one shared inbox. The commit gate is lesson 08's,
    unchanged — persist, surface case, positive-ack, verify. The fleet adds the
    queue, the inbox_id, and the no-DM-approval rule."""
    key = propose(action, inbox.store)            # lesson 08: durable, idempotency-keyed
    inbox.enqueue({"agent_id": agent_id, "key": key, "inbox_id": inbox.new_id()})
    return key                                    # the agent's run suspends here
```

What the fleet adds is not a new commit protocol — it is the *queue discipline*: one inbox, an `inbox_id` on every decision, and the hard rule that no approval happens off-channel. The protocol is lesson 08's; the governance is the fleet's.

This is the de-dup rule made visible. Budgets, kill switches, and HITL are defined once in the single-agent chapter and *applied* — by import, by reference — at fleet scale. A fleet lesson that re-derives the propose-then-commit protocol has misunderstood the architecture: the protocol does not change when there are more proposers, only the plumbing around it does.

## Governance-as-Code: the Registry Is a Contract

Step back and look at what every pattern has in common. Each one is backed by a schema — a JSON Schema for the registry and the manifest, a JSON contract for the handoff packet, a structured record for the audit trail. Nothing that governs the fleet lives only in prose. That is the meaning of **governance-as-code**: the rules a fleet runs by are machine-readable artifacts you validate in CI, diff in review, and version in git, the same as the application code they govern.

The payoff is that a fleet becomes *addressable*. A control plane can read the registry and know, without asking a human, what agents exist, what each may do, what it costs, and what needs a gate. Today that reader is Claude Code, pointed at your `registry.yaml`. The registry does not encode the reader, only the contract — which is exactly why a local model can take over the same job tomorrow with no change to the fleet. You are not building a control plane wedded to one vendor; you are building a contract any control plane can speak.

```
registry.yaml ──┐
manifests/*.yaml ├──▶ control plane ──▶ governs ──▶ agent loops
schemas/*.json ──┘   (Claude Code now,
                      a local model later)
```

The same discipline shows up on the platforms. Azure AI Foundry Agent Service is the managed instance of exactly this shape: the agent registry, an Entra-backed identity per agent, role-based access control (RBAC) scoping what each may touch, per-agent cost tracking, and human-approval gates on tool calls — all configuration the platform enforces, not logic baked into each agent. You are building the open, file-backed version of the same idea, which is the point: the pattern is the platform, whether the platform is a cloud product or a folder of YAML.

## This Seeds the M7 Finale

Be explicit about where this goes, because the whole chapter has been pointing at it. **The capstone of this lesson is a small governed fleet, and M7 imports it.** The M7 finale is the governed multi-agent SWE team — a fleet of coding agents that build software under exactly this governance layer: a registry that knows every agent, a shared inbox where a human approves the merges, a fleet-budget-guard that caps the team's spend, cross-agent audit that survives an incident review. M7 does not invent that layer. It picks up the `module4-fleet/` package you assemble here — the registry, the schemas, the budget-guard, the shared inbox — and wraps the M6 coding agents in it.

That is what compounding means in this book, made concrete one more time. The single agents you governed in lessons 06–08 became the controls a fleet reuses. The fleet you assemble now becomes the governance M7's team runs under. Nothing here is a throwaway exercise; the small governed fleet is the literal foundation of the course's largest system. Build it so the reuse is real — typed schemas, importable governors, a registry M7 can read on day one — and the finale starts from a running fleet instead of a blank folder.

A fleet is not a bigger agent. It is a contract that lets many agents run while a human stays accountable for all of them — and a contract written as code is one you can hand to the next system without rewriting a word.

## Core Concepts

- A fleet pattern is a concern made concrete — team-registry, cross-agent-audit, fleet-budget-guard, hierarchical-delegation, shared-inbox-HITL, agent-clone-fork — each backed by a schema and a human gate, reached for by name like a circuit breaker.
- Fleet-budget-guard and shared-inbox-HITL are built by reference, not from scratch: they import the lesson-06 governor and the lesson-08 propose-then-commit protocol unchanged, adding only per-agent attribution, a team ceiling, and queue discipline (one inbox, an `inbox_id`, no off-channel approvals).
- Governance-as-code means every rule a fleet runs by is a machine-readable artifact — JSON/YAML registries and schemas validated in CI — which makes the fleet addressable: a control plane (Claude Code now, a local model later) reads the contract, not the vendor.
- The capstone is a small governed fleet — registry, schemas, fleet-budget-guard, shared inbox — that the M7 governed-multi-agent SWE-team finale imports and wraps the M6 coding agents in; the fleet you assemble here is the literal foundation of the course's largest system.

<div class="claude-handoff" data-exercise="exercises/module4/13-fleet-patterns/">

**Build It in Claude Code** — implement two fleet patterns over the `_harness/` registry and package the result for M7. First, **fleet-budget-guard**: build `FleetBudgetGuard` that holds a per-agent `TaskBudget` (imported from lesson 06, not rewritten) under one team ceiling, charges every action to its agent, and trips on per-agent *or* team cap — prove the runaway-delegation case where many small workers under one manager would slip past a manager-only cap. Second, **shared-inbox-HITL**: build a single inbox where every agent submits proposals through lesson 08's propose-then-commit (imported, not re-taught), each decision carries an `inbox_id`, and an off-channel approval is rejected. Then assemble the governed `module4-fleet/` package — registry, schemas, the budget-guard, the shared inbox — as the drop-in artifact M7 imports to wrap its coding agents.

</div>
