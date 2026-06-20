# Synthesis — Extraction Context

**Model:** Opus (Cowork session — Microsoft Learn connector available live)
**Phase:** 2 (Distillation — between extraction and lesson authoring)
**What this is:** Take all 9 sub-repo extraction outputs and produce one unified, seam-filtered content base per module. This is editorial work, not authoring. No lessons are written here. No files are moved. Content is evaluated, classified, de-duplicated, and organized.

**Session architecture:** Your call. Use subagents as you see fit. Split across sessions or run in one — whatever produces the cleanest output. The targets below are logical units, not mandatory session boundaries.

---

## Role in Build Phase

This sub-repo receives the outputs of all 9 extractions and distills them into 5 module content files — one per course module. The output is the raw material for lesson authoring (Handoff 2). Nothing reaches Handoff 2 that has not passed through this synthesis.

**You are operating under an editorial mandate, not a mechanical one.** The criteria are in `COURSE-CRITERIA.md`. Read it before processing any content.

---

## Required Reading (in order, before any synthesis begins)

1. `specs/northstar/sub-repos/synthesis/COURSE-CRITERIA.md` — defines usable content, classification labels, gap severity
2. `specs/northstar/SYLLABUS.md` — module structure, phase verdicts, seam framing, How To
3. `specs/northstar/REFERENCE-LAYER.md` — Microsoft Learn orchestration patterns (the spine)
4. `specs/northstar/SPEC.md` — thesis, archetype framework, AI Platform Engineering definition

Do not begin any synthesis target until all four are read. The criteria are the frame; everything else is material.

**Microsoft Learn connector:** You have live access via `microsoft_docs_search` and `microsoft_docs_fetch`. Use it. When source content maps to a Microsoft Learn pattern, fetch the live doc and confirm the mapping. When you find a gap, search Microsoft Learn before declaring it CRITICAL — it may already exist there. REFERENCE-LAYER.md gives you the starting URLs; go beyond it where the content calls for it.

---

## Source Inputs

All content is pre-organized in this sub-repo. Do not reach back to the original sub-repos.

```
specs/northstar/sub-repos/synthesis/source/
├── module1/                          ← 5 files
│   ├── aefs-module1-setup-tooling.md
│   ├── aefs-module1-nlp-transformer-forward.md
│   ├── rust-module1-rust-book-structure.md
│   ├── rust-module1-rust-exercises-by-topic.md
│   └── ts-module1-typescript-topics.md
├── module2/                          ← 5 files
│   ├── aefs-module2-generative-ai.md
│   ├── aefs-module2-llm-engineering.md
│   ├── asdg-module2-eval-guides.md
│   ├── asdg-module2-prompting-context.md
│   └── asdg-module2-retrieval-systems.md
├── module3/                          ← 18 files
│   ├── aefs-module3-agent-engineering.md    [PRIMARY]
│   ├── aefs-module3-tools-protocols.md      [PRIMARY]
│   ├── asdg-module3-agentic-systems.md      [PRIMARY]
│   ├── asdg-module3-design-patterns.md      [PRIMARY]
│   ├── asdg-module3-frameworks-tools.md     [SUPPLEMENTARY]
│   ├── asdg-module3-memory-state.md         [SUPPLEMENTARY]
│   ├── asdg-module3-tool-use-computer-agents.md [SUPPLEMENTARY]
│   ├── loop-module3-loop-docs.md            [SUPPLEMENTARY]
│   ├── loop-module3-loop-patterns.md        [SUPPLEMENTARY]
│   ├── loop-module3-loop-reference.md       [SUPPLEMENTARY]
│   ├── loop-module3-loop-skills.md          [SUPPLEMENTARY]
│   ├── loop-module3-loop-stories.md         [SUPPLEMENTARY]
│   ├── loop-module3-loop-templates.md       [SUPPLEMENTARY]
│   ├── fleet-module3-fleet-patterns.md      [SUPPLEMENTARY]
│   ├── fleet-module3-fleet-reference.md     [SUPPLEMENTARY]
│   ├── fleet-module3-fleet-schemas.md       [SUPPLEMENTARY]
│   ├── fleet-module3-fleet-stories.md       [SUPPLEMENTARY]
│   └── fleet-module3-fleet-templates.md     [SUPPLEMENTARY]
├── module4/                          ← 9 files
│   ├── aefs-module4-infrastructure-production.md  [PRIMARY]
│   ├── aipe-module4-inference-serving-chapters.md [PRIMARY]
│   ├── aipe-module4-inference-reference-docs.md   [PRIMARY]
│   ├── aipe-module4-full-sweep-checklist.md       [PRIMARY]
│   ├── mwml-module4-madewithml-notebook-outline.md [PRIMARY]
│   ├── mwml-module4-deploy-scripts.md             [SUPPLEMENTARY]
│   ├── mwml-module4-madewithml-code-inventory.md  [SUPPLEMENTARY]
│   ├── asdg-module4-deploy-chapters.md            [SUPPLEMENTARY]
│   └── asdg-module4-case-studies.md               [SUPPLEMENTARY]
├── module5/                          ← 1 file
│   └── aefs-module5-capstone.md
└── reference/                        ← 2 files
    ├── obook-orange-book-structure.md   [reference only — not a lesson source]
    └── aefs-scripts-inventory.md        [Handoff 2 tooling — not a lesson source]
```

**Source key:**
- `aefs` = ai-engineering-from-scratch
- `asdg` = ai-system-design-guide
- `aipe` = ai-performance-engineering
- `mwml` = made-with-ml
- `rust` = 100-exercises-to-learn-rust
- `ts` = typescript-projects
- `loop` = loop-engineering
- `fleet` = fleet-engineering
- `obook` = loop-engineering-orange-book

**PRIMARY vs. SUPPLEMENTARY — guidance, not mandate:**
- PRIMARY files are the expected starting point for each module. Read them first.
- SUPPLEMENTARY files fill gaps and resolve de-duplication. If PRIMARY coverage is thin, pull from SUPPLEMENTARY. If your judgment says a SUPPLEMENTARY file has better content for the seam than the PRIMARY, use it. The labels are a starting point, not a ceiling.

---

## Synthesis Targets

Five passes, one per module, in sequence. **Do not begin the next target until the current one is complete and written to disk.**

---

### Target 1 — Module 1

**Purpose:** Rust foundation + TypeScript foundation + NLP transformer-forward subset + tooling setup

**Source content files (all in `source/module1/`):**
- `aefs-module1-setup-tooling.md`
- `aefs-module1-nlp-transformer-forward.md`
- `rust-module1-rust-book-structure.md`
- `rust-module1-rust-exercises-by-topic.md`
- `ts-module1-typescript-topics.md`

**Synthesis task:**
1. Apply all 6 COURSE-CRITERIA.md criteria to every content block
2. Classify each block: LESSON / EXERCISE / REFERENCE / CUT
3. De-duplicate: Rust and TypeScript repos have dedicated material — ai-engineering-from-scratch has overlap. Best version wins.
4. Flag any Module 1 gaps from SYLLABUS.md that no source covers
5. Note which content blocks map to REFERENCE-LAYER.md patterns (Module 1 maps to complexity ladder — Gap 2)

**Output:** `output/module1-synthesis.md`
**If missing content:** Log in `output/gaps.md` with severity (CRITICAL / HIGH / LOW)

---

### Target 2 — Module 2

**Purpose:** Foundation models as APIs, LLM engineering, prompt/context engineering, RAG, evals

**Source content files (all in `source/module2/`):**
- `aefs-module2-generative-ai.md`
- `aefs-module2-llm-engineering.md`
- `asdg-module2-prompting-context.md`
- `asdg-module2-retrieval-systems.md`
- `asdg-module2-eval-guides.md`

**Synthesis task:**
1. Apply all 6 criteria
2. Classify each block
3. De-duplicate: ai-engineering-from-scratch and ai-system-design-guide both cover RAG, prompting, and evals. Best version wins — ai-system-design-guide is more architecture-centric (preferred for AI Platform Engineering seam).
4. Flag gaps
5. Cross-reference REFERENCE-LAYER.md: Module 2 maps to prompt chaining and routing patterns

**Output:** `output/module2-synthesis.md`

---

### Target 3 — Module 3

**Purpose:** MCP/A2A protocols, agent engineering, orchestration patterns, multi-agent systems

**Source content files (`source/module3/` — PRIMARY first, then SUPPLEMENTARY):**

PRIMARY (read in full):
- `aefs-module3-tools-protocols.md`
- `aefs-module3-agent-engineering.md`
- `asdg-module3-agentic-systems.md`
- `asdg-module3-design-patterns.md`

SUPPLEMENTARY (read for de-duplication / gap-fill only):
- `asdg-module3-frameworks-tools.md`
- `asdg-module3-memory-state.md`
- `asdg-module3-tool-use-computer-agents.md`
- `loop-module3-loop-patterns.md`
- `loop-module3-loop-skills.md`
- `loop-module3-loop-templates.md`
- `loop-module3-loop-stories.md`
- `loop-module3-loop-docs.md`
- `loop-module3-loop-reference.md`
- `fleet-module3-fleet-patterns.md`
- `fleet-module3-fleet-schemas.md`
- `fleet-module3-fleet-templates.md`
- `fleet-module3-fleet-stories.md`
- `fleet-module3-fleet-reference.md`

REFERENCE ONLY (do not synthesize into lessons):
- `source/reference/obook-orange-book-structure.md`

**Synthesis task:**
1. Apply all 6 criteria — this module has the highest volume. Be strict.
2. Classify each block. REFERENCE-LAYER.md is especially important here — all 7 orchestration patterns map to Module 3.
3. De-duplicate aggressively: loop-engineering, fleet-engineering, ai-system-design-guide, and ai-engineering-from-scratch all cover agent patterns. Keep the most concrete, TypeScript/Rust-native version. Prefer REFERENCE-LAYER.md-aligned content.
4. Orange book: tag relevant sections as REFERENCE (not LESSON). It supplements teaching; it is not the source of lesson content.
5. Flag gaps — Module 3 is the seam's core; CRITICAL gaps here block the course.
6. Cross-reference all 7 REFERENCE-LAYER.md patterns. Every pattern must map to at least one LESSON candidate.

**Note on volume:** Phase 14 (42 lessons), phase 15 (22 lessons), phase 16 (25 lessons), plus supplementary content from 4 other sources. Many will be CUT or merged. This is expected. A dense Module 3 with 40 high-quality lessons beats a bloated Module 3 with 89 mediocre ones.

**Output:** `output/module3-synthesis.md`

---

### Target 4 — Module 4

**Purpose:** Inference serving, MLOps, infrastructure, production operations, finops

**Source content files (`source/module4/` — PRIMARY first, then SUPPLEMENTARY):**

PRIMARY (read in full):
- `aefs-module4-infrastructure-production.md`
- `aipe-module4-inference-serving-chapters.md`
- `aipe-module4-inference-reference-docs.md`
- `aipe-module4-full-sweep-checklist.md`
- `mwml-module4-madewithml-notebook-outline.md`

SUPPLEMENTARY (read for de-duplication / gap-fill only):
- `mwml-module4-deploy-scripts.md`
- `mwml-module4-madewithml-code-inventory.md`
- `asdg-module4-deploy-chapters.md`
- `asdg-module4-case-studies.md`

**Synthesis task:**
1. Apply all 6 criteria
2. Classify each block
3. De-duplicate: ai-engineering-from-scratch and ai-performance-engineering both cover inference serving. ai-performance-engineering is more technically precise (O'Reilly book level) — prefer it for inference serving concepts. made-with-ml provides the MLOps workflow spine.
4. made-with-ml training internals (train.py, tune.py, models.py) are ALREADY classified as antilibrary in the source extraction — do not reclassify as LESSON. They are REFERENCE at most.
5. Flag gaps — especially around cost management, FinOps, and SRE for AI (SYLLABUS.md has these; coverage may be thin).
6. Cross-reference REFERENCE-LAYER.md: Module 4 maps to orchestrator-workers and evaluator-optimizer patterns.

**Output:** `output/module4-synthesis.md`

---

### Target 5 — Module 5 Capstone

**Purpose:** Select 10–15 capstone projects from Phase 19's 85 items

**Source content file (`source/module5/`):**
- `aefs-module5-capstone.md`

**Synthesis task:**
1. Read all 85 Phase 19 items
2. Apply the Module 5 Capstone Selection Criteria from COURSE-CRITERIA.md (all 5 criteria must pass)
3. Select 10–15 projects maximum. Justify each selection (one line: which seam, which system-level skill, which portfolio signal).
4. Classify the remaining items as CUT with one-line reason each
5. Cross-reference REFERENCE-LAYER.md: capstone projects should exercise at least one orchestration pattern each
6. Identify if any CRITICAL gap from the synthesis report (from gaps.md) can be addressed by a capstone project design — flag this.

**Priority selection guidance from COURSE-CRITERIA.md:**
Prioritize: terminal-native-coding-agent, multi-agent-software-team, llm-observability-dashboard, speculative-decoding-server, github-issue-to-pr-agent, constitutional-safety-harness, mcp-server-with-registry.

**Output:** `output/module5-synthesis.md`

---

### Target 6 — Cross-Cutting Threads

**Purpose:** Resolve the four binding threads across all modules

**Run after Targets 1–5 are complete.**

**Threads to resolve:**

| Thread | What it tracks | How to resolve |
|--------|---------------|----------------|
| `[THREAD: eval]` | Evaluation frameworks, metrics, benchmarks | Find all LESSON/REFERENCE blocks tagged eval across all 5 synthesis files. Map each to its module. Confirm eval is present in M2 (RAGAS, DeepEval), M3 (agent evals), M4 (observability). |
| `[GAP 2: complexity ladder]` | Direct model call → single agent → multi-agent | Find the bridge content between M2 and M3. Confirm the transition is explicit in the synthesis. |
| `[THREAD: versioning]` | Dataset, prompt, model, checkpoint versioning | Confirm versioning appears in M2 (prompt caching), M3 (agent state), M4 (MLflow). |
| `[THREAD: safety]` | Guardrails, kill switches, HITL, red-teaming | Distributed across M2 (safety evals), M3 (loop budget, kill switches, HITL), M4 (chaos, compliance). Confirm all three receive safety content. |

**Output:** `output/cross-cutting.md`

---

### Target 7 — Gaps and Synthesis Report

**Purpose:** Document what was found, what was cut, and what the course still needs

**Run after all other targets complete.**

**What to produce:**

1. **Gaps** (`output/gaps.md`): Every SYLLABUS.md lesson with no usable source content. Severity: CRITICAL / HIGH / LOW. For each HIGH/CRITICAL gap: suggest a Microsoft Learn URL from REFERENCE-LAYER.md or flag for new content authoring.

2. **Synthesis report** (`output/synthesis-report.md`):
   - Total content blocks reviewed across all 9 source repos
   - Total classified as LESSON / EXERCISE / REFERENCE / CUT
   - Per-module lesson candidate count
   - De-duplication decisions (what was merged, what won)
   - Antilibrary summary (what was excluded and why)
   - Module 5 selection rationale (the 10–15 chosen and why)

---

## Repo Notes

- All source content is pre-organized in `source/`. Do not reach back to original sub-repos.
- `source/reference/obook-orange-book-structure.md` — structure-only PDF extraction. Reference only, never a lesson source.
- `source/reference/aefs-scripts-inventory.md` — build tooling inventory for Handoff 2. Not a lesson source.
- Ahab interview prep was routed to the Ahab project during extraction — it is not present here. Do not look for it.
- made-with-ml training internals (train.py, tune.py, models.py) are already excluded from the extracted content — do not reclassify anything as training-focused.
- The synthesis output is the input to Handoff 2 (lesson authoring). Write at lesson-authoring fidelity: enough structure that a future agent can write the lesson directly from it.
- HOLD is a valid 5th classification: use it when you are uncertain whether something passes the seam test and want Ray to decide.

---

## Output Block Format

Each synthesis file uses this block structure. Consistency here is what makes Handoff 2 (lesson authoring) executable without ambiguity.

```markdown
## [Section name from SYLLABUS.md]

### [lesson-slug]
**Classification:** LESSON | EXERCISE | REFERENCE | CUT | HOLD
**Source:** [prefix]-[filename] (e.g. aefs-module3-tools-protocols)
**REFERENCE-LAYER.md pattern:** [pattern name] | none
**Microsoft Learn:** [URL if fetched live] | not applicable
**Why:** [one line — seam alignment reason, or cut reason]

[synthesized content block — enough for an author to write the lesson without returning to source]
```

EXERCISE blocks attach to a parent LESSON:
```markdown
#### Exercise: [slug]
**Attach to:** [parent lesson slug]
**Type:** build | benchmark | observe
**Prompt:** [what the student is asked to do — 2-3 sentences]
```

HOLD blocks include a question for Ray:
```markdown
### [lesson-slug]
**Classification:** HOLD
**Source:** [prefix]-[filename]
**Question for Ray:** [one sentence — what judgment call is needed]
```

---

## Done Checklist

- [ ] `output/module1-synthesis.md` — Module 1 content classified and unified
- [ ] `output/module2-synthesis.md` — Module 2 content classified and unified
- [ ] `output/module3-synthesis.md` — Module 3 content classified and unified (aggressively trimmed)
- [ ] `output/module4-synthesis.md` — Module 4 content classified and unified
- [ ] `output/module5-synthesis.md` — 10–15 capstone projects selected with rationale
- [ ] `output/cross-cutting.md` — four binding threads resolved across all modules
- [ ] `output/gaps.md` — all SYLLABUS.md lessons with no source coverage, severity-rated
- [ ] `output/synthesis-report.md` — full accounting of what was included, cut, and why

**Done when:** All 8 output files exist and every SYLLABUS.md lesson has a classification (LESSON / EXERCISE / REFERENCE / CUT / GAP).

---

## GSTACK REVIEW REPORT

**Spec under review:** synthesis/CONTEXT.md + COURSE-CRITERIA.md
**Review date:** 2026-06-18
**Lens:** Is this CONTEXT.md ready to hand to Opus? Will it produce the unified content base the Build phase needs?
**Codex:** Unavailable (Cowork). Claude subagent only. [Claude-only].

---

### Phase 0 — Scope

- UI scope: NO — Phase 2 (Design) skipped
- DX scope: YES — Opus is the executor. DX = how clear is this CONTEXT.md as an Opus program.
- Mode: SELECTIVE EXPANSION — spec is structurally sound; session architecture is the gap.

---

### Phase 1 — CEO Review [Claude-only]

**Premise audit:**

| Premise | Status | Note |
|---------|--------|------|
| Editorial synthesis is needed between extraction and lesson authoring | VALID | 9 output/ folders → 280+ raw content items → without synthesis, lesson authoring is chaotic |
| Opus can make editorial judgment calls within the criteria | VALID | COURSE-CRITERIA.md is specific enough for Opus to classify without ambiguity |
| This is editorial work, not authoring — clear scope boundary | VALID | "No lessons written here" is explicit. Good. |
| 7 targets in one Opus session is feasible | FLAG | Module 3 alone has 7 source inputs, each potentially large. Sessions will hit context limits. |
| COURSE-CRITERIA.md gives Opus sufficient guidance | VALID | 6 criteria + 4 classification labels + gap severity + capstone selection criteria = complete editorial frame |

**Dream state delta:**

```
Now:    9 output/ folders, 280+ raw content items, no unified view
After:  5 module-synthesis.md files, cross-cutting threads resolved, gaps mapped
12-mo:  Complete Sans Python course live on LearnHouse
```

**Error registry:**

| # | Failure mode | Trigger | Fix |
|---|-------------|---------|-----|
| 1 | Opus hits context limit mid-Module 3 | 7 large source files + 4 required reading docs in one session | Split into 5+1 sessions; specify read budget per target |
| 2 | De-duplication produces wrong winner | "Best version wins" is a taste judgment without a tiebreaker | Priority order added to each target (primary vs. supplementary sources) |
| 3 | Module 3 synthesis is still bloated | No explicit cut target | Add: "Module 3 LESSON candidates: target 35–45 max" |
| 4 | Gaps.md identifies a CRITICAL gap after all 5 modules are done | No feedback loop back to source repos | Gap severity guide in COURSE-CRITERIA.md already handles this |
| 5 | Capstone selection diverges from editorial intent | "Best judgment" without enough grounding | Priority candidates already listed; add: "if uncertain, flag as HOLD for Ray" |

**PHASE 1 COMPLETE.** One flag: session architecture. Everything else is solid.

---

### Phase 3 — Eng Review [Claude-only]

**Session architecture issue:**

Current CONTEXT.md sends Opus through 7 sequential targets in one session. Projected context consumption:

| Target | Source files | Estimated size |
|--------|-------------|----------------|
| Required reading (4 docs) | COURSE-CRITERIA, SYLLABUS, REFERENCE-LAYER, SPEC | Large — SYLLABUS.md alone is substantial |
| Module 1 | 4 files | Moderate |
| Module 2 | 5 files | Moderate |
| Module 3 | 12+ files | Very large — 7 inputs, phases 14/15/16 are dense |
| Module 4 | 7 files | Large |
| Module 5 | 1 large file (85 items) | Large |
| Cross-cutting | Review all 5 outputs | Moderate |
| Gaps + report | Review all 5 outputs | Moderate |

Total: likely exceeds Opus context window before Target 5 completes.

**Fix:** Split into 5+1 bounded sessions.

```
Session 1 (Module 1):  Required reading → Target 1 → output/module1-synthesis.md
Session 2 (Module 2):  Required reading → Target 2 → output/module2-synthesis.md
Session 3 (Module 3):  Required reading → Target 3 → output/module3-synthesis.md  [longest]
Session 4 (Module 4):  Required reading → Target 4 → output/module4-synthesis.md
Session 5 (Module 5):  Required reading → Target 5 → output/module5-synthesis.md
Session 6 (Synthesis): Read all 5 outputs → Targets 6+7 → cross-cutting.md, gaps.md, synthesis-report.md
```

Each session starts with required reading (4 docs) then processes one module. Module 3 may need its own sub-split: Tools&Protocols first, then Agent Engineering (phases 14/15/16), then supplementary (loop/fleet/design-guide).

**Read budget per target — missing from current spec:**

The CONTEXT.md lists source files but doesn't tell Opus what to prioritize if content is too large. This creates ambiguity. Each target needs: PRIMARY sources (read in full) vs. SUPPLEMENTARY sources (read curriculum-map.md only; pull full content only if needed for de-duplication).

**Module 3 lesson target — missing:**

Current spec: "A dense Module 3 with 40 high-quality lessons beats a bloated Module 3 with 89." This is prose guidance, not a target. Opus needs a number. Recommendation: **Target 35–45 LESSON candidates.** 

**DX score delta:**

| Dimension | Current | After fix |
|-----------|---------|-----------|
| Session architecture | 7 targets, 1 session — context burn risk | 5+1 bounded sessions, each feasible |
| Read budget | Not specified | PRIMARY vs. SUPPLEMENTARY per target |
| Module 3 cut target | Prose ("around 40") | Explicit: 35–45 LESSON candidates |
| Module 5 uncertainty handling | "Flag for Ray" — not in CONTEXT.md | Add: "HOLD" as 5th classification for taste calls |
| DX score | 7/10 | 9/10 |

**PHASE 3 COMPLETE.** Three gaps: session split, read budget, Module 3 lesson target.

---

### Phase 3.5 — DX Review (Opus as developer) [Claude-only]

**Journey trace:**

| Stage | What Opus encounters | Status |
|-------|---------------------|--------|
| Discover | CONTEXT.md with role, inputs, 7 targets, done checklist | FOUND |
| Required reading | 4 docs listed with paths | CLEAR |
| Source inputs | All 9 repo paths listed | CLEAR |
| Target 1–5 processing | Source files listed, synthesis task described | MOSTLY CLEAR — read budget missing |
| De-duplication judgment | "Best version wins" + criteria | WORKABLE — criteria are specific |
| Module 3 | 12+ source files, density warning in notes | RISK — volume without a cap |
| Output format | File path per target specified, but synthesis-within-file format not described | FLAG |
| Done signal | 8 output files enumerated | CLEAR |
| Uncertainty | No explicit handling for "I'm not sure" cases | MISSING |

**One output format gap:** CONTEXT.md specifies WHERE each output file goes but not the INTERNAL FORMAT. For lesson authoring (Handoff 2) to consume these files cleanly, each synthesis.md should follow a consistent block structure. Minimum viable format:

```markdown
## [Section name from SYLLABUS.md]

### [Lesson candidate slug]
**Classification:** LESSON / EXERCISE / REFERENCE / CUT
**Source:** [repo] / [file]
**REFERENCE-LAYER.md pattern:** [pattern name or "none"]
**Why:** [one line — seam alignment reason]
**Content:** [the synthesized content block]
```

**DX score: 7/10 → 9/10** after adding session architecture, read budget, lesson target, and output block format.

---

### Decision Audit Trail [Claude-only]

| # | Decision | Auto-decide | Outcome | Reason |
|---|----------|-------------|---------|--------|
| A1 | 7 targets in one session vs. split | FLAG TO RAY | T1 — taste call | Context burn risk is real but Opus window may be larger than assumed |
| A2 | Read budget per target | AUTO: ADD | SUPPLEMENTARY label | Prevents context burn; minimal spec overhead |
| A3 | Module 3 lesson target | AUTO: 35–45 | ADD TO CONTEXT.md | Explicit cap needed; prose guidance insufficient for headless execution |
| A4 | 5th classification label (HOLD) | AUTO: ADD | ADD TO COURSE-CRITERIA.md | Prevents capstone/borderline content from being silently cut |
| A5 | Output block format | AUTO: ADD | ADD TO CONTEXT.md | Handoff 2 can't consume unstructured synthesis files |
| A6 | Phase 2 (Design) scope | AUTO: SKIP | NO UI | |

---

### Taste Decisions — Surface to Ray

**T1 — Session architecture:** 7 targets in one Opus session vs. 5+1 bounded sessions (one per module + final synthesis pass). Recommendation: **5+1 sessions.** Context burn on Module 3 is the risk that kills the whole pass.

**T2 — Module 3 primary/supplementary split:** Phases 14/15/16 from ai-engineering-from-scratch are PRIMARY. Loop-engineering, fleet-engineering, ai-system-design-guide are SUPPLEMENTARY. Recommendation: **Codify this in the spec.** Currently implied, not explicit.

**T3 — Module 5 fixed number:** 10–15 is the stated range. Should Opus pick the number or should Cowork pre-select before handing off? Recommendation: **Opus selects within 10–15, flags any HOLD cases for Ray.**

---

### Runs / Status / Findings

| Phase | Status | Key Finding |
|-------|--------|-------------|
| Phase 0 | DONE | DX=yes, UI=no, mode=SELECTIVE EXPANSION |
| Phase 1 (CEO) | DONE | One flag: 7-target single-session is a context risk |
| Phase 2 (Design) | SKIPPED | No UI scope |
| Phase 3 (Eng) | DONE | Three gaps: session split, read budget, output format |
| Phase 3.5 (DX) | DONE | 7/10 → 9/10 with 4 additions |

**VERDICT: DONE_WITH_CONCERNS — spec is ready pending 4 additions and Ray's call on T1.**

**AUTO-DECIDED (not requiring Ray):**
- Add SUPPLEMENTARY label to source inputs per target
- Set Module 3 lesson target: 35–45 LESSON candidates
- Add HOLD as 5th classification label in COURSE-CRITERIA.md
- Add output block format to CONTEXT.md

**REQUIRE RAY:**
- T1: 5+1 sessions vs. 7 targets in one Opus session
- T2: Codify primary/supplementary source priority in Module 3 (Cowork writes it vs. implicit)
- T3: Module 5 capstone — Opus selects within 10–15 vs. Cowork pre-selects
