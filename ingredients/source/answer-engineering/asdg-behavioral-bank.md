# ASDG Behavioral Bank — M3 Reference Ingredient

Distilled from:
- `vault/ai-system-design-guide/00-interview-prep/05-behavioral-for-ai-roles.md` (primary ore,
  all six STAR-L worked examples, question categories, red flags, "Why Behavioral Questions
  Matter" framing) — abbreviated below as **asdg 05**
- `vault/ai-system-design-guide/00-interview-prep/01-question-bank.md` (Q1-Q116; no dedicated
  behavioral section; behavioral questions from asdg 05 are the canonical source)

Cross-references (do NOT re-distill; pointer only):
- `ingredients/source/answer-engineering/asdg-question-taxonomy.md` — signal categories 1-4,
  Examples 1, 5, 6 in fuller skeleton form
- `ingredients/source/answer-engineering/asdg-delivery-and-leveling.md` — leveling bar, staff
  signal, delivery mechanics (two-length discipline, record-and-review loop)

Purpose: single authoritative behavioral reference for M3 lesson authors. Dense; no prose
polish. Everything traces to real ore; no invented examples.

---

## Why Behavioral Questions Matter (asdg 05, "Why Behavioral Questions Matter")

AI projects probe six challenge areas that behavioral questions specifically test. These are
not generic behavioral screens; they assess AI-role-specific judgment:

| AI challenge | What interviewers assess |
|---|---|
| Uncertainty | How do you make decisions with incomplete information? |
| Rapid change | How do you stay current and adapt? |
| Cross-functional work | How do you collaborate with research, product, legal? |
| Ethical concerns | How do you handle responsible AI considerations? |
| Technical debt | How do you balance shipping with correctness? |
| Stakeholder education | How do you explain AI limitations to non-technical peers? |

The ore's framing for the staff bar (asdg 05; see also `asdg-question-taxonomy.md` Signal
Category 4): "Behavioral prep is what separates staff candidates from senior candidates."
Communication/influence signal is weighted disproportionately at staff because senior ICs are
evaluated for technical depth; staff ICs are evaluated for whether they multiply others.

---

## Section 1: Ownership Category

### Hiring hypothesis

(asdg-question-taxonomy.md Signal Category 1; consistent with asdg 05 Theme 3 and Example 5)

Did this candidate drive outcomes, or did they participate and observe? Interviewers look for
personal accountability for a decision, system, or result: "I built," "I decided," "I was
responsible for," not "we explored" or "I was involved." The "I" vs "we" discipline is the
central discriminant.

### Real behavioral questions (asdg 05)

| Question (verbatim or lightly trimmed) | Source in ore |
|---|---|
| "Tell me about the most complex AI project you worked on." | asdg 05, Theme 3 (Project Challenges) |
| "Describe a project that failed. What happened and what did you learn?" | asdg 05, Theme 3 (Project Challenges) |
| "Tell me about a time you led a technical initiative without formal authority." | asdg 05, Leadership and Influence |
| "Tell me about a time you started an AI project with unclear requirements." | asdg 05, Theme 1 (Handling Ambiguity); Example 1 |
| "Describe a situation where you changed direction mid-project." | asdg 05, Theme 1 |
| "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong." | asdg 05, Example 5 |

### Category-specific failure modes / red flags (asdg 05, Red Flags to Avoid; asdg 05 Examples)

- **Using "we" instead of "I":** The cardinal ownership failure. Candidate describes a team
  outcome without naming their specific action. Interviewers cannot assess the candidate's
  individual contribution; the answer reads as participation, not ownership.
- **Blaming others:** "The team didn't..." or "management decided without consulting me..."
  -- signals no accountability. (asdg 05, Red Flags table: "Blaming others / Does not take
  responsibility.")
- **No specific examples / inflating experience:** Vague claims without a concrete project or
  timeline. The ore flags this as a signal the candidate may be overstating involvement.
  (asdg 05, Red Flags: "No specific examples / May be inflating experience.")
- **Activity without result:** Candidate describes what they did but not what changed. The
  Result and Learning steps are where ownership lands; an answer that ends at Action is
  structurally incomplete.
- **Walked-back-without-a-memo pattern (contrast with Example 5):** The ore's positive model
  in Example 5 is the one-page memo stating plainly the recommendation was wrong. The failure
  mode is its inverse: tuning incrementally to avoid admitting error, or waiting until others
  surface the failure (see also `asdg-delivery-and-leveling.md`, Section A5 on recovery).

---

## Section 2: Conflict Category

### Hiring hypothesis

(asdg 05, Theme 4 Cross-Functional Collaboration; Collaboration and Conflict questions;
consistent with asdg-question-taxonomy.md Signal Category 4 Communication/influence)

Can this candidate navigate real organizational disagreements: with a PM over AI capability
claims, with a peer over a technical approach, with leadership after being overruled? The
interviewer is probing the disagree-and-commit pattern, de-escalation, and proportional
escalation. The test is not whether the candidate won the argument, but whether they operated
constructively after the argument's outcome.

### Real behavioral questions (asdg 05)

| Question (verbatim or lightly trimmed) | Source in ore |
|---|---|
| "Tell me about a disagreement with a colleague about a technical approach." | asdg 05, Collaboration and Conflict |
| "Describe working with someone who had a very different working style." | asdg 05, Collaboration and Conflict |
| "How do you work with researchers who have different priorities?" | asdg 05, Theme 4 |
| "Tell me about a conflict with a product manager over AI capabilities." | asdg 05, Theme 4 |
| "Describe collaborating with legal on an AI feature." | asdg 05, Theme 4 |
| "Describe working with a team that had different priorities." | asdg 05, Example 4 |
| "Describe a time you raised a concern and the team decided against you. What did you do?" | asdg 05, Example 6 |
| "Tell me about a time you had to say no to a stakeholder request." | asdg 05, Theme 2 (Managing Expectations) |
| "Describe a situation where expectations were unrealistic." | asdg 05, Theme 2 |

### Category-specific failure modes / red flags (asdg 05)

- **Defending a position past the point of reason:** The ore names "defending wrong answers"
  as a communication pitfall (asdg 05, cross-referenced in `asdg-delivery-and-leveling.md`
  A5). In a conflict story, the equivalent is retelling the argument as if the candidate was
  simply right and the other party was simply wrong. This signals low calibration and a
  fragile ego.
- **No relationship outcome:** A conflict story that ends at the decision without addressing
  what happened to the working relationship afterward. Interviewers probe: "What was the
  relationship like after?" A candidate who cannot answer this has told a grievance story,
  not a collaboration story.
- **Only technical answers / lacks awareness of human factors:** (asdg 05, Red Flags table.)
  Conflict questions are explicitly about the human dimension; a candidate who answers only
  with technical content is missing the signal category.
- **Relitigating in hallway conversations:** Example 6 names the negative as its inverse: "I
  committed to the launch without relitigating it in hallway conversations." The failure mode
  is continuing to campaign after the decision is made. (asdg 05, Example 6 Action step.)
- **Vague "we aligned":** A conflict resolution that does not show the specific move the
  candidate made to reach alignment. The ore's positive examples (Examples 4, 6) both name
  concrete mechanisms: a collaboration structure with co-authorship credit (Ex 4), two
  specific mitigations asked for inside the launch window (Ex 6).

---

## Section 3: Failure Category

### Hiring hypothesis

(asdg 05, Theme 3 Dealing with Failure; asdg 05, Preparation Checklist: "Include at least one
story where you were wrong"; consistent with asdg-question-taxonomy.md Signal Category 2
Judgment Under Uncertainty)

Does this candidate learn from failures without defensiveness, or do they polish failure into
partial success? The ore's framing (Theme 3): "Strong candidates learn from failures without
defensiveness." Three sub-signals: (1) taking responsibility, (2) root cause analysis, (3)
systems thinking about prevention. The Learning step is the load-bearing move in a failure
story; it is where the interviewer assesses whether the candidate extracted a generalizable
lesson or filed the experience away.

### Real behavioral questions (asdg 05)

| Question (verbatim or lightly trimmed) | Source in ore |
|---|---|
| "Tell me about an AI system that did not work as expected." | asdg 05, Theme 3 |
| "How do you handle a model that performs poorly in production?" | asdg 05, Theme 3 |
| "Describe a time you shipped something that had issues." | asdg 05, Theme 3 |
| "Describe a project that failed. What happened and what did you learn?" | asdg 05, Theme 3 (Project Challenges) |
| "Tell me about a difficult technical decision you made with incomplete information." | asdg 05, Technical Decision Making |
| "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong." | asdg 05, Example 5 |
| "Tell me about a time you started an AI project with unclear requirements." [when the project did not land as hoped] | asdg 05, Theme 1 / Example 1 |

The ore's Preparation Checklist (asdg 05) states explicitly: "Include at least one story where
you were wrong and one where you were overruled (Examples 5 and 6 show the shape)." Having no
failure story is itself a red flag.

### Category-specific failure modes / red flags (asdg 05)

- **No Learning step:** The ore's STAR-L framework adds Learning precisely because "the most
  important part of any story about failure" is what changed afterward. A failure story that
  ends at Result ("and then we rolled it back") without a Learning step is structurally
  incomplete and reads as low-reflection.
- **Polished excuse instead of honest scoping:** Framing a failure as almost-a-success or
  beyond-my-control. Example 2 models the positive: "First, I did not hide the problem.
  I immediately flagged it to leadership with the data showing the gap." The failure mode
  is its inverse: discovering the problem late, framing it as an external event, or burying
  the magnitude.
- **Only technical root cause, no human factor:** The ore's Theme 3 "what they look for"
  includes "taking responsibility" as distinct from "root cause analysis." A candidate who
  diagnoses the technical failure but does not acknowledge their role in it has answered
  half the question.
- **No prevention or systems change:** Theme 3's third sub-signal is "systems thinking about
  prevention." The Learning step must name what changed, not just what was learned
  abstractly. Example 2: "I established testing practices that caught similar issues in
  future projects." Example 5: "a new team rule -- any architecture pitch must include a
  cost model under realistic update patterns."
- **Dismissing ethics / creating liability:** (asdg 05, Red Flags table.) Applicable when the
  failure involved an AI-specific risk (bias, safety, regulatory): dismissing the ethical
  dimension as a side issue signals a candidate who may create downstream liability.

---

## Section 4: Technical Influence Category

### Hiring hypothesis

(asdg 05, Theme 5 Responsible AI; asdg 05, Leadership and Influence; consistent with
asdg-question-taxonomy.md Signal Category 4 Communication/influence; staff bar from
`asdg-delivery-and-leveling.md` C2-C4)

Can this candidate move from "I shipped" to "I changed what others could ship"? This category
probes leading without authority, convincing others, and technical influence: the staff signal.
Senior ICs are evaluated for technical depth; staff ICs are evaluated for whether they multiply
others. The question behind these questions: does the candidate leave organizational artifacts
(processes, standards, patterns, templates) that outlast the individual project?

The ore also routes responsible AI and ethics questions here because raising an ethical concern
is an act of influence: it is the candidate asserting a position to a stakeholder audience that
may not share it. (asdg 05, Theme 5; Example 3.)

### Real behavioral questions (asdg 05)

| Question (verbatim or lightly trimmed) | Source in ore |
|---|---|
| "Tell me about a time you led a technical initiative without formal authority." | asdg 05, Leadership and Influence |
| "Describe a situation where you had to convince others to adopt a new approach." | asdg 05, Leadership and Influence |
| "Tell me about a time you raised an ethical concern." | asdg 05, Theme 5; Example 3 |
| "How do you think about fairness in AI systems?" | asdg 05, Theme 5 |
| "Describe a situation where you prioritized safety over speed." | asdg 05, Theme 5 |
| "How do you explain AI limitations to non-technical colleagues?" | asdg 05, Theme 2 |
| "Tell me about a time you raised a concern and the team decided against you. What did you do?" | asdg 05, Example 6 |
| "Describe working with a team that had different priorities." [when the candidate changed how the team worked] | asdg 05, Example 4 |
| "How do you stay current with the rapidly changing AI field?" | asdg 05, Growth and Learning |
| "Tell me about a skill you developed recently." | asdg 05, Growth and Learning |

### Category-specific failure modes / red flags (asdg 05)

- **"We" without "I changed":** The influence story must name the candidate's specific move
  that changed what others could do. "We established a template" is weaker than "I proposed
  the collaboration structure, which became the template we now use for research-to-production
  handoffs" (the move Example 4 models).
- **Influence-as-winning:** Framing the influence story as the candidate convincing others
  they were right. The ore's positive models (Examples 3, 4, 6) show influence operating
  through alignment of incentives, concrete evidence, and proposed alternatives -- not
  persuasion contests.
- **Dismissing ethics:** (asdg 05, Red Flags.) Especially damaging in this category because
  raising responsible AI concerns is itself an influence act. A candidate who dismisses or
  minimizes ethical concerns in a "prioritizing safety" question signals they will not
  exercise the influence needed when it matters.
- **No questions for interviewer:** (asdg 05, Red Flags: "Lacks curiosity or engagement.")
  For the influence category specifically: a candidate who has no questions about the
  company's processes for raising concerns, cross-functional collaboration, or AI ethics
  is missing an opportunity to demonstrate the category-relevant mindset.
- **Stopping at the decision outcome:** Example 6 models the key move: after being overruled,
  the candidate converted the lost argument into cheap guardrails (audit log, anomaly alert)
  and a written record. The failure mode is a candidate who ends the story at "I disagreed
  but deferred" without naming the constructive action that followed.
- **Ethics framed as obstruction:** Example 3 shows the positive: framing the ethical concern
  as a business and legal risk, not as a moral objection alone. The failure mode is the
  candidate presenting themselves as a blocker rather than a problem-solver who happened to
  surface a risk. (asdg 05, Example 3 Action step.)

---

## Section 5: All Six STAR-L Worked Examples in Skeleton Form

All six from asdg 05. For Examples 1, 5, 6: condensed (fuller skeletons in
`asdg-question-taxonomy.md` Behavioral STAR-L Worked Examples section).

---

### Example 1: Handling Ambiguity (asdg 05, Example 1)

**Question asked:** "Tell me about a time you started an AI project with unclear requirements."

| STAR-L | Condensed real details |
|---|---|
| S | Stakeholders had conflicting visions for AI-powered search: Sales wanted "magic," Engineering wanted quarterly scope, Leadership wanted competitor differentiation |
| T | Tech lead: align stakeholders, define a concrete first version |
| A | Interviewed five stakeholders; found common thread (reduce time to find information); built three rapid prototypes: keyword ranking, semantic search (embeddings), conversational RAG; demoed each with real queries from support logs, showing actual performance and engineering effort |
| R | Shipped semantic search in 6 weeks; user time-to-answer dropped 40%; clear success enabled phase two buy-in |
| L | Ambiguity often comes from stakeholders optimizing for different things; concrete options with real tradeoffs move conversations forward faster than abstract discussion; now starts every ambiguous project with quick prototypes |

**Best M3 lesson category:** Ownership (but deployed effectively in conflict and influence lessons too)

**Algorithm framing:** Primary signal: Judgment under uncertainty; secondary: Communication/influence.
The unfakeable specificity: three prototype levels + "real queries from support logs" + 40% drop.
Note: "fuller skeleton in asdg-question-taxonomy.md."

---

### Example 2: Managing Failed Expectations (asdg 05, Example 2)

**Question asked:** "Tell me about a time an AI system did not perform as expected in production."

| STAR-L | Condensed real details |
|---|---|
| S | Content recommendation system launched; performed great in testing but showed 30% lower engagement in production than heuristic baseline |
| T | ML engineer who built it: diagnose the issue, decide whether to roll back, regain stakeholder trust |
| A | Did not hide the problem; immediately flagged to leadership with data showing the gap; proposed keeping 10% traffic on new system while investigating; found two issues: test set was not representative (from high-engagement users only) and cold start was worse than expected; implemented stratified testing matching production user distribution; added heuristic fallback for cold users; created real-time monitoring dashboard |
| R | Revised system outperformed baseline by 15% after two more weeks of iteration; established testing practices that caught similar issues in future projects |
| L | Production is the only true test for ML systems; now always instruments for monitoring before launch and plans for rapid iteration; transparency during failures builds more trust than hiding problems |

**Best M3 lesson category:** Failure (also strong for Ownership: "I did not hide the problem")

**Algorithm framing:** Primary signal: Ownership (took responsibility, flagged immediately);
secondary: Judgment (controlled rollout, diagnostic discipline). Unfakeable specificity:
"30% lower engagement," "10% traffic hold," "15% improvement after two weeks," "stratified
testing matched production user distribution."

---

### Example 3: Ethical Concern (asdg 05, Example 3)

**Question asked:** "Tell me about a time you raised an ethical concern about an AI system."

| STAR-L | Condensed real details |
|---|---|
| S | Building a resume screening system; training data was heavily biased toward engineers from top universities |
| T | Raise the concern in a way that would be taken seriously without being dismissed as blocking the project |
| A | Quantified the problem: model had 80% precision on Stanford graduates but only 45% on state school graduates with similar qualifications; presented it as a business and legal risk (cited recent lawsuits over biased hiring); proposed two alternatives: (1) rebalance training data for diverse representation; (2) use model only for matching, not ranking, with human review for all candidates; team chose option 1 plus fairness metrics in evaluation suite |
| R | Delayed launch by three weeks; shipped system that performed consistently across demographics; legal and HR were grateful; fairness metrics became standard for all ML models |
| L | Framing ethical concerns in terms of business risk makes them more actionable; raising concerns early with proposed solutions is more effective than waiting until problems are entrenched |

**Best M3 lesson category:** Technical Influence (raising a concern, reframing it, changing the
standard for all ML models -- an organizational artifact that outlasted the project)

**Algorithm framing:** Primary signal: Communication/influence; secondary: Ownership (named the
risk, proposed alternatives, did not stop at the objection). Unfakeable specificity: "80%
precision on Stanford graduates," "45% on state school graduates," "three-week delay,"
"fairness metrics became standard for all ML models."

---

### Example 4: Cross-Functional Collaboration (asdg 05, Example 4)

**Question asked:** "Tell me about working with a team that had different priorities."

| STAR-L | Condensed real details |
|---|---|
| S | Research team had developed a novel retrieval approach showing 20% better recall on benchmarks; they wanted to publish and move on; product wanted it shipped; candidate was the engineer responsible for productionizing |
| T | Get the system into production while maintaining a good relationship with researchers who had different incentives |
| A | Started by understanding what researchers cared about: credit for the innovation, not having their method "dumbed down"; proposed collaboration structure: they remain authors on publications about the production system; candidate documents which contributions directly impacted production metrics; weekly meetings to review changes and ensure scientific integrity; when simplification was needed for latency, showed benchmarks proving their key innovations were preserved; researchers contributed optimization ideas |
| R | Shipped in 8 weeks with 18% recall improvement (slightly less than benchmark due to latency constraints); researchers published a follow-up paper on production learnings; team established a template for research-to-production collaboration |
| L | Understanding what motivates others is the key to collaboration; by making production success support researchers' goals (impact and credit), turned potential friction into partnership |

**Best M3 lesson category:** Conflict (also strong for Technical Influence: "established a template"
is the organizational artifact that signals staff-level impact; see `asdg-delivery-and-leveling.md` C3)

**Algorithm framing:** Primary signal: Communication/influence; secondary: Judgment (aligned incentives
rather than overriding them). Unfakeable specificity: "20% better recall on benchmarks,"
"18% recall in production," "latency constraints explained the delta," "follow-up paper on
production learnings," "template for research-to-production collaboration."

---

### Example 5: Being Wrong and Walking It Back (asdg 05, Example 5)

**Question asked:** "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong."

| STAR-L | Condensed real details |
|---|---|
| S | Pushed hard to replace retrieval pipeline with pure long-context approach; argued in two design reviews; team committed a quarter to the migration partly on candidate's conviction |
| T | Owned proving the new system out before full cutover |
| A | Eval results: quality matched, but cost ran 4x projection (cache hit rates collapsed under update frequency; p95 latency doubled); first instinct was to tune out of it; after two weeks of marginal gains, wrote a one-page memo with the numbers, stated plainly that the recommendation had been wrong on the economics; proposed a hybrid: long-context for small static corpora, retrieval for everything else; presented to the same audience originally convinced |
| R | Hybrid kept; salvaged about 60% of migration work; postmortem produced a new team rule: any architecture pitch must include a cost model under realistic update patterns, not just a quality benchmark |
| L | Conviction is useful for getting decisions made and dangerous for unmaking them; now attaches explicit kill criteria to own proposals so walking back is a checkpoint, not a confession |

**Best M3 lesson category:** Ownership (primary); also strong for Failure

**Algorithm framing:** Primary signal: Ownership; secondary: Judgment (kill criteria device).
Unfakeable specificity: "two design reviews," "a quarter committed," "cost ran 4x projection,"
"two weeks of marginal gains," "one-page memo," "60% of migration work salvaged." Note: "fuller
skeleton in asdg-question-taxonomy.md."

---

### Example 6: Raising a Concern That Was Dismissed (asdg 05, Example 6)

**Question asked:** "Describe a time you raised a concern and the team decided against you. What did you do?"

| STAR-L | Condensed real details |
|---|---|
| S | Before a launch, flagged that the agent's tool permissions were broader than the feature needed: it could write to systems it only needed to read; leadership weighed the two-week delay against launch commitments and decided to ship as-is with a fast-follow ticket |
| T | Disagreed with the call; job was to ensure the decision was made with full information, then either escalate or commit |
| A | Wrote the risk down concretely: specific blast radius if the agent was prompt-injected, with a realistic attack path, not a vague "this is risky"; asked for two mitigations that fit inside the launch window: an audit log on the write paths and an anomaly alert on write volume; both accepted; documented disagreement in the decision record and committed to the launch without relitigating in hallway conversations |
| R | Launch was fine; three weeks later the alert fired on a misconfigured integration test (not an attack), but it proved the monitoring worked; the permission scoping shipped a month later, prioritized off the back of that signal |
| L | Being overruled is not the end of the job; converting a lost argument into cheap guardrails and a written record is usually worth more than winning the argument, and builds the credibility that makes the next concern land harder |

**Best M3 lesson category:** Technical Influence (also strong for Conflict)

**Algorithm framing:** Primary signal: Communication/influence; secondary: Judgment (proportional
escalation, specific risk quantification). Unfakeable specificity: "blast radius if prompt-injected,"
"audit log on the write paths," "anomaly alert on write volume," "documented disagreement in the
decision record," "alert fired three weeks later on a misconfigured integration test." Note: "fuller
skeleton in asdg-question-taxonomy.md."

---

## Section 6: Mapping Table

| M3 lesson category | Best worked examples (primary) | Additional useful examples | Real questions to use (top priority) |
|---|---|---|---|
| **Ownership** (`ownership-stories`) | Example 5 (wrong call, walked back publicly) | Example 1 (ambiguity, tech lead with specific result), Example 2 (production failure, flagged immediately) | "Tell me about a time you led a technical initiative without formal authority."; "Describe a project that failed. What happened and what did you learn?"; "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong." |
| **Conflict** (`conflict-stories`) | Example 4 (cross-functional, different priorities, incentive alignment) | Example 6 (overruled, committed and converted) | "Tell me about a disagreement with a colleague about a technical approach."; "Describe working with a team that had different priorities."; "Describe a time you raised a concern and the team decided against you. What did you do?" |
| **Failure** (`failure-stories`) | Example 2 (production underperformance, no hiding, systematic fix) | Example 5 (wrong call: the failure IS the over-conviction story) | "Tell me about an AI system that did not work as expected."; "Describe a time you shipped something that had issues."; "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong." |
| **Technical Influence** (`influence-stories`) | Example 3 (ethical concern, reframed as business risk, standard changed) | Example 6 (overruled but converted; guardrails and written record), Example 4 (template outlasted project) | "Tell me about a time you raised an ethical concern."; "Describe a situation where you had to convince others to adopt a new approach."; "Describe a situation where you prioritized safety over speed."; "Tell me about a time you led a technical initiative without formal authority." |

Note on Example overlap: Examples 4, 5, and 6 serve multiple categories. This is expected and
intentional; the ore's own Preparation Checklist (asdg 05) says to prepare 5-7 stories that
COVER the categories, not one story per category. Lesson authors should choose which framing
to foreground based on the lesson's primary signal, not avoid the example because it appears
elsewhere.

---

## Section 7: Red Flags Master Table (asdg 05, "Red Flags to Avoid")

The ore's canonical table, verbatim:

| Behavior | Why it is a red flag |
|---|---|
| Blaming others | Does not take responsibility |
| No specific examples | May be inflating experience |
| Only technical answers | Lacks awareness of human factors |
| Dismissing ethics | May create liability |
| No questions for interviewer | Lacks curiosity or engagement |

Additional red flags surfaced in the Examples and Themes (asdg 05; distilled above in
per-category failure modes):

| Behavior | Category where it most often surfaces | Ore location |
|---|---|---|
| Using "we" instead of "I" for ownership actions | Ownership | asdg-question-taxonomy.md Signal Cat 1; asdg 05 Example 5 contrast |
| Ending a failure story without the Learning step | Failure | asdg 05 Theme 3 "what they look for"; STAR-L framework throughout |
| Defending a wrong position past the point of evidence | Conflict, Failure | asdg 05 (Red Flags implied); cross-ref asdg-delivery-and-leveling.md A5 |
| Relitigating a decision after committing | Conflict | asdg 05 Example 6 Action step (the positive names the negative) |
| Influence framed as persuasion-winning, not alignment | Technical Influence | asdg 05 Examples 3, 4, 6 (all use alignment-of-incentives, not argument-winning) |
| Ethics framed as obstruction rather than risk | Technical Influence | asdg 05 Example 3 Action step |

---

## Section 8: AI-Specific Behavioral Themes (asdg 05, themes summary)

Five themes the ore names as AI-role-specific. These cut across all four M3 lesson categories;
lesson authors can draw on them for framing context.

| Theme | Ore's "what they look for" (verbatim/trimmed) | Maps to M3 category |
|---|---|---|
| **Theme 1: Handling Ambiguity** | Systematic approach to exploring unknowns; willingness to prototype and learn; knowing when to commit vs. keep exploring | Ownership, Failure |
| **Theme 2: Managing Expectations** | Clear communication without jargon; proposing alternatives, not just saying no; building trust through honesty about limitations | Conflict, Technical Influence |
| **Theme 3: Dealing with Failure** | Taking responsibility; root cause analysis; systems thinking about prevention | Failure, Ownership |
| **Theme 4: Cross-Functional Collaboration** | Respecting different expertise; finding common ground; translating between technical and business language | Conflict, Technical Influence |
| **Theme 5: Responsible AI** | Awareness of AI risks; willingness to slow down for safety; practical approach to mitigation | Technical Influence |

Source: asdg 05, AI-Specific Behavioral Themes.

---

## Preparation Checklist (asdg 05, verbatim, for lesson reference)

The ore's own checklist for candidates; M3 lessons can quote or adapt this directly:

- Prepare 5-7 stories covering: leadership, failure, conflict, ambiguity, learning
- Include at least one story where you were wrong and one where you were overruled
  (Examples 5 and 6 show the shape)
- Practice telling stories in 2-3 minutes (timed), plus a 30-second version of each
- For each story, identify: situation, your specific actions, measurable results, learnings
- Include at least one AI-specific story (model failure, bias, stakeholder education)
- Record yourself once per story and fix what you hear
- Do one full mock with a peer who interrupts
- Prepare 3-5 thoughtful questions for interviewers, including the leveling and compensation
  set for late-stage calls
- Research the company's AI products and potential ethical considerations

Source: asdg 05, Preparation Checklist. Delivery mechanics (two-length discipline,
record-and-review, mock with interruptions) are expanded in
`asdg-delivery-and-leveling.md` Section A.
