# CONTEXT — Sans Python — AI Platform Engineering (COMPLETED)

The first book, shipped: 8 modules, every lesson in the `STYLE.md` voice, with runnable M6/M7/M8
portfolio artifacts. `mdbook build library/completed/sans-python` passes.

What's here:
- `src/` — the lessons (mdBook source; `book.toml` `src = "src"`). `SUMMARY.md` is the spine.
- `exercises/` — the Claude Code exercises + the runnable artifacts (each module's `smoke.py` /
  `pytest`). M8 reuses the **real** M7 fleet via `exercises/module8/fleet_adapter.py`.
- `theme/` — the mdBook theme overrides (copy-to-Claude button).
- `book.toml` — mdBook config.
- The build records for this book live OUTSIDE it, in `build-log/sans-python/` (PLANs + verdicts).

## Second-level intent sub-router

Pick your intent. Each has a **distinct** load-list. Do not load across rows.

<!-- route-table -->
| I want to… | Load | Do NOT load | Handoff | Gate |
|---|---|---|---|---|
| **author** (add/expand a lesson) | `library/completed/sans-python/src`, `platform/conventions`, `platform/pipeline`, `ingredients` | `build-log`, `vault`, other books | `platform/pipeline/CONTEXT.md` AUTHOR | `GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP` |
| **fix-a-lesson** (patch a shipped lesson) | the lesson under `library/completed/sans-python/src`, its exercise under `library/completed/sans-python/exercises`, and the verify verdict in `build-log/sans-python` | `platform/pipeline`, `ingredients`, `vault` | none — fix, re-run the artifact gate, report | none (autonomous) |
| **publish** (build/move a public copy) | `library/completed/sans-python/book`, `library/completed/sans-python/theme`, `platform/pipeline` | `ingredients`, `vault`, `build-log` | `platform/pipeline/CONTEXT.md` SHIP | `GATE-PUBLISH` |
| **status** (what's the state of this book) | `CATALOG.md`, `BACKLOG.md` | everything else | — | none (autonomous) |

## Why fix-a-lesson is split out

A shipped-lesson fix needs **two** places and only two: the lesson/exercise in this book, and its
**verify verdict** in `build-log/sans-python/<mN>/output/verify/` (to see what was checked and not
regress it). It must **not** load the pipeline internals — you are not re-authoring a stage, you are
patching prose or an artifact and re-running that artifact's gate.

## Hard rules (local — they NARROW, never broaden)

- `STYLE.md` is law (Tier 1). No template endings; vary rhythm (STYLE §8).
- Don't touch the 8 artifact gates except the documented `fleet_adapter.py` docstring.
- Never load any path containing `skills/` or `gstack/`.

## Build / verify commands

```
mdbook build library/completed/sans-python
python platform/bin/route-lint
```
