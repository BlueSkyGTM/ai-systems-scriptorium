# Decompose the Question

The question arrives. You hear the words. Your instinct is to answer.

That instinct is the problem.

The instinct pulls you toward the surface form: the words the interviewer said, the topic they
named, the example they asked for. But the surface form is a proxy. Behind every interview
question is a hiring hypothesis: something the interviewer is trying to confirm or disconfirm
about you as a candidate. Answer the proxy, and you may miss the hypothesis entirely. Answer
the hypothesis, and the surface form takes care of itself.

Step one of the Algorithm is to pause long enough to do one thing: separate what the question
says from what the question is for.

## The Signal Behind the Question

Interviewers do not design questions from scratch. They pull from a signal map: a set of
competencies the role requires, translated into question formats. The question is the
instrument; the signal is what it measures.

For an AI Engineering role, the signal map clusters into four categories.

**Ownership signals.** Did you drive something, or were you along for it? Questions in this
category ask about a project, a decision, a system you built. The hypothesis being tested:
does this candidate take responsibility for outcomes, or do they participate and observe?

**Judgment under uncertainty signals.** Did you make a defensible decision with incomplete
information? Questions here name a tradeoff, a constraint, or a failure. The hypothesis: can
this candidate reason through ambiguity, or do they require certainty before acting?

**Technical depth signals.** Do you know how the thing works, not just that it exists?
Questions probe your implementation experience, your knowledge of failure modes, your ability
to explain a system at multiple levels of abstraction. The hypothesis: is this candidate's
knowledge operational, or is it surface-level familiarity?

**Communication and influence signals.** Can you move people who do not share your technical
context? Questions here name a stakeholder, a disagreement, a decision made without authority.
The hypothesis: can this candidate operate in a real organization, or only within a technical
team?

Most questions test more than one signal. A question about a system design decision you made
under time pressure is simultaneously an ownership signal, a judgment signal, and a technical
depth signal. Your job in decomposition is to identify which signal is primary.

## How to Decompose

Decomposition is a three-part move, and it runs in your head before you speak.

**Part 1: Parse the literal components.** What is the question actually naming? Strip the
framing words ("tell me about a time when," "walk me through how you would") and find the
noun and verb: "a time you made a technical decision with limited data." Noun: a technical
decision. Verb: made (past tense, real example). Constraint: limited data. You now have the
skeleton.

**Part 2: Assign it to a category.** Which signal category does it belong to? The limited-data
constraint is a judgment-under-uncertainty signal. Technical decision is a technical depth
signal. The combination is ownership plus judgment: they want to see you owned the call and
reasoned through the gap.

**Part 3: Name the primary hypothesis.** What single thing, if demonstrated, would make this a
strong answer? For this question: "I am someone who makes defensible technical calls in
ambiguity and can articulate the reasoning." Everything in your answer is either evidence for
that hypothesis or noise.

## A Worked Example

Question: "How would you approach evaluating the quality of an LLM-powered feature before
shipping it?"

Literal parse: evaluation approach, LLM feature, pre-ship. The verb is "how would you" (not
"tell me about a time"), so this is a forward-looking technical question, not a behavioral one.

Category: technical depth, with a secondary ownership signal (what is your standard? do you
have one?).

Primary hypothesis: "This candidate knows what production-quality evaluation actually looks
like; they have a framework, not a vague intention to test."

What does that hypothesis demand from an answer? Specificity: named techniques, not "I would
run tests." A framework: some structure that shows the answer is systematic, not improvised.
Production grounding: the framing should reflect real constraints (cost, latency, coverage),
not a research paper.

Notice what the hypothesis does not demand: a comprehensive survey of every evaluation
technique that exists. The question is not testing your survey coverage. It is testing whether
you have a real framework. An answer that names LLM-as-judge, the RAG triad (context
relevance, groundedness, answer relevance), and calibration against human labels is stronger
than an answer that names ten techniques shallowly.

The decomposition told you: depth on a real framework beats breadth on every framework.

## The AI Systems Design Variant

AI/ML systems-design interview questions require one additional decomposition move: identify
the production constraint that the design must honor. An open-ended design prompt ("design a
retrieval-augmented generation system for a customer-support product") is never open-ended in
practice. The interviewer has a set of production realities in mind: latency budget, cost per
query, freshness requirements, failure mode tolerance, compliance constraints.

Your decomposition surfaces those constraints before you design anything. "Before I sketch the
architecture, I want to clarify: is this optimizing for latency or cost? Are we in a regulated
environment?" That move is itself signal. It demonstrates judgment: the candidate who asks
about constraints before drawing boxes is the candidate who has shipped production systems
[MS-Learn: Azure AI Foundry, Well-Architected Framework for AI Workloads].

## What Decomposition Is Not

Decomposition is not stalling. You are not pausing because you do not know what to say. You
are pausing because the first thing you say should be aimed at the right target. Interviewers
read the pause correctly when what follows is clearly purposeful.

Decomposition is not performing a framework. You are not supposed to say "step one of my
framework." You are supposed to think through the steps and then answer. The internal process
is invisible; the output is a well-aimed answer.

Decomposition is not guaranteed by the question's category. Two questions that are both
"ownership" questions may test very different hypotheses depending on the role level, the
company's current priorities, and what the interviewer already heard in earlier rounds. The
category is a starting point; the hypothesis requires reading the specific question.

## Core Concepts

- Every interview question is an instrument for a hiring hypothesis; the surface form of the
  question and the signal it collects are different things.
- The four AI Engineering signal categories: ownership, judgment under uncertainty, technical
  depth, and communication/influence; most questions blend two or more, so identify the
  primary one.
- Decompose in three moves: parse the literal components, assign to a category, name the
  primary hypothesis.
- For AI systems-design questions, add one move: surface the production constraints before
  designing anything; the move is itself a signal of operational experience.
- Breadth without a hypothesis is noise; a focused answer aimed at the primary signal
  outperforms a comprehensive survey aimed at nothing.

<div class="claude-handoff" data-exercise="draft/exercises/01-question-decomposition/">

**Build It in Claude Code**: Work through ten unseen interview questions using the three-part
decomposition process. For each: parse the literal components, assign to a signal category,
name the primary hypothesis in one sentence. Then compare your decompositions against the
provided rubric to calibrate your signal-reading.

</div>
