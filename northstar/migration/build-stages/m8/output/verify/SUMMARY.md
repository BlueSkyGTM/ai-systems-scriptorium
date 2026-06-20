# M8 VERIFY ledger — Module 8, Final Systems Engineering Exam (capstone guides)

CODE passed the BUILD→TEST gate separately. VERIFY (1 subagent) checked the 3 capstone guides: claims, STYLE,
and three coherence checks. All 3 guides PASS. Per-chapter verdicts: this folder.

## The three coherence checks
- **(a) Catalog accuracy — PASS.** All 20 case studies in `02` match `asdg-module4-case-studies.md` (numbers,
  names, architecture types, what-you-replicate). The "seam" column was correctly upgraded from the source's
  Build/Both phase-marker to a genuine architectural seam, validated against the underlying case-study files.
- **(b) Rubric == checker — PASS, no drift.** The R1–R7 acceptance rubric in `03` is clause-for-clause
  identical to `rubric.py`'s `CRITERIA` (RUNS / EVAL-GATED / AUDITED / BUDGET-BOUNDED / HITL-GOVERNED /
  PROBLEM-FRAMED / TESTED+VERSIONED).
- **(c) Runbook == real surfaces — PASS, no drift.** Every operator surface in `03` matches the shipped M7
  fleet (registry + dual budgets, the inbox four-move with `by=` + re-read-on-commit, `answers_four_clauses` +
  the `complete` boolean, the read-only kill-switch).

## Other
- **No platform markers needed** — the guides make no unsourced external claims (the D6 distributed-systems
  note is framed as assumed background).
- **STYLE — all 3 PASS:** H1s, seam leads, `## Core concepts`, `01`'s `## What you build` + claude-handoff div;
  HITL expanded on first use; **the finale's closing lands the thesis** (single agent → team → fleet →
  production system) without the banned template ending.
- **mdbook build PASS** — the final full build, all 8 modules (M1–M8).
