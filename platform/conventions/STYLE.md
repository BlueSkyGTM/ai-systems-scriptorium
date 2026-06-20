# Style Contract

The writing spec for every lesson. Distilled from William Zinsser's *On Writing Well*, treated as an
engineering spec — clutter is a defect, not a style choice. The canonical worked example is `src/preface.md`
+ `src/README.md`. If a draft and this contract disagree, the contract wins.

This is a checklist. Run it on every lesson before it ships.

## 1. Unity (the unifier — never break)

Holds across all lessons. This is what makes 280 lessons from 9 sources read as one book.

- [ ] **Pronoun:** second person. "You build the retriever." Never "we," never "the student."
- [ ] **Tense:** present. "The agent reads state." Not "will read" / "would read."
- [ ] **Point of view:** the practitioner doing the work, now.
- [ ] **Mood:** one voice — confident, blunt, opinionated. A narrator with a stake, not neutral gray.

## 2. Simplicity — cut the clutter

- [ ] Strip every sentence to its cleanest components. If a word earns nothing, delete it.
- [ ] **Kill qualifiers:** very, rather, quite, pretty, somewhat, really, basically, actually, just.
- [ ] **Kill dead adverbs** that repeat the verb (*shouted loudly*, *gather together*).
- [ ] **Kill jargon and inflation:** "in order to" → "to"; "utilize" → "use"; "leverage" → "use"; "facilitate"
      → "help"; "at this point in time" → "now". No `-ize` coinages.
- [ ] **Active voice.** "The gateway routes the request," not "the request is routed by the gateway."
- [ ] **Concrete nouns, active verbs.** Show the thing doing the thing.

## 3. One idea per lesson

- [ ] A lesson teaches one concept and answers one question. If it needs two, it's two lessons.
- [ ] One thought per paragraph. A new idea starts a new paragraph.

## 4. The lead and the ending

- [ ] **Lead (1–2 sentences):** the problem, and why a seam engineer needs this. The first sentence's only
      job is to make the reader read the second. No throat-clearing, no "In this lesson we will…".
- [ ] **Ending — the seam line:** one sentence on what this means for an AI Platform Engineer. Then stop.
      Zinsser: end with a click, the moment the reader didn't quite expect but recognizes as right. **Vary the
      shape** — a consequence, a warning, a cost, a reframe, a question answered — and never reuse a fixed
      template (see §8). The "An AI Platform Engineer who…" opener is banned as a default; earn the ending fresh.
- [ ] **Then the handoff:** the copy-button block that hands the work to Claude Code.

## 5. Core concepts (the retention hook)

Every lesson ends by naming its **core concepts** — the 1–4 testable ideas it actually teaches. Not the
topic, the *claims*: one sentence each, in the lesson's voice, that a learner should recall and apply cold.

- State them as **propositions, not terms.** "The agent loop adds a stop condition and turn budget a chatbot
  lacks," not "the agent loop."
- 1–4 per lesson. If you can't write them in one line each, the lesson isn't focused enough — go back to §3.
- These feed the spaced-repetition layer (one card per concept) and double as the reader's recap.

Emit them as a `## Core concepts` section (a short list) just before the Claude Code handoff.

## 6. Visuals earn their place

- [ ] A diagram must *replace* words, not decorate them. Keep the DAG, pipeline, or architecture that carries
      information prose can't. Cut the picture that only impresses.

## 7. The Zinsser pass (mandatory rewrite — rewriting is the method)

No lesson ships on its first draft. After drafting, run this pass:

1. Cut **15–25%** of the words. The first draft is always too long.
2. Delete every qualifier and dead adverb (§2).
3. Convert passive → active.
4. Check unity: one pronoun, one tense, one POV, start to end (§1).
5. Confirm the lead grabs and the ending lands (§4).
6. Read it aloud. If you stumble, the reader will too. Fix the stumble.

## 8. Variety — don't go mechanical (Zinsser's caution)

Clarity is the goal; monotony is the failure mode it slips into. Short, clean sentences are the default — but a
whole lesson of identical short em-dash declaratives is its own kind of clutter, and an identical ending across
every lesson tells the reader a template wrote it, not a person.

- [ ] **Vary the rhythm.** Mix sentence lengths. Let one longer, breathing sentence carry a complex idea, then
      cut back to short. A drumbeat of `X is Y. Do Z. Never W.` fatigues the reader; break it on purpose.
- [ ] **No template endings.** Rotate the seam line's shape (see §4). If you can predict a lesson's last
      sentence from its first, rewrite it.
- [ ] **Let the writer show.** A dry aside, an unexpected turn, one flash of earned opinion — Zinsser's
      "warmth." The voice is blunt and confident, not robotic. Aim for one genuinely human moment per lesson.
- [ ] **Respect the reader's stamina.** When names and acronyms stack up (MemGPT → Letta → Mem0 → Voyager),
      slow down: gloss, group, or cut. A parade the reader can't hold is lost on them.

This section is the polish layer, not the foundation (§§1–4 come first). But it is the difference between prose
that is correct and prose that is alive — and for a book that invokes Zinsser by name, it has to be alive.

## 9. Headings — Title Case

One convention, applied everywhere: **Title Case** for every heading (H1 page titles, H2/H3 sections)
*and* every `SUMMARY.md` table-of-contents label. Capitalize every **major** word; lowercase the minor
words — articles (a, an, the), coordinating conjunctions (and, but, or, nor, for, so, yet), and short
prepositions (of, to, in, on, at, by, for, with, from, …) — except the first and last word.

- [ ] **Preserve proper nouns, acronyms, and code identifiers exactly.** Rust, TypeScript, Docling, MCP,
      RAG, LLMOps, FinOps, DevOps, K8s, A2A, HITL, KV-Cache, A/B — these keep their own casing.
- [ ] **Hyphenated compounds:** capitalize the first and last element; lowercase a minor word in the middle.
      "The Day-One Stack", "Issue-to-PR", "Chain-of-Thought", "SRE-for-AI", "In-Context".
- [ ] **Consistency is the point.** Every heading and ToC label reads the same way — no sentence-case /
      Title-Case mix. The handoff CTA (**Build It / Inspect It / Try It in Claude Code**) is title case like
      everything else; the `Exercise · <path>` tag (injected by `theme/copy-to-claude.js`) keeps each
      handoff block self-evidently distinct.

The conversion that establishes this lives at `build-log/caps-sweep-title.py` (fence-aware, proper-noun- and
acronym-guarded, caps the first/last of hyphen compounds); re-run after a bulk authoring pass to catch drift.

## What this is not

Not a layout. Not a word count. It is a discipline. A 90-word lesson and a 900-word lesson both pass if both
are cut to the bone and hold the voice.
