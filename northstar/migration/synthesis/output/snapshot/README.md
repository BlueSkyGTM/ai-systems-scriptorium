# Prerequisite Snapshot — Method & Status

The snapshot turns the consolidated library (`synthesis/source/`) into a **directed
prerequisite graph**: a map of what concepts exist and what must be learned before what.
It's the missing picture — we have all the material but no view of what it adds up to.

Built natively (LLM pass over the indexed source), not via docling. docling stays as an
optional later hardening pass if the build handoff needs a re-runnable pipeline.

## What each module file contains

- **Nodes** — concepts at lesson/topic granularity (finer is noise for a flow audit), tagged
  with track and Build/Learn type.
- **Internal edges** — `A → B` means "A is a prerequisite for B" *within this module*.
- **Outbound edges** — concepts here that are prerequisites for something in a *later* module
  (the cross-module forward signal the flow audit needs).
- **Inbound assumptions** — what this module assumes is already known.

Edges mean **"requires,"** directed. That's the property the Step-2 topological audit runs on:
flag any concept that depends on something taught later.

## Status

| Module | Files | Snapshot |
|--------|-------|----------|
| 1 | 5 | done |
| 2 | 5 | done |
| 3 | 18 | done |
| 4 | 9 | done |
| 5 | 1 | done |
| cross-module | — | done (`step2-flow-audit.md`) |

**All five modules snapshotted. Step 2 (flow audit vs roadmap.sh) complete — PASS, no backward-ordering
violations.** The library was renumbered to the **8-module structure** (old M3 split into M3 Agent
Foundations + M4 Multi-Agent Systems; Deploy→M5; capstones→M6/M7/M8). Each `module*.md` carries a
renumber-map header; edge lists are renumbered. Canonical structure lives in `SYLLABUS.md`. Next:
reconcile `artifacts-plan.md` to own-module structure, then write `build/CONTEXT.md`.

## Cross-cutting findings so far (feed Step 2 audit)

1. **The "Optimize archetype" (model training) is the through-line seam question.** aipe's training/CUDA chapters are cut to antilibrary in M4, but M5's GPT-from-scratch training track (lessons 30–48) is present. Northstar must resolve this *once, consistently*: is from-scratch model training in-seam literacy or out-of-seam Optimize depth?
2. **Generative media (M2 Track E) is ~90% off-seam** — strongest single CUT candidate; source self-flags 13/15 lessons antilibrary.
3. **Triple RAG coverage** (M1 NLP cluster + M2 aefs Ph11 + M2 asdg Ch06) — biggest dedup/merge job; a curation task, not a sequencing error.
4. **mwml MLOps (M4 Track E) is partly off-seam** — model-centric training-pipeline material is a CHECK/antilibrary candidate (the M4 analog of generative-media).
5. **No backward-edge violations** found in any module — ordering is sound; the work is curation (dedup + cut), not resequencing.
6. **Module 3 is a structural outlier** — 18 files / ~130 lessons / 8 tracks, ~2–3× any other module. It splits cleanly at the single-agent↔multi-agent seam (the complexity ladder). Strong candidate to become two modules (Agents | Multi-Agent & Fleet). See Step 2.
7. **Repeated "Optimize / research-policy" CHECK across M3/M4/M5** — model-training (M4 aipe, M5 GPT-from-scratch) and frontier-safety-research (M3 Track F) are the same off-seam question recurring. One consistent ruling needed.

After all modules: a combined edge list + the Step-2 flow audit against roadmap.sh.
