# CONTEXT — Anatomy of an Answer (PLANNED)

The career book. Where every other Scriptorium book builds the skills, this one teaches the reader
to demonstrate those skills under pressure: an internal framework for reasoning to a strong answer,
not a script to recite. It covers the AI Engineer hiring loop in full — behavioral, technical, and
AI/ML systems-design interviews — and positions the Sans Python portfolio artifacts as the resume.

**Not started.** Starting it is gated at `GATE-NAME-BOOK` (propose the real title first).

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

- **Load (when it graduates):** this folder's `README.md`, `vault/ai-system-design-guide` chapter
  `00` via `vault/MANIFEST.md`, `ingredients/source/module4/asdg-*`, `platform/pipeline`.
- **Do NOT load:** the shipped book, other planned books (including `show-dont-tell` — this book
  supersedes the interview angle; the orchestrator reconciles the catalog).

## Handoff & gates

`GATE-NAME-BOOK` → process ore via `vault/CONTEXT.md` → `platform/pipeline/CONTEXT.md`
(`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`). See `platform/HUMAN-GATES.md`.
