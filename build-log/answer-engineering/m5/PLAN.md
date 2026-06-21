# Module 5 — AI/ML Systems-Design Interviews — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared via Ray's "LOCK IT").** All open decisions
resolved at lock as recommended: reorder M5-before-M4 confirmed; reasoning-to-a-design guardrail locked;
SPIDER as the construct motion; four lessons (scope → justify → production-reasoning → full-run+audit);
pull asdg ch.11-14 + MS-Learn for L3 depth; two worked designs per lesson; `check_prep.py` v4 in place
with `--module 5`. Fourth authoring stage for Answer Engineering
(M1-3 shipped 2026-06-21). **Reorder confirmed by Ray:** M5 (systems-design) is authored before M4
(technical screens). Reason: an ore survey found the vault has abundant, excellent systems-design ore
(the SPIDER framework + 9 whiteboard exercises + the pitfalls + asdg ch. 11-17) but essentially **zero
live-coding screen material**; building M4 as scoped would require inventing coding problems from
scratch, which the book's no-fabrication rule forbids. M4 is deferred until its ore is sourced
(likely reframed around the real Sans Python portfolio code). Blueprint order is soft — both are Phase 2.

## The stage in one line

M1 installed the Algorithm; M2 deepened it; M3 ran it on behavioral questions. M5 runs it on the hardest
interview surface for an AI Engineer: the open-ended systems-design prompt, where the reader must scope
an ambiguous problem, draw the boxes, justify every box with production reasoning, and survive the
weak-design audit — under a 45-minute clock. Seam: a Production AI Engineer has built real systems but
freezes on "design an X for us" because they reach for a textbook reference architecture instead of the
production reasoning that actually separates a senior answer from a staff one.

## THE decision to lock: reasoning to a design, not a reference architecture

The book's thesis forbids canned answers. For systems-design that means: the worked examples show the
**Algorithm + SPIDER producing a design from production reasoning**, never a memorizable "here is the RAG
architecture, copy it." Here is the prompt; here is how you scope it (what is actually being asked, the
implicit constraints, the scale); here is what the interviewer is evaluating (production thinking, not
diagram completeness); here is the design constructed box by box with each choice justified; here is the
weak-design stress-test (cost, latency, eval, reliability, failure modes). The reader learns the motion
that produces a design, not a diagram to reproduce. If this guardrail is wrong, say so at lock; it shapes
every worked example.

## Locked-on-the-blueprint decisions

1. **Stage = module.** Same ICM shape; reads its sources, writes `build-log/answer-engineering/m5/`,
   hands the deepened voice + the systems-design bank forward to M6 (portfolio layer).
2. **Held to the three contracts** (STYLE + STANDARDS + AUTHORING) + the locked M1-3 voice. Cold workers
   get all of it in-brief.
3. **House cadence: overview + 4 lessons + 4 exercises.**
4. **SPIDER is the construct motion** — the systems-design analogue of M3's STAR-L. SPIDER (Scope,
   Prioritize, Initial design, Deep dive, Evaluate, Reliability) is the domain-specific expansion of the
   Algorithm's "construct" step under a 45-minute clock. M5 presents it as a tool the reader runs, not a
   ritual to recite.
5. **No fabrication.** Every worked design is built from the real `asdg` ore (the 9 whiteboard exercises
   + SPIDER + the systems-design pitfalls); no invented benchmarks or made-up production numbers. Where a
   production-reasoning claim needs external grounding (cost/latency/reliability/eval patterns), it is
   grounded via the **Microsoft Learn connector** with live-verified URLs (Azure Well-Architected
   Framework for AI workloads; Azure AI Foundry observability) — real citations, applied where they fit,
   never forced and never fabricated.

## Proposed M5 split (overview + 4 lessons, mapped to the Algorithm × SPIDER)

| # | Lesson (slug) | The systems-design move and its signal | Worked-example ore |
|---|---------------|----------------------------------------|--------------------|
| 0 | `00-overview` | Why the round is open-ended on purpose; what is actually evaluated (production reasoning, not textbook architecture); SPIDER as the construct motion; how to read a worked design (for the reasoning, not the diagram). | blueprint + M1-3 recap + SPIDER |
| 1 | `reading-the-design-prompt` | Decompose + scope the ambiguous prompt before drawing anything (SPIDER Scope + Prioritize). Signal: the candidate who scopes (requirements, scale, constraints, the implicit ask) vs the one who designs blind. | asdg 04 Ex.1 Enterprise RAG; Ex.2 Support Chatbot |
| 2 | `justify-every-box` | Construct the design so every component choice is earned by production reasoning, not vocabulary (model selection, retrieval strategy, data pipeline). Signal: justification depth — "why this, not that, at this scale." | asdg 04 Ex.7 Semantic Search; Ex.4 Document Processing |
| 3 | `production-reasoning-as-the-differentiator` | The staff signal: cost + token economics, latency budgets, eval, reliability, failure modes (SPIDER Evaluate + Reliability). What a senior answer skips and a staff answer makes load-bearing. | asdg 04 Ex.5 Content Moderation (latency cascade); Ex.8 Eval Pipeline (CI gating); asdg ch.11-14 + MS-Learn |
| 4 | `the-full-design-under-pressure` | One full end-to-end design walked under the 45-min SPIDER clock, then the systematic **weak-design audit** (the M5 analogue of M2's weak-answer audit). | asdg 04 Ex.9 Agent Memory or Ex.3 Code Review Assistant |

**Thesis demonstration (carried from M3).** One whiteboard exercise is constructed twice toward
**different evaluation signals** — e.g. the same prompt foregrounded once for retrieval-quality reasoning
and once for cost/latency reasoning — with the contrast taught in-prose, proving the method transfers
and the design is not a fixed artifact to memorize.

## Ore augmentation (the first move)

A distillation pass produces `ingredients/source/answer-engineering/asdg-systems-design.md`: the SPIDER
framework (the 45-min phase budget + the worked design transcript), the 9 whiteboard exercises in
skeleton form (premise + scale + the production-reasoning anchors per exercise), the systems-design
pitfalls (the weak-design red flags from asdg 03), and selected production-reasoning depth from asdg
ch. 11-14 (infrastructure / security / reliability / eval) with the MS-Learn anchors identified. Author
against this ingredient, not raw vault.

## The compounding throughline (STANDARDS Part 3)

M5 EXTENDS the prep dossier: the reader builds their own **systems-design log**. A new
`exercises/prep/systems-design-log.md` holds at least one open-ended design prompt run end to end through
the Algorithm + SPIDER: the scoped requirements, the box-by-box design with justifications, the
production-reasoning section (cost / latency / eval / reliability), and a weak-design audit verdict.
`check_prep.py` grows to **v4** in place (the `--module 5` set): validates the systems-design log (a
prompt; the SPIDER phases present; justified components; a production-reasoning section covering all four
of cost, latency, eval, reliability; an audit verdict; no placeholders). M1-3 checks stay byte-identical.
**Numbering note:** the validator gains `--module 5`, leaving `--module 4` open for when M4 ships; the
`all` mode validates the shipped modules' artifacts (1, 2, 3, 5) and M4 joins later. The
validator-as-throughline keeps compounding toward the M8 capstone that composes and grades the whole
dossier.

## The fleet plan (orchestration + the delegation Ray asked for)

**Conductor-direct, no handler tier** (one small cluster, per the JP A/B and AE M1-3). Round 1: one
**Sonnet** worker runs the systems-design distillation, fed by a **Haiku** doing the fetching — surveying
asdg ch. 11-14 and pulling/verifying the MS-Learn production-reasoning anchors via the connector (real
URLs, no fabrication). The conductor authors `00-overview` + updates SUMMARY. Round 2: four **Sonnet**
lesson-writers (one lesson each) + one **Sonnet** exercises/validator worker, parallel, each briefed with
the three contracts + the M1-3 voice exemplars + the ingredient. The conductor (Opus) runs the Zinsser +
STYLE + STANDARDS review gate on every draft, watches the recurring risks (fourth-wall leaks; any worked
design drifting into a paste-ready reference architecture; any fabricated production number), live-checks
every MS-Learn citation, and reconciles `check_prep.py` v4 so it stays runnable and backward-compatible.

## Open decisions for lock

1. **The reorder M5-before-M4** — confirmed by Ray; logged here, will be noted in build-progress at ship.
2. **The reasoning-to-a-design guardrail** (above) — the call that shapes every worked example.
3. **SPIDER as the construct motion** (the systems-design STAR-L). Recommend yes; it is the ore's native
   framework and maps cleanly onto the Algorithm's construct step.
4. **Four lessons** (scope → justify → production-reasoning → full-run-and-audit) vs a different cut.
   Recommend the four above; they trace the SPIDER motion and end in a full timed walkthrough + audit.
5. **Ore breadth:** pull asdg ch. 11-14 + MS-Learn for the L3 production-reasoning depth (recommended,
   per the blueprint's Ore-to-Module map) vs staying inside the interview-prep chapter.
6. **Worked examples per lesson:** two strong fully-reasoned designs (depth over breadth), ~6 of the 9
   whiteboard exercises across L1-L4, with one built two ways for the thesis. Recommend as scoped.
7. **`check_prep.py` v4 extends in place** with `--module 5` (gap at 4 until M4 ships). Recommend yes,
   consistent with M2/M3.

On lock: the fleet augments the ore + authors M5, VERIFY gates it (voice + claims + grounding + no
reference-architecture drift + live MS-Learn checks + the extended validator runs), BUILD/TEST runs
`mdbook build` + `check_prep.py` v4 + pytest, and the stage stops at `GATE-APPROVE-SHIP` before folding
into `src/` and `exercises/`.
