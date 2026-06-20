# GLM Extractor — fleet-engineering

Repo-specific extractor for **fleet-engineering** (Module 3 — multi-agent / fleet governance; supplements phase 16 Multi-Agent & Swarms). Self-contained; do not reuse sibling skills.

**Operating principle:** Claude orchestrates, GLM writes. Frame everything as **governance-as-a-technical-skill**: registries, identity, kill switches, budget guards, HITL. **No antilibrary** — all content is Module 3 seam.

## 1. Repo shape
Small, dense. Reference docs verbatim + categories GLM-summarized:
- `FLEET.md`, `fleet-budget.md`, `FLEET-STATE.md`, `AGENTS.md` — short root reference docs.
- `patterns/` — 6 pattern `.md` (agent-clone-fork, cross-agent-audit, fleet-budget-guard, hierarchical-delegation, shared-inbox-hitl, team-agent-registry) + `README.md` + `registry.yaml` (the *pattern* registry — distinct from `agents/registry.yaml`).
- `schemas/` — `agent-manifest.schema.json`, `agent-registry.schema.json`.
- `agents/registry.yaml` — the live fleet registry.
- `stories/` — 5 incident stories. `templates/` — 8 starter files (YAML/JSON/runbooks).
- Visuals: 2 images (`assets/cobus-greyling.jpg`, `assets/visuals/fleet-engineering-header.jpg`); Mermaid in `README.md` + `docs/{pattern-picker,primitives,concepts,stack}.md`.

## 2. Runner (`extract.py`)
- `single` — GLM doc from a blob (patterns, stories, templates, schemas, inventory, map, summaries).
- `passthrough` — verbatim concat under `## <path>` headers; `--append` to add sections to an existing file (FLEET.md/budget/state/registry "full content as-is").

## 3. API config (universal)
`glm-5.1` (`GLM_MODEL`), coding endpoint, coding-plan key, **no second keys**. Traps: `1113` on general endpoint = model-not-in-plan; glm-5.x reasoning → `thinking` disabled (baked in). `1302` = RPM (single-mode here won't hit it).

## 4. Targets → mode
| # | Output | How |
|---|---|---|
| 1 | `output/inventory.md` | single — dir tree + counts + one-line purpose + AGENTS.md summary |
| 2+8 | `module3-fleet-reference.md` | GLM summary head + **passthrough** `FLEET.md`, then `--append` `fleet-budget.md` + `FLEET-STATE.md` verbatim (`[THREAD: safety]`) |
| 3 | `module3-fleet-patterns.md` | single — 6 patterns: name / problem / fleet design / seam; `[THREAD: safety]` on governance+kill-switch+HITL |
| 4+7 | `module3-fleet-schemas.md` | single — 2 schemas (purpose + field table + raw JSON + what student implements) + `--append` live `agents/registry.yaml` annotated |
| 5 | `module3-fleet-stories.md` | single — 5 stories: what happened / pattern shown / lesson; `[THREAD: safety]` |
| 6 | `module3-fleet-templates.md` | single — 8 templates: filename / purpose / pattern implemented |
| 9 | `output/visuals/` | mechanical — copy 2 images; extract Mermaid (README + 4 docs) → `diagrams.md` |
| — | `output/curriculum-map.md` | single — content → Module 3 mapping |
| — | `output/antilibrary.md` | mechanical — **expected empty**, note it |

## 5. Verify
6 pattern sections, 5 stories, 8 templates, 2 schemas + registry; FLEET/budget/state verbatim present; 2 images copied; no FAILED markers; no empty files. Mark checklist with verified counts.

## 6. Manifest
```
skills/glm-extractor/
├── SKILL.md
└── extract.py   (single | passthrough)
```
