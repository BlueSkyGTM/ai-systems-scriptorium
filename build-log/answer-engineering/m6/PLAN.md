# Module 6 — The Sans Python Portfolio as Resume — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` self-cleared under Ray's standing "finish the job;
offload to sonnets, haikus for fetching" directive; "you're doing fine keep it up" = go for Phase 3).**
Fifth authoring stage for Answer Engineering (M1-3 + M5 shipped). **M6 opens Phase 3: the portfolio
layer.** Ore is confirmed present (the Sans Python completed book's runnable portfolio artifacts), so
there is no M4-style blocker.

## The stage in one line

Phase 2 taught the reader to reason to a strong answer (behavioral, systems-design). Phase 3 turns to the
proof they bring with them: the Sans Python portfolio. M6 teaches the reader to walk an interviewer
through a real artifact, foregrounding the decisions, tradeoffs, and failure modes they handled (the why),
tailored to the role, instead of a line-by-line code tour. Seam: a Production AI Engineer has shipped real
systems but loses the room by narrating what the code does instead of why they built it that way.

## THE decision to lock: narrate the reasoning behind the artifact, not the code

The book's thesis carries into Phase 3. A portfolio walkthrough is not a code reading; it is the same
"show the reasoning" move applied to something the reader already built. Every worked walkthrough
foregrounds the decision layer: here is the artifact in one breath, here are the three decisions that
mattered, here is the alternative each rejected and the tradeoff it accepted, here is the failure mode it
guards against, and here is how the emphasis shifts for a different role. The lessons never teach a
memorized script for "walk me through your project"; they teach how to construct the walkthrough from the
artifact in front of you, so it transfers to any artifact and any role. If this guardrail is wrong, it
shapes every worked walkthrough.

## Locked-on-the-blueprint decisions

1. **Stage = module.** Same ICM shape; writes `build-log/answer-engineering/m6/`, hands the portfolio
   layer forward to M7 (live practice) and M8 (the hiring loop + full-dossier grade).
2. **Held to the three contracts** + the locked M1-5 voice.
3. **House cadence: overview + 4 lessons + 4 exercises.**
4. **No fabrication.** Every worked walkthrough is built from the REAL Sans Python portfolio artifacts
   (their `src/` lessons + code under `library/completed/sans-python/`); no invented projects, no invented
   decisions. MS-Learn is not a portfolio-narration domain; M6 grounds on the Sans Python ore and does not
   force MS-Learn citations (a Tier-2 narrowing, same posture as M3 behavioral).
5. **Worked-example artifacts:** the **terminal coding agent** (`exercises/module6/01-terminal-coding-agent`
   + `src/module6/01-terminal-coding-agent.md`: sandbox, killswitch, budget, verify-gate decisions) and
   the **production RAG chatbot** (`exercises/module6/02-production-rag-chatbot` +
   `src/module6/02-production-rag-chatbot.md`: ingest/index/retriever/guardrail/drift/eval decisions).
   These two span the range (a safety-railed single agent; an applied-AI RAG product) and are the most
   role-relevant for an AI Engineer. The other portfolio projects (voice assistant, issue-to-PR agent, the
   M7 research/devops/fleet agents, the M8 exam) are the reader's own bank, referenced not deep-dived.

## Proposed M6 split (overview + 4 lessons)

| # | Lesson (slug) | The move and its signal | Worked-example ore |
|---|---------------|-------------------------|--------------------|
| 0 | `00-overview` | Phase 3 opens: you interview ON your portfolio. What a walkthrough is (reasoning, not code reading); how to read a worked walkthrough. | blueprint + M1-5 recap |
| 1 | `the-artifact-walkthrough` | The shape of a walkthrough: the 60-second overview then the decision tour; what to foreground vs. skip. Signal: can you make an interviewer understand the system fast, then go deep where it counts? | terminal coding agent |
| 2 | `foreground-the-decisions` | The decision/tradeoff/failure-mode layer at depth: interviewers buy the why, not the code. Signal: every component was a choice you can defend, the same discipline as M5's justify-every-box but on a system you actually shipped. | production RAG chatbot |
| 3 | `tailoring-to-the-role` | Same artifact, different emphasis per role (applied-AI product vs. ML-platform vs. research-adjacent). Carries the anti-memorization thesis: the walkthrough bends to the role's signal. | RAG chatbot narrated two ways |
| 4 | `the-portfolio-narrative-document` | The finale: compose the written portfolio-narrative document (the throughline artifact), interview-ready and peer-reviewable, then run the **weak-walkthrough audit** on it (the M6 analogue of M2's weak-answer / M5's weak-design audit). | both artifacts + the audit |

## Ore augmentation (the first move)

A distillation pass produces `ingredients/source/answer-engineering/portfolio-artifact-catalog.md`: for
each featured artifact, the one-line purpose, the architecture in brief, and the 3-5 load-bearing
decisions with the alternative each rejected, the tradeoff accepted, and the failure mode guarded against,
all traced to the artifact's real `src/` lesson + code. Plus a short index of the other portfolio
projects (purpose + headline decision each) so lessons can reference the reader's full bank. Author
against this ingredient, not the raw Sans Python tree.

## The compounding throughline (STANDARDS Part 3)

M6 EXTENDS the prep dossier: the reader builds a **portfolio-narrative document**. A new
`exercises/prep/portfolio-narrative.md` holds a structured, interview-ready walkthrough of at least one
portfolio artifact (their own, or a Sans Python one if they worked the book): the artifact, a one-paragraph
overview, the key decisions, the tradeoffs, the failure modes handled, a role-tailoring note, and a
self-audit verdict. `check_prep.py` grows to **v5** in place (the `--module 6` set): validates the
portfolio narrative (at least one `## Artifact <n>` entry with the seven fields, no placeholders). M1-3 + M5
checks stay byte-identical. **Numbering:** the validator gains `--module 6`; `--module 4` stays open
(deferred); `all` validates the shipped modules' artifacts (1, 2, 3, 5, 6). The validator-as-throughline
keeps compounding toward the M8 capstone that composes and grades the whole dossier.

## The fleet plan (Haiku-fetch / Sonnet-author tier)

**Conductor-direct.** Round 1: one **Haiku** surveys the two featured artifacts' `src/` lessons + code and
returns the decisions/tradeoffs/failure-modes per artifact; one **Sonnet** distills that into
`portfolio-artifact-catalog.md`. The conductor (Opus) authors `00-overview` + SUMMARY. Round 2: four
**Sonnet** lesson-writers + one **Sonnet** exercises/validator worker, parallel, each briefed with the
three contracts + the M2/M5 voice exemplars + the ingredient. The conductor runs the Zinsser + STYLE +
STANDARDS review gate, watches the recurring risks (fourth-wall leaks; any walkthrough drifting into a
line-by-line code tour or a memorized script), and reconciles `check_prep.py` v5.

## Open decisions (resolved at self-lock, as recommended)

1. The narrate-the-reasoning guardrail (above).
2. Four lessons (walkthrough shape -> foreground decisions -> role tailoring -> document + audit).
3. The two featured artifacts (terminal coding agent + production RAG chatbot).
4. `check_prep.py` v5 in place with `--module 6`.
5. MS-Learn not forced (portfolio narration is interview craft).

On lock: the fleet augments the ore + authors M6, VERIFY gates it (voice + grounding + no code-tour drift +
the extended validator runs), BUILD/TEST runs `mdbook build` + `check_prep.py` v5 + pytest, and the stage
ships at `GATE-APPROVE-SHIP` (cleared under the standing directive) folded into `src/` and `exercises/`.
