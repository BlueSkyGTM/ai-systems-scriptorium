# ASDG Interview Frameworks and Pitfalls Catalog

Distilled from: `vault/ai-system-design-guide/00-interview-prep/02-answer-frameworks.md`
and `vault/ai-system-design-guide/00-interview-prep/03-common-pitfalls.md`.

Purpose: raw material for M1 Lesson 2 (construct the answer -- Algorithm step 3) and for
the pitfalls material feeding step 4 (stress-test). The frameworks are the ore's named
constructs; they are NOT invented for this book. Each is presented here in compressed
form for lesson-authors to work from.

---

## The Five Named Frameworks (asdg 02-answer-frameworks)

### Framework 1: SPIDER

**What it is:** A six-phase structure for answering any systems-design interview question
involving AI components. The ore presents it as the primary framework for 45-minute loops.

**Phases and time budget (from ore):**

| Phase | Letter | What you do | Time |
|-------|--------|-------------|------|
| Scope and clarify | S | Ask about scale, latency, accuracy bar, compliance, existing infra, budget | 5 min |
| Prioritize requirements | P | Create a priority matrix; state priorities explicitly before designing | 3 min |
| Initial architecture | I | Draw the high-level system; explain each component briefly (what, why, alternatives) | 10 min |
| Deep dive critical paths | D | Choose 2-3 areas to go deep; signal intent before diving ("I will go deeper on the RAG pipeline because retrieval quality is critical here") | 15 min |
| Evaluation and observability | E | Metrics, evaluation approach, monitoring, alerting | 5 min |
| Reliability and scale | R | Failure modes, scaling bottlenecks, cost scaling | 5 min |

**Algorithm step 3 mapping:** SPIDER is a construction tool for systems-design questions.
It maps directly onto "how to construct the answer" (Algorithm step 3) when the question
type is a design prompt. Lesson 2 should name this explicitly: if the question is a design
prompt, SPIDER is the construction scaffold.

**Key ore insight (asdg 02-answer-frameworks, Key Takeaways):**
"Always end deep dives with one sentence on observability and one on failure modes; this
is the single biggest gap between senior and staff answers."

### Condensed SPIDER Transcript (gist, from asdg 02-answer-frameworks worked example)

Prompt: "Design a document Q&A system for a 10,000-employee company."

The 45-minute transcript demonstrates these moves in order:

- **[0:00 S]** Candidate asks: document count, freshness requirement, internal vs external,
  accuracy bar, p95 latency budget. Interviewer answers: 2M mixed documents, daily freshness,
  internal, soft accuracy bar, p95 under 3s. Candidate converts to numbers: 500-2,000 queries/hour
  at peak. Interviewer confirms.
- **[0:05 P]** Candidate names the full pipeline out loud before drawing anything: ingestion
  on the left (connectors, parsing, chunking, embedding, vector store), serving on the right
  (query, hybrid retrieval, rerank, generation with citations), eval and monitoring as a
  cross-cutting layer.
- **[0:08 I]** Draws and narrates: SharePoint/Confluence connectors, document-AI tier with
  vision-LLM fallback for complex layouts, structure-aware chunking 300-500 tokens, vector DB
  with metadata (source, team, date, access tags). Interviewer probes hybrid retrieval choice.
  Candidate explains why: internal corpora are full of project codenames and acronyms;
  embeddings miss exact-match tokens; BM25 catches them; RRF to fuse; cross-encoder rerank
  on top 50. "That combination is the difference between 70% and 90%+ retrieval hit rate here."
- **[0:18 D]** Interviewer steers to access control. Candidate leads with the decision, then
  the reason, then the failure mode: permissions evaluated at retrieval time not index time;
  every chunk carries ACL tags; the retrieval query filters on the caller's groups before
  similarity scoring, so a result the user cannot read never enters the candidate set;
  index-time filtering breaks the moment permissions change; cache keys include the permission
  set to prevent cross-group leakage.
- **[0:30 E]** Candidate critiques own design before interviewer asks: nightly sync means up
  to 24h staleness; reranker adds ~150ms at p95 (acceptable for quality); failure modes named
  (provider outage falls back to second model; retrieval returning nothing returns "not found
  in our docs" rather than letting the model improvise).
- **[0:38 R]** Candidate checks requirements explicitly: 3s p95 gives a budget of ~400ms
  retrieval, ~150ms rerank, ~2s generation, with streaming so perceived latency is under a
  second. Names eval plan: 200-case golden set from real employee questions; faithfulness and
  citation accuracy scored by LLM judge calibrated monthly against human review; 2% production
  sample.

**What the transcript demonstrates (ore's own summary, asdg 02-answer-frameworks):**
- Scope took five minutes and produced numbers the whole design referenced.
- Candidate narrated while drawing and invited steering at each phase.
- Deep-dive answers led with the decision, then the reason, then the failure mode.
- Candidate critiqued own design before the interviewer had to.
- Evaluation was part of the design, not an afterthought.

---

### Framework 2: ETA

**What it is:** A three-part structure for concept explanation questions ("Explain RAG,"
"What is speculative decoding?"). Ordered from simple to technical to applied.

**Steps:**

| Letter | What you do | Example (KV cache) |
|--------|-------------|-------------------|
| Explain simply | One-sentence definition anyone can understand | "KV cache stores intermediate computations during LLM generation so we do not have to redo work for previous tokens when generating each new token." |
| Technical details | Add depth appropriate for the interviewer | Memory formula, layers, heads, sequence length; per-request memory at 70B/8K context |
| Applications and tradeoffs | Connect to practical usage; discuss tradeoffs | Production serving requires it; PagedAttention and GQA exist to reduce KV cache memory; context caching features from providers are server-side KV cache persistence for shared prefixes |

**Algorithm step 3 mapping:** ETA is the construction tool for technical-depth questions
where the question type is conceptual ("explain" or "what is"). When the ore's question
bank asks Q22 (KV cache), Q23 (speculative decoding), Q28 (RAGAS), or similar, ETA is
the appropriate construction scaffold. The lesson should contrast it with SPIDER: ETA is
for explaining a component; SPIDER is for designing a system.

---

### Framework 3: Tradeoff Analysis

**What it is:** A four-step framework for comparison and justification questions ("compare
embedding model options," "RAG vs fine-tuning," "when would you skip reranking?").

**Steps (from asdg 02-answer-frameworks):**

1. State the options clearly (two or three named options, not "depends")
2. Define evaluation criteria weighted for the specific decision (quality, cost at scale,
   latency, operational overhead -- the weights change per context)
3. Analyze each option against the criteria; build a comparison matrix
4. Make a recommendation with reasoning; name the risk and how you mitigate it

**Algorithm step 3 mapping:** Tradeoff analysis is the construction tool when the
question contains "compare," "choose between," "when would you use X vs Y," or "justify."
The ore's Q2 (RAG vs fine-tuning) and Q19 (SLM vs frontier) are the canonical examples.
The key construction move: candidates who say "it depends" without naming what it depends
on and how each dependency changes the answer fail to demonstrate judgment. The framework
forces the second half of the sentence.

**Ore's key insight (asdg 02-answer-frameworks, Key Takeaways):**
"'It depends' is fine ONLY when followed by 'it depends on X, Y, Z, and here is how each
changes the answer'; otherwise it reads as hedging."

---

### Framework 4: Debugging Framework

**What it is:** A four-step diagnostic motion for troubleshooting questions ("how would you
debug X," "the system is doing Y, how do you fix it," "your RAG system works in test but
fails in production").

**Steps (from asdg 02-answer-frameworks):**

1. Gather information: When, who, what. "When did this start? What changed? Is it all
   requests or a subset? What does the error look like exactly? Are there patterns (time of
   day, user segment, query type)?"
2. Form hypotheses: 3-5 candidates ranked by likelihood. "Based on the symptoms, my top
   hypotheses are: retrieval quality degraded; model output quality dropped; context length
   exceeded; rate limiting causing timeouts."
3. Describe diagnostic approach: traces, isolation, comparison to known-good baseline.
4. Propose fixes and verification plan: fix per hypothesis; roll out gradually; set up
   monitoring to catch recurrence.

**Algorithm step 3 mapping:** The debugging framework is the construction tool for
production-incident and troubleshooting questions. The candidate who leads with
"gather information, form hypotheses, isolate, verify" is demonstrating the systematic
approach the interviewer is looking for. The ore's Q51 (47 LLM calls instead of 5),
Q55 (RAG works in test but fails in production), and Q113 (computer-use agent fails 30%
of real workflows) are all debugging-framework questions.

---

### Framework 5: STAR-L

**What it is:** The behavioral answer framework. STAR (Situation, Task, Action, Result)
extended with Learning, the additional step that separates AI-role behavioral answers from
generic behavioral answers.

**Steps:**

| Letter | What you do | Common failure |
|--------|-------------|----------------|
| Situation | Set context briefly; enough for the interviewer to understand the stakes | Too long; goes past two sentences |
| Task | What was your SPECIFIC responsibility (not "we were trying to") | Using "we" instead of "I" |
| Action | What did YOU do? Use "I", be specific about the moves | Describing intent ("I decided to investigate") instead of action ("I instrumented detailed tracing and found...") |
| Result | Quantify: percent improvement, time saved, complaints dropped | Ending with "the decision was made" without saying what happened |
| Learning | What would you do differently? What changed in how you work? | Omitting this entirely; "I learned it was important to communicate" (too vague) |

**Algorithm step 3 mapping:** STAR-L is the construction scaffold for all behavioral
questions. The lesson should name the two moves that separate strong STAR-L answers from
weak ones: (1) the "I" discipline (use the first person for every action; "we" hides
ownership), and (2) the quantified result (behavioral answers without numbers "get scored
as anecdotal" -- asdg 02-answer-frameworks Key Takeaways).

**The L is load-bearing for AI roles.** The ore explains why (asdg 05-behavioral-for-ai-roles,
Why Behavioral Questions Matter): AI projects have unique characteristics (uncertainty, rapid
change, cross-functional work, ethical concerns) that behavioral questions probe specifically.
The Learning step is where the candidate demonstrates they have internalized the AI-specific
lesson, not just learned a generic one.

**Two preparation signals the ore calls out (asdg 05-behavioral, Practicing Out Loud):**
- Candidates need two lengths per story: 2-minute full STAR-L and 30-second elevator version.
  If only the long version exists, they will ramble when time is short.
- Record and review once per story: one listen-through catches filler words, buried results,
  and over-explained context.

---

## Pitfalls Catalog (asdg 03-common-pitfalls)

This catalog feeds Algorithm step 4 (stress-test) and the "could a weak candidate give this
answer?" check from draft 02-signal-to-answer. Organized by which step they attack.

### Pitfalls that kill the Decompose step (step 1)

| Pitfall | What it looks like | Why it fails | Source |
|---------|-------------------|--------------|--------|
| Jumping to solutions | "I would use LangChain with Pinecone and GPT-5.5." (without any scope) | Signals no production experience; built things without requirements | asdg 03, Pitfall 1 (in frameworks) |
| Solving a different problem | Designs a multi-agent autonomous system when asked for a simple Q&A tool | Excitement about a technology overrides the stated requirements | asdg 03, Pitfall 15 |
| Not asking clarifying questions | Assumes scale, latency, compliance without asking | Misses the decomposition move that is itself a signal | asdg 03 (anti-pattern) |

### Pitfalls that kill the Construct step (step 3)

| Pitfall | What it looks like | Why it fails | Source |
|---------|-------------------|--------------|--------|
| Skipping the data pipeline | Designs retrieval and generation in detail but does not mention how data gets into the system | "A beautiful RAG architecture is useless if the document ingestion pipeline produces garbage chunks" | asdg 03, Pitfall 1 |
| One-size-fits-all model selection | "I would always use the biggest frontier model for the best quality" | No cost analysis, no routing, no cascade; signals no production constraint experience | asdg 03, Pitfall 2 |
| Ignoring the evaluation layer | Describes building the system but not how to know if it works | AI systems fail in subtle ways; without evaluation you ship broken systems and never detect degradation | asdg 03, Pitfall 3 |
| Post-retrieval tenant filtering | `results = vector_db.search(query, top_k=100)` then filter by tenant | "Sensitive documents from other tenants are retrieved and loaded into memory"; this is a security red flag | asdg 03, Pitfall 4 |
| No graceful degradation | "If the LLM fails, the user gets an error" | LLM providers have outages; rate limits get hit; failure handling separates production-ready from prototype | asdg 03, Pitfall 5 |
| Treating prompts as magic | "And then we prompt the model to..." without discussing structure | Does not show operational experience; interviewers want system prompt structure, output format spec, few-shot examples | asdg 03, Pitfall 10 |
| Overcomplicating the design | Three vector databases, a message queue, a stream processor, all before requirements are established | Complexity without justification signals inexperience, not depth | asdg 03, Pitfall -- frameworks Mistake 4 |

### Pitfalls specific to AI systems (what weak candidates miss entirely)

| Pitfall | The gap | Source |
|---------|---------|--------|
| Ignoring hallucination risk | Designs system that blindly trusts LLM output | asdg 03, Pitfall 19 |
| Security as an afterthought | Does not mention prompt injection, data leakage, or output filtering until asked | asdg 03, Pitfall 20 |
| Confusing embedding and generation models | Treats embedding models as if they generate text, or vice versa | asdg 03, Pitfall 6 |
| Misunderstanding context windows | Assumes 1M context window means 1M useful tokens; does not account for "lost in the middle" | asdg 03, Pitfall 7 |
| Not knowing token economics | Discusses features without understanding cost; cannot do a back-of-envelope cost calculation | asdg 03, Pitfall 8 |

### Five named prompt failure modes (new in pitfalls -- worth naming unprompted)

From asdg 03-common-pitfalls, Pitfall 10 extended table. The ore notes: "naming two or three
of these unprompted moves a prompting answer from junior to senior, because each one is a
production incident the interviewer has probably lived through."

| Failure mode | What it looks like | Defense |
|--------------|-------------------|---------|
| Lost in the middle | Critical instruction buried at token 40K gets ignored | Put rules at start and end; keep middle for data |
| Instruction hierarchy break | Retrieved document text overrides the system prompt | Wrap untrusted content in delimiters; treat it as data, never as instructions |
| Format slipping | JSON output degrades after long sessions or model updates | Engine-level structured output (json_schema, tool schemas), not "please return JSON" |
| Cache-busting dynamism | A timestamp at the top of the prompt kills the prefix cache on every request | Static content first, dynamic content last |
| Prompt-model coupling | A prompt tuned on one provider silently underperforms after a model swap | Version prompts with the model ID; re-run evals on every model change |

### Communication pitfalls (attack the signal regardless of technical content)

| Pitfall | Better | Source |
|---------|--------|--------|
| Monologuing without interaction | Check in every 3-5 minutes: "Should I go deeper on retrieval or move to generation?" | asdg 03, Pitfall 11 |
| Not leading with structure | Lead with a roadmap: "I will structure my answer in four parts..." | asdg 03, Pitfall 12 |
| Jargon without explanation | Brief explanation when introducing terms: "vLLM, which implements PagedAttention -- this manages the KV cache like virtual memory, reducing fragmentation" | asdg 03, Pitfall 13 |
| Defending wrong answers | "That is a good point. I had not considered that. Let me revise my approach." | asdg 03, Pitfall 14 |

---

## Quick Reference: Signals of Strong Answers vs Weak Answers

From asdg 02-answer-frameworks. Load-bearing for the stress-test step (step 4).

| Strong signal | Weak signal |
|---------------|-------------|
| Asks clarifying questions | Jumps to architecture immediately |
| Uses concrete numbers ("adds ~50ms latency") | Uses ranges without anchoring ("probably fast enough") |
| Discusses tradeoffs explicitly ("we gain X but lose Y") | Names one option without acknowledging alternatives |
| Mentions failure modes proactively | Describes happy path only |
| References real systems or research | Stays at abstract level |
| Checks in with interviewer | Monologues for 10 minutes |
| Connects to personal experience | Describes what "someone" would do |
| Acknowledges uncertainty honestly | Claims certainty where none exists |
