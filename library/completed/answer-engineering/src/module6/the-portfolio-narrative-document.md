# The Portfolio Narrative Document

The portfolio round is not an oral exam you improvise. The engineers who walk in and win it are the
ones who wrote their walkthrough down first.

This lesson does two things. It teaches you to compose the written document that becomes your interview
preparation artifact: a structured, peer-reviewable walkthrough of one portfolio project that captures
the decision layer, not the code. Then it turns the weak-walkthrough audit on that document the way
earlier lessons turned the weak-answer audit on behavioral answers and the weak-design audit on system
designs. You write the document, then you break it before the room does.

## Why a Written Document

Rehearsal alone has a structural flaw. You rehearse what you remember, and memory is not flat: the
first decision you made on a project is easier to recall than the third, the happy path is easier to
recall than the failure mode, and the thing you are proud of is easier to recall than the thing that
almost didn't work. The rehearsed walkthrough drifts toward the peaks of your memory, not toward the
structure the interviewer is evaluating.

A written document fixes this. When the reasoning is on the page, you can see what is missing. A
decision you thought you could defend turns out to have no named alternative. A failure mode you
believed was addressed turns out to be implied, not stated. Your peer can read the document and ask
the obvious follow-up; your rehearsal can't do that.

The document is also revisable between interviews. After a portfolio round where an interviewer probed
your evaluation story and found it thin, you open the document and add a section. After a round where
your role-tailoring note was wrong for the room, you revise it. A rehearsed monologue is hard to
update in a targeted way; a document has sections you can edit.

The result is what you rehearse from, not what you perform in the room. The room will steer you off
the script. You need the document solid enough that you can leave it and come back.

## The Document's Structure

A portfolio narrative document covers one artifact. Write one document per artifact you plan to walk
through. The document has six sections.

**The Artifact and One-Paragraph Overview.** Name the artifact, what it does, and why you built it.
One paragraph, sixty seconds aloud. The overview is not an architecture diagram in prose. It is the
answer to: what problem did this solve, who was the user, and what makes it different from a toy? For
your production RAG chatbot, that paragraph names the regulated-vertical problem, the citation
contract as the design constraint, and the eval gate as the thing that makes it shippable rather than
experimental. For your terminal coding agent, it names the plan/act/observe loop, the cost ceiling,
and the fact that "done" is a test verdict from the harness, not a claim from the model. The overview
is what orients the interviewer before you go deep.

**The Key Decisions with the Four-Part Defense.** This is the center of the document. For each
load-bearing decision, you write four things: the decision itself, the alternative you rejected, the
tradeoff you accepted, and the failure mode it guards against. You are not describing the code; you
are describing the reasoning that produced the code.

For the terminal coding agent, that means writing out why the verification gate defaults to REJECT
rather than ACCEPT, what trusting the model's self-assessment would have cost, what running the full
suite every loop iteration costs you, and what happens when you get it wrong, which is the agent
declaring a broken fix a success. You write all four parts for every decision that would stop an
interviewer. Two or three decisions per artifact is right; five is too many unless you can move
quickly through them.

The four-part structure is not a formula to recite aloud. It is the structure your reasoning should
have when you write it down, so you know it before you go into the room. In the room you use your
judgment about how much of it to surface and when.

**The Tradeoffs.** List the tradeoffs the decisions accepted. Not all tradeoffs live inside one
decision; some span the artifact. The terminal coding agent's budget with two caps (dollars and
iterations, checked before each call) means a task that would finish on the next call gets killed
early. That is a tradeoff you named and accepted; it belongs in this section with the reason you
accepted it. For the RAG chatbot, the relevance floor that refuses when no chunk clears the threshold
means some valid questions get a refusal instead of an answer. Write that down. The interviewer who
asks "what would you change?" is looking for this section.

**The Failure Modes Handled.** Name the failure modes the artifact explicitly defends against, and
for each one, how. This is different from the tradeoffs: a failure mode is something that could go
wrong at runtime; a tradeoff is something that is always true. The coding agent's kill switch is
read-only from the agent's perspective because a writable kill switch the agent can set is a kill
switch in name only. That is a failure mode handled. The RAG chatbot's hardcoded prohibitions floor
cannot be lowered by operator configuration; that guards against a pressured or misconfigured
operator disabling the security layer. Write these down explicitly. The interviewer who asks "what
could go wrong?" is coming to this section.

**The Role-Tailoring Note.** The same artifact narrates differently for different roles. Write
explicit notes for the two or three roles you are most likely to interview with. For an applied-AI or
product-engineering role, you foreground the user-facing reliability story: the RAG refusal floor,
the citation contract, the guardrail split between hardcoded prohibitions and tunable defaults, the
drift monitor. For an ML-platform or infrastructure role, you foreground the seams and operability:
the model seam that lets you swap any vendor with zero loop changes, the `VectorIndex` protocol that
makes a cloud migration a one-line constructor change, the eval gate running in CI. For a
research-adjacent role, you foreground the rigor: precision and faithfulness metrics, the
deterministic gate that needs no LLM judge, the refusal-rather-than-fabricate design.

The decisions do not change. The emphasis and the lead change. Write the role note as a short
paragraph per role, starting with: "Lead with X, because this role is evaluating for Y."

**What to Leave Out.** Write a short list of things you chose not to include in the walkthrough: the
scaffolding that does not bear load, the implementation details that are not decisions, the components
that are downstream consequences of a decision rather than decisions themselves. For the coding agent,
the specific tool handlers (read, write, test) are implementations of the tool registry decision, not
separate decisions. For the RAG chatbot, the ingest pipeline's format-specific parsers are
implementations of the chunk contract decision. You leave these out of the walkthrough because the
interviewer cannot evaluate your judgment on implementation details; they can only evaluate it on
decisions. Writing down what you are leaving out keeps the walkthrough focused and prevents you from
drifting into code narration when you are nervous.

## The Throughline

The document is the thing the module's exercises have been building toward. The walkthrough shape from
Lesson 1, the decision layer from Lesson 2, and the role-tailoring note from Lesson 3 all land in
this document. It is the throughline artifact you carry into the preparation dossier, revise between
interviews, and return to when you need to know what you actually built and why.

## The Weak-Walkthrough Audit

Now you turn the audit on your own document. The questions below are what the interviewer runs on
your walkthrough; you run them first. For each question, the verdict is pass or gap. A gap is not
failure; it is the thing you fix before the room finds it.

The audit runs by category.

### Is It a Decision Tour or a Code Reading?

**"Can I identify the three decisions that mattered most in this artifact without looking at the
code?"** If the answer is no, the document is still a code narration with decision language on top.
The decisions should be extractable as claims: "I built the verification gate to default to REJECT
rather than ACCEPT, because..." If your document requires the code to be legible, it is not a
decision tour.

**"Does each key decision appear in one place in the document, or is it scattered across the
overview, the tradeoffs, and the failure modes?"** A decision should have a home: the four-part
defense section. The overview names the artifact; the tradeoffs and failure modes sections can
reference decisions, but the decision itself lives in one place. If you have to read three sections
to reconstruct one decision, the document is understructured.

### Does Every Decision Have All Four Parts?

**"For each key decision, have I named the alternative I rejected?"** A decision without a rejected
alternative is not a decision; it is a description of what you built. The alternative is what makes
the decision legible: you could have done X, you did Y, here is why.

**"For each key decision, have I named the tradeoff I accepted?"** The tradeoff is what the
alternative would have gotten you and what your decision cost you. If you cannot name the cost, you
did not fully analyze the decision.

**"For each key decision, have I named the specific failure mode it guards against?"** This is the
most commonly missing part. "I used a sandbox for tests" becomes defensible when you say: "I used a
subprocess sandbox with a wall-clock timeout to guard against a model-generated test suite that loops
forever or calls out to the network." The failure mode is the why.

### Did You Lead with the Differentiator?

**"What is the first decision in your document? Is it the one that demonstrates your judgment, or
is it the one you built first?"** The first decision you name sets the interviewer's hypothesis about
you. For the terminal coding agent, leading with the model seam (because it was the first thing you
built) is weaker than leading with the verification gate (because it shows you understand that the
hard problem in a coding agent is not the model, it is the harness). Lead with the decision that most
directly answers: what makes this system trustworthy?

**"Does the overview bury the lead?"** The overview paragraph names the artifact. If it spends three
sentences on what the components are and one on what problem they solve, it is not oriented toward
the interviewer's hypothesis. The one-paragraph overview should be deliverable in sixty seconds with
the differentiating problem front-loaded.

### Is It Tailored to a Role or Is It a Generic Monologue?

**"Does the document have a role-tailoring note, and is it specific?"** A role note that says "for
platform roles, talk about the seams" is a category, not a note. A useful role note names the
specific lead decision for that role: "For an ML-platform interview, lead with the `VectorIndex`
protocol seam, because the interviewer is evaluating whether you can design for replaceability across
the full stack." Specificity is what separates a tailoring note from a reminder to yourself.

**"If I removed the role-tailoring note and delivered the document as written, what role would it
be optimized for?"** Every document has a default emphasis. Know what yours is. An artifact that
leads with the eval gate and the precision/faithfulness metrics by default is optimized for a
research-adjacent or evaluation-focused role. If you are walking into an infra interview, the lead
should move to the protocol seam and the deterministic gates running in CI.

### Can You Defend the Follow-Up?

**"For each key decision, what is the most obvious follow-up, and is the answer in the document?"**
The coding agent's kill switch being read-only will draw: "What if the operator loses the file?"
The RAG chatbot's relevance floor will draw: "How do you set the threshold, and how do you know when
it is wrong?" Write the obvious follow-up for each decision. If you cannot answer it from what is in
the document, the decision defense is incomplete.

**"What would an interviewer ask about the failure mode I did not include?"** The absence of a named
failure mode is itself a probe target. If you built a multi-agent system and your document names no
failure mode around budget runaway, the interviewer will go there. The what-to-leave-out section
keeps you honest: if you chose not to address it, know why.

### Did You Claim Work You Cannot Defend?

**"Is every decision in the document one I made, not one I read about?"** The document is a
walkthrough of your work. A candidate who says "and we used a relevance floor to prevent fabricated
citations" can defend: what threshold, how was it calibrated, what happened when it refused valid
questions, and how was it tuned. A candidate who borrowed the architecture without building it cannot
answer the third question. Write only the decisions you can defend under probing.

**"Can I describe what a specific failure would have looked like if I had not made each decision?"**
If you cannot, the decision is a pattern you named but did not actually implement. The verification
gate's failure mode is not "the agent might give wrong results"; it is "the agent called
`verify_done()` on a fix that broke three other tests, and without the gate running the real suite,
it returned success." That specificity is only available if you built the thing.

## Verdict and Repair

Run the audit by category. Each gap is one edit to the document. If a decision is missing its
rejected alternative, add it. If the overview buries the lead, reorder it. If the role-tailoring
note is a category reminder rather than a specific lead, make it specific. The document is not done
when you finish writing it; it is done when it passes all seven categories.

The audit does not need to surface every possible weakness. It needs to surface the ones the
interviewer will find in the first ten minutes. Those are always the same: a code narration masking
as a decision tour, a decision without a named alternative, and a walkthrough that delivers the same
monologue regardless of the role in the room.

Fix those three and the rest of the document will hold.

## Core Concepts

- The portfolio narrative document captures the decision layer: the four-part defense for each key
  decision (decision, rejected alternative, accepted tradeoff, failure mode guarded), written before
  rehearsal so the reasoning is explicit, peer-reviewable, and editable between interviews.
- A written document reveals structural gaps that rehearsal conceals: a decision without a named
  alternative, a failure mode implied rather than stated, and an overview that buries the lead are
  invisible in practice and visible on the page.
- The weak-walkthrough audit runs by category before the room does: decision tour vs. code reading;
  four-part completeness; whether the differentiator leads; role specificity; follow-up defensibility;
  and whether every claimed decision can survive targeted probing.
- The role-tailoring note does not change the decisions; it changes the lead decision and the emphasis,
  because the interviewer for an applied-AI role and the interviewer for an ML-platform role are
  evaluating different signals from the same artifact.

<div class="claude-handoff" data-exercise="exercises/module6/the-portfolio-narrative-document/">

**Try It in Claude Code:** finish your portfolio-narrative document for one artifact, then run the weak-walkthrough audit on it and record the verdict: which checks it passes, which it fails, and the one change you made.

</div>
