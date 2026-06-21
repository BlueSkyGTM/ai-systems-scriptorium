# Module 1 Dossier — Answer Engineering

Source ore: `vault/ai-system-design-guide/00-interview-prep/` (8 files, Q1-Q116 question
bank plus frameworks, pitfalls, behavioral, whiteboard exercises, job-market trends, FAQ).

Distilled ingredients: `ingredients/source/answer-engineering/asdg-question-taxonomy.md`
and `ingredients/source/answer-engineering/asdg-interview-frameworks.md`.

This dossier rules on what of the ore belongs in M1 vs. what is held for later modules.
Format mirrors `ingredients/dossiers/module4.md`.

---

## What M1 Is

M1 installs the Algorithm: the four-step internal reasoning process (decompose the question,
identify the signal, construct the answer, stress-test it) that lets a candidate answer
questions they have never seen. The two draft lessons in `library/in-progress/answer-engineering/draft/`
cover steps 1-2 (decompose + signal) and step 3 (construct), with step 4 (stress-test)
folded into Lesson 2 as the final check. M2 goes deeper on each step.

M1's job with the ore is to provide enough grounded material to make the framework
concrete -- real questions to decompose, real frameworks to use for construction, real
pitfalls to run as stress-tests. It does NOT exhaust the ore. The ore is too wide for one
module and is deliberately held in layers.

---

## Keep / Cut / Hold Table

| Ore section | M1 ruling | Destination | Reason |
|-------------|-----------|-------------|--------|
| Q1-Q49 (foundational question bank: RAG, Agentic, Model Selection, Optimization, Evaluation, Production, Tooling, Ensemble) | **HOLD for later** -- select 4-6 as worked decomposition examples | M1: 4-6 as in-lesson examples only; M5: full systems-design bank | M1 needs examples, not the full bank; dumping 49 questions into M1 inverts the blueprint thesis (the book argues against memorization) |
| Q50-Q116 (advanced: December 2025 through June 2026) | **HOLD** | M5 (systems-design interview) and M7 (example bank) | Staff-level material; M1's reader is establishing the framework, not running the advanced set |
| System Design Scenarios (5 walkthroughs: customer support chatbot, document processing, enterprise RAG, code assistant, content moderation) | **HOLD** | M5 | These are full 35-minute walkthroughs; M1 does not have room and they belong in the systems-design module |
| 02-answer-frameworks: SPIDER full definition + time budget | **KEEP for M1 Lesson 2** | `asdg-interview-frameworks.md` already distilled; lesson-author uses ingredient | SPIDER is the construction scaffold for design questions; Lesson 2 names it explicitly |
| 02-answer-frameworks: SPIDER 45-minute worked transcript | **KEEP gist for M1 Lesson 2** | Condensed in `asdg-interview-frameworks.md`; do NOT reproduce full transcript in lesson | The gist (the five moves the transcript demonstrates) is lesson material; the full transcript is M5 material |
| 02-answer-frameworks: ETA, tradeoff, debugging frameworks | **KEEP for M1 Lesson 2** | Distilled in `asdg-interview-frameworks.md` | These are construction tools Lesson 2 names by type ("for a concept question, use ETA; for a design question, use SPIDER") |
| 02-answer-frameworks: STAR-L definition and examples | **KEEP for M1 Lesson 2** | Distilled in ingredient | STAR-L is the behavioral construction scaffold; Lesson 2 references it as the tool for behavioral questions |
| 03-common-pitfalls: architecture pitfalls (Pitfalls 1-5) | **KEEP for M1 Lesson 2** (as stress-test material) | Distilled in `asdg-interview-frameworks.md` pitfalls catalog | The pitfalls feed step 4 (stress-test) and the "could a weak candidate give this answer?" check |
| 03-common-pitfalls: AI-specific pitfalls (Pitfalls 18-20) | **KEEP for M1 Lesson 2** (stress-test) | Distilled in ingredient | Same reason; these are the most differentiating failures at the senior level |
| 03-common-pitfalls: five named prompt failure modes | **KEEP for M1 Lesson 2** | Distilled in ingredient | The ore explicitly says naming 2-3 of these unprompted moves an answer from junior to senior; M1 should teach the habit |
| 03-common-pitfalls: communication pitfalls (Pitfalls 11-14) | **KEEP for M1, not just Lesson 2** | Lesson 1 (decomposition includes the check-in move) and Lesson 2 (structure your answer before speaking) | Communication pitfalls span both lessons |
| 05-behavioral: six STAR-L worked examples | **KEEP 3 for M1** (Examples 1, 5, 6) | `asdg-question-taxonomy.md` has skeletons; M3 gets the full bank | Examples 1 (ambiguity), 5 (being wrong), 6 (concern dismissed) are the three most load-bearing for teaching the Algorithm; Examples 2-4 are M3 behavioral bank material |
| 05-behavioral: Practicing Out Loud section | **HOLD** | M7 (deliberate practice) | This is a practice methodology, not an Algorithm-installation lesson |
| 05-behavioral: Questions to Ask Your Interviewers; Red Flags | **HOLD** | M8 (hiring loop end-to-end) | Loop logistics, not framework installation |
| 05-behavioral: Compensation and Leveling questions | **HOLD** | M8 | Recruiting logistics |
| 04-whiteboard-exercises (9 exercises) | **HOLD** | M5 | These are the simulation medium for the systems-design module |
| 06-job-market-trends-2026 | **HOLD** | M8 (end-to-end loop) or standalone appendix | Hiring landscape, not framework; adds context but not the Algorithm |
| 07-faq | **HOLD** | M5 and M7 reference material | Short-answer Q&A belongs in the example bank and reference, not the framework module |
| 01-question-bank: Q1, Q2, Q5, Q11, Q27, Q55 (selected for diversity across categories) | **USE in M1 lessons** | Lesson 1 worked examples (decomposition) and Lesson 2 worked examples (construction) | These 6 cover: RAG design (technical depth), RAG vs fine-tuning (judgment), evaluation (ownership), agent vs workflow (technical depth), no-ground-truth eval (technical depth), RAG test-to-production failure (debugging/judgment). They touch all four signal categories with minimal overlap. |

---

## Three-Source Rule Status for M1

Per PLAN.md locked decision: M1 runs three sources.

| Source | What it provides | Status |
|--------|-----------------|--------|
| Distilled ingredient (`ingredients/source/answer-engineering/`) | Real questions per signal category; five named frameworks; pitfalls catalog; three STAR-L skeletons | Produced by this distillation pass; ready |
| MS Learn connector (Azure AI Foundry, Well-Architected Framework for AI workloads) | Grounds the "AI systems-design decomposition move" (surface production constraints before designing) -- the lesson cites a real URL, not a marker | Worker must USE the connector inline per PLAN.md; do not leave `[MS-Learn: ...]` unresolved |
| Editorial seam framing | "Why does a Production AI Engineer need this?" anchor in every lesson lead | Conductor authors this; it connects the Algorithm to the portfolio-as-resume thesis |

---

## Module Map Summary (what M1 teaches vs holds)

M1 scope: the Algorithm's structure + enough grounded examples to install it. Two lessons.
- Lesson 1 (decompose): four signal categories with definitions and representative questions;
  the three-part decomposition move; the systems-design variant (surface production constraints
  first); 2-3 worked question decompositions drawn from the ingredient.
- Lesson 2 (construct): the three construction properties (specific, structured, complete);
  the five frameworks as construction tools (SPIDER for design, ETA for concept, tradeoff for
  comparison, debugging for troubleshooting, STAR-L for behavioral); 2-3 worked construction
  examples including one behavioral STAR-L; the stress-test check; pitfalls as stress-test
  inputs.

M3 holds: full behavioral bank (all 6 STAR-L examples + question categories from asdg 05);
  ownership/communication question deep bank; the Practicing Out Loud practice guide.

M5 holds: systems-design question bank (Q1-Q116 for selection); 9 whiteboard exercises;
  full SPIDER transcript from the ore; 5 design-scenario walkthroughs; grounding on Azure AI
  Foundry and Well-Architected Framework (more depth than M1's introductory citation).

M6 holds: portfolio-narrative material; how to walk an interviewer through a real artifact.

M7 holds: full example bank in rotation format; deliberate practice guide from asdg 05.

M8 holds: job market trends (asdg 06); loop logistics; compensation and leveling questions.

---

## Framing Judgment Calls (for conductor review)

1. **Step 4 (stress-test) is folded into Lesson 2, not a standalone lesson.** The draft
   lesson `02-signal-to-answer.md` already contains the stress-test as the final check in
   the construction move ("could a weak candidate give this answer?"). The PLAN.md confirms
   M2 deepens each step; M1 introduces all four without full treatment. This is the right
   cut: stress-test without construction context is not teachable.

2. **Three STAR-L examples selected rather than all six.** Examples 1, 5, and 6 were chosen
   because they are the hardest and most differentiating: ambiguity (primary judgment),
   being-wrong (primary ownership), and concern-dismissed (primary communication/influence).
   Examples 2-4 (production failure, ethical concern, cross-functional collaboration) are
   all strong and belong in M3's behavioral bank where they get full treatment. The selection
   is a judgment call; no ore was fabricated.

3. **The ore's behavioral section (asdg 05) uses "STAR-L" as its named framework.** The
   draft lessons and blueprint use the same name. This is not a collision; the ore coined the
   name and the book inherits it. The ingredient file preserves the source attribution.

4. **The question bank (Q1-Q116) is deliberately NOT reproduced in M1.** The blueprint
   thesis is that memorization fails; dumping the bank into Module 1 would contradict the
   book's argument. M1 uses 4-6 questions as decomposition/construction examples only. The
   full bank is M7's example-bank-in-rotation module. This is a framing decision, not a
   coverage decision.

5. **June 2026 model prices and names (Claude Sonnet 4.6, Claude Fable 5, GPT-5.5, Gemini
   3.1 Pro, DeepSeek V4 Flash) appear in the ore as current.** The ingredient files preserve
   them verbatim for accuracy. Lesson authors should not update them from memory; they should
   use what the ore states and note "verify current" per the ore's own practice.
