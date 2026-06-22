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
- **Done When** -- the acceptance check. Concrete and verifiable (a test passes, a query returns the
  seeded outlier, an exit code is 0). No "looks good."
- **Stretch** (optional) -- one harder variant.

## How the Handoff Works

The lesson's `claude-handoff` block carries `data-exercise="exercises/moduleN/<lesson-slug>/"`. The
copy button packages the lesson title, the lesson file path, the exercise path, and the task into one
payload. Paste it into Claude Code; it reads the brief and starts (or resumes) the build. Progress
lives in git and the exercise folder, so the next session picks up where this one stopped.

## The Module 1 Throughline Artifact

Module 1 builds `module1-sql/`: a local telemetry store (three tables that mirror what a production
AI system emits) plus the query library that answers production questions against it, gated by a
deterministic `smoke.py` and a `pytest` suite. The store and its queries grow lesson by lesson, from
the foundational `GROUP BY` queries through window functions, diagnostic CTEs, and the lineage walk.
This is the first artifact in the repository that becomes your portfolio; later modules extend the
same store (a warehouse target and dbt models, orchestration, lineage).

The coaching contract in `exercises/CLAUDE.md` instructs the coaching agent to find `module1-sql/`
and read its current state before adding to it. You are continuing a build, not starting one.

## The Telemetry Data Is Synthetic

The store is seeded with synthetic-but-realistic telemetry so the whole module runs offline, with no
cloud calls: `sqlite3` (standard library) holds the data, `duckdb` (one pip install) runs the
analytic queries. The seed plants known outliers (one slow route, one expensive tenant, one stale
source) so every query has a verifiable answer the smoke gate can assert.
