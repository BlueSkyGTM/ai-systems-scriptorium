# The Issue-to-PR Autonomous Agent

A backlog fills faster than a team can clear it, and most of what fills it is small: a failing test, a one-line bug, a check gone flaky. Each is cheap to fix and expensive to context-switch into — which is exactly the work you want a loop to take off the team's plate and hand back as a pull request someone can merge in a glance.

## The Business Problem: a Worker, Not a Chatbot

The product category is now familiar. You label an issue, and minutes later a pull request appears — branched, fixed, tested, with the change explained. No one opened an editor. The vendors call these async coding agents; the job they do is the oldest one in software, triaged down to its safe core: turn a described problem into a reviewed change.

The leverage is obvious and the danger is its mirror image. An autonomous worker that clears the boring volume is a force multiplier. The same worker, pointed at `main` with the authority to merge, is a machine for breaking trunk on a schedule — and the failure compounds quietly, because the thing that broke the build is the thing that reports the build is fine. The whole design problem is keeping the leverage while refusing the danger. You let the agent have the volume. You keep the merge.

That single line — *the agent proposes, the human merges* — is what separates this artifact from a demo that opens forty bad PRs over a weekend. Everything below exists to enforce it.

## Capability, One Stack, and the Portable Seam

The capability is an autonomous worker: issue in, reviewed PR out, running unattended under a budget and a kill-switch. You already have the parts. This is the Module 4 loop — `trigger → action → verification → budget/kill-switch` — wrapped around the coding step you built as artifact 01. Nothing here is a new idea; the work is the wiring and the gates.

The one stack is GitHub plus GitHub Actions. The trigger is a labeled issue, delivered as a webhook — GitHub fires an `issues` event with the `labeled` action, and a `pull_request` event when the branch lands. The action runs your coding agent against a checkout. The verification waits on the Actions run for the head commit, polling that run until its `status` is `completed` and reading its `conclusion`. The PR is opened with a fine-grained token scoped to one repository — Contents and Pull-requests read/write, nothing else. Pick this stack and commit to it; you learn more from one wired path than from an abstraction over three.

The **portable seam** is the loop itself: `issue → branch → fix → PR`, gated by a CI check that defaults REJECT. The git host is swappable. Replace "open a PR via the GitHub API" with "open a merge request via the GitLab API," replace "poll the Actions run" with "poll the pipeline status," and the loop above does not change. The seam is the shape, not the vendor — which is why the scaffold draws the host interaction down to two functions (`open_pr`, `run_ci`) and keeps the loop ignorant of which host it talks to.

## The Build Sequence

Build it in the order the loop runs, because each stage gates the next.

1. **Scope the credentials first.** Before any code runs, decide what the agent may touch. It gets a capability broker, never a raw token: one repository, a branch-prefix allowlist (`agent/…`), and the action set `read / branch / commit / open_pr`. `merge` is not in the set. An out-of-scope request raises and stops the run — it is never retried into existence.

2. **Wire the trigger with a no-op exit.** An open issue fires the loop; an empty queue exits at near-zero cost. A loop that spends fifty thousand tokens discovering it has nothing to do bankrupts you on quiet days. The early exit is the first thing you build and the first thing you test.

3. **Drop in the action.** The coding step reads the issue, opens a branch off the allowlist, and drafts a minimal fix. In production this is artifact 01 — the real plan-act-observe coder in its sandbox. On the dry-run path it is a deterministic mock, so the thing under test is the loop and its gates, not the model's mood. The action reports the tokens it spent so the budget can charge it.

4. **Make the verifier reproduce the real gate.** This is the stage teams get wrong. The verifier runs *what CI runs* — the project's actual test and lint command against the head commit — and defaults to REJECT, approving only on a green exit. A verifier that runs a cached shortcut instead of the real path issues false approvals that fail downstream; a verifier that shares the implementer's session rubber-stamps its own work. Independent, real, REJECT-by-default. No exceptions.

5. **Bound the run, then stop short of the merge.** Every step charges a per-run budget — dollars, tokens, iterations — and a breach blocks the next action. The agent reads an operator-owned kill-switch before every action. On a green gate it opens the PR: branch, rationale, CI evidence. Then it stops. The merge is a human action behind a review gate; the agent has no path to it, by construction.

## The Operator Surfaces

Module 8 hands the student the operator's seat: they set the budget, hold the kill-switch, and judge the output. That only works if the surfaces are real in the code, not narrated in a README. This artifact exposes five.

**Scoped credentials.** The agent holds capabilities, not secrets. The broker grants `commit` on `agent/fix-42` and refuses `commit` on `main`, refuses any action on a second repo, and has no `merge` to grant. A real `GITHUB_TOKEN`, if you opt in, is read once at the edge and never passed into the loop — the blast radius of a prompt-injected agent is the allowlist, not your account.

**The kill-switch.** A file the operator owns. The agent calls `tripped()` before every action and halts when it returns true; the class exposes no method to write or clear that file. Stopping is the operator's privilege. A switch the agent can reset is not a switch.

**The CI verification gate.** It defaults REJECT and approves only on real, reproduced evidence. This is the difference between an agent you can run unattended and one you have to babysit — and the EU AI Act's human-oversight requirement reads against it directly: Article 14 obliges a high-risk system to let a person interpret its output, intervene in its operation, and disregard or reverse the result. An inspectable PR plus a gate that fails closed is how you meet it.

**Never auto-merge.** There is no merge in the code — not gated, not flagged, not behind a config you could flip. A passing run produces a PR artifact and an escalation path produces a note for a human. The most dangerous action is removed, not guarded, because a guard is something a tired operator disables at 2 a.m. and a missing function is not.

**The budget.** A per-run ceiling on steps and tokens, charged as the loop runs, stopping the next action on breach. It is the same cost governor from Module 4, applied — the loop's fourth stage, not a new invention.

Climb the autonomy ladder with these, never skip it: L1 reports, L2 acts on small wins behind the verifier and the allowlist, L3 almost never. The merge stays human at every rung.

## The BUILD→TEST Gate

The scaffold passes a local, offline gate before it ships. `python smoke.py` runs the whole loop on a fixture repo — a tiny git repo with a seeded off-by-one bug and an `ISSUE.md` — reading the issue, branching, drafting the mock fix, running the fixture's own tests as CI, and writing a PR body to `outputs/` on the pass. `python -m pytest tests/` pins the four operator surfaces: a passing fix opens a PR on a new branch and leaves `main` unmerged; a non-fixing edit leaves CI red and escalates instead of opening a PR; the kill-switch halts the loop before it spends a token; an out-of-scope credential request is refused.

The hard constraint is that this gate runs on the Python standard library alone. Git is invoked through `subprocess` against your local binary — that is allowed, git is available — but no `anthropic`, no GitHub SDK, no network. The real-model and real-GitHub paths are guarded behind import checks and `.env`, opt-in and never on the test path. The smoke run touches a local git repo and nothing else, so the gate is deterministic and reproducible on a laptop with no cloud account.

## Strong-Project Done-When

This is a portfolio piece, so it clears the hireability bar, not only the smoke test. It has a real entry point (`smoke.py`), not a notebook. Its README frames the business problem — a backlog cleared into reviewed PRs — before a line of code. It ships operator-surface tests, not only a happy-path assertion. It is versioned with a clean layout and an `outputs/skill-issue-to-pr-agent.md` that another agent can load and run. And it makes the one claim that matters in an interview legible in the code: *this worker is autonomous and it cannot merge.*

## What Module 7 Reuses

This artifact is the **autonomous-execution pattern**: a governed loop that discovers work, acts inside a budget, verifies against a gate it cannot fake, and hands the irreversible step to a human. Module 7 composes single agents into a governed fleet, and this is the node that does the unattended work — the same loop, now one worker among many, with the merge gate promoted to a shared human-in-the-loop (HITL) inbox. You do not rebuild the pattern in M7; you instantiate it. Build the seam clean here and the fleet inherits a worker it can already trust to stop in the right place.

## What You Build

You wrap the Module 4 loop around a coding step to turn a fixture issue into a reviewed PR. A scoped credential broker that refuses trunk and refuses a second repo. A trigger with a no-op exit. The coding action (a deterministic mock standing in for artifact 01). A CI verifier that runs the repo's real tests and defaults REJECT. A budget and an operator-owned kill-switch as the stop. On a green gate it opens a PR — a branch plus a body artifact — and stops; on a red gate it escalates to a human. It never merges. The whole thing runs offline on the standard library, and four tests prove the operator surfaces hold.

## Core Concepts

- An issue-to-PR agent is the Module 4 loop (`trigger → action → verification → budget/kill-switch`) wrapped around the artifact-01 coding step; the work is the wiring and the gates, not a new idea.
- The portable seam is `issue → branch → fix → PR` behind a CI gate that defaults REJECT — the git host is swappable, so the vendor lives in two functions (`open_pr`, `run_ci`) and the loop stays host-agnostic.
- The verifier must reproduce the real CI gate and default to REJECT; a cached shortcut or a self-grading checker issues false approvals that fail downstream.
- Never auto-merge: the most dangerous action is removed from the code, not guarded — the agent opens a PR and stops, and the merge is a human action behind an HITL gate at every autonomy rung.
- The operator surfaces are real, not decorative — scoped capabilities (no `merge`, no trunk), a kill-switch the agent reads but cannot clear, a REJECT-by-default CI gate, and a per-run budget — because Module 8 hands the student that exact seat.

<div class="claude-handoff" data-exercise="exercises/module6/04-issue-to-pr-agent/">

**Build It in Claude Code** — wrap the M4 loop around a coding step to turn an issue into a reviewed PR. Build a scoped **credential broker** (one repo, an `agent/` branch allowlist, no `merge` action — out-of-scope requests hard-stop); a **trigger** with a no-op exit on an empty queue; an **action** that branches and drafts a fix (a deterministic mock standing in for artifact 01); a **CI verifier** that runs the repo's real tests and defaults REJECT; and a per-run **budget** plus an operator-owned **kill-switch** the agent reads but cannot clear. On a green gate, write a PR body to `outputs/` and **stop** — never merge; on a red gate, write an escalation note. Prove with tests: a passing fix opens a PR on a new branch and leaves `main` unmerged, a failing CI run escalates instead, the kill-switch halts before any spend, and an out-of-scope credential request is refused. Run `python smoke.py` and `python -m pytest tests/` — stdlib only, offline.

</div>
