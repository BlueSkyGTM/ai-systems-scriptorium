# Answer Engineering — Build Progress

Per-stage authoring status. One row per module.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | The Framework | ✅ Shipped | 2026-06-21 | Overview + 2 lessons (decompose-the-question, construct-the-answer) + 2 exercises. Installs the four-step Algorithm (decompose, identify the signal, construct, stress-test) and the four AI-Eng signal categories. Seeds the **prep dossier** throughline (`exercises/prep/`): `decomposition-log` + `answers-log` + the `check_prep.py` validator (with pytest, negative case tested); ships `exercises/CLAUDE.md`. First module of this book, so it also distilled the book's first ingredient from raw `asdg` ore (`ingredients/source/answer-engineering/`) and stood up the mdBook scaffold. Plan: `m1/PLAN.md`. |
| M2 | The Algorithm in Detail | ⬜ Not started | — | Deepens each of the four steps. See `library/in-progress/answer-engineering/README.md`. |
| M3–M8 | per blueprint | ⬜ Not started | — | Phase 2 example banks (behavioral, technical, systems-design) + Phase 3 portfolio layer. The prep dossier + `check_prep.py` extend through these; M8 composes and grades the full dossier. |

## Provenance

M1 graduated the book through `GATE-NAME-BOOK` (title "Answer Engineering" chosen 2026-06-21, was
"Anatomy of an Answer"/`interview-algorithm`) and ran the full AUTHOR → VERIFY → BUILD/TEST → SHIP
cycle. `GATE-LOCK-PLAN` was cleared by Ray's "GO FOR BROKE" against a pre-vetted draft (low wasted-work
risk); `GATE-APPROVE-SHIP` was presented and approved before the commit.

Authored **conductor-direct, no handler tier** (one small cluster, per the Just Python A/B result in
`platform/ORCHESTRATION.md`). Round 1: one Sonnet worker distilled the raw `asdg` interview ore
(`vault/ai-system-design-guide/00-interview-prep/`, 8 files) into the book's first reusable ingredient
(a signal taxonomy + frameworks catalog + M1 dossier), while the conductor scaffolded the book and
authored the intro + overview. Round 2: two Sonnet lesson-writers + one exercises/validator worker ran
in parallel, each briefed cold with STYLE + STANDARDS + AUTHORING + the voice exemplar + the ingredient
+ the connector instruction.

VERIFY (conductor): caught and fixed 5 fourth-wall leaks (the workshop term "the ore" and source-internal
"Example N" numbering leaking into reader-facing prose) and aligned a lesson handoff with the exercise's
real design. Every Microsoft Learn citation was **fetched live and confirmed to match its claim** (Azure
Well-Architected AI application-design + operations, Azure AI Foundry observability); zero fabricated
citations (the fix for the JP M2/M3 problem). Every worked example traces to the real `asdg` ore (no
invented questions or transcripts). BUILD/TEST: `mdbook build` clean; `check_prep.py` exits cleanly and
its pytest passes 9/9 (positive + negative cases).

The career-artifact pattern is established here: the proof is a **document** (the prep dossier) gated by
a structured-completeness validator, the same shape Local Metal uses for a hardware module where no
code-execution gate exists.
