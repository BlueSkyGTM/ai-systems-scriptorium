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
      Zinsser: end with a click, the moment the reader didn't quite expect but recognizes as right.
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

## What this is not

Not a layout. Not a word count. It is a discipline. A 90-word lesson and a 900-word lesson both pass if both
are cut to the bone and hold the voice.
