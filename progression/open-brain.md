# Open Brain — open spaced repetition + GBrain

> Spaced repetition that lives *inside* a knowledge graph instead of beside it. The forgetting curve,
> fought in context.

**Status:** concept / spec. Build target: an [Extra Credit](../extra-credit/CONTEXT.md) tool wired into
this `progression/` folder. No Anthropic API key required (scheduling is date arithmetic; the only LLM
steps — card generation and conversational quizzing — run in-session, not on GBrain's key).

## What it is

Open Brain = an **FSRS** scheduler (the modern algorithm Anki now uses) running over **GBrain** as the
card + state store. The items are not hand-made flashcards — they are each lesson's `## Core concepts`
propositions (the [STYLE §5](../platform/conventions/STYLE.md) retention hook), which are already
author-curated, load-bearing claims. The item bank is produced for free by AUTHOR; Open Brain only
schedules and quizzes.

## Why GBrain, not a flashcard app

The edge over Anki is **graph-contextual review**: every card links back to its source lesson and that
lesson's connections, so a *miss* surfaces the surrounding *why* — review reinforces the web, not an
isolated fact. New cards generate themselves as the curriculum grows. And it all sits next to the rest
of the brain (the gap report, the cusp, the artifacts), so review is one hop from everything else.

## The shape — agent-driven, not a deck

Do **not** build a deck UI. Nobody tends a deck (the same friction that ruled out Obsidian). Instead:

1. **Generate** — from a lesson's `## Core concepts`, author one card per proposition as a GBrain page
   (`type: card`), linked to its source lesson page.
2. **Schedule** — FSRS state in the card's frontmatter: `due`, `stability`, `difficulty`, `reps`,
   `last_grade`, `last_reviewed`.
3. **Quiz** — the agent pulls the due / weak / stale cards from the graph and quizzes the reviewer
   *conversationally*, infers the grade (again | hard | good | easy) from the answer, and writes the
   next interval back to GBrain (and a `add_timeline_entry` review-log row).
4. **Recover** — on a miss, traverse to the linked lesson + connections and re-teach in context before
   rescheduling.

The "schedule" the human sees is just *"here's what you're about to forget — want a quick round?"*

## Scope — the recall-fluency layer only

SR optimizes recall; the hireability bet is fluency + portfolio, not memorization. So Open Brain stays
on the layer the **ML-system-design interview** actually tests at recall speed: named patterns
(ReAct, MAST, the four primitives, PagedAttention), key numbers/formulas (the KV-cache math, latency
budgets, the hiring screens), and the "speak-to-it" literacy for the antilibrary gaps (LoRA vs QLoRA,
when to fine-tune). The `## Core concepts` bank already *is* this layer — keep it there. Do not SR whole
lessons; that is rote-learning a project-based skill.

## Data model (GBrain)

- **Card page** — `type: card`, slug `card-<book>-<lesson>-<n>`; body = the proposition (front) + the
  answer/elaboration (back); frontmatter carries the FSRS state; `add_link` → its source lesson page
  (`tests`).
- **Review log** — a timeline entry per review (date, grade) on the card page.
- **Due query** — `list_pages type=card` filtered by `due <= today`, ranked by staleness/difficulty.

## Open decisions (flag before build)

1. **Who reviews?** Ray's own interview prep vs. a *reader-facing* course feature (the `progression`
   spec frames it as a reader's progress). The loop is the same; the cadence and the "will they review"
   risk differ. The agent-driven shape is the mitigation for both.
2. **Cards persisted vs. generated-on-the-fly** — persist in GBrain (history, FSRS state survives) is
   the recommendation; on-the-fly loses the schedule.
3. **Cadence** — on-demand ("quiz me") first; a scheduled nudge only if reviews actually happen.

## Build plan (when greenlit)

An Extra Credit tool: `extra-credit/tools/open-brain/` — a stdlib FSRS implementation + a thin GBrain
client (put_page / list_pages / add_link / add_timeline_entry) for card CRUD and due-queries. Prototype
on one module's `## Core concepts`, run the quiz loop with the agent, then promote into `progression/`.
