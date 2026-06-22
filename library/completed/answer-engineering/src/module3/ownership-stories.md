# Ownership Stories

The interviewer running a behavioral round is settling one question before any other: can I trust this
person with an outcome? Ownership stories are the evidence they read.

## The Signal and the Hypothesis

Every question in this category tests the same hypothesis: did this candidate drive something, or did
they watch someone else drive it? The interviewer is not looking for a record of participation. They
are looking for an "I" behind a decision, a build, or a result, and they will read your pronouns to
find it.

The canonical failure mode is the "we" answer. "We explored three approaches." "The team shipped in
six weeks." None of these let the interviewer locate your contribution. "We" is a place to hide. An
ownership answer replaces it: "I interviewed five stakeholders and found the common thread." "I wrote
the memo." "I built the three prototypes."

Four failure modes define the category:

**The "we" answer.** The candidate narrates a team outcome without naming their own action. The
interviewer cannot score ownership because none is visible.

**Blaming others.** "Management changed scope at the last minute." This may be factually true and is
fatal regardless. Ownership means describing what you did inside the constraint, not the constraint
that made it hard.

**Activity without result.** The candidate describes what they built but not what changed. The Result
and Learning steps are where ownership lands; an answer that stops at Action is half-built.

**Vague or inflated claims.** "I led the AI initiative" with no project, no timeline, no number. The
stress-test for an ownership answer is specificity no weak candidate could invent.

## Worked Example One: Driving a Decision Under Ambiguity

**The question:** "Tell me about a time you started an AI project with unclear requirements."

### Decompose First

The signal: ownership under uncertainty. The hypothesis: does this candidate make progress when the
path is unclear, or do they wait for clarity they cannot have? What the hypothesis requires as
evidence: a real project with actual ambiguity, the specific move the candidate made to resolve it,
and a result that shows the resolution worked.

### Construct the STAR-L

Take a candidate who joins a project with three stakeholders pulling in three directions. Sales wants
what they call "magic search." Engineering wants a scoped deliverable. Leadership wants
differentiation from competitors. The candidate is the tech lead.

The weak version: "I ran stakeholder interviews and we aligned on a direction. We shipped the MVP in
six weeks." That describes the shape of the work without showing any reasoning. The interviewer learns
nothing about judgment.

The strong construction builds toward the evidence the hypothesis requires.

The candidate interviews five stakeholders one by one. What they find: all three factions share one
concern, time to answer. Sales calls it "magic" because customers spend twenty minutes finding
something that should take two. Engineering calls it "scope" because they need an estimable
deliverable. Leadership calls it "differentiation" because competitors do not solve this either.

That thread becomes the anchor. The candidate builds three rapid prototypes: keyword ranking, semantic
search using embeddings, and conversational RAG. Each is demoed with real queries from support logs,
with actual performance numbers and cost attached. Semantic search answers faster and fits the quarter.

Semantic search ships in six weeks. User time-to-answer drops forty percent. That result clears
buy-in for phase two.

The Learning step: prototyping with real tradeoffs visible moves a stalled conversation faster than
any abstract proposal. The candidate now starts every ambiguous project with a prototype pass, not a
requirements document.

### The Stress-Test

Could a weak candidate give this same answer? No, because of three specifics: the thread found across
all five stakeholders, the three prototype levels against real support queries, and the forty percent
drop. Remove any of those and the answer goes generic. They are the proof the candidate did the work.

Note what "I" does in this construction. The candidate interviewed. The candidate found the thread.
The candidate built and demoed the prototypes. The team shipped together, but the decisions belong to
one person. That is the "I" discipline under pressure.

## Worked Example Two: Owning the Call and the Walkback

**The question:** "Tell me about a time you strongly advocated for a technical decision that turned
out to be wrong."

### Decompose First

The signal is ownership with two layers. First: did the candidate advocate with real conviction, or
did they hedge from the start? Second, and more important: when the decision failed, did they own it,
or did they let someone else surface the problem?

The evidence required: a real decision, real conviction, a real failure with numbers, and a clear
record of the candidate naming the failure themselves rather than waiting to be caught.

### Construct the STAR-L

Take a candidate who campaigns to replace a retrieval pipeline with a pure long-context approach. Not
a suggestion: two design reviews, sustained argument, and enough conviction that the team commits a
quarter of migration work partly on the candidate's recommendation. The Situation is that the
candidate believed this most. That matters. The interviewer needs to see real skin in the call.

Eval results come back. Quality matches the old system. Cost runs four times the projection. Cache hit
rates collapse under actual update frequency; P95 latency doubles. Both assumptions the pitch relied
on fail in production.

Here is where ownership separates from description. The candidate's first instinct is to tune out of
it. Two weeks of marginal gains later, they write a one-page memo: not a Slack message, not a hallway
word, a memo with the numbers, stating plainly that the recommendation was wrong on the economics.
They propose a hybrid: long-context for small static corpora, retrieval for everything else, and
present it to the same audience they originally convinced.

The hybrid ships. About sixty percent of the migration work is salvaged. The postmortem produces a
team rule: any architecture pitch must include a cost model under realistic update patterns.

The Learning step: the candidate attaches explicit kill criteria to their own proposals going forward,
so walking back is a checkpoint in the process rather than a public admission.

### The Stress-Test

The specifics that make this unfakeable: two design reviews, a quarter committed, four times the
projected cost, two weeks of marginal gains before the memo, sixty percent salvaged. No weak candidate
invents those details. More importantly, no weak candidate foregrounds the memo. Anyone can say "the
decision turned out wrong." Only one candidate wrote it down, with the numbers, to the same room.

Note what this case does not foreground: the kill criteria device, the internal calibration that
changed. Those are what a failure question draws out. An ownership question draws out the act: the
candidate who made the call, ran two weeks of repair attempts, then named the failure publicly rather
than waiting for someone else to. Same story, different signal, different layer. That is the Algorithm
doing its job.

## Core Concepts

- The ownership signal is the "I" behind a decision: the interviewer needs to locate one specific
  person's call, not a team's collective motion.
- Four failure modes kill ownership answers: the "we" answer, blaming others, activity without result,
  and vague or inflated claims.
- Construction starts from the hypothesis: identify what accountability evidence the question requires,
  then build toward it.
- The stress-test for ownership is memo-level specificity: a detail or decision only someone who
  actually made the call could supply.

The interviewer deciding whether to trust you with an outcome reads your answer, not your resume. One
specific, owned, named decision is worth more than a paragraph of activity.

<div class="claude-handoff" data-exercise="exercises/module3/ownership-stories/">

**Try It in Claude Code:** Write one of your own ownership stories, run the full Algorithm on it (decompose the signal and hypothesis, construct the STAR-L toward that evidence, apply the stress-test), then run the weak-answer audit from Module 2 and add the result to your behavioral bank.

</div>
