# CONTEXT — progression/ (the AI-run progress spec)

Progression is **AI-run, not built**: no manual state, no progress UI. This folder holds the spec for
how an agent tracks a reader's progress through a book.

## What's here

- `README.md` — the progress spec: GBrain memory per book + spaced repetition over each lesson's
  `## Core concepts` propositions + "progress = scan completed artifacts."
- `open-brain.md` — the named spaced-repetition concept: **Open Brain** (open spaced repetition +
  GBrain), agent-driven adaptive quizzing over the §5 `## Core concepts` bank; build target = an
  Extra Credit tool.

## Load / don't-load

- **Load:** `progression/README.md`. To run progress, also read a book's `exercises/**` and
  `outputs/skill-*.md` to scan completed artifacts.
- **Do NOT load:** the pipeline internals, the vault, or other books' source — progression reads
  artifacts, it does not author.

## Handoff

This is a spec, not a stage. No gates own this folder. The `## Core concepts` item bank it consumes
is produced by AUTHOR per `platform/conventions/STYLE.md` §5.
