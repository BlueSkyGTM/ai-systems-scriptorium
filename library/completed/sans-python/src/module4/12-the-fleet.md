# The Fleet — Graduation to Governed Many

One agent you can hold in your head. Twelve you cannot — and the day you discover you are running twelve is usually the day an audit finds the four you forgot about. A fleet is what a pile of loops becomes when you stop tracking it by memory and start governing it as infrastructure, and that shift is the job this lesson names.

## Loops Live Inside Fleets

The relationship is the whole idea, so state it plainly: **loops live inside fleets.** A loop is one agent system run as governed infrastructure — the `trigger → action → verification → budget/kill-switch` shape from lessons 10 and 11. A fleet is the layer above: the registry, identity, and oversight that govern *many* loops at once. You do not choose between them. You build loops, and once you have enough of them, the fleet is the thing that keeps them from becoming a liability.

```
Loop   = trigger + action + verification + budget/kill-switch   (inside one agent system)
Fleet  = registry + identity + permissions + inbox + audit + economics + kill switch
```

The line between "a few loops I run" and "a fleet I govern" is not a feeling. It is a threshold, and fleet engineering names a specific one: **3 loops or 5 agents.** That number is a working heuristic, not a law of nature — but it marks the point where holding the fleet in your head stops being reliable. Below it, you can hold the whole thing in your head — you know what each loop does, who owns it, what it can touch. Above it, you cannot, and "I think that's all of them" stops being an acceptable answer to an incident reviewer. The threshold is the moment your single-agent safety controls need a governance layer wrapped around them.

This is the complexity ladder again, one rung up. Lesson 01 gated entry into multi-agent at all: more agents, not a bigger agent, and only past the single-agent ceiling. The same discipline gates the fleet. You do not stand up a registry and an audit pipeline for two loops you can name from memory — that is governance theater, cost with no incident it prevents. You graduate when the count forces it, not before.

## The Accountability Test Is the Whole Standard

Before the seven concerns, there is one sentence that defines whether a fleet is governed at all. For any automated action, you must be able to answer:

> *Which agent did it, with what authority, against what task, evidenced by what?*

Four clauses — **which / authority / task / evidence** — and a fleet that cannot answer all four for every action it takes is not governed. It is unattended. The test is useful precisely because it is unforgiving: an on-call engineer who approves a deploy by Slack DM instead of the logged inbox has broken the *evidence* clause, and "it was fine, I was watching" is not an answer an auditor accepts. Every governance concern that follows exists to make one of those four clauses answerable in code rather than from memory.

Hold this sentence. It is the spine of lesson 13's audit pattern, and it is the standard the M7 finale is graded against.

## The Seven Concerns, in Order

A fleet governs seven things. The order is not arbitrary — each concern assumes the one before it exists, so you build them in sequence:

**Registry** — the machine-readable list of what agents exist. You cannot govern what you have not enumerated, and the first honest fleet audit almost always finds agents nobody listed. One real team had 8 "official" agents and 14 actually running; the six shadows shared an API key and had no owner. The registry is boring catalog work, and it is the floor everything else stands on.

**Identity** — each agent in the registry has a stable ID and a named owner. An agent without an accountable owner fails the accountability test before it runs a single action; "which agent, owned by whom" is two of the four clauses answered by identity alone.

**Permissions** — what each agent may touch, declared as least privilege. The researcher reads; it does not write. The deployer writes; it does not read customer data. Permissions are the *authority* clause, made explicit and diffable instead of implied by whatever credential happened to be in the environment.

**Inbox-HITL** (human-in-the-loop) — one queue where proposed actions wait for a human. This is the propose-then-commit protocol from lesson 08, applied across the fleet: proposals from every agent land in *one* inbox, approvers work the queue, and the same persist-surface-acknowledge-verify gate governs each. You defined that protocol once for a single agent; the fleet inbox is that protocol with more proposers. Lesson 13 builds it.

**Audit** — the evidence trail that answers the fourth clause. Every action leaves a record tied to a correlation ID, so an incident review can reconstruct who did what across agent boundaries. Audit is not extra work bolted on; done right, it is the byproduct of the inbox and the registry doing their jobs.

**Economics** — the budget governor from lesson 06, now running at fleet scale. The same deterministic stack of caps — `max_tokens`, iteration, per-task, velocity, calendar — but with a *team* total and per-agent attribution, so one runaway loop cannot quietly absorb the whole fleet's budget. A real fleet capped the manager loop but not its workers; the manager spawned twelve retries on a flaky API and spent eight times normal by 6 a.m., because the cap had no per-agent attribution to catch the runaway delegation tree. Cap the manager *and* the workers. Lesson 13's fleet-budget-guard does exactly this.

**Kill switch** — the control plane from lesson 07, shared across the fleet. One switch the operator owns and no agent can write, checked by every loop before every action. The only thing that changes at scale is the number of readers: many loops, one switch, still in the operator's hand.

Three of those seven — inbox-HITL, economics, kill switch — you already built for a single agent in lessons 06, 07, and 08. At fleet scale you do not rebuild them. You point them at many agents instead of one. That is the entire trick, and it is why the single-agent safety chapter had to come first: the fleet is those controls, multiplied, plus a registry that knows who is being controlled.

## The Fleet Is Addressable as Code

Here is the part that makes this platform engineering and not a spreadsheet of agents. The registry is not a wiki page someone updates by hand. It is a machine-readable file — JSON or YAML — and every governance check reads against it. Two schemas carry the load: an **AgentManifest** that declares one agent's identity, permissions, autonomy tier, budget, and required human gates; and an **AgentRegistry** that indexes every manifest with its owner and status. Both ship as JSON Schema, so a malformed registry fails validation in CI before it governs anything.

```yaml
# module4-fleet/registry.yaml — the fleet's source of truth, diffable and reviewable
fleet: module4-fleet
version: 1.0.0
agents:
  - id: researcher-01
    owner: platform-team           # identity: who is accountable
    autonomy_tier: F1              # F0 manual … F3 fully autonomous
    status: active
    permissions:                   # least privilege, declared not implied
      tools: [search, read_file]
      can_write: false
    budget_daily_tokens: 200000    # economics: per-agent cap, not just a team total
    human_gates: [production_data_access]   # inbox-HITL: what needs a person
    evidence: orchestrator.py      # audit: where to prove this agent acts
```

Everything that governs the fleet — identity, permissions, budgets, gates — lives in a file you can `git diff`, review in a pull request, and validate in CI. That is the everything-as-code stance: the fleet's governance is not tribal knowledge held by whoever has been on the team longest; it is a reviewable artifact. The **autonomy tier** field (F0 through F3, manual to fully autonomous) is how an agent earns trust over time — a new agent ships at F1 (report-only, human-gated), and promotion to a higher tier is a reviewed change to this file, not a quiet config edit.

Because the registry is addressable as code, something else falls out for free: a control plane can *point at it*. Today that control plane is Claude Code reading the registry to know what agents it governs; tomorrow it is a local model doing the same. The fleet does not care who reads it, only that what governs it is written down in a contract a machine can parse. This is the golden-path, internal-developer-platform idea from platform engineering, applied to a fleet of agents: the registry is the platform's source of truth, and every agent is a paved-road tenant of it.

Microsoft's agent platforms encode this same shape. Azure AI Foundry Agent Service gives each agent its own Entra-backed identity, scopes what it may touch with role-based access control, tracks per-agent cost and quota centrally, and gates tool calls behind human approval workflows — governance declared centrally rather than wired into each agent. You are building the open, file-backed version of the same control plane.

## What Graduation Costs

Do not romanticize this. Standing up a fleet is unglamorous: a two-hour inventory that turns up four duplicate "weekly report" agents with different credentials, an audit that scores your team 32 out of 100 and names the shadows, an afternoon spent retiring agents nobody will miss. The first week of fleet engineering is catalog work — and that is the point. The boring enumeration is what makes the exciting automation safe to leave running. A fleet you govern is one you can sleep through the night with; a fleet you merely operate is one you find out about during the incident.

## Core Concepts

- Loops live inside fleets: a loop is one governed agent system (`trigger → action → verification → budget/kill-switch`); a fleet is the registry-and-oversight layer above many loops, and you graduate at the 3-loop / 5-agent threshold — not before, because below it the controls are theater.
- The accountability test — *which agent, with what authority, against what task, evidenced by what?* — is the whole standard; a fleet that cannot answer all four clauses for every action is unattended, not governed.
- A fleet governs seven concerns in order — registry → identity → permissions → inbox-HITL → audit → economics → kill switch — and three of them (inbox-HITL, economics, kill switch) are the single-agent controls from lessons 06–08 pointed at many agents, not rebuilt.
- The registry and per-agent manifests are machine-readable JSON/YAML validated in CI, which makes the fleet addressable as code — a control plane (Claude Code now, a local model later) reads the contract to know what it governs; that is platform engineering applied to agents.

<div class="claude-handoff" data-exercise="exercises/module4/12-the-fleet/">

**Build It in Claude Code** — turn the `_harness/` into a governed fleet. Promote `registry.yaml` into a real machine-readable fleet registry: give each agent a stable `id`, a named `owner`, an `autonomy_tier`, least-privilege `permissions`, a per-agent `budget_daily_tokens`, and `human_gates`. Write a JSON Schema for the registry and validate the file against it, so a malformed entry fails before it governs anything. Then make the orchestrator *read* the registry to authorize each agent's action — an agent attempting a tool outside its declared permissions is refused, and the refusal is logged with the accountability sentence (which agent, what authority, what task, what evidence). Prove the fleet can answer all four accountability clauses for one real action.

</div>
