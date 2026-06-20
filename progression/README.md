# Progression — the AI-run progress spec

Progression is run by the AI, not built as a feature. There is no progress database and no UI. An
agent reconstructs where a reader stands from three signals, on demand.

## 1. GBrain memory, per book

Each book gets a persistent GBrain namespace. The agent writes what the reader has covered, struggled
with, and shipped — durable memory across sessions, keyed to the book. This replaces a state file.

## 2. Spaced repetition over `## Core concepts`

Every lesson ends with a `## Core concepts` section: 1–4 testable **propositions** (per
`platform/conventions/STYLE.md` §5 — claims, not terms). The item bank already exists, one card per
proposition. The agent schedules review of these cards with spaced repetition, surfacing the ones due
and the ones the reader missed.

## 3. Progress = scan completed artifacts

The reader's real progress is the work they've shipped, not a checkbox. The agent measures it by
scanning, for the book in question:

- `library/<bucket>/<book>/exercises/**` — completed exercise work and artifacts.
- `outputs/skill-*.md` — the skill write-ups a reader produces.

A module is "done" when its artifacts exist and pass their gates — the same gates the build pipeline
runs. No manual marking.

## How an agent uses this

On entering a book: read the GBrain memory, scan the artifacts to confirm what's actually complete,
surface the spaced-repetition cards that are due, and point the reader at the next unstarted lesson.
On finishing a lesson: record it in GBrain and add its `## Core concepts` cards to the schedule.
