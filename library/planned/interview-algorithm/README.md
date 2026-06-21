# Algorithmic Interviewing — Blueprint

## Positioning

Every other Scriptorium book builds production AI engineering skill. This one teaches the reader
to prove it in a hiring loop. The relationship is deliberate: you interview ON the Sans Python
portfolio. The terminal coding agent, the governed fleet, the M8 exam system — those are not
exercises to discard; they are the resume. This book is the bridge between having built something
real and being able to explain it under pressure to someone who did not see you build it.

The two books work concurrently or in sequence. A reader mid-way through Sans Python can start
this book immediately; a reader who finished Sans Python already has the artifacts and can treat
this as the final unlock.

## Thesis

Most interview prep teaches memorization: stock answers, the STAR template filled in, a list of
company-specific talking points rehearsed until they feel fluent. That approach breaks the moment
a question arrives in a form that was never explicitly covered.

This book teaches a different thing: an internal Algorithm. Not a script, not a lookup table, but
a transferable reasoning process that the reader can apply to any behavioral question, any
technical screen, any AI systems-design prompt. The goal is a candidate who can answer what was
never covered, because they understand WHY excellent answers are excellent: what signal the
interviewer is actually collecting, what gap a weak answer exposes, and how to construct a
response that demonstrates real production thinking.

The framework is the core artifact. The large bank of worked examples exists to load the
framework into intuition: the reader sees the algorithm applied enough times that it becomes
automatic, not effortful.

## Scope

**IN:**

- The reasoning framework itself: the internal algorithm for decomposing an interview question,
  identifying the underlying signal, and constructing an answer that demonstrates it
- Behavioral interview preparation: STAR as a tool, not a template; situational variants; the
  signal map for standard behavioral categories (ownership, conflict, failure, influence)
- Technical interview preparation: live coding under time pressure, the communication layer,
  how to think out loud without losing the thread
- AI/ML systems-design interview: how to approach an open-ended design prompt, what the
  interviewer is evaluating, how to anchor your answer in production reasoning rather than
  textbook architecture [MS-Learn: Azure AI Well-Architected Framework]
- The portfolio-as-resume: how to walk through a Sans Python artifact in an interview,
  what to emphasize, how to connect it to the role's scope
- Worked examples: a large, classified bank of questions with full algorithm walkthroughs
- Candidate tasks: practice exercises that build the reasoning habit, not trivia recall

**DELIBERATELY OUT:**

- Rote question dumps with canned answers (this is the thing the book argues against)
- Company-specific trivia (which PM runs which team, exact tech stacks of target employers)
- LeetCode grinding as a primary strategy; competitive-programming contest prep
- Salary negotiation, offer comparison, recruiting logistics (adjacent, not in scope)

## Ore to Module Map

Primary ore: `vault/ai-system-design-guide` (prefix `asdg`), specifically:

| Ore Source | What It Feeds |
|---|---|
| `asdg` ch. `00-interview-prep/` (8 files) | The example bank; interview question taxonomy; behavioral + technical + systems-design worked examples |
| `asdg` ch. `11–14` (infrastructure, security, reliability, eval) | AI/ML systems-design interview depth; production reasoning anchors |
| `asdg` ch. `15–17` (design patterns, case studies, tool use) | Systems-design interview: how to pattern-match real architectures |
| `asdg` `COURSES.md` | Portfolio-narrative appendix; learning-path credibility signals |
| `asdg` `GLOSSARY.md` | Vocabulary for technical precision in interviews |

The `asdg` interview prep chapter was extracted but held out of Sans Python's curriculum
(routed as "Ahab"). That material is the raw ore for the example bank here. It does not
arrive pre-framed; the distillation work is to impose the Algorithm framework on it.

## Proposed Curriculum Arc

Eight modules, three phases: Framework first, then example banks by interview type, then the
portfolio layer.

**Phase 1: The Framework**

- Module 1: Why Memorization Fails — the problem the book solves; what interviewers actually
  evaluate; introducing the Algorithm and its four steps
- Module 2: The Algorithm in Detail — decompose the question, identify the signal, construct the
  answer, stress-test it; the internal monologue made explicit

**Phase 2: Example Banks by Interview Type**

- Module 3: Behavioral Interviews — the signal map for standard categories (ownership, conflict,
  failure, technical influence); worked examples; candidate tasks
- Module 4: Technical Screens — live coding communication layer; how to narrate your reasoning;
  worked examples from AI engineering screens (not LeetCode for its own sake)
- Module 5: AI/ML Systems-Design Interviews — how to read an open-ended design prompt; the
  "draw the box, justify every box" discipline under time pressure; production reasoning as
  differentiator [MS-Learn: Azure AI Foundry, Well-Architected Framework for AI workloads];
  worked examples at the level of the M7/M8 artifacts

**Phase 3: The Portfolio Layer**

- Module 6: The Sans Python Portfolio as Resume — walking an interviewer through a real artifact;
  what to foreground (decision-making, trade-offs, failure modes) vs. what to skip; tailoring
  the narrative to the role's scope
- Module 7: Live Practice and Calibration — the example bank in full; a structured self-review
  rubric; how to run deliberate practice (algorithm application, not rote repetition)
- Module 8: The Hiring Loop End-to-End — sequencing the preparation; what to do differently at
  each interview stage (recruiter screen, hiring-manager, technical, panel); closing the loop

## The Artifact Strategy

Sans Python's proof mechanism is code: every module ends in a runnable artifact the reader
committed, evaluated, and debugged. The artifact is both the learning object and the portfolio
item.

This book adapts that strategy to a career artifact. The reader's runnable proof is:

1. A personal instance of the framework, annotated with their own examples from the Sans Python
   portfolio (Module 6/7 task: write your own algorithm walkthrough for each of your M6/M7/M8
   artifacts, on paper, timed)
2. A portfolio narrative document: a structured, written walkthrough of at least one major
   artifact, interview-ready, peer-reviewable, and stored in the repository alongside the
   artifact itself
3. Deliberate-practice logs: scored repetitions of algorithm application across the example
   bank, tracking which signal categories the reader is consistently strong on and which need
   more reps

These are not creative-writing exercises. They are the same discipline as the M8 exam: a
concrete output the reader can evaluate against a rubric, not a feeling of readiness.

## Dual-Use Note

Like every Scriptorium book, this one is written to be read by a human learner and ingested
by an LLM coaching session. The algorithm structure is especially legible to both: a reader
can internalize it step by step; an LLM can use the worked examples as a rubric for evaluating
practice answers. A coaching session that loads the framework chapter and the relevant example
bank can give structured feedback on any practice answer, without hallucinating criteria.

## Candidate Names (GATE-NAME-BOOK)

The final title is a human decision at `GATE-NAME-BOOK`. Three candidates follow.

**Lead candidate: Algorithmic Interviewing**

Reframes the interview as a problem-solving domain rather than a performance domain.
"Algorithmic" signals engineering and precision; it describes the book's central
contribution — a transferable reasoning algorithm, not a script — while remaining
readable to non-engineers. Short, distinctive, and clear of the "guide" / "handbook" /
"prep" cluster that saturates the category.

**Candidate 2: Answer Architecture**

Foregrounds the structural, engineering-minded approach to constructing answers. Works well
as a subtitle companion (e.g. "Answer Architecture: The AI Engineer's Interview Framework").
Slightly softer signal on the AI Engineering angle than the lead candidate.

**Candidate 3: Interview Algorithm**

The original working title. Accurate and precise; reads slightly more like an internal
project name than a book cover. Retains value as a subtitle or module name. Better
suited as the framework's name inside the book than as the cover identity.
