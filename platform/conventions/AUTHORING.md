# Authoring Contract

The curriculum the authoring agent follows. This is the Build phase: turn each distilled ingredient into a
finished mdBook lesson **and** its Claude Code exercise, in the locked voice, at the locked difficulty, with
nothing left to chance.

**Read this file first, then `STANDARDS.md`, then `STYLE.md`, before writing a single lesson.** AUTHORING is
the process; `STANDARDS.md` is the difficulty-and-strength bar; `STYLE.md` is the voice. All three are
book-agnostic.

## What you're turning into what

| Input | Output |
|-------|--------|
| `ingredients/source/moduleN/*.md` (distilled source — substance + resolutions) | finished lesson(s): `src/moduleN/<lesson-slug>.md` |
| `ingredients/dossiers/moduleN.md` (the keep/cut/merge/thread ruling) | — (read-only; tells you what belongs and why) |
| Microsoft Learn (via connector) | validated production pattern woven into the lesson |
| `platform/templates/concept-lesson.md` / `build-lesson.md` | the skeleton each lesson fills |
| your seam framing | the "why a Production AI Engineer needs this" in every lead |

## The three sources (rule 10 — non-negotiable)

No lesson is authored from one source. Every lesson combines:

1. **Distilled ingredient** — the raw material, in `ingredients/`. Two layers: the dossier ruling in
   `ingredients/dossiers/moduleN.md` (what belongs and why) **and** the full extraction detail in
   `ingredients/source/moduleN/*.md` (every kept lesson, with its tools/examples/time estimates).
   Read the dossier first for what belongs; reach into `ingredients/source/` for the depth.
2. **Microsoft Learn** — the production pattern / validation. **Use the connector. Do not assume from
   memory.** Confirm the architecture maps to current practice (LLMOps inner/outer loop, eval-driven
   development, the complexity ladder, prompt versioning).
3. **Editorial seam framing** — sequence, what belongs together, and the answer to "why does a Production AI
   Engineer need this?" baked into the lead.

If you have only one source, you are not authoring — you are copying. Stop and get the other two.

## How To — author one lesson

1. **Orient.** Read `STYLE.md`. Read the target `ingredients/source/moduleN/*.md` and its
   `ingredients/dossiers/moduleN.md` ruling. Note the threads tagged for this material (eval, versioning,
   safety, complexity ladder).
2. **Split into lessons.** One idea per lesson (STYLE §3). A chapter ingredient may become 1–5 lessons.
3. **Pick the skeleton.** Concept (understand) or Build (ship code). Copy from `platform/templates/`.
4. **Pull the three sources.** Substance from `ingredients/source/`; pattern from Microsoft Learn
   (connector); seam framing from you.
5. **Draft** against the skeleton. Author in the threaded language at point-of-use — TypeScript from Module
   3, Rust from Module 5 (per the language-tracks ruling in the dossiers). Surface the relevant thread inline where it belongs.
6. **Run the Zinsser pass** (STYLE §6): cut 15–25%, kill qualifiers/passive/jargon, verify unity, confirm
   lead and ending. Read it aloud.
7. **Write the lesson** to `src/moduleN/<lesson-slug>.md`. Add its entry to `src/SUMMARY.md` in prereq order.
8. **Write the exercise.** Create `exercises/moduleN/<lesson-slug>/README.md` (see `exercises/README.md` for
   the brief format). Point the lesson's `claude-handoff` block at it.
9. **Verify.** `mdbook build` passes (no broken links). The lesson conforms to the skeleton and STYLE.

**Done when:** every lesson in the module has a file + a SUMMARY entry + a `## Core concepts` block (1–4
testable propositions, STYLE §5 — the spaced-repetition cards) + an exercise brief, and `mdbook build` is
clean.

## Order

Author module by module, in the book's `SUMMARY` order (the eight-module shape; the reference book runs
**M1 → M8**). Earlier modules are prerequisites for later ones; the threads (a second language, eval,
safety, the data layer) only make sense in sequence. The difficulty ramp is governed by `STANDARDS.md`
Part 1: no forward dependencies, one idea per lesson, difficulty earned from a real problem.

## Non-negotiables

- **The voice is law.** `STYLE.md` wins every disagreement. The locked voice example is the book's own
  `src/preface.md` + `src/README.md`; Sans Python's are the reference exemplar until a book locks its own.
- **The bar is law.** Every lesson clears `STANDARDS.md`: the per-lesson difficulty self-check (Part 1) and,
  for build lessons, the strong-project rubric (Part 2). The conductor reviews against it at the gate.
- **Three sources, always** (rule 10). Microsoft Learn via the connector, not memory.
- **Don't reproduce, link.** Do not rebuild the source repo's from-scratch lessons (for the reference book,
  `ai-engineering-from-scratch`'s 500+); link them as reference. The spine is business-application artifacts.
- **Out-of-scope stays cut.** Material outside the seam is left out, not authored into a lesson — routed to a
  focused companion book if it deserves one. If a lesson pulls toward it, you've drifted off the seam.
- **Ship the artifact contract** (`STANDARDS.md` Part 3). Every book has a named compounding throughline
  (later artifacts reuse earlier ones; the capstone composes, it does not rebuild) and an
  `exercises/CLAUDE.md` coaching contract (read the lesson, find the throughline artifact and read its
  current state, then coach without solving). A book missing either does not graduate to ship.
- **Compounding holds.** Author the artifacts so the reuse is real, not restated. In the reference book:
  M6 agents are reused in M7 teams; M7's team builds the M8 system.

## Execution model — Opus orchestrates Sonnet

The build runs as a supervisor/worker fleet — the same pattern the curriculum teaches (M4/M7). Roles:

- **Opus = editor-in-chief (orchestrator).** Holds `STYLE.md` and the locked voice. Plans the module, assigns
  lessons, and — non-negotiable — runs the **Zinsser pass + STYLE review on every draft before it lands.**
  The voice is enforced at *review*, not just at draft. Opus is the judgment layer; it does not delegate taste.
- **Sonnet = the drafters (workers).** Each authors one lesson (or one chapter's lessons) from the three
  sources against the matching skeleton. Fast and cheap for the bulk drafting. Every worker gets `STYLE.md`
  **and** the canonical example (`src/preface.md` + `src/README.md`) in its context.

Rules that keep the fleet from drifting:

1. **One module at a time, in order (M1→M8).** Later modules depend on earlier voice + threads being locked.
2. **Review gate is mandatory.** No worker draft ships unreviewed. Opus edits it to the contract or sends it
   back.
3. **Exemplars compound.** Once a module's first lessons are approved, feed them to later workers as voice
   anchors — the book teaches itself its own style.
4. **Code does the mechanical, never the prose.** Scripts may scaffold lesson files, generate slugs, update
   `SUMMARY.md`, create `exercises/` folders, run `mdbook build`, and lint for STYLE violations (qualifiers,
   passive voice, "in order to"). Scripts may **not** generate lesson prose — that automates away the
   judgment the Style Contract exists to protect.

## When the repo ships

This file, `STYLE.md`, `platform/templates/`, and `ingredients/dossiers/` are the **workshop** — they guide
authoring and stay in the build repo. The shipped course is `book.toml` + `src/` + `exercises/` + `theme/`. (If you lift this
out as a standalone Claude Code repo, rename this file to `CLAUDE.md` so the agent reads it on entry.)
