# loop-engineering — Extraction Context

<!-- Claude Code: read this file, then work through Extraction Targets in order. -->

## Role in Curriculum

Agentic loop patterns for Module 3. Supplements phases 14 (Agent Engineering) and 15 (Autonomous Systems) from ai-engineering-from-scratch. Loop engineering covers: how to design agent loops that are safe, budgeted, and verifiable. Patterns, skills, templates, and stories are the primary curriculum material. The orange book (a separate repo) is the companion guide.

## Curriculum Mapping

| Module | Section | Source (path) |
|--------|---------|----------------|
| Module 3 | Agent Engineering | `patterns/`, `skills/`, `templates/`, `LOOP.md` |
| Module 3 | Autonomous Systems | `stories/`, `docs/`, `examples/` |
| Module 3 | Safety / kill switches | `loop-budget.md`, `skills/loop-budget/`, `patterns/` |

## Extraction Targets

Work through these in order.

### Target 1: Repo inventory
- **Source:** Root directory + first-level listing of `patterns/`, `skills/`, `templates/`, `stories/`, `examples/`, `docs/`, `tools/`, `starters/`
- **What:** List all files and directories at one level deep. Note file counts.
- **Output:** `output/inventory.md`
- **Format:** Directory tree with file counts and one-line purpose per section.
- **If missing:** Log and stop — required first step

### Target 2: LOOP.md — primary reference
- **Source:** `LOOP.md`
- **What:** Extract full content. This is the core conceptual document.
- **Output:** `output/content/module3-loop-reference.md`
- **Format:** Full content as-is, with a 3–5 sentence summary at the top.
- **If missing:** Log in inventory.md and continue

### Target 3: Patterns
- **Source:** `patterns/*.md` (all pattern files)
- **What:** Extract each pattern. From the directory: changelog-drafter.md, ci-sweeper.md, daily-triage.md, dependency-sweeper.md, issue-triage.md, post-merge-cleanup.md, pr-babysitter.md, plus README.md.
- **Output:** `output/content/module3-loop-patterns.md`
- **Format:** One section per pattern: pattern name, problem it solves, loop design (trigger → action → verification → budget), seam relevance. Tag patterns that demonstrate kill switches / budget guards with `[THREAD: safety]`.
- **If missing:** Log in inventory.md and continue

### Target 4: Skills
- **Source:** `skills/loop-budget/`, `skills/loop-triage/`, `skills/loop-verifier/`, `skills/minimal-fix/`
- **What:** For each skill: extract the SKILL.md file. Summarize the skill's purpose, inputs, outputs, and how it demonstrates a loop engineering concept.
- **Output:** `output/content/module3-loop-skills.md`
- **Format:** One section per skill: skill name, purpose, input/output, what loop principle it demonstrates.
- **If missing:** Log in inventory.md and continue

### Target 5: Templates
- **Source:** `templates/`
- **What:** Extract all template files. These are the starting points students use when building their own loops.
- **Output:** `output/content/module3-loop-templates.md`
- **Format:** One section per template: filename, purpose, what the student fills in, what loop pattern it implements.
- **If missing:** Log in inventory.md and continue

### Target 6: Stories (worked examples)
- **Source:** `stories/*.md`
- **What:** Extract all stories. Stories are narrative accounts of real loop runs — they show patterns succeeding and failing in practice.
- **Output:** `output/content/module3-loop-stories.md`
- **Format:** One section per story: title, what happened, what it demonstrates, what the student learns from it.
- **If missing:** Log in inventory.md and continue

### Target 7: Budget and run log docs
- **Source:** `loop-budget.md`, `loop-run-log.md`
- **What:** Extract both files. Loop budget is the kill switch / cost guard concept. Run log is how loops track execution.
- **Output:** Append to `output/content/module3-loop-reference.md` as additional sections.
- **Format:** Full content with a 2-sentence summary at the top of each section. Tag with `[THREAD: safety]`.
- **If missing:** Log in inventory.md and continue

### Target 8: docs/ anti-patterns and concepts
- **Source:** `docs/anti-patterns.md`, `docs/failure-modes.md`, `docs/concepts.md`, `docs/loop-design-checklist.md`
- **What:** Extract all four files. Anti-patterns and failure modes are high-value teaching material.
- **Output:** `output/content/module3-loop-docs.md`
- **Format:** One section per file, full content. Anti-patterns and failure modes tagged with `[THREAD: safety]`.
- **If missing:** Log missing files in inventory.md and continue

### Target 9: Visuals
- **Source:** `assets/` + any `*.png`, `*.svg`, `*.jpg` + Mermaid diagrams in `*.md` files
- **What:** Collect all diagrams. 6 images total — collect all of them.
- **Output:** `output/visuals/` for images; `output/visuals/diagrams.md` for Mermaid diagrams
- **If missing:** Log "no visuals found" in inventory.md and continue

## Repo Notes

- **AGENTS.md and STATE.md:** Read both and include summaries in inventory.md — these describe the repo's own agent setup and may contain meta-information useful for understanding the overall structure.
- **registry.yaml in patterns/:** Contains the pattern registry schema. Extract and include in the patterns output — students will reference this when building their own pattern registries.
- **starters/:** Likely starter templates for new loop projects. Extract and note in inventory.
- **loop-budget concept:** This is the kill switch for runaway agent loops. It's both a pattern and a skill — extract it as `[THREAD: safety]` material for Module 3's safety content.
- **No antilibrary:** All content is seam-relevant. Loop engineering patterns are Module 3 core.

## Done Checklist

_All targets complete and verified 2026-06-18. Generation by glm-5.1 (thinking disabled) via repo-local `skills/glm-extractor/` (single | passthrough). Reference + teaching docs preserved verbatim. Zero failed/empty outputs._

- [x] `output/inventory.md` — structure + counts + AGENTS.md & STATE.md summaries
- [x] `output/curriculum-map.md` — content → Module 3 (Agent Engineering / Autonomous Systems) mapping
- [x] `output/content/module3-loop-reference.md` — GLM summary + LOOP.md + loop-budget.md + loop-run-log.md verbatim (`[THREAD: safety]`)
- [x] `output/content/module3-loop-patterns.md` — 7 patterns (trigger→action→verify→budget; safety-tagged) + pattern registry
- [x] `output/content/module3-loop-skills.md` — 4 skills (purpose / I/O / loop principle)
- [x] `output/content/module3-loop-templates.md` — 8 templates (fill-in / pattern implemented)
- [x] `output/content/module3-loop-stories.md` — 10 worked-example stories
- [x] `output/content/module3-loop-docs.md` — anti-patterns + failure-modes + concepts + loop-design-checklist verbatim (safety-tagged)
- [x] `output/antilibrary.md` — noted empty (all content is Module 3 seam)
- [x] `output/visuals/` — 6 images copied + 3 Mermaid diagrams
