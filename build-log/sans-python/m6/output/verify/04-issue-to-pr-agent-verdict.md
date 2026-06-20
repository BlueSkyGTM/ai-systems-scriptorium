# VERIFY verdict — 04 Issue-to-PR Autonomous Agent (build-guide chapter)

Artifact: `build-stages/m6/output/author/04-issue-to-pr-agent.md`
Scaffold: `build-stages/m6/output/author/exercises/module6/04-issue-to-pr-agent/`
Gate: AUTHOR → **VERIFY** (prose: claims + STYLE + guide-matches-scaffold). CODE already passed BUILD→TEST.
Verifier: Sonnet VERIFY subagent. Date: 2026-06-19.

## Markers resolved (all removed from student-facing prose)

| # | Marker (original) | Resolution | Source |
|---|---|---|---|
| 1 | `[verify: GitHub webhook `issues`/`pull_request` events]` | Confirmed. GitHub fires an `issues` event (actions include `labeled`, `opened`, …) and a `pull_request` event (`opened`, `labeled`, `synchronize`, …). `labeled` is an explicit `issues` action. Rewrote into prose. | GitHub docs (WebFetch) |
| 2 | `[MS-Learn: GitHub Actions workflow run status / conclusion API]` | Confirmed. `GET /repos/{owner}/{repo}/actions/runs/{run_id}` returns `status` (queued/in_progress/completed/…) and `conclusion` (success/failure/…), keyed to `head_sha`. MS Learn corroborates the Actions-run pass/fail signal; GitHub REST docs give the exact fields. Rewrote into prose ("polling that run until its `status` is `completed` and reading its `conclusion`"). | GitHub REST docs (WebFetch) + MS Learn |
| 3 | `[verify: GitHub fine-grained PAT / installation-token scopes]` | Confirmed. Fine-grained PATs scope to a single repository ("Only select repositories") with granular permissions incl. **Contents** and **Pull requests** read/write. Matches scaffold `.env.example` guidance. Rewrote into prose ("fine-grained token scoped to one repository — Contents and Pull-requests read/write, nothing else"). | GitHub docs (WebFetch) |
| 4 | `[verify: EU AI Act Article 14 human oversight requirements]` | Confirmed and NOT overstated. Article 14 requires a high-risk system to let a person **interpret** output, **intervene/interrupt** (stop button), and **disregard, override or reverse** the output. Guide's "interpret, intervene, and reverse" maps exactly. Rewrote into prose attributing it to Article 14 without inflating the statute. | artificialintelligenceact.eu Art. 14 (WebFetch) |

## Defects fixed

- **HITL acronym never glossed.** "HITL" appeared unexpanded (lines 63, 74). Expanded on first use → "human-in-the-loop (HITL) inbox" (STYLE §8 / acronym-expansion rule).
- All 4 markers removed; grep clean (no `[verify`/`[MS-Learn` anywhere in the two M6 guides verified).

## Guide-matches-scaffold (confirmed)

- M4 loop `trigger → action → verification → budget/kill-switch` → `loop.py` `run_loop` (kill-switch check → no-op trigger exit → broker read scope → branch → `draft_fix` → commit → `run_ci` → APPROVE opens PR / REJECT escalates). Match.
- Build steps 1–5 map exactly:
  1. credential broker — `creds.py` `Scope(repo, branch_prefixes=("agent/",), actions={read,branch,commit,open_pr})`; `merge` absent; `ScopeError` hard-stop (never retried). ✓
  2. no-op trigger — `loop.py` `if issue is None → "no-op"` before spend. ✓
  3. action reports tokens — `action.py` `FixProposal.tokens_used`, charged in loop. ✓ mock standing in for artifact 01 (`_real_fix` guarded behind `anthropic` import + `.env`). ✓
  4. verifier runs the repo's real tests, default REJECT — `ci.py` `run_ci` shells the test command, `Verdict.REJECT` default, APPROVE only on exit 0. ✓
  5. budget + kill-switch, stop short of merge — budget charged per step; `kill_switch.tripped()` before each action; PR opened with branch/rationale/CI evidence then stop. ✓
- Five operator surfaces (scoped creds, kill-switch, CI gate, never-auto-merge, budget) all real in code; `git_ops.py` has **no `merge()`** (explicit comment confirms). README lists the same five. Guide says "exposes five" — match.
- Portable seam drawn to two functions `open_pr` / `run_ci` — scaffold has `git_ops.open_pr` and `ci.run_ci`. ✓
- `## What you build` + handoff brief: "four tests prove the operator surfaces hold" — scaffold `tests/test_smoke.py` has exactly 4 tests (passing fix opens PR + `main` unmerged; failing CI escalates, no PR; kill-switch halts before spend; out-of-scope cred refused). Confirmed by live run: **4 passed**. ✓
- claude-handoff div → `exercises/module6/04-issue-to-pr-agent/` (correct exercise). Brief names match scaffold elements (`outputs/` PR body, escalation note, `agent/` allowlist, stdlib/offline).
- BUILD→TEST re-run live: `python smoke.py` exit 0 (outcome "acted", PR artifact, no merge); `python -m pytest tests/` = **4 passed**.

## STYLE (full-read)

- H1 ✓ ("The Issue-to-PR Autonomous Agent"; "pull request" glossed in the lead). Seam-framed lead ✓ (backlog → loop hands back a reviewed PR).
- Unity: 2nd person, present tense, blunt/opinionated voice — held throughout, incl. inserted prose. ✓
- `## What you build` ✓ · `## Core concepts` ✓ (5 propositions — consistent with the artifact-guide grain; in-voice).
- claude-handoff div present, correct exercise path. ✓
- Ending shape: build-guide closes its argument on "The merge stays human at every rung" (operator-surfaces) and "the fleet inherits a worker it can already trust to stop in the right place" (M7-reuse) — consequence/reframe, not the banned template. ✓
- Acronyms: PR glossed in lead; CI house-standard (M4/M5); HITL now expanded on first use (fixed above).

## FLAGGED (non-blocking)

- Build step 4 says the verifier runs "the project's actual test **and lint** command." The fixture's default CI command (`ci.default_ci_command`) runs tests only (pytest, or the test file directly when pytest is absent). This is describing the *production* gate, and `run_ci(command=...)` is configurable to include lint — so the statement is true of the general case, not a claim about the fixture. Reader-accurate; left as-is. Flagging for awareness only.

## Verdict

**PASS.** All 4 markers resolved against authoritative sources (GitHub webhook events, Actions run status/conclusion, fine-grained PAT scopes, EU AI Act Art. 14) and removed from student-facing prose; HITL acronym defect fixed; guide matches the scaffold (M4 loop, five operator surfaces, two-function host seam, four tests, no merge in code); STYLE holds. The load-bearing claim — *autonomous and cannot merge* — is true in the code (`git_ops.py` has no merge path). Ready for SHIP.
