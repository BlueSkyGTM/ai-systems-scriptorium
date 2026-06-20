# CONTEXT — platform/ (THE BUILD ENGINE)

The AI-engineering-specialized engine that builds the books. AI-eng-specialized **on purpose** — it
grounds in Microsoft Learn + curated AI-eng ore; do not genericize it to other domains.

## What's here

- `platform/pipeline/` — the reusable AUTHOR→VERIFY→BUILD/TEST→SHIP stage pattern. Start here to
  author or ship.
- `platform/conventions/` — the writing law: `STYLE.md` (Zinsser-grade Style Contract, **Tier-1
  policy**) + `AUTHORING.md` (the curriculum the authoring agent follows).
- `platform/templates/` — the lesson skeletons (`concept-lesson.md`, `build-lesson.md`).
- `platform/HUMAN-GATES.md` — the single source of truth for human gates (referenced by ID).
- `platform/route-manifest.yaml` — the single source of truth for paths.
- `platform/bin/route-lint` — the executable "a cold agent can route this" check. Run it.
- `platform/route-fixtures/` — adversarial near-miss route fixtures (run by route-lint).

## Load / don't-load

- **Load when authoring:** `platform/pipeline`, `platform/conventions`, `platform/templates`, plus
  the book and its `ingredients`.
- **Do NOT load:** the `vault` raw ore (author against `ingredients`), shipped-book internals you
  aren't editing, anything under `skills/` or `gstack/`.

## Handoff & gates

Author/ship → `platform/pipeline/CONTEXT.md`. Gates (by ID, in `platform/HUMAN-GATES.md`):
`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`, `GATE-NAME-BOOK`, `GATE-PUBLISH`.
