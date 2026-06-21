# Module 3 — Behavioral Interviews — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared via Ray's "lock").** Third authoring stage
for Answer Engineering (M1-2 shipped 2026-06-21). M3 opens Phase 2 of the book (the example banks). It
is the first module whose job is not to teach a new concept but to load the Algorithm into intuition by
applying it, end to end, across a bank of real behavioral questions. All four open decisions resolved at
lock: the anti-memorization guardrail below is locked; four lessons by category; two strong reasoned
examples per lesson; `check_prep.py` extends in place to v3.

## The stage in one line

M1 installed the Algorithm; M2 deepened it. M3 is reps: the reader watches the four steps run on real
behavioral questions across every category an AI Engineer faces, until the moves are automatic, then
builds their own behavioral bank the same way. Seam: a Production AI Engineer has the framework but
freezes on "tell me about a time" because they have no rehearsed, audited stories; M3 is where the
stories get built and stress-tested before the room.

## THE decision to lock: worked examples, not canned answers

The book's thesis forbids rote question dumps with model answers (that is the thing it argues against;
see the blueprint's DELIBERATELY OUT list). So every worked example in M3 shows the **Algorithm
reasoning**, not a script to memorize: here is the question, here is the decomposition (the signal and
hypothesis), here is how the STAR-L answer is constructed toward that signal, here is the stress-test
and the one specific thing that makes it unfakeable. The reader learns the move, not the words. The
lessons never present a paste-ready answer; they present the thinking that produces one, on questions
the reader will adapt to their own experience. If this guardrail is wrong, say so at lock; it shapes
every worked example.

## Locked-on-the-blueprint decisions

1. **Stage = module.** Same ICM shape; reads its sources, writes `build-log/answer-engineering/m3/`,
   hands the deepened voice + the behavioral bank forward to M4.
2. **Held to the three contracts** + the locked M1-2 voice. Cold workers get all of it in-brief.
3. **House cadence: overview + 4 lessons + 4 exercises**, one behavioral category per lesson.
4. **No fabrication.** Every worked example is built from the real `asdg` behavioral ore (the six
   STAR-L examples + the real behavioral question bank); no invented stories presented as real.
   MS-Learn is not a behavioral-craft domain; M3 grounds on the ore and does not force MS-Learn
   citations (a Tier-2 narrowing logged here, same posture M2's behavioral lessons took).

## Proposed M3 split (overview + 4 lessons, one behavioral category each)

The blueprint names the behavioral categories: ownership, conflict, failure, technical influence. Each
lesson gives the signal map for that category (what hypothesis its questions test, the category-specific
failure modes), two or three worked examples (the Algorithm applied end to end), and a candidate task.

| # | Lesson (slug) | The category and its signal | Worked-example ore |
|---|---------------|-----------------------------|--------------------|
| 0 | `00-overview` | Why the bank exists: reps load the framework into reflex; how to read a worked example (for the move, not the words). | blueprint + M1-2 recap |
| 1 | `ownership-stories` | Did you drive it or watch it? The "I" vs "we" discipline; owning the outcome, not the activity. | asdg 05 Theme 3 (complex project), Example 5 (walkback) |
| 2 | `conflict-stories` | Disagreement with a PM, a peer, a stakeholder: the disagree-and-commit pattern, de-escalation, the proportional escalation. | asdg 05 Collaboration, Example 4 (different priorities) |
| 3 | `failure-stories` | A project that failed or shipped late: the Learning step as the load-bearing move; honest scoping over a polished excuse. | asdg 05 failure questions, Example 5 (wrong call) |
| 4 | `influence-stories` | Leading without authority, convincing others, technical influence: the move from "I shipped" to "I changed what others could ship" (the staff signal). | asdg 05 Leadership, Example 6 (concern dismissed) |

## Ore augmentation (the first move)

M1 distilled three of the six `asdg` STAR-L examples (1, 5, 6). M3 needs the full behavioral bank. A
distillation pass produces `ingredients/source/answer-engineering/asdg-behavioral-bank.md`: all six
STAR-L worked examples in skeleton form, the behavioral question bank grouped by the four categories,
and the category-specific failure modes (the behavioral red flags from asdg 05). Author against this
ingredient, not raw vault.

## The compounding throughline (STANDARDS Part 3)

M3 EXTENDS the prep dossier: the reader builds their own **behavioral bank**. A new
`exercises/prep/behavioral-bank.md` holds the reader's own STAR-L stories, one or more per category,
each run through the full Algorithm and the M2 weak-answer audit (so the M2 work is reused, not
restated). `check_prep.py` grows to **v3** in place (the `--module 3` set): validates the behavioral
bank (at least four stories covering all four categories, each with the five STAR-L parts and an audit
verdict; no placeholders). The validator-as-throughline keeps compounding toward the M8 capstone that
composes and grades the whole dossier.

## The fleet plan (orchestration)

**Conductor-direct, no handler tier** (one small cluster, per the JP A/B and AE M1-2). Round 1: one
Sonnet worker runs the behavioral-bank augmentation; the conductor authors `00-overview` and updates
SUMMARY. Round 2: four Sonnet lesson-writers (one category each) + one exercises/validator worker,
parallel, each briefed with the three contracts + the M1-2 voice exemplars + the ingredient. The
conductor runs the Zinsser + STYLE + STANDARDS review gate on every draft, watches for the two recurring
risks (fourth-wall leaks; any worked example drifting into a paste-ready canned answer), and reconciles
`check_prep.py` v3 so it stays runnable and backward-compatible.

## Open decisions for lock

1. **The anti-memorization guardrail** (above) — the call that shapes every worked example.
2. **Four lessons by category** (ownership / conflict / failure / influence) vs a different cut.
   Recommend the blueprint's four; they are the standard behavioral taxonomy and map cleanly to the ore.
3. **Worked examples per lesson:** two or three. Recommend two strong, fully-reasoned examples over a
   thin bank of many; depth on the move beats breadth (the same principle M1 taught about answers).
4. **`check_prep.py` v3 extends in place** (recommended, consistent with M2).

On lock: the fleet augments the ore + authors M3, VERIFY gates it (voice + claims + grounding + no
canned-answer drift + the extended validator runs), BUILD/TEST runs `mdbook build` + `check_prep.py` v3
+ pytest, and the stage stops at `GATE-APPROVE-SHIP` before folding into `src/` and `exercises/`.
