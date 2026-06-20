# Module 8 — Final Systems Engineering Exam — Build Plan

Status: **PLAN LOCKED (2026-06-19)** by Opus. The course's terminal node. **No new agent code** — M8 points the
**M7 governed fleet** (artifact 03) at a production-grade systems problem; the student operates and judges it.
Pipeline: **AUTHOR → VERIFY → BUILD→TEST → SHIP** (the gate proves the exam harness *runs* the M7 fleet end to
end). Canonical build layer: `northstar/migration/`.

M8 = **3 guide chapters** in `src/module8/` + **1 exam exercise** in `exercises/module8/`. The exam is the
portfolio capstone: a fleet of agents, run as governed infrastructure, building a production system, judged
against real reference architectures — the AI Platform Engineering job description, demonstrated.

## The exam (what the student does)
Pick one of three tracks, pick a reference architecture (from the 20 `asdg` Ch16 case studies), write a task
spec, point the M7 governed fleet at it, **operate** it (budgets, HITL inbox, audit, kill-switch), and **judge**
the output against an acceptance rubric. Build *a version of* a real architecture — not blank-page invention.

**Three tracks** (each anchored to case studies):
- **Eval-gated CI/CD** — #18 eval-gated CI/CD, #19 distillation w/ eval-gated canary, #17 multi-tenant LoRA w/ eval-gated promotion.
- **Multi-tenant RAG** — #08 multi-tenant SaaS, #01 enterprise RAG, #12 compliance RAG (audit trail), #15 enterprise KM.
- **Agentic system** — #07 autonomous coding agent, #09 multi-agent support, #16 computer-use agent, #20 MCP knowledge agent.

## Student role (locked in M6 PLAN): operator + judge + architect-of-record
(1) frame the problem + pick the reference architecture; (2) configure + operate the M7 fleet — set budgets,
approve the HITL inbox, review the audit, hold the kill-switch; (3) judge output against the acceptance rubric;
(4) intervene on failure. The exam tests whether you can **run a governed fleet to ship a system and judge it.**

## Deliverables
**A. 3 guide chapters** → `build-stages/m8/output/author/` :
- `01-the-exam.md` — the brief: the three tracks, "build a version of" (not blank-page), how the M7 fleet does
  the building and the student operates+judges; the compounding arc's terminal node (single→team→fleet→system).
- `02-reference-architectures.md` — the catalog: the 20 `asdg` Ch16 case studies distilled as reference
  architectures (the table from `asdg-module4-case-studies.md`), grouped by track, with "what you replicate"
  and the seam; how to choose one and scope "a version of."
- `03-operating-and-grading.md` — the **operator runbook** for the M7 fleet (configure registry/budgets, work
  the HITL inbox, read the audit's four clauses, use the kill-switch) + the **acceptance rubric** (the
  hireability strong-project bar applied to a *system*: runs/deployed, eval-gated, audited, budget-bounded,
  README framing the problem, tests, versioned) + the assumed-not-taught distributed-systems vocabulary note
  (load balancing, caching, sharding, async/queues, CAP for distributed agent state — deviation D6).

**B. The exam exercise** → `build-stages/m8/output/author/exercises/module8/` :
- `spec_template.md` — the task-spec the student fills (chosen track + reference arch + acceptance criteria).
- `run_exam.py` — the driver: loads the M7 fleet (artifact 03) and points it at a task spec (`ship_feature`/
  `load_fleet`), under the operator console.
- `rubric.py` — the acceptance-rubric checker: evaluates the produced system against the criteria (tests pass,
  audit complete, budget respected, eval gate met) → a pass/fail-per-criterion report.
- `sample_spec.md` + `smoke.py` — a worked example: point the fleet at a sample reference-arch spec, ship a
  version (mock LLM), run the rubric checker, print the graded result.
- `tests/`, `README.md` (the exam instructions + the operator runbook), `outputs/skill-final-exam.md`.

## BUILD→TEST gate
`python smoke.py` runs the exam end to end **offline/stdlib-only** — points the M7 fleet at the sample spec
(deterministic mock), the fleet ships a version under governance, the rubric checker grades it; `python -m
pytest tests/` passes (the fleet ships; the rubric fails a deliberately-deficient output; the operator surfaces
work). Reuse the M7 artifact-03 fleet (import it; don't rebuild). No cloud/GPU/Docker. `mdbook build` at SHIP.

## Sources + claim-authority
1. `synthesis/source/module4/asdg-module4-case-studies.md` (the 20 case studies) + the shipped M7 fleet
   (`exercises/module7/03-governed-multi-agent-fleet/`) — import/point at it.
2. **MS Learn** for any Azure reference-arch detail · **WebFetch** for non-MS. Mark platform claims; resolve at VERIFY.
3. **Do not read any path containing `skills/` or `gstack/`.**

## Execution model
Opus = editor-in-chief. **One Sonnet drafter** for all of M8 (the 3 guides + the exam harness) — coherence
matters: the rubric in the guide must match `rubric.py`; the runbook must match the M7 fleet's real surfaces.
Then VERIFY (claim/STYLE/guide-matches-harness), BUILD/TEST (Opus re-runs the exam smoke), SHIP.

## Done-when
3 guides in `src/module8/`, `src/SUMMARY.md` entries, the exam exercise in `exercises/module8/` passing the
BUILD→TEST gate, `outputs/skill-final-exam.md`, VERIFY + BUILD/TEST verdicts, and `mdbook build` clean (the
**final full build** of the complete course).
