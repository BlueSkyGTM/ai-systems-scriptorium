# ASDG Question Taxonomy — Signal-Organized

Distilled from: `vault/ai-system-design-guide/00-interview-prep/01-question-bank.md` (Q1-Q116)
and `vault/ai-system-design-guide/00-interview-prep/05-behavioral-for-ai-roles.md`.
Reorganized under the four Algorithm signal categories. Not a copy of the ore's table of
contents; the ore is topic-organized, this is signal-organized.

Purpose: raw material for Lesson 1 (decompose the question) and Lesson 2 (construct the
answer) in M1, and the example bank in M3 (behavioral) and M5 (systems-design).

---

## Signal Category 1: Ownership

**Hiring hypothesis:** Does this candidate drive outcomes, or do they participate and observe?
The interviewer is looking for evidence that the candidate has personal accountability for
a decision, a system, or a result: "I built," "I decided," "I was responsible for," not "we
explored" or "I was involved."

### Representative questions (verbatim or lightly trimmed from ore)

| Question | Primary | Secondary | Source |
|----------|---------|-----------|--------|
| "Tell me about the most complex AI project you worked on." | Ownership | Technical depth | asdg 05-behavioral, Theme 3 |
| "Describe a project that failed. What happened and what did you learn?" | Ownership | Judgment under uncertainty | asdg 05-behavioral, Q categories |
| "Tell me about a time you led a technical initiative without formal authority." | Ownership | Communication/influence | asdg 05-behavioral, Leadership |
| "Tell me about a time you pushed back on a product decision." | Ownership | Communication/influence | draft 02-signal-to-answer worked example |
| "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong." | Ownership | Judgment under uncertainty | asdg 05-behavioral Example 5 |
| "How do you evaluate a RAG system?" (asked of a tech lead) | Ownership (framing implies you have one) | Technical depth | asdg 01-question-bank Q5, Q39 |

**Key tell:** strip "tell me about a time" or "walk me through" -- the noun that remains
("a project you led," "a decision you made") tells you the category. Ownership questions
demand a first-person subject.

---

## Signal Category 2: Judgment Under Uncertainty

**Hiring hypothesis:** Can this candidate make a defensible decision with incomplete
information, or do they require certainty before acting? The interviewer is checking for
the ability to bound unknowns, name the risk explicitly, and commit to a direction.

### Representative questions

| Question | Primary | Secondary | Source |
|----------|---------|-----------|--------|
| "Tell me about a difficult technical decision you made with incomplete information." | Judgment | Ownership | asdg 05-behavioral, Technical Decision Making |
| "How do you decide what to build when the path is not obvious?" | Judgment | Ownership | asdg 05-behavioral, Theme 1 |
| "When would you choose RAG over fine-tuning, and vice versa?" | Judgment | Technical depth | asdg 01-question-bank Q2 |
| "When would you use a small language model vs a frontier model?" | Judgment | Technical depth | asdg 01-question-bank Q19 |
| "Are reasoning models worth the cost?" | Judgment | Technical depth | asdg 01-question-bank Q20, Q52 |
| "Describe a situation where you changed direction mid-project." | Judgment | Ownership | asdg 05-behavioral, Theme 1 |
| "Tell me about a time you chose a simpler solution over a more sophisticated one." | Judgment | Communication/influence | asdg 05-behavioral, Technical Decision Making |
| "Your agent takes 47 LLM calls to complete a task that should take 5. How do you debug this?" | Judgment | Technical depth | asdg 01-question-bank Q51 |

**Key tell:** these questions almost always contain a constraint, a fork, or a failure.
"Incomplete information," "two options," "did not work as expected." The interviewer is
not checking recall; they are checking reasoning under pressure.

---

## Signal Category 3: Technical Depth

**Hiring hypothesis:** Is this candidate's knowledge operational, or is it surface-level
familiarity? They can name the thing AND explain its failure modes, tune its parameters,
and connect it to production constraints.

### Representative questions

| Question | Primary | Secondary | Source |
|----------|---------|-----------|--------|
| "Walk me through the architecture of a production RAG system." | Technical depth | Ownership (do you have a real one?) | asdg 01-question-bank Q1 |
| "Explain chunking strategies and when to use each." | Technical depth | Judgment | asdg 01-question-bank Q4 |
| "What is the KV cache and why does it matter?" | Technical depth | -- | asdg 01-question-bank Q22, Q57 |
| "What is speculative decoding and when would you use it?" | Technical depth | Judgment | asdg 01-question-bank Q23 |
| "Explain the ReAct pattern and its failure modes." | Technical depth | Judgment | asdg 01-question-bank Q12 |
| "What is the difference between an agent and a workflow?" | Technical depth | Judgment | asdg 01-question-bank Q11 |
| "How do you implement guardrails for an autonomous agent?" | Technical depth | Judgment | asdg 01-question-bank Q56 |
| "How do you detect and handle hallucinations?" | Technical depth | Judgment | asdg 01-question-bank Q29 |
| "Explain the RAGAS evaluation framework." | Technical depth | Ownership | asdg 01-question-bank Q28 |
| "How do you evaluate LLM outputs when there is no ground truth?" | Technical depth | Judgment | asdg 01-question-bank Q27 |

**Depth marker the ore calls out (asdg 02-answer-frameworks, Key Takeaways):** "Always end
deep dives with one sentence on observability and one on failure modes; this is the single
biggest gap between senior and staff answers."

Depth expected for chunks example (asdg 03-common-pitfalls Pitfall 9): not "I use recursive
chunking" but WHY each choice -- smaller chunks give more retrieval precision, larger chunks
give more context, overlap prevents losing context at boundaries, semantic chunking for
complex document structure.

---

## Signal Category 4: Communication and Influence

**Hiring hypothesis:** Can this candidate operate in a real organization -- move decisions,
align stakeholders, translate between technical and business language -- or can they only
operate within a technical team?

### Representative questions

| Question | Primary | Secondary | Source |
|----------|---------|-----------|--------|
| "How do you explain AI limitations to non-technical colleagues?" | Communication/influence | Judgment | asdg 05-behavioral, Theme 2 |
| "Tell me about a conflict with a product manager over AI capabilities." | Communication/influence | Ownership | asdg 05-behavioral, Collaboration |
| "Describe working with a team that had different priorities." | Communication/influence | Judgment | asdg 05-behavioral Example 4 |
| "Tell me about a time you raised an ethical concern." | Communication/influence | Ownership | asdg 05-behavioral Example 3 |
| "Describe a situation where you had to convince others to adopt a new approach." | Communication/influence | Ownership | asdg 05-behavioral, Leadership |
| "Describe a time you raised a concern and the team decided against you. What did you do?" | Communication/influence | Judgment | asdg 05-behavioral Example 6 |
| "How do you work with researchers who have different priorities?" | Communication/influence | Judgment | asdg 05-behavioral, Theme 4 |
| "Tell me about a disagreement with a colleague about a technical approach." | Communication/influence | Ownership | asdg 05-behavioral, Collaboration |

**Staff-level tell (ore-stated):** "Behavioral prep is what separates staff candidates from
senior candidates." (asdg README.md) The communication/influence signal is weighted
disproportionately at the staff level because senior ICs are evaluated for technical depth;
staff ICs are evaluated for whether they multiply others.

---

## AI/ML Systems-Design Decomposition Variant

Systems-design questions require one extra decomposition move before designing anything:
surface the production constraints the design must honor. The ore calls out this move
explicitly (asdg 02-answer-frameworks, SPIDER S-phase; draft 01-question-decomposition).

The signal collected by the clarifying-questions move IS ITSELF a signal of operational
experience. Candidates who begin with "I would start by clarifying: what is the scale,
the latency budget, and the compliance requirements?" are distinguishing themselves from
candidates who immediately name a stack.

### Real design-prompt questions from the ore

| Prompt | Production constraints to surface first | Source |
|--------|----------------------------------------|--------|
| "Design a customer support chatbot." | Volume (10K tickets/day?), languages, SLA for first response, compliance requirements, existing stack | asdg 01-question-bank Scenario 1 |
| "Design a document Q&A system for a 10,000-employee company." | Document volume, freshness SLA, internal vs external, accuracy bar, p95 latency budget | asdg 02-answer-frameworks, SPIDER worked transcript |
| "Design a RAG system for enterprise search." | Document count (10M), user count (50K), RBAC requirements, real-time update SLA | asdg 01-question-bank Scenario 3 |

**SPIDER S-phase questions to ask verbatim (asdg 02-answer-frameworks):**
"What is the scale? What are the latency requirements? What accuracy or quality bar must we
meet? Are there compliance or security requirements? What is the existing infrastructure?
What is the budget constraint?"

The design-prompt decomposition move is what the draft lesson calls the "AI/ML systems
design variant" (draft 01-question-decomposition, section "The AI Systems Design Variant"):
surface the production constraints before you design anything; the move is itself a signal.

---

## Behavioral STAR-L Worked Examples (condensed)

Raw material for M1 Lesson 2 (construct the answer) and M3's behavioral bank. Three of
the six examples from asdg 05-behavioral-for-ai-roles.md, condensed to skeleton form.
The full text lives in the ore; do not reproduce it verbatim in lesson prose -- summarize
the moves.

### Example 1: Handling Ambiguity (asdg 05-behavioral Example 1)

**Question asked:** "Tell me about a time you started an AI project with unclear requirements."

| STAR-L part | What the ore shows |
|-------------|-------------------|
| Situation | Stakeholders had conflicting visions for AI-powered search (Sales wanted "magic," Engineering wanted quarterly scope, Leadership wanted differentiation) |
| Task | Tech lead. Had to align stakeholders and define a concrete first version |
| Action | Interviewed five stakeholders to find common thread (reduce time to find information); built three rapid prototypes at different sophistication levels (keyword ranking, semantic search, conversational RAG); demoed each with real queries from support logs |
| Result | Shipped semantic search in 6 weeks; user time-to-answer dropped 40% |
| Learning | Ambiguity often comes from stakeholders optimizing for different things; concrete options with real tradeoffs move conversations forward faster than abstract discussion |

**Algorithm framing (M1):** Primary signal is Judgment under uncertainty; secondary is
Communication/influence (stakeholder alignment). The construction move that makes this strong
is the prototype-as-argument: showing three concrete options with real tradeoffs.

### Example 5: Being Wrong and Walking It Back (asdg 05-behavioral Example 5)

**Question asked:** "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong."

| STAR-L part | What the ore shows |
|-------------|-------------------|
| Situation | Pushed to replace retrieval pipeline with pure long-context approach; argued in two design reviews; team committed a quarter to the migration partly on candidate's conviction |
| Task | Owned proving the new system out before full cutover |
| Action | Eval results showed quality matched but cost ran 4x projection (cache hit rates collapsed under update frequency; p95 latency doubled). First instinct was to tune out; after two weeks of marginal gains, wrote a one-page memo stating plainly the recommendation was wrong on the economics. Proposed a hybrid: long-context for small static corpora, retrieval for everything else. Presented to the same audience |
| Result | Hybrid kept; salvaged 60% of migration work; postmortem produced a new team rule: any architecture pitch must include a cost model under realistic update patterns |
| Learning | Conviction is useful for getting decisions made and dangerous for unmaking them; now attaches explicit kill criteria to own proposals |

**Algorithm framing (M1):** Primary signal is Ownership (took the call and walked it back
publicly); secondary is Judgment (kill criteria as a structural device). The specificity that
makes this unfakeable: "cost ran 4x projection," "two weeks of marginal gains," "one-page memo."

### Example 6: Raising a Concern That Was Dismissed (asdg 05-behavioral Example 6)

**Question asked:** "Describe a time you raised a concern and the team decided against you. What did you do?"

| STAR-L part | What the ore shows |
|-------------|-------------------|
| Situation | Before a launch, flagged that agent's tool permissions were broader than the feature needed: it could write to systems it only needed to read; leadership decided to ship as-is with a fast-follow ticket |
| Task | Disagreed with the call; job was to ensure the decision was made with full information, then either escalate or commit |
| Action | Wrote the risk down concretely: specific blast radius if the agent was prompt-injected, with a realistic attack path, not a vague "this is risky." Asked for two mitigations that fit inside the launch window: an audit log on the write paths and an anomaly alert on write volume. Documented disagreement in the decision record and committed without relitigating |
| Result | Launch was fine; three weeks later the alert fired on a misconfigured integration test (not an attack), but it proved the monitoring worked; the permission scoping shipped a month later |
| Learning | Being overruled is not the end of the job; converting a lost argument into cheap guardrails and a written record is usually worth more than winning the argument, and builds credibility |

**Algorithm framing (M1):** Primary signal is Communication/influence (operated in a real
organization without authority); secondary is Judgment (proportional escalation, specific
risk quantification). The specificity: "blast radius if prompt-injected," "audit log on
the write paths," "documented disagreement in the decision record."
