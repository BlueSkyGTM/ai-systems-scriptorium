# ASDG Systems Design — M5 Reference Ingredient

Distilled from:
- `vault/ai-system-design-guide/00-interview-prep/02-answer-frameworks.md` (primary ore:
  SPIDER framework, worked design transcript, ETA / tradeoff / debugging frameworks, common
  mistakes) — abbreviated below as **asdg 02**
- `vault/ai-system-design-guide/00-interview-prep/04-whiteboard-exercises.md` (9 whiteboard
  design exercises with full solution walkthroughs) — abbreviated below as **asdg 04**
- `vault/ai-system-design-guide/00-interview-prep/03-common-pitfalls.md` (20 named pitfalls
  across architecture, technical knowledge, communication, interview strategy, AI-specific) —
  abbreviated below as **asdg 03**
- `vault/ai-system-design-guide/00-interview-prep/01-question-bank.md` (Q1-Q116; 5 system
  design scenarios; design-prompt-style questions only pulled) — abbreviated below as **asdg 01**

Cross-references (do NOT re-distill; pointer only):
- `ingredients/source/answer-engineering/asdg-interview-frameworks.md` — ETA, tradeoff,
  debugging, STAR-L framework detail
- `ingredients/source/answer-engineering/asdg-question-taxonomy.md` — Q1-Q49 concept and
  technical question taxonomy

Distillation date: 2026-06-21
Scope: systems-design interview ore for Answer Engineering M5. Dense; no prose polish.
Everything traces to real ore; no invented examples.

---

## Section 1: The SPIDER Framework

**Source:** asdg 02, "System Design Framework (SPIDER)" and "Worked Example: SPIDER in a
45-Minute Session"

SPIDER is the ore's canonical framework for any AI system design interview question.
Six phases with a hard 45-minute time budget across them.

### Time budget per phase (asdg 02, SPIDER mermaid diagram)

| Phase | Letter | Time | Core move |
|---|---|---|---|
| Scope and Clarify | S | 5 min | Narrow the problem space; show you think before you build |
| Prioritize Requirements | P | 3 min | State what matters most; design toward it explicitly |
| Initial Architecture | I | 10 min | Draw the high-level system before diving into details |
| Deep Dive Critical Paths | D | 15 min | Show depth on 2-3 areas; signal intent before diving |
| Evaluate and Observability | E | 5 min | Metrics, eval, monitoring, alerting |
| Reliability and Scale | R | 5 min | Failure modes and growth; where are the bottlenecks? |

Total: 43 minutes active + buffer. The ore notes that if the interviewer cuts you off, hitting
the highest-signal phases (S, I, D) still produces a strong signal. (asdg 02, Key Takeaways)

### S — Scope and Clarify

**Purpose:** "Narrow the problem space and show you think before you build." (asdg 02)

**Anti-pattern named in ore:** "Jumping straight into architecture without understanding
requirements." (asdg 02, S anti-pattern)

**Key questions to ask (asdg 02, S phase):**
- What is the scale? (users, requests, data volume)
- What are the latency requirements?
- What accuracy or quality bar must we meet?
- Are there compliance or security requirements?
- What is the existing infrastructure?
- What is the budget constraint?

**Example in ore** (asdg 02, S phase example): chatbot scoping — candidate asks about volume,
customer-facing vs internal, language support, ticketing integration, accuracy/escalation target.

### P — Prioritize Requirements

**Purpose:** "Identify what matters most and design toward it." (asdg 02)

**Move:** Create an explicit priority matrix (latency, accuracy, cost, multi-language) and
state priorities out loud before drawing anything. (asdg 02, P phase)

**Sample language from ore:** "Given these requirements, I will prioritize latency and
accuracy. Cost optimization will be a second-order concern once we have the basic system
working." (asdg 02)

### I — Initial Architecture

**Purpose:** "Draw the high-level system before diving into details." (asdg 02)

**Standard AI system components named in ore (asdg 02, I phase):**
```
Client → API GW → AI Layer → LLM(s)
                  ↓
                Data/RAG
```

**Move:** Explain each component briefly — what it does, why needed, what alternatives exist.

### D — Deep Dive Critical Paths

**Purpose:** "Show depth on the most important parts." (asdg 02)

**Selection criteria for what to deep dive (asdg 02):**
- What the interviewer seems most interested in
- What is novel or complex about this system
- Where the biggest risks lie

**Example deep dives named in ore (asdg 02):**
- RAG pipeline: chunking, embedding, retrieval, reranking
- Agent loop: tool selection, error handling, termination
- Data pipeline: ingestion, processing, indexing
- Security: isolation, permissions, audit

**Signal move:** "I will now go deeper on the RAG pipeline since retrieval quality is critical
to this system." (asdg 02, D phase example)

### E — Evaluation and Observability

**Purpose:** "Show you think about production operations." (asdg 02)

**Four things to cover (asdg 02, E phase):**
1. Metrics: what to measure (latency p50/p95/p99, token usage/cost, quality scores, error
   rates by type, cache hit rates)
2. Evaluation: how you know it works
3. Monitoring: how you detect problems
4. Alerting: when humans get paged

**Key Takeaway from ore:** "Always end deep dives with one sentence on observability and one
on failure modes; this is the single biggest gap between senior and staff answers." (asdg 02)

### R — Reliability and Scale

**Purpose:** "Address failure modes and growth." (asdg 02)

**Failure modes to discuss (asdg 02, R phase):**
- LLM provider outage
- Rate limiting
- Bad model outputs
- Data pipeline failures
- Cache invalidation

**Scaling questions to address (asdg 02, R phase):**
- Where are the bottlenecks?
- What scales horizontally vs vertically?
- What costs scale with usage?

---

## Section 2: The SPIDER Worked Transcript

**Source:** asdg 02, "Worked Example: SPIDER in a 45-Minute Session"

**Design problem:** "Design a document Q&A system for a 10,000-employee company."

**What this transcript demonstrates (asdg 02, end of transcript):**
- Scope took five minutes and produced numbers the whole design referenced
- Candidate narrated while drawing and invited steering at each phase
- Deep-dive answers led with the decision, then the reason, then the failure mode
- Candidate critiqued their own design before the interviewer had to
- Evaluation was part of the design, not an afterthought

### Transcript skeleton (asdg 02, timestamp-annotated)

**[0:00 - S: Scope]**
Candidate asks: document count, types, freshness. Gets: 2M docs, mixed PDFs/wikis, daily
freshness. Asks: accuracy bar, internal vs customer-facing. Gets: internal, soft accuracy bar,
p95 under 3s. Candidate states back: 500-2,000 queries/hour at peak from 5% of 10K employees.
Interviewer confirms.

**[0:05 - P: Plan out loud]**
Candidate names the full pipeline in one sentence before drawing: ingestion (connectors, parsing,
chunking, embedding, vector store) + serving (query, hybrid retrieval, rerank, generation with
citations, response) + eval/monitoring as cross-cutting layer.

**[0:08 - I: Draw and narrate]**
Connectors pull from SharePoint/Confluence nightly. PDFs: document-AI tier + vision-LLM fallback
for complex layouts. Chunking: structure-aware, 300-500 tokens, headers prepended. Embeddings
into vector DB with metadata: source, team, date, access tags.

Interviewer probes: "Why hybrid retrieval instead of pure vector?"
Candidate: "Internal corpora full of project codenames and acronyms. Embeddings miss exact-match
tokens; BM25 catches them. RRF to fuse, cross-encoder rerank on top 50. That combination is the
difference between 70% and 90%+ retrieval hit rate here."

**[0:18 - D: Deep dive where interviewer steers]**
Interviewer: "Go deeper on access control."
Candidate: "Permissions evaluated at retrieval time, not index time. Every chunk carries ACL
tags. Retrieval query filters on caller's groups before similarity scoring. Index-time filtering
breaks the moment permissions change. Cache keys include the permission set so cached answers
never leak across groups."

**[0:30 - E: Self-critique]**
Candidate flags own weaknesses unprompted: nightly sync = up to 24h staleness (acceptable per
requirements; would add webhook-based invalidation for wikis later). Reranker adds ~150ms at
p95. Failure modes: provider outage falls back to second model; retrieval returning nothing
returns "not found in our docs" rather than letting model improvise.

**[0:38 - R: Latency budget + quality eval story]**
Candidate: "3s p95 gives a budget of ~400ms retrieval, ~150ms rerank, ~2s generation, with
streaming so perceived latency is under a second. For quality: 200-case golden set from real
employee questions, score faithfulness and citation accuracy with LLM judge calibrated monthly
against human review, sample 2% of production traffic."

---

## Section 3: The 9 Whiteboard Exercises

**Source:** asdg 04, Exercises 1-9 (all sections)

This is the primary worked-example bank for M5 lesson authors. Each entry: short title,
problem premise, scale/constraints, key components a strong design includes, and 2-3
production-reasoning anchors specific to that exercise.

---

### Exercise 1: Enterprise RAG System

**Source:** asdg 04, "Exercise 1: Enterprise RAG System"

**Problem premise:** RAG-based knowledge assistant for a large enterprise.

**Scale/constraints:**
- 10 million documents from multiple sources (SharePoint, Confluence, Google Drive, wikis)
- 50,000 employees with role-based access
- Documents update continuously
- Must respect document permissions at query time
- Sub-3 second response time for 95% of queries
- Multiple languages (English, Spanish, Mandarin)

**Key components a strong design includes (asdg 04, Ex 1):**
- Connectors with delta sync per source (Graph API, webhooks, push notifications)
- Adaptive chunking by document type: Markdown/HTML by headers; PDFs layout-aware; wikis by
  section; target 512 tokens / 50-token overlap
- Multilingual embedding: Cohere embed-v3 (multilingual) as primary
- Vector DB (Pinecone or Qdrant at this scale) with metadata filtering for permissions
- Hybrid retrieval: vector search + BM25; RRF fusion; cross-encoder rerank (bge-reranker-v2-m3)
- Permission resolution at retrieval time (not index time), cached with 5-min TTL
- Generation with citation enforcement; "not found" response when retrieval returns nothing
- Offline metrics: Precision@5, Recall@5, MRR, RAGAS (faithfulness, relevance)
- Online metrics: user feedback, query reformulation rate, citation click-through

**Production-reasoning anchors:**
1. **Latency budget math:** Permission (50ms cached) + embedding (100ms) + vector search (100ms)
   + reranking (150ms) + LLM generation (1500ms) + overhead (100ms) = 2000ms (buffer for p95).
   Any design that skips this math leaves the p95 claim ungrounded. (asdg 04, Ex 1, Scaling)
2. **Permission failure mode:** Post-retrieval filtering is a data-leak risk and is explicitly
   called wrong in the ore. Retrieval-time filtering follows the source of truth; index-time
   filtering breaks the moment permissions change. (asdg 04, Ex 1, Query Pipeline)
3. **Freshness vs. webhook cost tradeoff:** Nightly sync = up to 24h staleness; acceptable for
   the stated requirements; webhook-based invalidation added for wikis later as a cost-justified
   upgrade. This is the design's named weakness; the candidate who surfaces it unprompted
   demonstrates production maturity. (asdg 02, transcript 0:30; asdg 04, Ex 1 patterns)

---

### Exercise 2: Customer Support Chatbot

**Source:** asdg 04, "Exercise 2: Customer Support Chatbot"

**Problem premise:** AI-powered customer support for an e-commerce company.

**Scale/constraints:**
- 10,000 conversations per day
- Product catalog (1M products), order history, FAQs
- Goal: resolve 70% of tickets without human handoff
- Multilingual (3 languages), integration with Zendesk

**Key components a strong design includes (asdg 04, Ex 2):**
- Agent with flow control: Intake → Classify → Router → specialized flows (Order, Product Q&A,
  Returns, Human)
- Four named tools: lookup_order, search_products, create_return, escalate_to_human
- Escalation criteria (6 named): explicit request, high negative sentiment, payment disputes, low
  confidence after 2 attempts, complex multi-order issues, refund above threshold
- Zendesk integration: webhook receives tickets; AI handles via API; resolution closes ticket;
  escalation assigns to queue with context summary; all interactions logged to ticket timeline

**Production-reasoning anchors:**
1. **Escalation criteria specificity:** The ore names six explicit escalation triggers, not just
   "low confidence." A design that has only a confidence threshold misses the business-logic
   cases (payment disputes, refund thresholds). (asdg 04, Ex 2, Escalation Criteria)
2. **Tool scoping:** write tools (create_return) vs. read tools (lookup_order) are separated.
   The create_return tool carries an explicit reason and items list, not a free-form string.
   This is the minimum scoping pattern; the agent that gets broad write access is a reliability
   and security risk. (asdg 04, Ex 2, Tool Design)
3. **Human handoff with context:** Escalation passes a context summary to the queue, not just
   a ticket number. The ore models this as the mechanism that makes escalation useful rather than
   a fallback that loses work. (asdg 04, Ex 2, Integration Pattern)

---

### Exercise 3: Code Review Assistant

**Source:** asdg 04, "Exercise 3: Code Review Assistant"

**Problem premise:** Automated code review assistant for a development platform.

**Scale/constraints:**
- Reviews pull requests automatically
- Must provide specific, actionable feedback
- Respects repository style guides and conventions
- Integration with GitHub/GitLab
- 50,000 PRs per day

**Key components a strong design includes (asdg 04, Ex 3):**
- Context assembly per changed file: diff, full file content, related files (imports, tests,
  types), repository conventions (.eslintrc, .editorconfig), previous review comments
- Six named review categories: bug_risk, security, performance, maintainability, style,
  test_coverage
- Model selection: Claude Sonnet 4.6 (primary, price-to-quality for code); Opus 4.8 for
  hardest reviews; GPT-5.5 as fallback; CodeQL + LLM for security scanning; linters + LLM
  explanation for style
- Structured output format: critical issues (must fix) vs suggestions (consider fixing), with
  inline before/after code snippets
- Latency target: review ready within 2 minutes of PR creation; parallel processing of files;
  stream results as available; cache repository conventions

**Production-reasoning anchors:**
1. **Context assembly is the design:** The ore spends more lines on what goes into the context
   than on the model call. Previous review comments (learning from feedback), related files
   (imports, tests), and repository conventions are what separate a useful review from a generic
   one. (asdg 04, Ex 3, Context Assembly)
2. **Model tier routing:** Critical security reviews route to Opus 4.8; style violations route to
   linters + LLM explanation (not the frontier model). The design makes explicit that model tier
   matches task severity, not that one model handles all 50K PRs. (asdg 04, Ex 3, Model Selection)
3. **Streaming for perceived latency:** Target is 2 minutes, not 2-minute synchronous wait.
   Streaming results as available means reviewers can start reading before the full review lands.
   (asdg 04, Ex 3, Latency Strategy)

---

### Exercise 4: Document Processing Pipeline

**Source:** asdg 04, "Exercise 4: Document Processing Pipeline"

**Problem premise:** Document processing pipeline for financial services.

**Scale/constraints:**
- 100,000 documents per day (invoices, contracts, forms)
- Extract structured data with 99% accuracy
- Handles PDFs, scanned documents, handwritten notes
- HIPAA/SOC2 compliance
- Human review for low-confidence extractions

**Key components a strong design includes (asdg 04, Ex 4):**
- Pipeline: Ingest → Classify → Extract → Validate → [Auto-pass / Review / Reject]
- Classification: fine-tuned LayoutLMv3 or ViT; confidence threshold 0.95 for auto-routing
- Tiered extraction: Tier 1 = Document AI (Textract/Azure) for structured forms (fast, cheap,
  returns confidence); Tier 2 = Vision LLM (Claude Opus 4.8, GPT-5.5, Gemini 3.1 Pro) for
  complex layouts; cross-validate both outputs
- Named validation rules per document type (invoices: total > 0, date valid, tax ID regex,
  line items sum to total; contracts: 2+ parties, valid date, signature present)
- Human review interface: original doc image, extracted fields with confidence scores, validation
  errors highlighted, LLM-suggested corrections, one-click approval or field-level corrections
- HIPAA/SOC2: AES-256 at rest, TLS 1.3 in transit, audit log for all access and changes, PHI
  detection and masking, retention policies, access controls with MFA

**Production-reasoning anchors:**
1. **Tiered extraction as cost + accuracy lever:** Document AI is cheap and fast; vision LLM is
   the fallback for what Document AI cannot handle. The 99% accuracy target requires combining
   both and cross-validating; neither alone hits the bar for the full document distribution.
   (asdg 04, Ex 4, Extraction Strategy)
2. **Validation rules as named business logic:** The ore provides concrete validation rules, not
   generic "validate the output." The key insight: schema validation is necessary but not
   sufficient; cross-field consistency (line items must sum to total) is where extraction errors
   surface as business failures. (asdg 04, Ex 4, Validation Rules)
3. **Human-in-the-loop interface design:** The reviewer sees the original image alongside the
   extraction, not just the extracted fields. This prevents the reviewer from normalizing
   extraction errors they cannot verify. (asdg 04, Ex 4, Human Review Interface)

---

### Exercise 5: Real-Time Content Moderation

**Source:** asdg 04, "Exercise 5: Real-Time Content Moderation"

**Problem premise:** Content moderation system for a social platform.

**Scale/constraints:**
- 1 million posts per day (text, images, video)
- Latency requirement: under 500ms for posts to be visible
- Detection targets: hate speech, violence, adult content, spam
- Appeal workflow for false positives
- 10 languages

**Key components a strong design includes (asdg 04, Ex 5):**
- Multi-stage cascade: Fast Filters (regex, blocklist, hash matching) → ML Classifiers (BERT
  for text, CLIP for images, X3D for video) → LLM Analysis (context-aware, for uncertain 5%)
  → Human Review (for remaining 0.5%)
- Latency budget: Stage 1 = 20ms; Stage 2 = 80ms (batched GPU); Stage 3 = 400ms async for
  borderline; total 500ms met because only 5% reach Stage 3
- Decision thresholds by category: hate speech (block 0.95, limit 0.80, review 0.60); adult
  content has higher block threshold (0.98) due to legal implications
- Four decision outcomes: BLOCK, ALLOW, LIMIT (reduce distribution), HUMAN_REVIEW
- Appeal workflow: user submits → different reviewer from original (blind review) → decision
  logged with reasoning → if overturned: content restored + original decision added as training
  negative + model retrained periodically

**Production-reasoning anchors:**
1. **Cascade architecture as the latency solution:** The 500ms target is achievable not by
   making each stage fast but by routing 95% of content to stages that cost 20-80ms. The LLM
   stage (400ms) only touches 5% of posts. Any design that routes all content through the LLM
   misses the target by 10x. (asdg 04, Ex 5, Latency Optimization)
2. **Threshold asymmetry is deliberate:** Adult content has a higher block threshold (0.98 vs
   0.95 for hate speech) because of legal implications. The ore names this explicitly; a design
   that uses uniform thresholds across all violation types is missing the business logic layer.
   (asdg 04, Ex 5, Threshold Strategy)
3. **Appeal workflow closes the training loop:** Overturned decisions feed back as negative
   training examples; the model retrains periodically. A design that has appeals only for user
   satisfaction misses the model-improvement flywheel. (asdg 04, Ex 5, Appeal Workflow)

---

### Exercise 6: Multi-Tenant AI Platform

**Source:** asdg 04, "Exercise 6: Multi-Tenant AI Platform"

**Problem premise:** AI-as-a-Service platform for enterprise customers.

**Scale/constraints:**
- 500+ enterprise customers
- Each customer has their own documents and models
- Complete data isolation between tenants
- Per-tenant usage tracking and billing
- Different pricing tiers with different capabilities
- SOC2 compliance required

**Key components a strong design includes (asdg 04, Ex 6):**
- API Gateway enforcing: Auth → Tenant Context → Rate Limit → Route
- Tenant-aware service layer: all operations scoped to tenant_id from context; retrieval
  filters by tenant; cache keys prefixed by tenant; audit logs include tenant
- Three shared infrastructure components: Shared Vector DB (metadata-filtered), Shared LLM
  (no tenant data in prompt history), Shared Object Storage (tenant paths: s3://bucket/{tenant_id}/)
- TenantContext: context manager that sets/clears tenant context on every request
- Middleware enforcing tenant context: extract from auth token → verify access → add to audit log
- Usage tracking schema: tenant_id, timestamp, operation, model, tokens_in, tokens_out, latency_ms,
  cost_cents; real-time usage aggregation in time-series DB + Redis counter for rate limiting

**Production-reasoning anchors:**
1. **Isolation at the metadata filter level, not application level:** The ore shows the "wrong"
   pattern (retrieve top-100, then filter by tenant) and the "right" pattern (filter in the DB
   query). Cross-tenant data retrieved into memory is a data-leak risk even if never returned
   to the user. (asdg 04, Ex 6; also named explicitly in asdg 03, Pitfall 4)
2. **Cache key scoping is not optional:** All cache keys must be prefixed by tenant_id. Without
   this, a cached response from tenant A is served to tenant B with the same query. The ore
   treats this as a critical isolation failure, not an optimization detail. (asdg 04, Ex 6;
   asdg 03, Pitfall 4)
3. **Billing granularity:** The usage schema captures cost_cents at the event level, not the
   daily roll-up. This enables per-operation billing, tier enforcement, and anomaly detection
   on individual requests. Real-time Redis counter for rate limiting runs in parallel to the
   async time-series write. (asdg 04, Ex 6, Billing and Usage Tracking)

---

### Exercise 7: Semantic Search at Scale

**Source:** asdg 04, "Exercise 7: Semantic Search at Scale"

**Problem premise:** Semantic search system for an e-commerce site.

**Scale/constraints:**
- 50 million products
- 100 million queries per day
- P99 latency under 100ms
- Support filters (price, category, brand, ratings)
- Personalization based on user history
- Real-time inventory updates

**Key components a strong design includes (asdg 04, Ex 7):**
- CDN/Edge cache for popular queries (~30% hit rate)
- Query service: embed query → ANN search → apply filters → personalize ranking → return
- Vector DB cluster: sharded by category; HNSW index with ef_search tuned for speed; metadata
  filtering with roaring bitmaps
- Hybrid search with dynamic weights: keyword-heavy queries (sparse 0.7 / dense 0.3); natural
  language queries (sparse 0.3 / dense 0.7); parallel retrieval + RRF merge + personalization boost
- Real-time updates: price/inventory changes flow through Kafka to vector DB metadata (seconds);
  description changes require full re-embed as async job with index swap

**Latency budget (asdg 04, Ex 7):**
```
Edge cache check:    5ms
Embedding lookup:   10ms (cached) / 30ms (compute)
Vector search:      30ms
Filtering:          10ms
Personalization:    10ms
Serialization:      10ms
Network overhead:   25ms
Total:             100ms (with cache hit)
```

**Production-reasoning anchors:**
1. **100ms is not achieved by making each component fast; it is achieved by the cache hit
   design:** The latency budget only closes at 100ms with a cache hit. Without the edge cache
   (~30% hit rate) and pre-computed embedding cache, the path runs to ~130ms+. The budget math
   is the answer to "how do you hit 100ms at this scale." (asdg 04, Ex 7)
2. **Dynamic hybrid weighting by query type:** Keyword-heavy queries ("nike air max 90 size 10")
   use sparse 0.7 / dense 0.3; natural language queries ("comfortable running shoes for flat
   feet") use sparse 0.3 / dense 0.7. A single fixed weight across all query types underperforms
   both extremes. (asdg 04, Ex 7, Hybrid Search Strategy)
3. **Inventory update vs description update are different operations:** Price/inventory changes
   update metadata only (no re-embed needed; propagates in seconds via Kafka). Description
   changes require full re-embed and async index swap. A design that re-embeds on every product
   change will not keep up at 50M products. (asdg 04, Ex 7, Real-Time Updates)

---

### Exercise 8: Evaluation Pipeline for a Production LLM Product

**Source:** asdg 04, "Exercise 8: Evaluation Pipeline for a Production LLM Product" (marked as
NEW in ore)

**Problem premise:** "Your company ships an AI assistant used by 50,000 daily users. Leadership
wants to ship model and prompt changes weekly without quality regressions. Design the evaluation
pipeline: offline evals, CI gating, judge calibration, and production monitoring. Budget: the
eval system itself should cost under 2% of inference spend."

**Scale/constraints:**
- 50,000 daily users; ~150K requests/day
- Weekly ship cadence for model and prompt changes
- Eval system cost cap: under 2% of inference spend

**Key components a strong design includes (asdg 04, Ex 8):**
- Dataset composition: 40% real production traces (stratified by intent cluster), 30%
  known-hard cases from incidents/complaints, 20% adversarial cases, 10% canary cases
  (behavior that must never change); dev set (visible) and held-out set (CI-only, rotated
  quarterly); refreshed quarterly from recent traffic
- Binary pass/fail per dimension (faithfulness, completeness, tone, safety), not Likert scales
  (reason: binary decisions are reproducible; Likert drifts)
- LLM-as-judge: cheap model (Claude Haiku 4.5, GPT-5.5-mini) with rubric and few-shot anchors
  per dimension
- Judge calibration: monthly agreement check against human-graded slice; judge-human agreement
  is a dashboard metric; below 85% agreement the judge prompt gets fixed before drawing any
  product conclusions
- CI gating: hard gates (safety regression blocks merge); soft gates (2pt quality regression
  threshold); overfitting warning (held-out success < dev success - 5pp)
- Production monitoring: 1-5% sampled judge scoring trended daily; outcome linkage (complaint
  rate, thumbs-down, escalation rate plotted against eval scores; divergence triggers eval
  review); drift alarms (input distribution shift, score drop by segment, judge agreement decay)

**Cost calculation from ore (asdg 04, Ex 8, Cost Control):**
- Sample 2% of 150K/day = 3K judged requests/day
- Judge cost: ~1K tokens per judgment at $1/1M model = ~$3/day
- Weekly human slice: 100 cases × ~3 min reviewer time
- CI runs: 500 cases × ~2K tokens per PR = under $2 per PR
- Total: well under 2% budget; human slice is the dominant cost

**What distinguishes strong candidates (verbatim from asdg 04, Ex 8):**
- Design the dataset before the scorer; a great judge on a stale dataset measures nothing
- Treat the judge as a system component with its own eval (calibration vs humans), not as
  ground truth
- Name eval gaming risks unprompted: dev-set overfitting, judge sycophancy, metric narrowing,
  silent exclusion of hard cases
- Link offline scores to production outcomes instead of celebrating green dashboards
- Quantify the eval budget and place the expensive human grading where it has the most leverage

**Production-reasoning anchors:**
1. **Eval gaming risks are the "what makes this hard" answer:** The ore explicitly names
   dev-set overfitting, judge sycophancy, metric narrowing, and silent exclusion of hard cases.
   A candidate who names these unprompted is demonstrating production experience, not theory.
   (asdg 04, Ex 8, What Distinguishes Strong Candidates)
2. **The judge needs its own eval:** Judge-human agreement below 85% invalidates the product
   conclusions, not just the eval. The calibration check is a gate before interpreting eval
   results, not a nice-to-have. (asdg 04, Ex 8, Scoring Design)
3. **Budget math closes at human grading, not LLM judging:** The LLM judge costs ~$3/day; the
   human slice (~100 cases/week) is the expensive part. But the human slice is what keeps the
   judge honest. Cutting it to save money destroys the calibration anchor. (asdg 04, Ex 8, Cost)

---

### Exercise 9: Memory and State for a Long-Running Agent

**Source:** asdg 04, "Exercise 9: Memory and State for a Long-Running Agent" (marked as NEW in
ore)

**Problem premise:** "Design the memory system for a personal AI assistant that works with a
user over months: it should remember preferences and facts, learn from past sessions, recall
relevant history at the right moments, and forget what it should not keep. Sessions can run
for hours. Support 1M users."

**Scale/constraints:**
- 1 million users
- Sessions up to hours long
- Cross-session memory that persists over months
- GDPR deletion requirement
- Latency budget: p95 < 150ms for recall on each turn

**Key components a strong design includes (asdg 04, Ex 9):**

**Memory hierarchy (L1-L4):**
- L1 Working memory: the context window; current session, tool results, scratchpad; managed by
  compaction + just-in-time loading
- L2 Episodic memory: what happened; past session summaries, trajectories, outcomes; vector DB,
  retrieved by similarity + recency
- L3 Semantic memory: what is true; extracted facts and preferences with provenance; structured
  records or knowledge graph
- L4 Procedural memory: how to do things; learned workflows, per-user playbooks; versioned
  files loaded on demand

**Write path (the hard part per ore):**
- Session end (or checkpoint): summarize episode → L2 (embedding + metadata: timestamp, topics,
  outcome, sentiment)
- Fact extraction pass → candidate facts → deduplicate against L3 → conflict check
- Conflict resolution: newer + higher confidence supersedes (keep old with valid_to timestamp);
  ambiguous → store as candidate, confirm with user at next natural opportunity
- Importance filter: discard chit-chat; keep preferences, commitments, corrections
- Bitemporal records (valid_from, valid_to) make supersession auditable and reversible

**Read path:**
- Each turn builds recall query from current intent; retrieves top-k from L2 (similarity +
  recency + importance weighting) and matching facts from L3
- Relevance gate: drop weak matches rather than stuffing them in; wrong memories poison
  the response worse than missing ones
- Recall budget: a few hundred tokens of memory per turn, never a transcript dump

**Forgetting and privacy:**
- Decay: episodic entries lose retrieval weight over time unless reinforced by access
- Consolidation: periodic job merges related episodes into summaries
- GDPR deletion: per-user partition keys everywhere; deletion removes L2/L3/L4 rows and
  invalidates caches; hard isolation per user; memory never shared across tenants by similarity

**Scale sketch (asdg 04, Ex 9):**
- Storage: thousands of L2 entries + hundreds of L3 facts per active user; vector DB
  partitioned by user_id
- Write path: async after session close; queue + worker pool
- Read path: p95 < 150ms recall (ANN on per-user slice is small)
- Cost: extraction pass uses cheap model (Haiku 4.5 / V4 Flash) with strict schema

**What distinguishes strong candidates (verbatim from asdg 04, Ex 9):**
- Separate in-session context management from cross-session memory instead of conflating them
- Spend time on the write path (extraction, dedup, conflict supersession) rather than only
  on retrieval
- Treat wrong recall as worse than no recall and design the relevance gate accordingly
- Name memory poisoning as a security surface: untrusted content written today and trusted
  tomorrow needs provenance tags and review gates
- Mention production frameworks (Mem0, Zep, Letta) as build-vs-buy options while being able
  to design from primitives

**Production-reasoning anchors:**
1. **The write path is where most candidates go thin:** Extraction, dedup, conflict
   supersession, and importance filtering are all harder than retrieval. The ore names "the
   write path (the hard part)" explicitly. A candidate who only designs retrieval has missed
   the architectural challenge. (asdg 04, Ex 9, Write Path)
2. **Memory poisoning as a security surface:** Untrusted content written into memory today
   can be trusted and acted on tomorrow. This requires provenance tags and review gates, not
   just retrieval quality. The ore names this as a distinguishing signal for strong candidates.
   (asdg 04, Ex 9, What Distinguishes Strong Candidates)
3. **Wrong recall is worse than no recall:** The relevance gate (drop weak matches) is a
   first-class design decision, not an optimization. Stuffing weak memories in poisons the
   response; the ore makes this a named design principle. (asdg 04, Ex 9, Read Path)

---

## Section 4: Weak-Design Red Flags

**Source:** asdg 03 (primary); asdg 02 "Common Mistakes" and "Anti-Patterns to Avoid";
asdg 04 "What Distinguishes Strong Candidates" sections.

These are the named failure modes across all design round pitfalls. Each entry: failure mode
name, one-line description, source citation.

### Architecture Failure Modes

| Failure mode | Description | Source |
|---|---|---|
| **Skipping the data pipeline** | Designs inference path in detail; barely mentions how data gets into the system; assumes embeddings appear magically; ignores updates and deletions. | asdg 03, Pitfall 1 |
| **One-size-fits-all model selection** | Uses a single frontier model for everything; no cost discussion; no model cascade or routing; no latency consideration. | asdg 03, Pitfall 2 |
| **Ignoring the evaluation layer** | Describes how to build the system but not how to know if it works; no test set; no quality metrics; no monitoring for production issues. | asdg 03, Pitfall 3 |
| **Post-retrieval tenant filtering** | Retrieves top-N across all tenants, then filters by tenant in application code; surfaces sensitive documents in memory before filtering; creates data-leak risk. | asdg 03, Pitfall 4 |
| **No graceful degradation** | System has no fallback when LLM provider is down, rate-limited, or returning errors; single provider dependency; no retry strategy. | asdg 03, Pitfall 5 |

### Technical Knowledge Failure Modes

| Failure mode | Description | Source |
|---|---|---|
| **Confusing embedding and generation models** | Attempts to "generate text" with embedding models, or treats generation as retrieval; breaks the RAG architecture conceptually. | asdg 03, Pitfall 6 |
| **Misunderstanding context windows** | Assumes 128K (or 1M) context means 128K tokens of useful context; ignores system prompt, retrieved chunks, conversation history; ignores "lost in the middle." | asdg 03, Pitfall 7 |
| **Ignoring token economics** | Discusses features without understanding cost implications; does not know that output tokens cost 2-4x input tokens; no caching strategy; no per-tier routing. | asdg 03, Pitfall 8 |
| **Shallow RAG understanding** | Can list components (chunk, embed, retrieve, generate) but cannot explain tradeoffs within each stage; no answer for "why hybrid search?" or "when to skip reranking?" | asdg 03, Pitfall 9 |
| **Treating prompts as magic** | Hand-waves "and then we prompt the model" without discussing prompt structure, output format, few-shot examples, or defense against edge cases. | asdg 03, Pitfall 10 |

**Prompt failure modes sub-list (asdg 03, Pitfall 10 table):**

| Prompt failure mode | What it looks like | Defense |
|---|---|---|
| Lost in the middle | Critical instruction at token 40K gets ignored | Put rules at start and end; keep middle for data |
| Instruction hierarchy break | Retrieved document text overrides system prompt | Wrap untrusted content in delimiters; treat as data |
| Format slipping | JSON output degrades after long sessions or model updates | Engine-level structured output (json_schema, tool schemas) |
| Cache-busting dynamism | Timestamp at top of prompt kills prefix cache on every request | Static content first, dynamic content last |
| Prompt-model coupling | Prompt tuned on one provider silently underperforms after model swap | Version prompts with model ID; re-run evals on every model change |

### Communication Failure Modes

| Failure mode | Description | Source |
|---|---|---|
| **Monologuing without interaction** | Talks for 10-15 minutes without checking in; misses signals about what the interviewer cares about; no steering invitations. | asdg 03, Pitfall 11 |
| **Not leading with structure** | Starts talking without signaling what they will cover; interviewer cannot map answer to expectations. | asdg 03, Pitfall 12 |
| **Technical jargon without explanation** | Drops terms ("PagedAttention," "GQA") without explaining; appears to name-drop; invites follow-up questions they may not be able to answer. | asdg 03, Pitfall 13 |
| **Defending wrong answers** | Doubles down when interviewer hints approach is wrong; stubbornness is a red flag; being coachable is valuable. | asdg 03, Pitfall 14 |

### Interview Strategy Failure Modes

| Failure mode | Description | Source |
|---|---|---|
| **Solving a different problem** | Gets excited about a technology and designs for it instead of stated requirements; adds multi-agent complexity to a simple Q&A prompt. | asdg 03, Pitfall 15 |
| **Not managing time** | Spends 20 minutes on architecture; no time for evaluation, reliability, or scaling; violates the 5/5-7/10-15/5-7 allocation. | asdg 03, Pitfall 16 |
| **Not drawing** | Describes architecture verbally without diagramming; visual communication shows stakeholder fluency. | asdg 03, Pitfall 17 |

### AI-Specific Failure Modes

| Failure mode | Description | Source |
|---|---|---|
| **Treating AI components as black boxes** | "Call the LLM" treated as atomic; no understanding of prefill vs decode, TTFT vs TPS, KV cache implications, batching effects. | asdg 03, Pitfall 18 |
| **Ignoring hallucination risk** | Designs system that blindly trusts LLM output; no retrieval grounding, citation enforcement, abstention, output validation, or confidence display. | asdg 03, Pitfall 19 |
| **Security as an afterthought** | Security considerations come at the end (or not at all); prompt injection, data leakage, and tenant isolation are novel AI attack surfaces that must be designed in. | asdg 03, Pitfall 20 |

### Eval-Specific Failure Modes (from asdg 04 "What Distinguishes Strong Candidates" sections)

| Failure mode | Description | Source |
|---|---|---|
| **Dataset designed after scorer** | Building the LLM judge before the dataset; a great judge on a stale dataset measures nothing. | asdg 04, Ex 8 |
| **Treating judge as ground truth** | Judge is a system component that needs its own calibration against human graders; below 85% agreement, judge prompt must be fixed before drawing product conclusions. | asdg 04, Ex 8 |
| **No offline-to-production linkage** | Green eval dashboards without checking whether they correlate to outcome metrics (complaint rate, thumbs-down, escalation); divergence signals an eval review is needed. | asdg 04, Ex 8 |
| **Memory write path omitted** | Designing retrieval only; missing extraction, dedup, conflict supersession, importance filtering — the part the ore calls "the hard part." | asdg 04, Ex 9 |
| **Wrong recall not treated as worse than no recall** | Stuffing weak memories into context rather than gating by relevance; wrong memories poison the response worse than missing ones. | asdg 04, Ex 9 |

---

## Section 5: Systems-Design Question Types

**Source:** asdg 01, System Design Scenarios (unnumbered, pp. 2349-2510); asdg 01 selected
design-prompt Qs from the numbered bank. Design-prompt-only; concept and behavioral questions
excluded.

### The 5 named design scenarios (asdg 01, System Design Scenarios section)

All are 35-minute exercises with explicit requirement sets:

| Scenario | Core design challenge | asdg 01 location |
|---|---|---|
| Design a customer support chatbot | Agent with RAG + tools + escalation + ticketing integration; multi-language | Scenario 1 |
| Design a document processing pipeline | Tiered extraction + validation + human-in-the-loop + compliance | Scenario 2 |
| Design a RAG system for enterprise search | Multi-tenant, permission filtering, hybrid search, real-time indexing | Scenario 3 |
| Design a code assistant | Repository-aware context, code-specific chunking, latency, privacy | Scenario 4 |
| Design an AI-powered content moderation system | Cascading classifiers, multi-modal, threshold tuning, human review, feedback loop | Scenario 5 |

### Design-prompt questions from the numbered bank (asdg 01; design-prompt-style only)

| Question | Category | asdg 01 location |
|---|---|---|
| "Walk me through the architecture of a production RAG system." | Full system design | Q1 |
| "How would you evaluate a RAG system?" | Eval system design | Q5 |
| "How would you handle multi-tenant RAG systems?" | Security/isolation design | Q7 |
| "How would you design a multi-agent system?" | Agent architecture design | Q14 |
| "How would you handle long-running agent tasks?" | State management design | Q16 |
| "How do you design a feedback loop for continuous improvement?" | MLOps pipeline design | Q37 |
| "Design an evaluation system for comparing two LLMs on open-ended tasks." | Eval system design | Q42 |
| "Design a system where one user's prompt cannot leak to another user." | Security design | Q58 |
| "Design a semantic cache that actually works in production." | Optimization/reliability design | Q64 |
| "How would you design a system that uses Claude Code as a CI/CD component for automated bug fixing?" | Agent pipeline design | Q68 |
| "How would you design a semantic routing system that dynamically selects the cheapest model that can handle a query with acceptable quality?" | Cost optimization design | Q73 |
| "How would you design a multi-provider LLM architecture for 99.9% availability?" | Reliability design | Q77 |
| "Design a Process Reward Model (PRM) for a customer-support agent." | Eval/RL system design | Q89 |
| "Your RAG agent reads web pages from untrusted sources. Design a layered defense against indirect prompt injection." | Security design | Q96 |
| "Design a real-time fraud detection system with a hard p99 < 500ms latency requirement." | Latency-constrained design | Q108 |
| "Design a skill system for a fleet of internal agents using Agent Skills." | Agent architecture design | Q114 |

**Grouping by design challenge type (derived from asdg 01 coverage):**

- **RAG system design:** Q1, Q5, Q7, Scenarios 1, 3
- **Agent / multi-agent design:** Q14, Q16, Q68, Q114, Scenarios 1, 4
- **Eval pipeline design:** Q5, Q42, Q89, Exercise 8 (asdg 04)
- **Security / isolation design:** Q7, Q58, Q96, Scenario 3
- **Cost and optimization design:** Q73, Scenario 5, Exercise 7 (asdg 04)
- **Reliability / availability design:** Q77, Pitfall 5 (asdg 03)
- **Document processing / extraction:** Q9, Scenario 2, Exercise 4 (asdg 04)
- **Memory and state design:** Q16, Exercise 9 (asdg 04)

---

## Section 6: Production-Reasoning Anchors (the L3 differentiator)

**Source:** asdg ch.11-14 (infrastructure, security, reliability, evaluation/observability),
surveyed for the production-reasoning moves a candidate deploys in a design round; grounded
externally against Microsoft Learn (Azure Well-Architected Framework for AI workloads + Azure
AI Foundry observability). Every MS-Learn URL below was fetched live 2026-06-21 and its content
confirmed to match the claim — cite these, do not invent others.

This is the ore for Lesson 3. The thesis: a merely-senior candidate optimizes ONE dimension
(usually latency or cost); a STAFF candidate threads cost + latency + reliability + evaluation
together and names the tradeoff when they conflict. The Well-Architected AI design-principles
page makes that tradeoff framing explicit ("Trade-off: Cost Optimization and Performance
Efficiency"), which is exactly the staff move.
**MS-Learn anchor (tradeoff framing):** https://learn.microsoft.com/azure/well-architected/ai/design-principles

### Pillar 1 — Cost / Token Economics

**Vault anchors (asdg ch.11):**
- ★ **Model routing by complexity** saves 50-80%: route 60-70% of simple queries to cheap models
  (Haiku/4o-mini), complex to frontier. (asdg 11/01-llm-infrastructure, Cost Optimization Strategies)
- **Semantic caching** (>0.95 cosine) targets 30%+ hit rate; the second lever after routing. (same)
- **Batch API** = 50% discount for jobs that tolerate async (nightly index refresh, eval runs). (same)
- ★ **Self-hosting crossover ~10M queries/month**, and the hidden cost is 1-2 dedicated engineers —
  naming that hidden cost is the staff signal. (asdg 11/01, Deployment Options)
- ★ **Quality-adjusted cost:** a frontier model at 200 tokens / 90% accuracy can beat a cheap model
  at 500 tokens / 50% accuracy once rework + fallback cost is counted. (asdg 14/02-observability,
  Cost Metrics)

**MS-Learn grounding:** "The same user can cost $0.001 one minute and $0.40 the next, depending on
context length, retrieval depth, and which model the request was routed to." Token spend scales
with context length, not user count; GPU idle time is the largest hidden self-hosted cost.
https://learn.microsoft.com/azure/well-architected/ai/design-principles (Cost Optimization:
"determine the cost drivers"; "pay for what you intend to use")

### Pillar 2 — Latency / Throughput

**Vault anchors (asdg ch.11, 13):**
- **TTFT vs total latency are separate budgets:** streaming makes a 2s TTFT feel fast even if total
  is higher; budget both. (asdg 11/01, Monitoring and Alerting)
- **P95/P99 SLA per use case**, not one global target (customer-facing p95 < 10s; background
  p99 < 120s). (asdg 11/01)
- ★ **Request hedging:** fire primary, after N ms fire redundant requests to other providers, take
  first response — costs 2-3x on the tail but buys p99 you can't negotiate from a provider.
  (asdg 13/03-reliability-patterns, Request Hedging)
- ★ **Inference is memory-bound, not FLOPS-bound:** KV-cache and concurrency saturate memory
  bandwidth first; "more GPUs ≠ more throughput." (asdg 11/01, Capacity Planning)

**MS-Learn grounding:** establish performance benchmarks as an ongoing operational process; collect
telemetry and identify bottlenecks (query latency, throughput, orchestrator local-vs-network time);
multimodal responses add significant latency.
https://learn.microsoft.com/azure/well-architected/ai/design-principles (Performance Efficiency)

### Pillar 3 — Reliability / Safety

**Vault anchors (asdg ch.12, 13):**
- **Retry with exponential backoff + jitter** for transient errors only; distinguish retryable
  (RateLimit, Timeout) from non-retryable (Auth, BadRequest). (asdg 13/03, Retry Patterns)
- **Circuit breaker** (open after N failures, half-open test) fails fast instead of timing out
  during an outage. (asdg 13/03, Circuit Breaker)
- **Graceful degradation ladder:** Full → Reduced (simpler model) → Minimal (cache) → Offline. (asdg 13/03)
- ★ **Never design around a single provider:** multi-provider failover with health checks; assume
  the provider WILL fail. (asdg 13/03, Multi-Provider Failover)
- ★ **IPI is the dominant attack vector now** (not direct injection): tag content trust level,
  guardrail untrusted content, gate write-capabilities when reading untrusted input. (asdg 12/01,
  Indirect Prompt Injection)
- ★ **Hallucination: retrieval quality is the primary lever** — the LLM cannot fix bad retrieval;
  prompt/output-validation/abstention are secondary layers. (asdg 13/01-guardrails)

**MS-Learn grounding:** distribute across Availability Zones; design for graceful degradation during
partial failures (serve simpler models / limit features); health monitoring with Azure Monitor.
https://learn.microsoft.com/azure/cloud-adoption-framework/ai/infrastructure/well-architected (Reliability)

### Pillar 4 — Evaluation / Observability

**Vault anchors (asdg ch.13, 14):**
- **Offline eval gates deploys; online eval (1-5% sample) detects drift** — offline does not catch
  all real-world issues. (asdg 14/01-llm-evaluation; asdg 14/02-observability)
- **LLM-as-judge needs debiasing:** run both A-vs-B and B-vs-A to detect 60-70% positional bias;
  a panel of diverse judges beats a single judge. (asdg 13/02-ensemble-methods)
- **CI quality gate** with concrete thresholds (golden set > 95%, avg quality > 4.0, no regressions)
  blocks the deploy; **canary** (5% → bake 30 min → increment) with **auto-rollback** triggers. (asdg 11/02-cicd)
- **RAG eval is four metrics:** faithfulness + relevance + context precision + context recall;
  evaluate retrieval separately from generation. (asdg 14/01, RAGAS)
- ★ **2026 layered eval stack:** distilled judges inline on all traces + frontier judge on a sample
  + human gold set; for agents grade the *trajectory* (PRM) and use **pass^k** (e.g. 70% pass^1 but
  12% pass^4 = fragile), not single-shot. (asdg 14/01, 2026 Eval Evolution)

**MS-Learn grounding:** Azure AI Foundry Observability = three capabilities — Evaluation (built-in
groundedness/relevance/safety/tool-accuracy evaluators), Monitoring (token use, latency, error
rates, quality scores via App Insights, alert on threshold breach), and Tracing (OpenTelemetry).
Three lifecycle stages: pre-production evaluation (bring-your-own-data + simulators/red-teaming),
and post-production continuous evaluation on **sampled** production traffic + scheduled eval for
**drift**. https://learn.microsoft.com/azure/ai-foundry/concepts/observability

### How the lesson uses this section

L3's worked examples (Content Moderation = latency cascade; Eval Pipeline = CI gating) already
carry per-exercise anchors in Section 3. This section supplies the *transferable* production
reasoning the candidate threads across any design, plus the authoritative external grounding so a
claim like "evaluate on a sampled fraction of production traffic" cites Microsoft Learn rather than
floating free. The staff move to teach: pick the two pillars the prompt stresses, go deep, and name
the tradeoff against a third.

