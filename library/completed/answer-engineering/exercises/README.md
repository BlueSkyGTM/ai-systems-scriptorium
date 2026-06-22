# Exercises

Every lesson has one exercise. Lessons are read in the book (mdBook); exercises are **built in Claude Code**,
in VS Code, with this repo open. The per-lesson **Copy for Claude Code** button hands the context across.

## Layout

```
exercises/
└── moduleN/
    └── <lesson-slug>/
        ├── README.md      <- the brief (what to build, done-when)
        └── <starter files, if any>
```

One folder per lesson, slug-matched to `src/moduleN/<lesson-slug>.md`.

## Brief Format (`exercises/moduleN/<lesson-slug>/README.md`)

Keep it to the Style Contract: short, second person, active. Sections:

- **Goal** -- one sentence: what you produce.
- **Why** -- one line: the seam reason (matches the lesson's seam line).
- **Steps** -- the ordered tasks. Imperative. Claude Code coaches you through these.
- **Done When** -- the acceptance check. Concrete and verifiable (the validator exits 0). No "looks good."
- **Stretch** (optional) -- one harder variant.

## How the Handoff Works

The lesson's `claude-handoff` block carries `data-exercise="exercises/moduleN/<lesson-slug>/"`. The copy
button packages the lesson title, the lesson file path, the exercise path, and the task into one payload.
Paste it into Claude Code; it reads the brief and starts (or resumes) the work. Progress lives in git
and the exercise folder, so the next session picks up where this one stopped.

## The Throughline Artifact: Your Prep Dossier

This book's portfolio artifact is not code; it is your **prep dossier** -- the career analogue of a
project repo. Module 1 seeds it with two logs and a validator:

- `prep/decomposition-log.md` -- ten interview questions decomposed (literal parse, signal category,
  one-sentence hypothesis) plus a calibration section.
- `prep/answers-log.md` -- five full Algorithm runs (decompose, identify, construct, stress-test) with
  each answer self-scored on specificity, structure, and completeness.
- `prep/check_prep.py` -- the validator that gates the dossier: it asserts both logs exist and are
  complete, and exits 0 only when they are. This is the done-when for the Module 1 exercises.

The coaching contract in `exercises/CLAUDE.md` instructs the agent to find the prep dossier and read its
current state before adding to it. You are continuing a build, not starting one.

## Compounding (later modules)

The dossier grows: Module 3 adds the behavioral example bank, Module 5 the systems-design logs, Module 6
the portfolio-narrative document, Module 7 the deliberate-practice scorecards. `check_prep.py` extends to
gate each. The capstone composes the whole dossier and grades it against a rubric in code. The reuse is
real, not restated.
