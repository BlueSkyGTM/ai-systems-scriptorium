# CLAUDE.md — Sans Python course (authoring repo)

You are authoring the **Sans Python — AI Platform Engineering** course: an mdBook of lessons (read here) +
exercises (built in Claude Code). Your job is to turn the migration ingredients into finished lessons, in one
locked voice, with nothing left to chance.

## Read before you write

1. **`AUTHORING.md`** — the authoring contract: the three-source rule, the per-lesson How To, thread
   placement, the Zinsser pass, done-when, and the M1→M8 order. **Read it fully first.**
2. **`STYLE.md`** — the Style Contract. The voice is law; this file wins every disagreement.
3. **`src/preface.md` + `src/README.md`** — the canonical voice. Match it.

## How this session runs

You (Opus) are the editor-in-chief; Sonnet subagents draft. You hold the voice and review every draft before
it lands. The full pattern, roles, and guardrails live in **`AUTHORING.md` → Execution model** — read it
there; it is not restated here.

## Where things are

- `src/moduleN/` — the organized ingredients (write finished lessons here) · `_dossier/moduleN.md` — the
  keep/cut/merge/thread ruling (read-only) · `../sub-repos/synthesis/source/moduleN/` — full extraction depth
  (author in place so this resolves) · `exercises/` — one brief per lesson · `theme/` — the copy-to-Claude
  button · `src/antilibrary.md` — what stays cut.

Start: read `AUTHORING.md`, then author Module 1.
