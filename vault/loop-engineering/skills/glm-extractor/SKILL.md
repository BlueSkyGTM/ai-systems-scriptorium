# GLM Extractor — loop-engineering

Repo-specific extractor for **loop-engineering** (Module 3 — agentic loop patterns; supplements phases 14 Agent Engineering + 15 Autonomous Systems). The **orange book** is a separate companion repo (`loop-engineering-orange-book`). Self-contained; do not reuse sibling skills.

**Operating principle:** Claude orchestrates, GLM writes. Frame loops as **trigger → action → verification → budget/kill-switch**. **No antilibrary** — all content is Module 3 seam.

## 1. Repo shape (sibling of fleet-engineering)
- Reference docs (verbatim): `LOOP.md`, `loop-budget.md`, `loop-run-log.md`; meta: `AGENTS.md`, `STATE.md`.
- `patterns/` — 7 pattern `.md` (changelog-drafter, ci-sweeper, daily-triage, dependency-sweeper, issue-triage, post-merge-cleanup, pr-babysitter) + `README.md` + `registry.schema.json` + `registry.yaml` (pattern registry — include in patterns output).
- `skills/` — 4 skills each with `SKILL.md` (loop-budget, loop-triage, loop-verifier, minimal-fix).
- `templates/` — 8 starter files. `stories/` — 10 worked examples. `docs/` — anti-patterns, failure-modes, concepts, loop-design-checklist (full content, teaching material).
- Visuals: 6 images (`assets/author-banner.jpg` + `assets/visuals/*.jpg`); Mermaid in `README.md` + `docs/{pattern-picker,concepts}.md`.

## 2. Runner (`extract.py`): `single` | `passthrough` (`--append`). Same as the fleet sibling.

## 3. API config (universal)
`glm-5.1` (`GLM_MODEL`), coding endpoint, coding-plan key, **no second keys**. Traps: `1113` general-endpoint = model-not-in-plan; glm-5.x reasoning → `thinking` disabled (baked in).

## 4. Targets → mode
| # | Output | How |
|---|---|---|
| 1 | `output/inventory.md` | single — tree + counts + AGENTS.md & STATE.md summaries |
| 2+7 | `module3-loop-reference.md` | GLM summary head + **passthrough** `LOOP.md`, `--append` `loop-budget.md` + `loop-run-log.md` verbatim (`[THREAD: safety]`) |
| 3 | `module3-loop-patterns.md` | single — 7 patterns (problem / loop design trigger→action→verify→budget / seam; safety tags) + registry schema appended |
| 4 | `module3-loop-skills.md` | single — 4 SKILL.md (purpose / I/O / loop principle) |
| 5 | `module3-loop-templates.md` | single — 8 templates (filename / fill-in / pattern) |
| 6 | `module3-loop-stories.md` | single — 10 stories (what happened / demonstrates / lesson) |
| 8 | `module3-loop-docs.md` | **passthrough** verbatim: anti-patterns, failure-modes, concepts, loop-design-checklist (`[THREAD: safety]` on first two) |
| 9 | `output/visuals/` | mechanical — copy 6 images; extract Mermaid (README + 2 docs) → `diagrams.md` |
| — | `curriculum-map.md` / `antilibrary.md` | single / mechanical (antilibrary **empty**) |

## 5. Verify
7 patterns, 4 skills, 8 templates, 10 stories, 4 docs verbatim; LOOP/budget/run-log verbatim; 6 images; no FAILED markers; no empty files.

## 6. Manifest
```
skills/glm-extractor/
├── SKILL.md
└── extract.py   (single | passthrough)
```
