# VERIFY verdict — 01-the-exam.md

Subagent: Sonnet VERIFY (M8 capstone guides). Gate: guide prose (claims, STYLE, coherence).
Harness already passed BUILD→TEST (smoke 7/7, pytest 9).

## Claim ledger

| # | Claim in guide | Source | Result |
|---|----------------|--------|--------|
| 1 | The exam reuses the M7 governed fleet; no new agent build | PLAN.md; fleet_adapter.py (imports real M7 `load_fleet`, never redefines) | VERIFIED |
| 2 | Five agents: architect, 2 coders, tester, reviewer | registry.yaml (architect-01, coder-1, coder-2, reviewer-01, tester-01) | VERIFIED |
| 3 | Operator surfaces: registry+budgets, HITL inbox, cross-agent audit, kill switch | governance/{fleet_budget,inbox,audit,killswitch}.py + fleet.py | VERIFIED |
| 4 | Student grades against a seven-criterion acceptance rubric | rubric.py CRITERIA (R1–R7) | VERIFIED |
| 5 | Three tracks; each anchored to specific Ch16 case studies | 02 catalog + asdg source; spec.py TRACKS | VERIFIED |
| 6 | Sample spec replicates a version of #07 autonomous coding agent, offline | sample_spec.md (track agentic-system, #07), smoke.py (stdlib mock) | VERIFIED |
| 7 | claude-handoff div: run_exam.py imports via fleet_adapter.py; smoke.py; pytest tests/; spec_template.md; four-clause audit; kill switch; team budget | run_exam.py, fleet_adapter.py, smoke.py, tests/, spec_template.md | VERIFIED |
| 8 | Compounding arc: single agent → team → governed fleet → production system | M6/M7/M8 PLANs; consistent with course arc | VERIFIED |

No platform markers present; no unsourced external claims. (grep for [PLATFORM]/[FLAG]/etc.: none.)

## Three coherence checks
- (a) Catalog accuracy — N/A here (catalog lives in 02); 01's track→case-study anchors (#18 eval-gated, #08 RAG, #07 agentic) cross-checked against 02 and the asdg source. CONSISTENT.
- (b) Rubric == checker — 01 references "seven-criterion acceptance rubric"; matches rubric.py. CONSISTENT.
- (c) Runbook == surfaces — 01's operator-role sentence (registry/budgets, HITL inbox, audit, kill switch) matches the four real M7 surfaces. CONSISTENT.

## STYLE result
- H1 `# The Exam` present. ✓
- Seam lead: "Every module before this one handed you a part. This one hands you the job." — hooks, present tense, second person, no throat-clearing. ✓
- `## What you build` present. ✓  `## Core concepts` present (4 propositions). ✓  claude-handoff div present and accurate. ✓
- Unity: second person + present tense throughout; no "we"/"the student". ✓
- No banned template ending. Finale closer — "It is the summit of the one you have been climbing — and the proof you can stand on it." — reframe shape, lands the compounding-arc thesis with a click. STRONG FINALE.
- Fix applied: expanded HITL on first use → "human-in-the-loop (HITL) inbox" (line 31), matching the course's own M4-lesson-08 convention.

## FLAGGED
- None.

## VERDICT: PASS
The finale's closing lands the thesis (the summit of the compounding arc) without any template ending. All claims verified against the harness and source. One small STYLE fix applied (HITL expansion).
