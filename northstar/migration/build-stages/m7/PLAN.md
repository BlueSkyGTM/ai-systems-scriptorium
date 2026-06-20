# Module 7 — Multi-Agent Artifacts — Build Plan

Status: **PLAN LOCKED (2026-06-19)** by Opus. M7 **composes** the M6 single-agent artifacts into governed teams,
wrapping them in the M4 fleet/loop layer. Pipeline: **AUTHOR → VERIFY → BUILD→TEST → SHIP** (same code gate as
M6). Canonical build layer: `northstar/migration/`.

**Finale principle — elevate, don't author (DRY):** reuse the M6 artifacts as *nodes* and the M4 fleet
primitives as *governance*; do not rebuild a coding agent or a fleet from scratch. A fleet of agents run as
governed infrastructure = AI Platform Engineering — the thesis, full circle.

M7 ships **3 artifacts**, each a build-guide chapter in `src/module7/` + a runnable, gate-passing scaffold in
`exercises/module7/`. Each exposes the **operator surfaces** the M8 student drives, and the finale (03) is the
governed fleet M8 points at a production problem.

## The 3 artifacts (compose M6 + M4; capability + portable seam)

| # / file | Artifact | Capability | Composes (reuses) | Operator surfaces | Dry-run (local smoke) |
|---|---|---|---|---|---|
| 01 `01-autonomous-research-agent.md` | Autonomous research agent | plan→execute→verify tree search with sub-agents + sandbox | M6 worker (01) pattern + M4 supervisor-worker/ReWOO planning + M3 verification gate | budget, per-result verification gate, kill-switch | supervisor decomposes a fixed question → mock sub-agents in sandbox → verify → synthesize, under budget |
| 02 `02-devops-k8s-agent.md` | DevOps K8s troubleshooting agent | supervisor + read-only specialists, HITL gate before any change | M6 agents under an M4 supervisor + M4 HITL (08) + audit | read-only enforcement, HITL approval gate (mock Slack), audit log, kill-switch | mock incident → read-only diagnose → propose remediation → HITL blocks auto-apply → on approval, simulate apply |
| 03 `03-governed-multi-agent-fleet.md` | **Governed multi-agent fleet (FINALE)** | a SWE team (architect / coders / reviewer / tester via A2A) wrapped in the fleet layer | **M6 coding agent (01) as the coder nodes** + M4 fleet (12/13: registry, budgets, HITL inbox, audit, kill-switch) + M4 A2A (02) | the full console: **registry, fleet budget, HITL inbox, cross-agent audit, kill-switch** | feature request → architect plans → coders implement (mock) → reviewer+tester verify → HITL inbox approves merge → audit complete, under fleet budget |

## The BUILD→TEST gate (same as M6, raised for composition)
Each scaffold passes locally and offline before SHIP:
- **`python smoke.py`** runs the *composition* end-to-end with deterministic mocks (no cloud/GPU/Docker), and
  **`python -m pytest tests/`** passes — exercising the operator surfaces (budget breach stops; kill-switch
  halts; verification/HITL gate blocks a bad/unapproved action; read-only specialist refuses a write).
- **Stdlib-only smoke path** — guard every third-party import (`anthropic`, k8s/slack SDKs) behind
  `try/except ImportError` with deterministic fallbacks. Real services opt-in via `.env`.
- The smoke must prove the **composition runs** (a team coordinating), not just a single agent. `npx tsc --noEmit`
  for any TS A2A contract. `mdbook build` at SHIP for the guides.

## "Strong project" bar (every artifact's done-when)
Locally-runnable composition (a real `smoke` entry, not a notebook) · README framing the **business problem** ·
evaluation/acceptance gate · tests (incl. operator-surface tests) · versioned · ships `outputs/skill-*.md`.

## M8 hand-off (finale 03 → exam)
Artifact 03 is the **governed fleet M8 operates.** Build it so M8 can point it at a new problem with no rewrite:
the registry/budget/HITL-inbox/audit/kill-switch are the **operator console**; the task spec is an input. The
M8 student (operator + judge + architect-of-record) configures budgets, approves the HITL inbox, reads the
audit, holds the kill-switch, and judges output against an acceptance rubric. Design 03's surfaces accordingly.

## Sources + claim-authority
1. `synthesis/source/module5/aefs-module5-capstone.md` (capstones 05, 06, 10★). Reuse the shipped
   `src/module4/*` (fleet/loop/A2A/HITL) and `exercises/module6/*` (the M6 nodes) — read them; compose them.
2. **MS Learn connector** for Azure (AKS for the K8s artifact, Azure AI Foundry agent service) · **WebFetch**
   for non-MS (A2A spec, Slack API shape, Kubernetes API concepts). Mark platform claims; resolve at VERIFY.
3. **Do not read any path containing `skills/` or `gstack/`.**

## Execution model
Opus = editor-in-chief. One Sonnet drafter per artifact (guide + composed scaffold + exercise README +
`outputs/skill-*.md`). Then VERIFY (claim/STYLE/guide-matches-scaffold), then BUILD/TEST (Opus re-runs each
smoke + pytest), then SHIP. The finale (03) gets the closest review — it is the course's largest system and the
M8 substrate.

## Done-when (per artifact)
A guide in `src/module7/`, a `src/SUMMARY.md` entry, a `## What you build` + `## Core concepts` block, a
runnable composed scaffold in `exercises/module7/<artifact>/` passing the BUILD→TEST gate, an `outputs/skill-*.md`,
a per-artifact VERIFY + BUILD/TEST verdict, and `mdbook build` clean at SHIP.
