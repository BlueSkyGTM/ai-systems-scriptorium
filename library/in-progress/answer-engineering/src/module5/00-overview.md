# Module 5: AI/ML Systems-Design Interviews

The systems-design round is the one most AI engineers walk into underprepared, because it is open-ended
on purpose. There is no single right answer, the prompt is deliberately vague, and the whiteboard is
empty. That emptiness is the test. The interviewer wants to watch you impose structure on an ambiguous
problem under a clock, and to hear whether the structure you impose is the structure of someone who has
run a system in production or the structure of someone who has only read about one.

This is where the Sans Python portfolio pays off, and where it can also let you down. You have built
real systems. The risk is that you walk in and reach for a reference architecture you half-remember,
draw the boxes everyone draws, and never say the one thing that separates a strong design from a
diagram: why. Why this component and not the cheaper one, why this retrieval strategy at this scale,
what breaks first, what it costs, how you would know it was working. The reasoning is the signal. The
diagram is just where the reasoning leaves its marks.

## What the Interviewer Is Actually Evaluating

A systems-design round is not testing whether you can name the parts of a RAG pipeline. It is testing
production judgment: whether you scope before you build, whether every box you draw is a choice you can
defend, and whether you reason about cost, latency, reliability, and evaluation the way someone does
who has been paged at 2am when one of them failed. A textbook-correct architecture with no production
reasoning scores lower than a simpler design whose every tradeoff is named out loud.

## The Algorithm, Under a Clock

The four-step Algorithm still runs here: decompose the prompt, identify the signal, construct the
answer, stress-test it. What changes is the construct step. For a 45-minute open-ended design, you need
a motion that fits the clock, and this module uses the one the field already has a name for: SPIDER.
Scope and clarify, Prioritize requirements, draw the Initial architecture, Deep-dive the critical
paths, Evaluate and observe, and address Reliability and scale. SPIDER is to a design answer what
STAR-L was to a behavioral one: the domain-specific shape the construct step takes. You run it, you do
not recite it.

## How to Read a Worked Design

Every worked design in this module runs the full reasoning: the prompt, the scoping that turns it from
vague to bounded, the components drawn with each choice justified, and the stress-test that finds what
breaks. Read each one for the reasoning, not the diagram. The failure mode of design prep is the same
as behavioral prep in a different costume: memorizing a reference architecture and drawing it on every
prompt. A memorized architecture survives exactly until the interviewer changes the scale or the
constraint, which they will. The designs here are demonstrations of how to think to a design, run on
real prompts, so you can run the same thinking on a prompt you have never seen.

## The Four Lessons

1. **Reading the Design Prompt** builds the scoping discipline: how to turn an open-ended prompt into a
   bounded problem before you draw anything, and why the candidate who scopes beats the one who designs
   blind.
2. **Justify Every Box** is the construct step at depth: drawing a design where every component is a
   choice you can defend with production reasoning, not vocabulary.
3. **Production Reasoning as the Differentiator** is the staff signal: threading cost, latency,
   reliability, and evaluation through a design, and naming the tradeoff when two of them conflict.
4. **The Full Design Under Pressure** runs one complete design end to end on the clock, then turns the
   weak-design audit on it the way Module 2 turned the weak-answer audit on a behavioral story.

## What This Module Feeds Forward

By the end you have a systems-design log in your prep dossier: at least one open-ended prompt taken all
the way through the Algorithm and SPIDER, with the design justified, the four production-reasoning
pillars threaded, and a weak-design audit on your own work. That log is the artifact you rehearse from
before a design round, and the portfolio module ahead builds directly on it: the systems you designed
on paper here are the systems you will walk an interviewer through there.
