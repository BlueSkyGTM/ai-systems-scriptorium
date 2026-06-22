# Exercises

Every lesson has one exercise. Lessons are read in the book (mdBook); exercises are **built in Claude
Code**, in VS Code, with this repo open. The per-lesson **Copy for Claude Code** button hands the
context across.

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

- **Goal** -- one sentence: what you build.
- **Why** -- one line: the seam reason (matches the lesson's seam line).
- **Steps** -- the ordered tasks. Imperative. Claude Code executes these with you.
- **Done When** -- the acceptance check. Concrete and verifiable (a test passes, a metric prints,
  an exit code is 0). No "looks good."
- **Stretch** (optional) -- one harder variant.

## How the Handoff Works

The lesson's `claude-handoff` block carries `data-exercise="exercises/moduleN/<lesson-slug>/"`. The
copy button packages the lesson title, the lesson file path, the exercise path, and the task into one
payload. Paste it into Claude Code; it reads the brief and starts (or resumes) the build. Progress
lives in git and the exercise folder, so the next session picks up where this one stopped.

## The Module 1 Throughline Artifact

Module 1 builds `HARDWARE.md`: the documented record of the machine you build, started with the
bill of materials and grown across the module with the prices you paid, the stress-test result, and
the first-boot identity of the rig. Alongside it you build `check_hardware.py`, a validator that
asserts the record is complete and free of placeholder text. This is the first artifact in the
repository that becomes your portfolio; later modules add to the same repo (the model stack, the
routing layer, the Claude Code wiring).

The coaching contract in `exercises/CLAUDE.md` instructs the coaching agent to find `HARDWARE.md`
and read its current state before adding to it. You are continuing a build, not starting one.

## Hardware Output Is Representative

This book is written against a reference build. Where an exercise shows a command's output
(`nvidia-smi`, a stress-test summary, a tokens-per-second figure), treat it as the result to expect,
not a value to copy. Your numbers come from your machine; the validator checks that you recorded real
ones, not that they match the page.
