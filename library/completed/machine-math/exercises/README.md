# Exercises

Every lesson has one exercise. Lessons are read in the book (mdBook); exercises are **built in
Claude Code**, in VS Code, with this repo open. The per-lesson **Build It in Claude Code** button
hands the context across.

## Layout

```
exercises/
├── ml/                    <- the throughline package; grows with every module
│   ├── __init__.py
│   ├── distances.py       <- M1 lesson 1
│   ├── knn.py             <- M1 lesson 2
│   └── ...                <- later modules add metrics.py, features.py, etc.
└── moduleN/
    └── <lesson-slug>/
        ├── README.md      <- the brief (what to build, done-when)
        └── test_*.py      <- the acceptance gate
```

One folder per lesson, slug-matched to `src/moduleN/<lesson-slug>.md`.

## Brief Format (`exercises/moduleN/<lesson-slug>/README.md`)

Short, second person, active. Sections:

- **Goal** -- one sentence: what you build.
- **Why** -- one line: the seam reason (matches the lesson's seam line).
- **The Shared Artifact** -- where the new file lives in `exercises/ml/`; what to read before
  touching it.
- **Steps** -- the ordered tasks, imperative, with the locked code embedded. Claude Code executes
  these with you.
- **Done When** -- the acceptance check. Concrete and verifiable: a pytest run exits 0. No "looks
  good."
- **Stretch** -- one harder variant.

## How the Handoff Works

The lesson's `claude-handoff` block carries `data-exercise="exercises/moduleN/<lesson-slug>/"`.
The copy button packages the lesson title, the lesson file path, the exercise path, and the task
into one payload. Paste it into Claude Code; it reads the brief and starts (or resumes) the build.
Progress lives in git and the exercise folder, so the next session picks up where this one stopped.

## The Module 1 Throughline Artifact

Module 1 builds the foundation of `exercises/ml/`, an importable NumPy package that every later
algorithm in the book reuses.

**Lesson 1 (Feature Vectors)** contributes `ml/distances.py`: three distance metrics
(`euclidean`, `manhattan`, `cosine_distance`) and two scalers (`minmax_scale`, `zscore`), plus
the `METRICS` dispatch dict that lets an algorithm accept a metric by string name.

**Lesson 2 (k-NN Voting)** contributes `ml/knn.py`: a `KNNClassifier` that imports `METRICS`
from `ml.distances` and implements measure-rank-vote in 20 lines. No distance logic is copied;
the import is the reuse.

The coaching contract in `exercises/CLAUDE.md` instructs the coaching agent to find the `ml/`
package, read its current state, and add to it without rebuilding what is already there. You are
continuing a build, not starting one.

## Compounding (Later Modules)

Later modules add to `exercises/ml/` one file at a time: `metrics.py` (evaluation metrics),
`features.py` (feature engineering transforms), and others as the curriculum builds. The Module 7
capstone imports the full package off disk. Every exercise must leave `exercises/ml/` in a state
the next lesson can import and extend.
