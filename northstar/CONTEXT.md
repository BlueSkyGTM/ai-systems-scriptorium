# Northstar — Context

<!-- Cowork only. Birds-eye view of the Sans Python course build. -->

> **⚠️ ARCHIVAL — superseded.** This doc describes an earlier generation: **LearnHouse** delivery and a
> per-repo `output/`-folder extraction workflow. Both are superseded. Delivery pivoted to **mdBook**; the live
> build is the **`migration/`** layer (`AUTHORING.md` = the build contract, `_dossier/` = the lesson audit,
> `src/` = lessons in progress). Extraction is complete (`migration/synthesis/source/`). State-of-record:
> `SPEC.md` (thesis) + `SYLLABUS.md` (structure). Kept as history, including the 2026-06-17/18 autoplan
> reports below.

## What This Is

Northstar is the master spec for Sans Python. It holds the thesis, all source material,
and the delivery platform. Everything here splinters into smaller specs that Claude Code
executes independently. Cowork maintains this view. Claude Code never sees the whole thing.

## Thesis

See `SPEC.md`. Locked. Return to it when anything drifts.

## Folder Map

```
specs/northstar/
├── CONTEXT.md         ← this file
├── SPEC.md            ← thesis, locked
├── sub-repos/         ← source material (7 repos, files dropped directly in each folder)
└── repo/              ← delivery platform + destination repo
    ├── CONTEXT.md     ← repo-level overview
    └── sans-python/   ← LearnHouse fork (the platform we ship on)
        └── CONTEXT.md ← platform inventory + feature selection log
```

## Pre-Build Checklist (resolve before handing any subfolder to Claude Code)

Flagged by /autoplan on 2026-06-17. None are session blockers — all must be resolved before Build phase begins.

1. ✓ **SYLLABUS.md How To section** — added 2026-06-17. Two handoffs: lesson-level audit + lesson authoring.
2. ✓ **Module completion criteria** — deferred. Student is Ray. Portfolio artifacts per module are sufficient exit signal.
3. ✓ **Prerequisite map** — deferred. LearnHouse handles IDE, playground, in-browser execution. No external prerequisites required.
4. ✓ **Cut logic structured format** — handled by `output/curriculum-map.md` in each sub-repo extraction.
5. ✓ **Phases 07, 12, 18 resolved** — verdicts in SYLLABUS.md. 07 + 12 → antilibrary. 18 → distributed per Gap 4.

✓ **JD audit complete** — AI Platform Engineer confirmed as discipline. Seam framing validated. Logged in SPEC.md.

---

## Source Material — Sub-Repos

Files are dropped directly in each sub-repo folder (no codebase/ subfolder).
Each sub-repo will get its own CONTEXT.md when it's ready for extraction.

| Sub-Repo | Role | Status |
|----------|------|--------|
| `ai-engineering-from-scratch` | Primary course material. 2884 files. Lesson scripts, phases, projects, outputs. | CONTEXT.md written. Ready for extraction. |
| `ai-system-design-guide` | AI systems design layer. 18 chapters: RAG, agents, MCP/A2A, evals, MLOps, security, case studies, 116 interview questions. The systems thinking backbone that ties the stack together. | CONTEXT.md written. Ready for extraction. |
| `made-with-ml` | ML course material. Notebooks, training, serving, deploy scripts. | CONTEXT.md written. Ready for extraction. |
| `ai-performance-engineering` | O'Reilly book. Inference serving subset in curriculum (cost/token, vLLM, hardware planning). Training/CUDA in antilibrary. | CONTEXT.md written. Ready for extraction. |
| `100-exercises-to-learn-rust` | Rust curriculum. Book format, exercises, helpers. | CONTEXT.md written. Ready for extraction. |
| `typescript-projects` | TypeScript project collection. 519 files. | CONTEXT.md written. Ready for extraction. |
| `loop-engineering` | Agentic loop patterns, templates, skills, stories. | CONTEXT.md written. Ready for extraction. |
| `fleet-engineering` | Fleet/multi-agent patterns, schemas, tools. | CONTEXT.md written. Ready for extraction. |
| `loop-engineering-orange-book` | PDF guide. Loop Engineering complete reference. | CONTEXT.md written. PDF structure extraction pending. |

## Delivery Platform — repo/sans-python/

LearnHouse fork. Self-hosted, Docker-containerized. Block-based editor, 30+ language
in-browser code execution, MCP-powered AI help, collaborative whiteboards, certificates,
user groups, assignment tracking. Full inventory in `repo/sans-python/CONTEXT.md`.

**Feature selection is not done.** Claude Code must not configure or extend the platform
until feature decisions are recorded in `repo/sans-python/CONTEXT.md`.

## Extraction Workflow

1. Add CONTEXT.md to a sub-repo folder (Cowork writes it)
2. Claude Code is pointed at the sub-repo — reads CONTEXT.md, extracts what matters
3. Deliverables land in an `output/` folder inside the sub-repo
4. Cowork reviews output, decides what carries forward into curriculum specs
5. Repeat for each sub-repo

## Open Questions

- Which sub-repos contribute curriculum content vs. just patterns/reference?
- Do LearnHouse's native block types replace the lesson-generation scripts from ai-engineering-from-scratch and made-with-ml?
- What does the MCP help layer in LearnHouse index? (our lesson content? external docs?)
- Which languages get in-browser execution playgrounds in the Sans Python course?
- Does the loop-engineering-orange-book get included as a reading resource?

## Current Focus

Pre-build checklist complete (2026-06-17). All 5 items resolved. Ready for extraction.

**Extraction order (revised):** ai-engineering-from-scratch first — has content-creating assets (lesson scripts, scaffold tooling) that need to be inventoried before curriculum build begins. Then made-with-ml (same reason — notebooks and deploy scripts). Cross-reference both against main repo (sans-python LearnHouse fork) to see what generation tooling can be adapted. ai-system-design-guide after those two.

## Skill Triggers

| Trigger | Skill |
|---------|-------|
| Session end, significant decisions made | `memory-manager` |
| Context getting long | `context-compressor` |
| Before handing any subfolder to Claude Code | `/autoplan` |

---

## GSTACK REVIEW REPORT

**Spec under review:** Northstar extraction strategy (SYLLABUS.md + CONTEXT.md)
**Review date:** 2026-06-17
**Lens:** Best way to get content from each sub-repo — CONTEXT.md structure, crawlable output
**Codex:** Unavailable (Cowork). Claude subagent only. Tables marked [Claude-only].

---

### Phase 0 — Scope

- UI scope: NO — Phase 2 (Design) skipped
- DX scope: YES — Phase 3.5 runs (Claude Code is the primary executor for all CONTEXT.md files)
- Mode: SELECTIVE EXPANSION — extraction schema is missing and must be designed now

---

### Phase 1 — CEO Review

**Premise audit [Claude-only]:**

| Premise | Status | Note |
|---------|--------|------|
| Resequencing thesis | VALID | Structurally validated by ai-system-design-guide |
| AI Systems Engineering discipline name | VALID | Confirmed against real architecture docs |
| Extraction-first workflow | VALID | Can't audit what you haven't seen |
| CONTEXT.md-as-handoff model | FLAG | Schema doesn't exist — Claude Code has nothing executable |
| 9 repos contain sufficient material | ASSUMED | Not verified end-to-end; binding gaps helped but didn't close this |

**Alternatives considered:**

A) Free-form CONTEXT.md per repo — fast, low overhead. Inconsistent across 9 repos; ad-hoc review.
B) Schema-driven CONTEXT.md — one schema, applied to all 9. Consistent output, crawlable by default, deterministic task for Claude Code. **Recommended.**
C) Extraction-first, CONTEXT.md-second — chicken-and-egg: Claude Code needs the CONTEXT.md to know what to do.

**Error registry:**

| # | Failure | Trigger | Fix |
|---|---------|---------|-----|
| 1 | Wrong material extracted | No extraction target spec | Schema with explicit targets |
| 2 | Uncrawlable output | No output format defined | Standard output/ folder schema |
| 3 | Audit on broken curriculum | Gap 5 unresolved | Resolve Gap 5 before extraction |
| 4 | 9 incompatible output formats | No schema | Schema-driven CONTEXT.md |

**Binding gap resolution timing:**

| Gap | Resolve when |
|-----|-------------|
| Gap 1 (eval thread) | During extraction — add eval thread notes to CONTEXT.md |
| Gap 2 (complexity ladder) | During extraction — task Claude Code to surface M2→M3 bridge material |
| Gap 3 (versioning thread) | During extraction — add versioning callout to relevant CONTEXT.md files |
| Gap 4 (safety delivery) | During extraction — per-module safety extraction task per CONTEXT.md |
| Gap 5 (data layer) | **BEFORE extraction** — affects Module 1 structure; needs a decision first |

---

### Phase 3 — Eng Review

**Extraction pipeline architecture:**

```
┌──────────────────────┐      ┌──────────────────────┐      ┌────────────────────┐
│  sub-repo CONTEXT.md │ ──▶  │  Claude Code         │ ──▶  │  output/           │
│  (schema-driven)     │      │  (extraction agent)  │      │  (crawlable)       │
└──────────────────────┘      └──────────────────────┘      └────────────────────┘
                                                                       │
                                                                       ▼
                                                             ┌────────────────────┐
                                                             │  Cowork Review     │
                                                             │  (Ray + agent)     │
                                                             └────────────────────┘
```

**Scope challenge:**
- Root CONTEXT.md extraction workflow (steps 1-4) is too abstract to execute. "Claude Code reads CONTEXT.md, extracts what matters" is a description, not a task.
- Minimum change set: (1) define CONTEXT.md schema, (2) write 9 CONTEXT.md files, (3) define output format.
- Pre-Build Checklist item 4 (structured cut logic) is solved by curriculum-map.md output file.
- Pre-Build Checklist item 5 (phases 07, 12, 18): still open — must be resolved before ai-engineering-from-scratch extraction.

**Proposed CONTEXT.MD schema for each sub-repo (D1: approved, schema-driven):**

```markdown
# [Repo Name] — Extraction Context

## Role in Curriculum
[1-2 sentences: which modules this repo feeds]

## Curriculum Mapping
| Module | Section | Source Material (path or pattern) |
|--------|---------|-----------------------------------|
| Module X | [section name] | [files/folders] |

## Extraction Targets
[Ordered. Claude Code works through these in sequence.]

### Target 1: [name]
- **Source:** [path or glob]
- **What:** [what to extract — scripts, schemas, README sections, etc.]
- **Output:** `output/content/[filename].md`
- **Format:** [how to structure the extracted content]
- **If missing:** Log the missing path in output/inventory.md and continue

### Target N: Visuals
- **Source:** Any image files (*.png, *.svg, *.jpg, *.gif) + embedded Mermaid diagrams in *.md files
- **What:** Collect all architecture diagrams, system diagrams, flowcharts
- **Output:** `output/visuals/` for images; `output/visuals/diagrams.md` for embedded diagrams (header + diagram + surrounding context)
- **If missing:** Log "no visuals found" in output/inventory.md and continue

## Repo Notes
[Gotchas: file encoding, directory quirks, what to skip]

## Done Checklist
- [ ] `output/inventory.md` — full list of extractable material found
- [ ] `output/curriculum-map.md` — lesson-to-module mapping table
- [ ] `output/content/` — one .md per extracted lesson/section
- [ ] `output/antilibrary.md` — material found but not in curriculum (can be empty)
- [ ] `output/visuals/` — collected diagrams and images (can be empty if none found)
```

**Output folder structure (crawlable across all 9 repos):**

```
sub-repos/[repo-name]/
└── output/
    ├── inventory.md         ← what exists in this repo
    ├── curriculum-map.md    ← lessons to modules mapping
    ├── antilibrary.md       ← material found but not in curriculum
    └── content/
        ├── [lesson-slug].md
        └── ...
```

---

### Phase 3.5 — DX Review (Claude Code as developer)

**Product type:** Agent handoff document (CONTEXT.md files are a Claude Code skill, not human docs)

**Developer persona:** Claude Code agent. Zero ambiguity tolerance. No error recovery unless CONTEXT.md specifies one.

**Current DX score:** 0/10. No CONTEXT.md files exist for 7/9 repos. No schema. Claude Code has nothing to execute.

**Journey trace:**

| Stage | What Claude Code Encounters | Status |
|-------|---------------------------|--------|
| Discover | "Each sub-repo will get its own CONTEXT.md when ready" | BLOCKED |
| Start | No CONTEXT.md in any of 7 pending repos | BLOCKED |
| Extract | No extraction targets defined | BLOCKED |
| Output | No output format defined | BLOCKED |
| Done | No done signal defined | BLOCKED |
| Error | No fallback if file doesn't exist | MISSING |

**DX score after schema:** 8/10. Gap to 10: error path ("If missing" field in each Extraction Target handles this).

---

### Decision Audit Trail [Claude-only]

| # | Decision | Outcome | Reason |
|---|----------|---------|--------|
| A1 | Schema-driven vs. free-form CONTEXT.md | SURFACE TO RAY | Architecture call |
| A2 | Output format (markdown vs. JSONL) | AUTO: markdown | Simpler, consistent with existing spec format |
| A3 | Phase 2 (Design) scope | AUTO: skip | No UI surface |
| A4 | Phase 3.5 (DX) scope | AUTO: include | Claude Code is the primary executor |
| A5 | Binding gaps 1-4 timing | AUTO: during extraction | Framing problems — solvable via CONTEXT.md notes |
| A6 | Gap 5 timing | SURFACE TO RAY | Affects Module 1 structure — needs decision first |

---

### Runs / Status / Findings

| Phase | Status | Key Finding |
|-------|--------|-------------|
| Phase 0 | DONE | UI=no, DX=yes, mode=SELECTIVE EXPANSION |
| Phase 1 (CEO) | DONE | Extraction schema is the missing architecture; Approach B recommended |
| Phase 2 (Design) | SKIPPED | No UI scope |
| Phase 3 (Eng) | DONE | Schema designed; output structure defined; Pre-Build item 4 addressed |
| Phase 3.5 (DX) | DONE | Current DX score 0/10; 8/10 after schema; error path handled in schema |

**VERDICT: DONE_WITH_CONCERNS** — Schema complete. Two decisions require Ray before work proceeds.

**UNRESOLVED DECISIONS:**
- D1: Schema-driven vs. free-form CONTEXT.md (architecture call)
- D2: Gap 5 data layer decision (blocks Module 1 structure; must resolve before extraction)

---

## GSTACK REVIEW REPORT — Extraction Outputs

**Spec under review:** All 9 sub-repo extraction outputs vs. SYLLABUS.md curriculum structure
**Review date:** 2026-06-18
**Lens:** Are extractions sufficient to begin Build phase (Handoff 1: lesson-level audit)?
**Codex:** Unavailable (Cowork). Claude subagent only. Tables marked [Claude-only].

---

### Phase 0 — Scope

- UI scope: NO — Phase 2 (Design) skipped
- DX scope: YES — Claude Code is the executor for both Build handoffs
- Mode: SELECTIVE EXPANSION — extraction quality passes; handoff architecture is the gap

---

### Phase 1 — CEO Review [Claude-only]

**Premise audit:**

| Premise | Status | Note |
|---------|--------|------|
| 9 extractions contain sufficient curriculum content | VERIFIED | Coverage maps cleanly to all 5 modules |
| Extraction = audit layer, not file copies | VALID | All outputs are markdown summaries; source stays in sub-repos |
| 3-source synthesis will be enforced during Build | FLAG | REFERENCE-LAYER.md exists but is not referenced in any sub-repo CONTEXT.md or the SYLLABUS.md How To. Claude Code won't consult it unless explicitly pointed there. |
| Module 3 density is appropriate for AI Platform Engineering | FLAG | 89 lessons from phases 14/15/16 + 11 files from loop/fleet + 5 from ai-system-design-guide = 105+ Module 3 inputs. This is a volume risk, not a content risk. Audit will trim — but the audit itself becomes harder when the surface area is this large. |
| SYLLABUS.md How To is sufficient for headless Claude Code execution | FLAG | How To is a readable description. It lacks: lesson-audit.md schema, explicit "read REFERENCE-LAYER.md first" instruction, error handling, and per-repo done signal. |

**Coverage map [Claude-only]:**

| Module | Primary source | Secondary sources | Raw lesson count | Status |
|--------|---------------|------------------|-----------------|--------|
| Module 1 | ai-engineering-from-scratch (ph00, ph05 subset) | 100-exercises-to-learn-rust, typescript-projects | 12 + 19 + 8 topics + 15 topics | SOLID |
| Module 2 | ai-engineering-from-scratch (ph08, ph11) | ai-system-design-guide (prompting, RAG, evals) | 15 + 17 + 3 files | SOLID |
| Module 3 | ai-engineering-from-scratch (ph13, ph14, ph15, ph16) | loop-engineering, fleet-engineering, ai-system-design-guide (agentic, memory, frameworks, patterns, tool-use) | 23+42+22+25 + 11 files + 5 files | DENSE — audit required |
| Module 4 | ai-engineering-from-scratch (ph17) | ai-performance-engineering, made-with-ml, ai-system-design-guide (deploy, case studies) | 28 + 3 + 3 + 2 files | SOLID |
| Module 5 | ai-engineering-from-scratch (ph19) | none | 85 items | KITCHEN SINK — needs editorial decision |

**Error registry:**

| # | Failure mode | Trigger | Fix |
|---|-------------|---------|-----|
| 1 | Claude Code builds lessons without Microsoft Learn thread | No explicit "read REFERENCE-LAYER.md" in Handoff 1 CONTEXT.md | Embed REFERENCE-LAYER.md as required input in build/CONTEXT.md |
| 2 | Module 5 audit produces 85 lesson files | No pre-selection of real capstone projects | Cowork decides: 10-15 capstone projects before handoff |
| 3 | lesson-audit.md format inconsistent across 9 repos | No schema defined | Define lesson-audit.md schema in build/CONTEXT.md |
| 4 | Orange book structure-only extraction causes confusion | Audit tries to pull lesson content from it | Explicit instruction: orange book = reference guide, not lesson source |
| 5 | Handoff 2 cannot execute | LearnHouse block format spec does not exist | Flag: must exist before Handoff 2. Not a Handoff 1 blocker. |

**Ahab routing confirmed:** ai-system-design-guide interview prep correctly routed to `output/content/ahab-interview-prep.md`. Ahab spec (`specs/ahab/`) needs to receive this output. Not a Northstar blocker.

**Dream state delta:**
- Current: 9 clean output/ folders, coverage verified, phase verdicts locked
- After Handoff 1: lesson-audit.md per repo, every content file has keep/cut/restructure verdict with reason
- After Handoff 2: lesson .md files per module in LearnHouse block format, ready to import
- 12-month ideal: complete Sans Python course live on LearnHouse

---

**PHASE 1 COMPLETE.** Codex: [unavailable]. Claude: 5 flags, 0 blockers, 2 taste decisions.
Premise gate: extractions are sufficient. **Handoff 1 is not yet ready to execute — build/CONTEXT.md is missing.**

---

### Phase 3 — Eng Review [Claude-only]

**Build phase architecture:**

```
┌─────────────────────────┐     ┌──────────────────────┐     ┌────────────────────────┐
│  build/CONTEXT.md       │ ──▶ │  Claude Code         │ ──▶ │  output/lesson-audit.md│
│  (Handoff 1 program)    │     │  (audit agent)       │     │  per sub-repo          │
│  + SYLLABUS.md          │     │                      │     │                        │
│  + REFERENCE-LAYER.md   │     │                      │     │                        │
└─────────────────────────┘     └──────────────────────┘     └────────────────────────┘
                                                                         │
                                                                         ▼
                                                             ┌────────────────────────┐
                                                             │  Cowork Review         │
                                                             │  Build Handoff 2 spec  │
                                                             └────────────────────────┘
```

**Gap: build/CONTEXT.md does not exist.**

SYLLABUS.md How To describes Handoff 1 in 6 steps. Claude Code is a headless AI — it needs a program, not a description. Minimum viable build/CONTEXT.md:

```markdown
# Northstar — Build Phase (Handoff 1: Lesson-Level Audit)

## Purpose
Audit every extraction output against SYLLABUS.md seam framing. Produce a lesson-audit.md
per sub-repo. Do not author lessons. Do not move files. Audit only.

## Required inputs (read these first, in order)
1. SYLLABUS.md — seam framing, module structure, phase verdicts
2. REFERENCE-LAYER.md — orchestration patterns, Microsoft Learn thread
3. specs/northstar/sub-repos/[repo]/output/curriculum-map.md — per repo

## Audit targets (9 repos, process in order)
[one section per repo, explicit path to output/content/ files]

## lesson-audit.md schema (same format across all repos)
| Lesson slug | Keep / Cut / Restructure | Reason (one line, seam-aligned) |

## Module 5 capstone instruction
Phase 19 has 85 items. Select 10-15 that best demonstrate AI Platform Engineering
system-level work. Cut the rest to antilibrary. Prioritize: production deployment,
observability, multi-agent coordination, inference optimization.

## Done checklist (per sub-repo)
- [ ] curriculum-map.md read
- [ ] Every content file in output/content/ audited
- [ ] lesson-audit.md written to output/lesson-audit.md
- [ ] Orange book noted as reference only — no lesson-audit.md required
```

**DX score delta:**

| Dimension | Current (SYLLABUS.md How To only) | After build/CONTEXT.md |
|-----------|----------------------------------|------------------------|
| Start signal | Implicit ("run Handoff 1") | Explicit CONTEXT.md entry point |
| Required inputs | Not enumerated | Listed in order |
| Output schema | Not defined | lesson-audit.md 3-column table |
| Done signal | "when every phase has lesson-audit.md" | Per-repo checklist |
| Error handling | None | "If missing: log and continue" |
| DX score | 5/10 | 9/10 |

**Existing scripts from ai-engineering-from-scratch:** `audit_lessons.py`, `build_catalog.py`, `scaffold-lesson.sh`, `scaffold_workbench.py`. These are BUILD tools, not audit tools — they apply to Handoff 2 (lesson authoring), not Handoff 1. Note them in build/CONTEXT.md as "available for Handoff 2."

---

**PHASE 3 COMPLETE.** Gap is clear: build/CONTEXT.md is missing. Writing it is the unblocking move.

---

### Phase 3.5 — DX Review (Claude Code as developer) [Claude-only]

**Journey trace — current state:**

| Stage | What Claude Code encounters | Status |
|-------|---------------------------|--------|
| Discover | SYLLABUS.md How To, Section "Handoff 1" | FOUND but implicit |
| Start | No build/CONTEXT.md, no entry-point task | MISSING |
| Read inputs | SYLLABUS.md says "9 output/ folders" — no paths listed | UNDERSPECIFIED |
| Consult REFERENCE-LAYER.md | Not mentioned in How To | MISSING |
| Audit Module 5 | 85 items, no triage instruction | AMBIGUOUS |
| Output format | lesson-audit.md format not defined | MISSING |
| Done signal | "every curriculum phase has lesson-audit.md" — which is 9 repos or 5 modules? | AMBIGUOUS |

**DX score: 5/10.** Claude Code could fumble this.

**After build/CONTEXT.md:** 9/10. Residual gap: Handoff 2 (LearnHouse block format spec doesn't exist — not a Handoff 1 blocker, but must exist before Handoff 2 begins).

---

### Decision Audit Trail [Claude-only]

| # | Decision | Auto-decide | Outcome | Reason |
|---|----------|-------------|---------|--------|
| A1 | Are extractions sufficient to proceed? | YES | PROCEED | Coverage maps cleanly; all phase verdicts locked; no blockers |
| A2 | Build/CONTEXT.md — write before handoff? | YES | WRITE IT | Headless principle (P5). Description ≠ program. |
| A3 | lesson-audit.md schema — define in Cowork? | YES | DEFINE IT | Prevents format drift across 9 repos (P4 — DRY) |
| A4 | Orange book — include in audit? | AUTO: NO | REFERENCE ONLY | Structure-only extraction; no lesson content to audit |
| A5 | Phase 2 (Design) scope | AUTO: SKIP | NO UI | No interface scope |
| A6 | Ahab routing | AUTO: NOTE | CONFIRMED | Not a Northstar blocker |

**Taste decisions — surface to Ray:**

- **T1 — Module 5 capstone scope:** Pre-select 10-15 capstone projects in Cowork before handoff, OR let Claude Code audit all 85 and make the selection? Recommendation: **Cowork pre-selects.** 85 items is too many for a headless agent to triage without editorial context Ray holds.
- **T2 — Module 3 pre-triage:** 105+ Module 3 inputs across all sources. Pre-trim in Cowork (identify the 30-40 core lessons before handoff) OR let audit do it? Recommendation: **Let audit do it.** SYLLABUS.md phase verdicts already give seam framing. Volume here is a feature — audit produces the right trim.
- **T3 — lesson-audit.md granularity:** 3-column table (slug | verdict | reason) OR richer format (includes REFERENCE-LAYER.md mapping, estimated lesson length, seam alignment score)? Recommendation: **3-column table.** Simpler output is faster to review; REFERENCE-LAYER.md mapping happens in Handoff 2.

---

### Runs / Status / Findings

| Phase | Status | Key Finding |
|-------|--------|-------------|
| Phase 0 | DONE | DX=yes, UI=no, mode=SELECTIVE EXPANSION |
| Phase 1 (CEO) | DONE | Extractions sufficient. 5 flags: REFERENCE-LAYER.md not wired, Module 5 scope, lesson-audit.md schema missing, orange book instruction, Handoff 2 blocker (Learnhouse spec). |
| Phase 2 (Design) | SKIPPED | No UI scope |
| Phase 3 (Eng) | DONE | build/CONTEXT.md is the gap. DX 5→9/10 after it's written. |
| Phase 3.5 (DX) | DONE | 5 missing/ambiguous stages in Claude Code journey. All resolved by build/CONTEXT.md. |

**VERDICT: DONE_WITH_CONCERNS**

**Recommendation: Write `specs/northstar/build/CONTEXT.md` before any Build phase handoff.**

This is the only unblocking move. Once it exists and T1/T2/T3 are resolved, Handoff 1 is ready.

**UNRESOLVED (taste — require Ray):**
- T1: Module 5 capstone — Cowork pre-selects 10-15 vs. Claude Code audits all 85
- T2: Module 3 triage — pre-trim vs. let audit handle it (recommendation: let audit)
- T3: lesson-audit.md granularity — 3-column vs. richer format (recommendation: 3-column)
