# Northstar — Fresh-Context Handoff

**Written:** 2026-06-18 (end of a long Opus session)
**For:** the next session, starting cold. Read this top-to-bottom first.

> **⚠️ ARCHIVAL — superseded 2026-06-18.** `SYLLABUS.md` is the curriculum state-of-record. This handoff is
> stale on several items it lists as TODO that are in fact **done** and present on disk (the roadmap.sh flow
> audit `snapshot/step2-flow-audit.md`; the 8-module renumber + antilibrary fold-in in SYLLABUS). It remains
> accurate only as history. The live build is the **`migration/`** layer (`AUTHORING.md` = the build contract,
> `_dossier/` = the lesson audit, `src/` = lessons in progress); the items this handoff lists as TODO were
> largely completed there. Residual cleanup only: the snapshot `module1-5.md` prereq files are still in old
> numbering. See `AUTOPLAN-REVIEW.md` for the evidence-based reconciliation.

---

## Where Northstar is

Phase 2 (synthesis = consolidation + indexing) is **done**. The prerequisite snapshot (Step 1) is
**done** for all modules. Most curation decisions (Step 3) are **done**. The curriculum's *shape* is
fully decided. What's left is one audit, a renumber, and writing the build spec — then it goes to
Claude Code.

**The library** lives at `specs/northstar/sub-repos/synthesis/source/` — consolidated, indexed
(`INDEX.md`), crawlable. **The map** lives at `specs/northstar/sub-repos/synthesis/output/snapshot/`
— per-module prereq graphs + the resolutions below.

**Headline:** no backward-ordering violations anywhere. The Sans Python sequencing thesis holds. The
work was curation (cut/dedup/thread/link), not resequencing — and that curation is largely done.

---

## Locked decisions (all in memory; don't re-litigate)

1. **8-module structure** — 5 teaching (Foundations, LLM Engineering, Agent Foundations, Multi-Agent
   Systems, Deploy & Performance Engineering) + **Agent Artifacts** + **Multi-Agent Artifacts** +
   **Final Systems Engineering Exam**. ([[curriculum-module-structure]])
2. **Compounding artifacts** — single agents (M6) → composed into teams (M7) → that team builds the
   exam system (M8). Reuse at each stage. Artifacts solve **real business problems**.
3. **Lean / link, don't reproduce** — do NOT reproduce `ai-engineering-from-scratch`'s 500+ from-scratch
   lessons. Link them as reference/antilibrary. Curriculum spine = business-application artifacts.
4. **Language threading** — Rust & TS threaded to point-of-use, no Module-1 wall. TS additive from
   Agent Foundations; Rust one concentrated ownership on-ramp at Deploy. ([[language-track-threading]],
   `snapshot/language-tracks.md`)
5. **Optimize ruling** — keep the fine-tune-vs-prompt *decision* + *operational* agent safety in-seam;
   antilibrary the model-training *implementation* (GPT-from-scratch, distributed training) and
   frontier-safety *research/policy*. ([[optimize-archetype-ruling]], `snapshot/step3-resolutions.md`)
6. **Reference layer = Microsoft Learn only, context-fill.** Coursera, Learning Commons graph,
   course-designer all scrapped. ([[northstar-reference-layer]])
7. **Flow-audit approach** = docling-graph + roadmap.sh benchmark; platformengineering.org + CNOE as
   structural/vocab reference only (not content). ([[curriculum-flow-audit-approach]])
8. **Step-3 resolutions** (in `snapshot/step3-resolutions.md`): generative media → antilibrary cut;
   RAG → one spine (asdg Ch06 + aefs Ph11); MCP → one spine (aefs Ph13); Track H → thin teaching +
   realized in artifacts.
9. **Autoplan** runs always: fetch-and-ground if a repo exists, else manual over local source (say so).
   ([[autoplan-hold]])

---

## What to do with fresh context (in order)

### 1. Step 2 — roadmap.sh flow audit
Fetch live: roadmap.sh **AI-Engineer**, **MLOps**, **System-Design** (and **AI-Agents**) DAGs. Assemble
the cross-module edge graph from the `snapshot/module*.md` edge-lists. Compare our ordering to the
benchmark; **mark deliberate deviations** (the seam — we expect to deviate, that's fine). Output a short
audit note. This is the one piece that genuinely needs live fetching + fresh context.

### 2. Renumber to the 8-module structure
The snapshot files use the old 5-module numbering (M4=Deploy, M5=Capstone). Renumber across:
- `SYLLABUS.md` (the canonical structure doc)
- `snapshot/module*.md` cross-references
- Fold the Step-3 **antilibrary rulings** into SYLLABUS.md's antilibrary section (generative media,
  GPT-from-scratch 30–49, distributed training 76–81, frontier-safety research, the aefs 500+ link-not-reproduce).
Mechanical but broad — do it carefully in one pass.

### 3. Reconcile the artifacts plan
`snapshot/artifacts-plan.md` was written under the old "distribute into modules" call. Update it to the
new structure: Agent Artifacts (M6) and Multi-Agent Artifacts (M7) are their own modules; bake in the
**compounding** design (M6 agents reused in M7 teams; M7 team builds the M8 exam) and the
**business-problem** focus. The candidate artifact list is still a good starting point.

### 4. Step 4 — write `build/CONTEXT.md`
The Handoff-2 spec (lesson authoring → Claude Code). Does not exist yet. Write it against the validated,
renumbered 8-module structure + the thesis/seam + the locked decisions above. Must include a How To
(project rule 09). This is what Claude Code is pointed at to build.

---

## Open items (Ray's call)

- Cleanup of copied originals in sub-repo `output/content/` (copied, not moved).
- 4/3 vs 4/4 artifact split (minor; superseded somewhat by the new own-module structure).

---

## Key files

| File | What |
|------|------|
| `SESSION-STATE.md` (workspace root) | current focus, next actions, resolved/open flags |
| `SPEC.md` | thesis, archetypes, AI Platform Engineering seam |
| `SYLLABUS.md` | module structure (needs 8-module renumber + antilibrary fold-in) |
| `REFERENCE-LAYER.md` | Microsoft Learn context-fill pointers |
| `synthesis/source/INDEX.md` | the consolidated library crawl map |
| `synthesis/output/snapshot/README.md` | snapshot method + cross-cutting findings |
| `synthesis/output/snapshot/module1–5.md` | per-module prereq graphs + edge lists (old numbering) |
| `synthesis/output/snapshot/language-tracks.md` | Rust/TS threading map |
| `synthesis/output/snapshot/step3-resolutions.md` | the Optimize ruling + all Step-3 cuts/merges |
| `synthesis/output/snapshot/artifacts-plan.md` | artifacts set (needs reconcile to 8-module) |
| Memory index (`MEMORY.md`) | all locked decisions, linked |
