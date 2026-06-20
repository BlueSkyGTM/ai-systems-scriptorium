# CONTEXT — platform/pipeline/ (the build pipeline)

The reusable stage pattern that builds every book, generalized from the proven sans-python build
(the per-stage `CONTEXT.md` + `PLAN.md` + `output/{author,verify,ship}/` ledgers now recorded in
`build-log/sans-python/`). One book moves through these stages, one stage per chapter/module.

## The stages

1. **AUTHOR** — turn `ingredients` (distilled source + the dossier ruling) into finished lessons +
   Claude Code exercises, in the `platform/conventions/STYLE.md` voice, using
   `platform/templates/`. Draft, then run the mandatory Zinsser rewrite pass (STYLE §7). Authority
   markers (`[MS-Learn: …]` / `[verify: …]`) are left for VERIFY.
   → Gate: **`GATE-LOCK-PLAN`** before drafting against a stage's PLAN.

2. **VERIFY** — check each draft against `STYLE.md` and against Microsoft Learn (the AI-eng grounding):
   voice/unity, the authority markers resolve, claims hold. Output is a verdict, not a rewrite.

3. **BUILD/TEST** — `mdbook build` the book; run each exercise's `smoke.py` + `pytest` from its real
   path (M8 reuses the **real** M7 fleet via `fleet_adapter.py`). Green is the bar.

4. **SHIP** — fold verified lessons into the book's `src/` and exercises into `exercises/`; write the
   ship record. → Gate: **`GATE-APPROVE-SHIP`** before folding content in. Publishing a public copy
   is the separate **`GATE-PUBLISH`**.

## Stage handoff convention

Each stage reads the previous stage's output and writes its own. For a book being built, the
working ledgers live under `build-log/<book>/<stage>/` (`PLAN.md` + `output/{author,verify,ship}/`).
The next stage picks up edits to those outputs.

## Load / don't-load

- **Load:** the stage you're in, the book, its `ingredients`, `platform/conventions`,
  `platform/templates`.
- **Do NOT load:** other stages' internals you aren't running, the `vault` raw ore, other books.

## Gates

`GATE-LOCK-PLAN` (lock a stage PLAN) · `GATE-APPROVE-SHIP` (approve a SHIP) · `GATE-NAME-BOOK`
(name a new book) · `GATE-PUBLISH` (public copy). All defined in `platform/HUMAN-GATES.md`.
