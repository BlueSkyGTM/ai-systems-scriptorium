# Module 4 — Technical Screens — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` self-cleared under the standing directive; Ray's "go"
to source + author the deferred M4).** The previously-deferred module, now buildable: an ore survey
(read-only Haiku) confirmed the coding tasks can be **grounded in the real Sans Python portfolio code**,
so nothing is fabricated. Authoring M4 makes the book complete (8 of 8).

## Why this was deferred, and what changed

M4 was deferred because the interview vault has no live-coding worked examples, and building it as a
LeetCode-style module would mean inventing coding problems (the no-fabrication rule forbids it). The
reframe removes the blocker: the worked coding tasks are drawn from the **real, already-tested Sans Python
portfolio code** (the terminal coding agent + the production RAG chatbot). Each task is "implement /
extend / debug X," where X is a self-contained pattern whose reference implementation exists in the
portfolio. The transferable core the blueprint always wanted, the **communication layer** (narrating your
reasoning while you code), is the spine; the grounded tasks are how it is taught.

## THE decision to lock: teach the communication layer, ground every task in real code

The screen tests how you think, not whether you finish. M4 teaches the communication layer: clarify the
problem before coding, narrate your reasoning, think out loud while implementing, debug out loud when
stuck, test as you go, manage the clock. Every worked task is grounded in a real Sans Python portfolio
pattern (cited file + lines); the lessons show the reasoning, not a paste-ready solution, and never
fabricate a problem. **Scope honesty:** M4 covers the communication layer and AI-engineering coding
patterns; it does NOT replace dedicated algorithm drilling, which M8 rightly says to source separately.
M4 keeps that line: it does not claim to be your only coding-screen prep.

## Locked decisions

1. **Stage = module.** Writes `build-log/answer-engineering/m4/`. House cadence: overview + 4 lessons + 4
   exercises.
2. **Held to the three contracts** + the locked M1-8 voice.
3. **No fabrication.** Every worked task traces to a real portfolio file (cited). Lesson-writers READ the
   cited real file and ground any shown code in it. MS-Learn not forced (coding-screen craft).
4. **No new runnable artifact** (ponytail/lean): the reference code already exists and is tested in the
   Sans Python portfolio; M4's throughline is a markdown log, not new code.

## Proposed M4 split (overview + 4 lessons; tasks grounded per the survey)

| # | Lesson (slug) | The move | Grounded worked task(s) |
|---|---------------|----------|--------------------------|
| 0 | `00-overview` | The screen tests how you think; the communication layer is the skill; tasks are grounded in your real portfolio. | survey + M1 Algorithm recap |
| 1 | `narrating-the-screen` | The communication layer: clarify first, narrate reasoning, think out loud; the pitfalls (monologue, no structure, jargon, defending a wrong answer). | retrieval relevance floor (`retriever.py`) |
| 2 | `the-happy-path-and-the-edges` | Implement + test as you go: happy path first, then the defensive cases, narrated. | token-budget guard (`budget.py`); content guardrail (`guardrail.py`) |
| 3 | `debugging-out-loud` | Getting stuck is expected: the gather/hypothesize/diagnose/verify motion; isolate and recover without a rewrite. | sandbox timeout hang (`sandbox.py`); tool path-jail bug (`tools/__init__.py`) |
| 4 | `the-clock-and-the-weak-screen-audit` | Time management + testing under pressure + the weak-screen audit (did you clarify, narrate, test, recover, or go silent and code?). | read-only kill switch (`killswitch.py`); drift monitor (`drift.py`) |

All task references are in `ingredients/source/answer-engineering/coding-screen-tasks.md` (premise + the
real `library/completed/sans-python/...` file + lines + the pattern + why it is an AI-eng screen task).

## The compounding throughline (STANDARDS Part 3) + the validator numbering

M4 EXTENDS the dossier with `exercises/prep/coding-screen-log.md` (the reader's logged screen reps: the
task, the clarifying questions asked, the approach narrated, where they got stuck and how they recovered,
the test cases, a verdict). `check_prep.py` grows to **v8** filling the long-open `--module 4` gap.
**Numbering decision (locked):** `--module 4` requires M1 + M2 + M3 + the coding-screen log (its place in
sequence); it is a **sibling branch** to M5-M8, which do NOT require it (their gates stay byte-identical,
so the 75 existing tests keep passing). `--module all` DOES include it (update the full-dossier fixture),
so "all" means the complete dossier. M4 is NOT wired into `grade_dossier.py`: consistent with M8, the
coding screen stays outside the graded interview-loop (dedicated algorithm drilling is sourced
separately); M4 gives the reader the communication skill + a practice log, not a graded loop stage.

## The fleet plan (Haiku-fetch / Sonnet-author; ponytail)

Conductor (Opus) writes the `coding-screen-tasks.md` ingredient from the survey + `00-overview` + SUMMARY.
Round 2: four Sonnet lesson-writers (each reads the cited real portfolio files for the exact patterns they
show) + one Sonnet exercises/validator worker (check_prep v8 `--module 4` + the coding-screen-log template
+ 4 exercises). VERIFY (Opus): STYLE + grounding (every shown pattern traces to the cited real file, no
fabricated problems) + no fourth-wall leaks + the validator runs. BUILD/TEST: `mdbook build` +
`check_prep.py` v8 pytest + `calibrate.py`/`grade_dossier.py --selftest` still green. Ship at
`GATE-APPROVE-SHIP` under the standing directive. After ship: the book is COMPLETE (8 of 8).
