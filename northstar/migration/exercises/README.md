# Exercises

Every lesson has one exercise. Lessons are read in the book (mdBook); exercises are **built in Claude Code**,
in VS Code, with this repo open. The per-lesson **Copy for Claude Code** button hands the context across.

## Layout

```
exercises/
└── moduleN/
    └── <lesson-slug>/
        ├── README.md      ← the brief (what to build, done-when)
        └── <starter files, if any>
```

One folder per lesson, slug-matched to `src/moduleN/<lesson-slug>.md`.

## Brief format (`exercises/moduleN/<lesson-slug>/README.md`)

Keep it to the Style Contract — short, second person, active. Sections:

- **Goal** — one sentence: what you build.
- **Why** — one line: the seam reason (matches the lesson's seam line).
- **Steps** — the ordered tasks. Imperative. Claude Code executes these with you.
- **Done when** — the acceptance check. Concrete and verifiable (a test passes, an endpoint responds, a
  metric prints). No "looks good."
- **Stretch** (optional) — one harder variant.

## How the handoff works

The lesson's `claude-handoff` block carries `data-exercise="exercises/moduleN/<lesson-slug>/"`. The copy
button packages the lesson title, the lesson file path, the exercise path, and the task into one payload.
Paste it into Claude Code; it reads the brief and starts (or resumes) the build. Progress lives in git + the
exercise folder, so the next session picks up where this one stopped.

## Compounding (M6–M8)

Artifact exercises reuse each other: a Module 6 single agent becomes a node in a Module 7 team, and the
Module 7 team builds the Module 8 system. Structure the exercise folders so later artifacts import earlier
ones — the reuse must be real, not restated.
