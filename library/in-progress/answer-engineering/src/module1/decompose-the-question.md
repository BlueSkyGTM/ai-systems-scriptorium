# Decompose the Question

The question arrives and your instinct fires: answer it. That instinct is the problem.

Every interview question is an instrument for a hiring hypothesis. The words the interviewer says are a
proxy; what they are actually collecting is evidence for or against a specific claim about you as a
candidate. Answer the proxy and you may never touch the hypothesis. Answer the hypothesis and the
surface form takes care of itself.

Step one of the Algorithm is the pause that separates those two outcomes.

## What a Question Is Actually Doing

Interviewers do not write questions from scratch. They pull from a signal map: competencies the role
requires, translated into question formats. The question is the instrument; the signal is what it
measures. For an AI Engineering role, that map clusters into four categories.

**Ownership.** Did you drive something, or were you along for it? The hiring hypothesis: does this
candidate take personal responsibility for outcomes, or do they participate and observe? The tell is in
the noun that survives after you strip the framing: "a project you led," "a decision you made," "a
system you built." The first-person subject is not optional.

**Judgment under uncertainty.** Did you make a defensible call with incomplete information? The hiring
hypothesis: can this candidate bound unknowns, name the risk explicitly, and commit to a direction?
These questions almost always contain a constraint, a fork, or a failure: "incomplete information," "two
options," "did not work as expected."

**Technical depth.** Do you know how the thing works, not just that it exists? The hiring hypothesis:
is this candidate's knowledge operational, or is it surface-level familiarity? Depth questions probe
implementation experience, failure modes, and the ability to explain a system at multiple levels of
abstraction. One habit marks the strong answer here: end every deep dive with a sentence on
observability and a sentence on failure modes. It is the single biggest gap between senior and staff
answers.

**Communication and influence.** Can you move people who do not share your technical context? The
hiring hypothesis: can this candidate operate in a real organization, or only within a technical team?
These questions name a stakeholder, a disagreement, or a decision made without authority.

Most questions blend two or more categories. A question about a technical decision you made under time
pressure is simultaneously an ownership question, a judgment question, and a technical depth question.
Your job in decomposition is to find the primary one.

## The Three-Part Move

Decomposition runs in your head before you speak. Three parts, in order.

**Parse the literal components.** Strip the framing words: "tell me about a time when," "walk me
through," "how would you approach." Find the noun and verb and constraint. Take "tell me about a
difficult technical decision you made with incomplete information": the noun is a technical decision,
the verb is made (past tense, real example), the constraint is incomplete information. You now have the
skeleton.

**Assign it to a category.** The incomplete-information constraint points to judgment under uncertainty
as the primary signal. The technical decision adds a technical depth secondary. But the combination
names ownership as the frame: they want to see you owned the call and reasoned through the gap.

**Name the primary hypothesis in one sentence.** What single thing, if demonstrated, would make this a
strong answer? For this question: "I am someone who makes defensible technical calls in ambiguity and
can articulate the reasoning." Everything in your answer is either evidence for that hypothesis or
noise.

## A Worked Decomposition

Question: "When would you choose RAG over fine-tuning, and vice versa?"

Literal parse: "when would you choose" is a forward-looking judgment prompt, not "tell me about a
time." The question names a fork between two technical approaches; there is no behavioral story being
asked for.

Category: judgment under uncertainty is primary (the question is a named tradeoff), with technical
depth as secondary (the interviewer expects you to know the implementation difference between the two).

Primary hypothesis: "This candidate understands the actual decision criteria for RAG versus fine-tuning
and can reason through the tradeoff without hedging."

What does that hypothesis demand? Not a survey of both techniques. Not "it depends" standing alone.
"It depends" earns its place only when you finish the sentence: "it depends on X, Y, Z, and here is how
each changes the answer." Standing alone, it reads as hedging. The hypothesis demands a named framework
for deciding, applied to a concrete case.

The decomposition tells you: lead with the decision criteria, not the technique definitions.

## The AI Systems-Design Variant

AI/ML systems-design questions require one additional decomposition move before you design anything:
surface the production constraints the design must honor.

An open-ended design prompt is never open-ended in practice. "Design a customer support chatbot" has a
volume behind it, a latency budget, a compliance environment, a freshness requirement, and an accuracy
bar. The interviewer has those realities in mind. Your decomposition surfaces them. "Before I sketch the
architecture, I want to clarify: is this optimizing for latency or cost? Are we in a regulated
environment? What is the query volume at peak?"

That move is itself a signal. The Azure Well-Architected Framework's guidance on AI application design
states that before selecting technologies, you must "clearly define the business problem you're
solving," including success metrics, user experience requirements, and regulatory constraints
(learn.microsoft.com/azure/well-architected/ai/application-design). The candidate who asks those
questions before drawing boxes is demonstrating the same discipline the framework mandates for
production AI systems. The candidate who names a stack first is demonstrating they have not shipped one.

## What Decomposition Is Not

Decomposition is not stalling. You are not pausing because you do not know what to say; you are pausing
because the first thing you say should be aimed at the right target. Interviewers read a purposeful
pause correctly when what follows is clearly intentional.

Decomposition is not performing a framework out loud. You are not supposed to say "step one of my
decomposition process." You run the steps internally; the output is a well-aimed answer.

Decomposition is not guaranteed by category alone. Two ownership questions may test very different
hypotheses depending on role level, the company's current priorities, and what the interviewer already
heard from earlier rounds. The category is a starting point; the specific hypothesis requires reading
the specific question.

The most common failure mode in an AI Engineering loop is not a knowledge gap. It is a candidate who
answered the surface of every question and never once named what the interviewer was actually trying to
learn. Decomposition is how you stop doing that.

## Core Concepts

- Every interview question is an instrument for a hiring hypothesis; the surface form and the signal it
  collects are different things, and answering one does not guarantee answering the other.
- The four AI Engineering signal categories are ownership, judgment under uncertainty, technical depth,
  and communication/influence; most questions blend two or more, so the task is to identify the primary
  one.
- Decompose in three moves: parse the literal components (noun, verb, constraint); assign to a signal
  category; name the primary hypothesis in one sentence.
- For AI systems-design questions, add one move before designing: surface the production constraints
  (scale, latency, accuracy bar, compliance); the move is itself evidence of operational experience.

<div class="claude-handoff" data-exercise="exercises/module1/decompose-the-question/">

**Try It in Claude Code:** decompose ten unseen questions from the provided bank through the three-part
process, producing a literal parse, a signal category, and a one-sentence primary hypothesis for each,
then write a calibration pass naming which signal categories you read well and which you misread.

</div>
