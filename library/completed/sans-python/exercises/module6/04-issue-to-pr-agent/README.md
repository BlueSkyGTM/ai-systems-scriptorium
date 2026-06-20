# Issue-to-PR Autonomous Agent

An autonomous worker that turns a tracker issue into a **reviewed** pull request: it reads the issue, opens a
branch, drafts a fix, runs CI, and — only if CI passes — opens a PR for a human to merge. It **never merges
itself.** When CI fails, it escalates to a person instead of opening a PR.

This is the M4 loop (`trigger → action → verification → budget/kill-switch`) wrapped around a coding step. The
coding step here is a deterministic mock; in production it is the terminal coding agent from artifact 01.

## The business problem

A backlog fills faster than a team can clear it. Most issues are small — a failing test, a one-line bug, a
flaky check — but each one costs a context switch. The promise of an autonomous worker is to take the boring,
verifiable volume off the team's plate and hand back review-ready PRs, while the team keeps the one decision
that matters: whether to merge. The risk is the inverse — an agent that merges its own unreviewed code on a
schedule is the most expensive way ever invented to break `main`. This scaffold is built so the leverage is
real and the risk is contained: every PR is gated by CI and every merge is a human's.

## Run it (offline, standard library only)

```
python smoke.py            # end-to-end on the local fixture repo
python -m pytest tests/    # operator-surface tests (or: python tests/test_smoke.py)
```

No network, no cloud, no Docker. The only external program is your local `git`. The smoke path uses a mock
coder and runs the fixture's own tests as "CI", so it is deterministic and reproducible.

## What's here

| File | Role |
|------|------|
| `loop.py` | The four-stage loop. Trigger → action → verify → budget/kill-switch. Never merges. |
| `action.py` | The coding step. Deterministic mock LLM on the smoke path; artifact 01 in production. |
| `ci.py` | Mock CI = runs the repo's real tests locally. Defaults **REJECT**; APPROVE only on green. |
| `git_ops.py` | Local git only (via `subprocess`). Branch + commit + a PR-body artifact in `outputs/`. **No merge.** |
| `creds.py` | Scoped-credential broker, an operator-owned kill-switch, and a per-run budget. |
| `fixture_repo/` | A tiny repo with a seeded off-by-one bug and an `ISSUE.md`. |
| `smoke.py` | Wires it all together on a fresh copy of the fixture. |
| `tests/test_smoke.py` | Asserts the four operator surfaces below. |
| `outputs/` | Where a PR body or an escalation note lands. |

## Operator surfaces (the things you drive)

- **Scoped credentials.** The agent asks a broker for a capability; the broker grants only in-scope actions on
  an allowlisted branch prefix. Trunk and other repos are refused. `merge` is not a grantable action.
- **Kill-switch.** `touch outputs/KILL` (with any content) halts the loop before its next action. The agent
  reads the switch; it cannot clear it.
- **CI verification gate.** Runs the repo's real tests; defaults REJECT. The agent cannot fake a green check.
- **Never auto-merge.** There is no merge anywhere in the code. A passing run opens a PR and stops; merging is
  a human action behind a review (HITL) gate.
- **Budget.** A per-run step/token ceiling. On breach, the next action does not run.

## Extend to real GitHub (opt-in)

The smoke path is local and offline. To run against a real repository:

1. **Fork a repo you own.** Never point this at a repo you do not control.
2. Copy `.env.example` to `.env` and set a **fine-grained** token (`GITHUB_TOKEN`) scoped to that one fork,
   with Contents and Pull-requests read/write only. No org scope. No classic tokens.
3. Replace the file write in `git_ops.open_pr` with a `POST /repos/{owner}/{repo}/pulls` call, and replace
   `ci.run_ci` with a poll of the GitHub Actions run for the head SHA. The loop above them does not change —
   that is the portable seam.
4. Keep the autonomy ladder: start at **L1** (open the PR, never merge), measure, and never grant merge to the
   agent. The human merges from the GitHub UI.

The default and dry-run path stays local. Real GitHub is something you turn on deliberately, on a fork, with a
narrow token — not the path the tests run.
