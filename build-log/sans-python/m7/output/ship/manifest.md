# M7 SHIP manifest — Module 7, Multi-Agent Artifacts

Shipped 2026-06-19. AUTHOR → VERIFY → BUILD→TEST → SHIP complete. `mdbook build` PASS (M1–M7 live). 3 governed-team
artifacts, each a guide + a runnable composed scaffold passing the offline gate (3/3 smoke, 24/24 tests).

## What shipped
- 3 build-guide chapters → `src/module7/` (01 autonomous-research-agent, 02 devops-k8s-agent, 03 governed-multi-agent-fleet).
- 3 composed scaffolds → `exercises/module7/<artifact>/` (each: smoke.py + tests + README + `outputs/skill-*.md`), all gate-passing.
- `src/SUMMARY.md` M7 section: Overview + 3 artifacts. `src/module7/README.md` rewritten (elevate-don't-author + operator-console + M8 framing).
- Runtime artifacts (audit.jsonl etc.) cleaned from scaffolds; only `skill-*.md` in `outputs/`.

## Pipeline records
- BUILD→TEST: `build-stages/m7/output/build-test/SUMMARY.md` (Opus re-ran all 3; 24/24).
- VERIFY: `build-stages/m7/output/verify/SUMMARY.md` (3 guides PASS; finale's full console verified vs code; M8 hand-off confirmed).

## The finale → M8
Artifact 03 (governed multi-agent fleet) is the **operator console M8 drives.** Its registry is the contract
M8 edits to point the fleet at a production problem; `ship_feature(...)` runs it; the student operates
(budgets, HITL inbox, audit, kill-switch) and judges. Thesis full circle: a fleet of agents run as governed
infrastructure = AI Platform Engineering.

## Next: M8 (Final Systems Engineering Exam)
The M7 governed fleet builds *a version of* a production architecture (eval-gated pipeline / multi-tenant RAG /
agentic MLOps), using the 20 `asdg` Ch16 case studies as reference architectures. **No new agent code** — M8 =
a guide + an exam exercise (reference-architecture catalog + an operator runbook for the M7 fleet + an
acceptance rubric). Student = operator + judge + architect-of-record. Write `build-stages/m8/PLAN.md` first.
