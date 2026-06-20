# M8 SHIP manifest — Module 8, Final Systems Engineering Exam — COURSE COMPLETE

Shipped 2026-06-19. AUTHOR → VERIFY → BUILD→TEST → SHIP complete. **This is the last module — the course is
built end to end.** Final full `mdbook build` PASS (all 8 modules render).

## What shipped
- 3 capstone guide chapters → `src/module8/` (01-the-exam, 02-reference-architectures, 03-operating-and-grading).
- The exam exercise → `exercises/module8/` (spec template, `fleet_adapter.py`, `run_exam.py`, `rubric.py`,
  `smoke.py`, sample spec, tests, README runbook, `outputs/skill-final-exam.md`), passing the BUILD→TEST gate
  from its shipped location (7/7 rubric, 9 tests) — and it **reuses the real M7 fleet** (no rebuild).
- `src/SUMMARY.md` M8 section: Overview + 3 chapters.

## Pipeline records
- BUILD→TEST: `build-stages/m8/output/build-test/SUMMARY.md` (the full composition chain runs end to end).
- VERIFY: `build-stages/m8/output/verify/SUMMARY.md` (3 coherence checks pass; finale lands the thesis).

## The course, end to end
M1 Foundations · M2 LLM Engineering · M3 Agent Foundations · M4 Multi-Agent Systems · M5 Deploy & Performance ·
M6 Agent Artifacts · M7 Multi-Agent Artifacts · M8 Final Exam. The compounding arc closes: single agent (M3) →
governed team (M4/M7) → production system (M8), built by a fleet the student operates and judges. Thesis full
circle — a fleet of agents run as governed infrastructure = AI Platform Engineering.

## Carried flags (non-blocking; for a closing reconciliation pass)
- The ~73% RAG-retrieval-failure figure (shipped in M2 `03-rag-system.md`, referenced in M5 L11) — soft
  provenance; rule on attribution across both lessons together.
- One M3 exercise (`05-typing-the-product-layer`) still carries a banned "An AI Platform Engineer who…" frame.
- M1/M2 module Overview READMEs were not re-read against the final structure; quick confirm.
