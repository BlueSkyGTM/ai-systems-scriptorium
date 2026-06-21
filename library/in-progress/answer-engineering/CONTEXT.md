# CONTEXT — Answer Engineering (IN PROGRESS)

The career book. Where every other Scriptorium book builds the skills, this one teaches the reader
to demonstrate those skills under pressure: an internal framework for reasoning to a strong answer,
not a script to recite. It treats answer construction as an engineering discipline. It covers the
AI Engineer hiring loop in full — behavioral, technical, and AI/ML systems-design interviews — and
positions the Sans Python portfolio artifacts as the resume.

**Graduated to in-progress 2026-06-21.** `GATE-NAME-BOOK` cleared (title **Answer Engineering**,
slug `answer-engineering`). No module locked yet; the next step is to process the ore and draft the
Module 1 plan. Module 1 ("The Framework", two lessons + two exercises) already has a working draft
in `draft/` from the planning phase — author from it, do not discard it.

## Ore (in the vault — not yet distilled)

- `vault/ai-system-design-guide` (`asdg`) — primary ore. Chapter `00-interview-prep/` (8 files,
  routed out of Sans Python's extraction as the "Ahab" interview block) contains the interview
  prep material this book supersedes with its framework framing. The systems-design interview
  material from chapters `11–17` (already distilled into `ingredients/source/module4/`) is
  supporting ore for the systems-design interview section.
- `vault/ai-system-design-guide` — `COURSES.md` and `GLOSSARY.md` reference files: curated
  course list and terminology, useful for the portfolio-narrative and prep appendix.
- Survey additional vault sources at process-ore time via `vault/MANIFEST.md`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain markdown.
A candidate and a coaching LLM are both valid consumers; the reasoning-framework structure
makes it especially legible to both.

## Load / don't-load

- **Load:** this folder's `README.md` and `draft/`, `vault/ai-system-design-guide` chapter `00`
  via `vault/MANIFEST.md`, `ingredients/source/module4/asdg-*`, `platform/conventions` (AUTHORING +
  STANDARDS + STYLE), `platform/pipeline`.
- **Do NOT load:** the shipped book, other planned books.

## Handoff & gates

`GATE-NAME-BOOK` cleared. For Module 1: draft its `build-log/answer-engineering/m1/PLAN.md`, stop at
`GATE-LOCK-PLAN`, then the fleet authors via `platform/pipeline/CONTEXT.md`, and stop at
`GATE-APPROVE-SHIP` per stage. See `platform/HUMAN-GATES.md`.
