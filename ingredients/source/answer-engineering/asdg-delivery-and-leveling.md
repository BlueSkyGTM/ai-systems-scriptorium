# ASDG Delivery and Leveling

Distilled from:
- `vault/ai-system-design-guide/00-interview-prep/05-behavioral-for-ai-roles.md` (asdg 05)
- `vault/ai-system-design-guide/00-interview-prep/06-job-market-trends-2026.md` (asdg 06)
- `vault/ai-system-design-guide/00-interview-prep/04-whiteboard-exercises.md` (asdg 04)

Purpose: raw material for M2 lessons `thinking-out-loud`, `reading-the-room`,
`the-question-behind-the-question`, and `the-weak-answer-audit`. Does NOT re-distill
anything already covered in `asdg-interview-frameworks.md` or `asdg-question-taxonomy.md`;
cross-references those files by pointer where overlap exists.

---

## Section A: Delivery and Practicing Out Loud

Feeds lesson: `thinking-out-loud`

### A1. The Two-Length Discipline

(asdg 05, Practicing Out Loud)

- Every story must exist in two versions: a **2-minute version** (full STAR-L, all five
  parts) and a **30-second version** (elevator form for "tell me briefly about...").
- The ore states the failure mode directly: "If you only have the long version, you will
  ramble when time is short." Candidates who have rehearsed only the long version are
  caught by a follow-up like "in thirty seconds, what was the outcome?"
- The 30-second version is not a summary of the 2-minute version; it collapses to the
  result and the learning. The situation and task are reduced to one phrase.
- Preparation implication from the ore's checklist (asdg 05, Preparation Checklist):
  "Practice telling stories in 2-3 minutes (timed), plus a 30-second version of each."
  The checklist treats this as a separate rehearsal step, not an afterthought.

### A2. The Record-and-Review Loop

(asdg 05, Practicing Out Loud)

- **One listen-through is the unit.** The ore prescribes: "Record and review once per
  story. One listen-through catches filler words, buried results, and the spots where you
  explain context nobody asked for."
- The ore lists exactly what one listen catches:
  - Filler words (the oral equivalent of weak verbs)
  - Buried results (the result arrives at 90 seconds instead of 60, after context nobody
    asked for)
  - Over-explained context (candidate explains background at the expense of the action
    and result, which is where the signal lives)
- The ore's framing: "You do not need ten takes; you need one honest one." Volume of
  rehearsal is not the variable; the single act of hearing yourself is.

### A3. Additional Practice Mechanics

(asdg 05, Practicing Out Loud)

- **Full mock with interruptions.** Peer runs 3-4 questions and interrupts mid-story
  with "why did you do that?" and "what would you do differently?" The ore's rationale:
  "Real interviewers probe; rehearsing only clean run-throughs leaves you brittle."
- **Drill the bridge sentences.** Transitions ("the result was...", "what I took from
  it...") keep the interviewer oriented. The ore prescribes practicing them until
  automatic, so cognitive load stays on content.
- **One mock per loop stage.** The ore distinguishes three shapes that reward different
  depths: recruiter screen, hiring-manager behavioral, bar-raiser cross-examination.
  At least one round of each shape before a full onsite.

### A4. Real-Time Delivery Mechanics from the Whiteboard Ore

(asdg 04, Tips for Whiteboard Exercises; SPIDER transcript sections throughout)

These are mechanics of a live session: the rhythm of motion and speech, not the
content of any particular solution.

**The narrate-while-drawing rule:**
- The SPIDER transcript (captured in `asdg-interview-frameworks.md`) demonstrates the
  model of narrating every move: "Draws and narrates: SharePoint/Confluence connectors,
  document-AI tier... interviewer probes hybrid retrieval choice. Candidate explains
  why..." The candidate's mouth and pen move together; the interviewer is never watching
  silent drawing.
- The ore makes this structural, not incidental: the SPIDER `I` phase (Initial
  architecture) is timed at 10 minutes of drawing AND explaining simultaneously.

**The check-in rhythm:**
- The ore's pitfall entry (asdg 03, Pitfall 11, captured in `asdg-interview-frameworks.md`)
  states the rule: "Check in every 3-5 minutes: 'Should I go deeper on retrieval or move
  to generation?'"
- In the whiteboard section (asdg 04, Tips for Whiteboard Exercises): "Check in with the
  interviewer on focus areas." This is not politeness; it is a signal-reading opportunity.
  The interviewer's redirect tells the candidate what is actually being probed.
- "Do not spend more than 5 minutes on clarification" and "leave time for reliability and
  evaluation" (asdg 04, Time Management) are the hard time-box rules.

**Signal intent before going deep:**
- The SPIDER transcript's `D` phase (Deep Dive) explicitly models this: "Interviewer
  steers to access control. Candidate leads with the decision, then the reason, then the
  failure mode." This is a structural pattern, not improvisation.
- The ore also states as a named strong-candidate phrase: "I will go deeper on the RAG
  pipeline because retrieval quality is critical here." Declaring intent before diving is
  itself a signal of structured thinking.

**What "thinking out loud" looks like done well vs done badly:**

| Done well | Done badly |
|-----------|-----------|
| Narrates every decision at the whiteboard: "I am putting the reranker here because..." | Silent drawing for 3 minutes, then a summary |
| Leads with the decision, then the reason, then the failure mode | Describes components without explaining why they are there |
| Checks in after each phase: "Should I go deeper or move on?" | Monologues until 35 minutes in, with no check-ins |
| Names what they are deferring: "I will simplify latency here and return to it" | Either ignores latency or digs in without noting the tradeoff |
| Self-critiques before the interviewer asks: "One weakness of this design is..." | Describes happy path only; waits to be challenged |

(Sources: asdg 04 Tips, SPIDER transcript in asdg 02 as captured in
`asdg-interview-frameworks.md`, asdg 03 Pitfall 11-14 as captured in same.)

### A5. Recovery: Correcting Course Mid-Answer

(asdg 03-common-pitfalls, Pitfall 14 as captured in `asdg-interview-frameworks.md`;
asdg 05, Red Flags to Avoid)

- The ore prescribes the recovery line when a candidate realizes they have answered the
  wrong question or defended a wrong position: "That is a good point. I had not considered
  that. Let me revise my approach." (asdg 03, Pitfall 14, Communication pitfalls table.)
- The ore names "defending wrong answers" explicitly as a communication pitfall. The
  reason: it signals low calibration and a fragile ego, both of which predict poorly in
  production environments where being wrong is routine.
- Example 5 in the behavioral ore (asdg 05) models the written equivalent: writing a
  one-page memo stating plainly the recommendation was wrong rather than tuning the
  answer incrementally to avoid admitting error.
- No specific recovery script is given for the case of misreading the question itself
  (e.g., answering a system-design question as if it were a concept question). The ore
  implies the same move: surface the mismatch, re-anchor to the real question, continue.

---

## Section B: Reading the Room and Interview Stages

Feeds lesson: `reading-the-room`

### B1. The Interview Loop: Stages, Signals, and Primary Probes

(asdg 06, Interview Process Patterns; asdg 05 supporting)

The ore presents the May 2026 standard loop at AI-native companies as five stages:

| Stage | Duration | Primary signal collected | What to prepare |
|-------|----------|--------------------------|-----------------|
| Recruiter screen | 30 min | Culture/mission fit, comp expectations, visa, basic role match | Have 30-second career narrative; know comp range; have leveling questions ready for late-stage (asdg 05, Questions to Ask Interviewers, comp/leveling set) |
| Technical phone screen | 60-90 min | Practical coding, production-style problem | Python production code; at least one LLM API integration pattern; algorithm fundamentals still tested at FAANG-tier |
| Take-home (48 hr-3 day) | 48 hr or 3 days | "Not a test of whether you can build, but how: code quality, evals, error handling" (asdg 06 quoting Alexey Grigorev field guide) | Add an AI audit note: what AI tools were used, what was changed, why. Transparency beats stealth. |
| Onsite/virtual loop | 4-6 hr | Coding + AI system design + project deep dive + behavioral | SPIDER for design rounds; STAR-L for behavioral; all four signal categories (see `asdg-question-taxonomy.md`) |
| Hiring manager / values round | Varies | Mission alignment, responsible AI judgment, culture signal | Explicit at Anthropic; weighted heavily at frontier labs. The ore notes Anthropic: "the answer that sounds like it was written the night before is a bad signal." |

Source: (asdg 06, Interview Process Patterns)

**Frontier-lab specifics (asdg 06):**
- Anthropic: 90-minute, 4-level progressively harder coding problem testing whether
  candidate writes clean modular code that absorbs new requirements; explicit Values round.
- OpenAI: "Design the OpenAI Playground" -- wireframes, API, DB schema for thread/message
  history; multi-tenant secure cloud IDE.
- Mistral (Paris): 5-round process, no remote, dedicated "LLM theory" stage covering
  transformer internals and alignment.

**AI-assisted coding is now standard (asdg 06, AI-role specifics):** Meta, Canva, Google,
Microsoft, Sierra, Cursor explicitly allow AI tools (Cursor, Copilot, Claude) in coding
rounds. What is evaluated shifts: prompt skill and output validation, not recall.

### B2. How Company Type Shifts What Is Probed

(asdg 06, Role Taxonomy and Skills by Career Level; asdg 06 company tier table)

| Company type | Emphasis in interview | What this means for prep |
|---|---|---|
| Frontier labs (Anthropic, OpenAI, xAI) | Research-to-production judgment, mission/values alignment, transformer internals, safety and ethics reasoning | Prepare values-round scenarios; know alignment concepts; be ready for LLM theory depth (Mistral stage) |
| Scale-ups (Cursor, Harvey, Sierra, Glean) | Shipping systems end-to-end, TypeScript+Python stack, agent debugging, customer-facing judgment | Sierra is in-person; Plan+Build+Present 2-hour agent assessment; no algorithm rounds |
| Enterprises (Deloitte, EY, Caterpillar, Citi) | Azure/Bedrock-heavy, governance/MLOps focus, on-prem capability, compliance (SOC 2/HIPAA/EU AI Act) | Regulatory fluency matters; FDE-style customer presence often expected |

Source: (asdg 06, What Job Listings Actually Require; asdg 06, By Company Tier)

### B3. Clarifying Questions as Live Signal

The clarifying-question move is already distilled in `asdg-interview-frameworks.md`
(SPIDER S-phase) and `asdg-question-taxonomy.md` (AI/ML Systems-Design Decomposition
Variant). Pointer only: do not re-expand here.

The M2 `reading-the-room` lesson should reference those entries and add ONE point the
taxonomy ore does not: in a live interview, the interviewer's RESPONSE to clarifying
questions is itself data. If they answer quickly and add volunteered detail, they are
signaling the design priority. If they answer minimally ("up to you"), they are signaling
that the scoping judgment itself is what is being tested.

---

## Section C: Leveling -- Senior vs Staff vs Principal

Feeds lessons: `the-question-behind-the-question` and `the-weak-answer-audit`

### C1. Role Taxonomy and Level Definitions

(asdg 06, Skills by Career Level; asdg 06, Role Taxonomy in 2026)

The ore organizes levels by what is expected at each band:

| Level | Band | What differentiates this level from the one below |
|-------|------|---------------------------------------------------|
| Mid-level IC | L4-L5 (3-5 yrs) | Hands-on with major LLM provider SDK + at least one orchestration framework; RAG fundamentals; containerization; cloud basics. "Python production proficiency" in 71% of AI job postings. |
| Senior IC | L6-L7 | "Production LLM systems shipped end-to-end." Multi-tenant isolation, eval-gated CI/CD, cost optimization, token budgets, model routing. The ore's language: "industry experience shipping real systems is a better signal than an academic credential." |
| Staff IC | L8+ | Owns agent orchestration layers, model-routing, LLMOps platforms "serving all eng teams." Runtime governance for non-deterministic systems. Architects for SOC 2/HIPAA/EU AI Act. The ore's language: "define technical vision and scale engineering teams matters more than coding prowess alone." |
| Principal/EM track | Director+ | AI Engineering Manager median $293.5K (highest-paying single role, asdg 06). Rubric: "can you put this person in a room with a PM and a junior eng and have them drive technical direction without making a mess" (5 of 7 hiring managers surveyed, per asdg 06, Design Gurus citation). |

Source: (asdg 06, Skills by Career Level; asdg 06, Manager Track)

### C2. The Senior-vs-Staff Distinction in Concrete Terms

(asdg 06, Skills by Career Level L8+; asdg 05; asdg 03 as captured in
`asdg-interview-frameworks.md` Key Takeaways)

The ore provides three concrete differentiators. These are not inferred; they are stated:

**1. Scope of ownership:**
- Senior: owns a system or feature end-to-end.
- Staff: owns the platform other engineers build on. The ore's language at L8+:
  "own agent orchestration layers, model-routing, LLMOps platforms serving all eng
  teams." The scope shift is from "a system" to "the platform that enables systems."

**2. Multiplying others:**
- Senior: high individual technical output.
- Staff: "scale engineering teams" (asdg 06, L8+ language). The hiring manager rubric
  at the manager/staff level: "can you put this person in a room with a PM and a junior
  eng and have them drive technical direction without making a mess."
- The ore in `asdg-question-taxonomy.md` Staff-level tell: "Behavioral prep is what
  separates staff candidates from senior candidates." The communication/influence signal
  is weighted disproportionately at staff because senior ICs are evaluated for technical
  depth; staff ICs are evaluated for whether they multiply others.

**3. Ambiguity tolerance and governance:**
- Senior: makes defensible technical decisions under uncertainty.
- Staff: architects for runtime governance of non-deterministic systems; handles
  compliance (SOC 2/HIPAA/EU AI Act Article 27). The ore at L8+: "trigger DPIA + FRIA
  under AI Act Article 27" is a staff-level responsibility, not a senior-level one.

### C3. What Staff-Level Signal Looks Like in an Answer

(asdg 05, Why Behavioral Questions Matter; asdg 06, L8+ description; asdg 04 strong
candidate distinguishers at exercises 8 and 9)

The ore provides negative and positive markers:

**In behavioral answers:**
- Senior answer: describes a system they built and the technical decisions they made.
- Staff answer: describes the organizational or platform impact of those decisions, and
  how they changed what other engineers could do. The "multiplying others" element is
  stated or clearly implied. Example 4 in asdg 05 (cross-functional collaboration,
  research-to-production) hints at the staff shape: "established a template for
  research-to-production collaboration" -- the result was a reusable organizational
  pattern, not just a shipped feature.

**In system-design answers:**
- The ore's key takeaway (asdg 02, captured in `asdg-interview-frameworks.md` under
  Technical Depth signal): "Always end deep dives with one sentence on observability
  and one on failure modes; this is the single biggest gap between senior and staff
  answers."
- Staff candidates in asdg 04 Exercises 8 and 9 "What Distinguishes Strong Candidates"
  sections name the governance layer unprompted: eval gaming risks, judge calibration
  as a system component with its own eval, memory poisoning as a security surface with
  provenance tags and review gates. These are cross-cutting concerns, not feature-level
  concerns; that cross-cutting awareness is the staff signal.

**In the hiring manager rubric (asdg 06):**
- "Mission alignment and safety judgment heavily weighted at frontier labs" specifically
  for EM and staff-equivalent roles. Senior candidates can be technically brilliant and
  safety-neutral; staff candidates at frontier labs are expected to demonstrate explicit
  safety judgment.

### C4. The Behavioral Prep Separates Staff from Senior Point

(asdg, cross-references: `asdg-question-taxonomy.md` Staff-level tell; asdg 05 Why
Behavioral Questions Matter; asdg 06 L8+)

The ore makes the claim without hedging: behavioral prep separates staff from senior.
The reason is structural: senior ICs are evaluated primarily on the technical signal;
staff ICs are evaluated for whether they can operate across organizational boundaries
and multiply other engineers. The communication/influence signal category
(see `asdg-question-taxonomy.md`) carries more weight at staff and above.

Concretely, what makes a staff-level behavioral answer different from a senior-level one:
- Senior: "I built X and it worked / failed / taught me Y."
- Staff: "I built X, which changed how the team could build Y and Z; here is the
  template or standard or pattern that came out of it."
- The staff answer includes an organizational artifact: a process, a standard, a
  platform, a rubric, a pattern other engineers adopted.

### C5. Compensation Ranges as Context

(asdg 06, Compensation Reality; labeled as ore's 2026 figures, treat as rough anchors
only; verify at levels.fyi)

The ore provides these as the US national bands for AI Engineer, not frontier labs:

| Level band | Base (2026 ore figure) | Total comp (2026 ore figure) |
|---|---|---|
| Entry 0-2 yr | $90-135K | $110-160K |
| Mid 3-5 yr | $140-210K | $170-260K |
| Senior 6-9 yr | $180-280K | $220-350K+ |
| Staff/Principal 10+ yr | $250-400K+ | $350-600K+ |

Frontier-lab contrast (Anthropic SF, from ore): Senior SWE $316K base / $563K TC;
Lead SWE $332K base / $785K TC. Ore's summary: "the gap between frontier-lab MTS comp
(~$600-795K median at Anthropic/OpenAI) and enterprise AI engineering (~$170-260K
mid-level) is 3-5x."

Source: (asdg 06, Compensation Reality, May 17 2026 sweep; ore's own caveat: "Verify
with levels.fyi for current data.")

Comp is included here only as context for the leveling conversation; it is not a lesson
focus. Lesson authors should link to the ore directly if they cite figures; do not
reproduce the full table in lesson prose.

---

## Cross-Reference Summary for Lesson Authors

| M2 lesson | Primary ingredient section to use | Pointer to M1 ingredient |
|---|---|---|
| `thinking-out-loud` | Section A (A1-A5) | A4 references SPIDER transcript detail in `asdg-interview-frameworks.md` |
| `reading-the-room` | Section B (B1-B2); B3 is pointer only | B3 points to `asdg-interview-frameworks.md` SPIDER S-phase and `asdg-question-taxonomy.md` AI/ML Systems-Design Decomposition Variant |
| `the-question-behind-the-question` | Section C1, C2, C3 | C2 references `asdg-question-taxonomy.md` Staff-level tell under Signal Category 4 |
| `the-weak-answer-audit` | Section C2, C3, C4 | The pitfalls catalog is in `asdg-interview-frameworks.md`; use this file for the leveling-bar layer of the audit |
