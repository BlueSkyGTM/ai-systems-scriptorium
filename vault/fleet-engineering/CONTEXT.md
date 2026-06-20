# fleet-engineering — Extraction Context

<!-- Claude Code: read this file, then work through Extraction Targets in order. -->

## Role in Curriculum

Fleet-level and multi-agent patterns for Module 3. Supplements phase 16 (Multi-Agent and Swarms) from ai-engineering-from-scratch. Fleet engineering covers: when you go from one agent to 3+ loops or 5+ agents — registry patterns, identity, governance, kill switches, budget guards. This is where governance becomes a technical skill.

## Curriculum Mapping

| Module | Section | Source (path) |
|--------|---------|----------------|
| Module 3 | Multi-Agent and Swarms | `patterns/`, `schemas/`, `FLEET.md`, `templates/` |
| Module 3 | Safety / governance | `patterns/fleet-budget-guard.md`, `patterns/cross-agent-audit.md`, `schemas/` |
| Module 3 | Fleet stories | `stories/` |

## Extraction Targets

Work through these in order.

### Target 1: Repo inventory
- **Source:** Root directory + first-level listing of `patterns/`, `schemas/`, `stories/`, `examples/`, `agents/`, `docs/`, `tools/`, `templates/`, `starters/`
- **What:** List all files and directories at one level deep with file counts.
- **Output:** `output/inventory.md`
- **Format:** Directory tree with file counts and one-line purpose per section.
- **If missing:** Log and stop — required first step

### Target 2: FLEET.md — primary reference
- **Source:** `FLEET.md`
- **What:** Extract full content. This is the core conceptual document for fleet engineering.
- **Output:** `output/content/module3-fleet-reference.md`
- **Format:** Full content as-is, with a 3–5 sentence summary at the top.
- **If missing:** Log in inventory.md and continue

### Target 3: Patterns
- **Source:** `patterns/*.md`
- **What:** Extract each pattern. From the directory: agent-clone-fork.md, cross-agent-audit.md, fleet-budget-guard.md, hierarchical-delegation.md, shared-inbox-hitl.md, team-agent-registry.md, plus README.md.
- **Output:** `output/content/module3-fleet-patterns.md`
- **Format:** One section per pattern: pattern name, problem it solves, fleet design (how agents coordinate, how governance is enforced), seam relevance. Tag governance/kill-switch patterns with `[THREAD: safety]`.
- **If missing:** Log in inventory.md and continue

### Target 4: Schemas
- **Source:** `schemas/agent-manifest.schema.json`, `schemas/agent-registry.schema.json`
- **What:** Extract both JSON schemas. These are the contracts for fleet-level agent identity and coordination.
- **Output:** `output/content/module3-fleet-schemas.md`
- **Format:** One section per schema: schema name, purpose, key fields (table: field | type | purpose), what the student implements using this schema.
- **If missing:** Log in inventory.md and continue

### Target 5: Stories
- **Source:** `stories/*.md`
- **What:** Extract all fleet stories. From the directory: budget-cap-saved-runaway.md, inbox-bypass-incident.md, langsmith-git-backup.md, registry-before-inbox.md, shadow-agents-audit.md.
- **Output:** `output/content/module3-fleet-stories.md`
- **Format:** One section per story: title, what happened, what fleet pattern it demonstrates, what the student learns. Tag safety/governance stories with `[THREAD: safety]`.
- **If missing:** Log in inventory.md and continue

### Target 6: Templates
- **Source:** `templates/`
- **What:** Extract all template files. These are starting points for building fleet infrastructure.
- **Output:** `output/content/module3-fleet-templates.md`
- **Format:** One section per template: filename, purpose, what fleet pattern it implements.
- **If missing:** Log in inventory.md and continue

### Target 7: agents/ registry
- **Source:** `agents/registry.yaml`
- **What:** Extract the agent registry YAML. This is the actual fleet registry — the data structure that holds agent manifests in production.
- **Output:** Append to `output/content/module3-fleet-schemas.md` as a "Live registry example" section.
- **Format:** Full YAML content with annotation: what each field means, what the student populates.
- **If missing:** Log in inventory.md and continue

### Target 8: Budget and FLEET-STATE.md
- **Source:** `fleet-budget.md`, `FLEET-STATE.md`
- **What:** Extract both. Fleet budget is the multi-agent cost guard. FLEET-STATE.md describes fleet state tracking.
- **Output:** Append to `output/content/module3-fleet-reference.md` as additional sections.
- **Format:** Full content with 2-sentence summary at the top of each. Tag with `[THREAD: safety]`.
- **If missing:** Log in inventory.md and continue

### Target 9: Visuals
- **Source:** `assets/` + any `*.png`, `*.svg`, `*.jpg` + Mermaid diagrams in `*.md` files
- **What:** Collect all diagrams. 2 images total — collect both.
- **Output:** `output/visuals/` for images; `output/visuals/diagrams.md` for Mermaid diagrams
- **If missing:** Log "no visuals found" in inventory.md and continue

## Repo Notes

- **AGENTS.md:** Read and include summary in inventory.md — describes the repo's own agent setup.
- **registry.yaml in patterns/:** The pattern registry (distinct from agents/registry.yaml). Extract and note the difference.
- **shared-inbox-hitl.md:** Human-in-the-loop pattern. High-value safety content — tag with `[THREAD: safety]`.
- **tests/:** Note the test structure. Fleet patterns that are tested are more trustworthy for curriculum use.
- **No antilibrary:** All fleet engineering content is Module 3 seam material.

## Done Checklist

_All targets complete and verified 2026-06-18. Generation by glm-5.1 (thinking disabled) via repo-local `skills/glm-extractor/` (single | passthrough). Reference docs + registry preserved verbatim. Zero failed/empty outputs._

- [x] `output/inventory.md` — structure + counts + AGENTS.md summary + pattern-vs-live registry note
- [x] `output/curriculum-map.md` — content → Module 3 (Multi-Agent & Swarms) mapping
- [x] `output/content/module3-fleet-reference.md` — GLM summary + FLEET.md + fleet-budget.md + FLEET-STATE.md verbatim (`[THREAD: safety]`)
- [x] `output/content/module3-fleet-patterns.md` — 6 patterns (problem/fleet design/seam; safety-tagged)
- [x] `output/content/module3-fleet-schemas.md` — 2 schemas (field tables + raw JSON) + live `agents/registry.yaml` annotated
- [x] `output/content/module3-fleet-stories.md` — 5 incident stories (safety-tagged)
- [x] `output/content/module3-fleet-templates.md` — 8 templates (purpose + pattern implemented)
- [x] `output/antilibrary.md` — noted empty (all content is Module 3 seam)
- [x] `output/visuals/` — 2 images copied + 5 Mermaid diagrams (`diagrams.md`)
