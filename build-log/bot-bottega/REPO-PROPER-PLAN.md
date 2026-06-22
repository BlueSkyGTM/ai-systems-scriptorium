# Repo-Proper Plan — the engine (PAFA + Governance as Architecture)

**Status:** bones for review. Final build waits on stress-test data. Built OUTSIDE the Scriptorium,
private for the foreseeable future. This plan supersedes the earlier `PLAN.md` (the agent-os-starter
draft); tonight's session crystallized the architecture much further.

## Goal

A private, cloneable engine repo that lets a **cold agent land dry, self-orient, and produce
production-grade work to a fixed standard, in isolated parallel silos** — with no theory, no vanity,
no recursion-tech. It generalizes what the Scriptorium proved. The same file architecture both
**supplies** the work (PAFA) and **governs** it to a standard (Governance as Architecture).

Success test: drop the repo on a new domain, type `start`, and it recreates what happens in the
Scriptorium — orientation, isolation, standards, gates — without a human re-explaining the project.

## What it is (one line)

The file tree is the **control surface**: routing, isolation, standards, and stopping points are
encoded as files, so the structure onboards and governs cold agents. It is not the whole system —
the operator's live judgment and the reference docs are too. (Reviewers flagged "the file tree IS
the system" as a slogan that papers over the run-state/side-effect problem; see review report.)

## Architecture

Two functions, one tree:

- **PAFA (supply).** A pull-based pipeline laid out as files: ingest -> distill -> inventory ->
  categorize -> scaffold -> mill -> ship. Built bottom-up; run top-down; pulled by address. Deferral
  falls out for free once the inventory (the address book) exists.
- **Governance as Architecture (oversight).** The host does not command, it oversees: holds work to
  an encoded standard, reviews what extensions produce, rejects what misses the bar. Standards,
  gates, and review are files, not a person's memory.

Orchestration:
- **Hosts = teams** (separate chats, separate filesystem lanes, real isolation).
- **Extensions = speed** (sub-agents inside a host; one slice, then dissolve; cannot drift).
- **Cascade governance.** A leaf task is made deadly specific so the leaf is fully blind (its
  blindness is the feature). Standards + context cascade down: each level holds just enough to govern
  its immediate children. Operator anchors the top goal.
- **Two-tier containment.** Hosts kept apart by filesystem boundaries; extensions kept in line by
  serving one conductor. Depth on one axis, isolation on the other.

Quality split (resolves "one standard, many problems"):
- **Universal craft standard** (goal-agnostic: runs / chains its artifact / reads clean / hits the
  difficulty bar) is one shared arm across all silos, because it judges form not content.
- **Goal fitness** ("does this serve THIS silo's problem") is local to each host, which holds that
  silo's goal. The universal arm deliberately never touches the goal.

## The distinctions that make this NOT ICM/MWP (the bones to get right)

1. **Inverted / abstraction layers, worked in reverse, with the operator.** MWP routes *top-down*
   to execute a spec it assumes you already have (CLAUDE.md -> CONTEXT -> stage -> reference ->
   artifacts). This engine adds the missing pass: the stack is *built bottom-up* (data -> purpose)
   and the goal is **co-discovered with the operator** in a loop before any milling. The CLAUDE.md
   is the crown written last, not the seed handed down. MWP has no discovery loop because
   concretization already knows its output; abstraction does not, so the inverted pass is the point.

2. **Staging contracts are vertical (buried per silo), not horizontal (shared stages).** MWP lays
   stages horizontally: one shared pipeline (`stages/01-extraction -> 02 -> 03`) the whole workspace
   walks through. Here, **each silo carries its own staging internally** — a complete vertical
   pipeline per branch. That is what makes "8 chats = 8 teams" instead of "8 chats = 8 stations on
   one belt." Parallelism is by self-contained silo, isolation is structural.

3. **A distillation front-end MWP lacks.** Every MWP example workspace is concretization
   (course-deck, script-to-animation, voice-driven-animation); its Stage 01 is extraction of
   *already-chosen* source. This engine adds Bytes -> Atoms -> Inventory -> Categorize: turning raw
   sprawl into addressable ore *before* a scaffold exists. That is the abstraction-mode contribution.

4. **Cascade depth.** MWP is flat stages + checkpoints + a human. This engine adds nested
   host/extension teams under the same standard.

5. **Operator always present. Full headless is not the goal.** The one job that cannot cascade is
   holding the goal. The operator stays at the goal and the gates.

## Borrowed from MWP (the steal-list — confirmed by reviewing `_core/CONVENTIONS.md`)

1. **One `_core/CONVENTIONS.md`** written as a flat enumerated list: each convention = name + rule +
   example + unambiguous pass condition. Zero theory. (Our STANDARDS/STYLE are the content; this is
   the form that makes them law.)
2. **Selective Section Routing** — load the *section* of a file, not the file. Finer-grained deferral
   than our current file-level loading.
3. **Docs Over Outputs** as explicit law — agents author from reference docs, never from a sibling's
   output ("early outputs are the worst outputs"). This is how you stop the model machine-learning
   its own conventions.
4. **The self-bootstrap kit** — `{{SCREAMING_SNAKE_CASE}}` templates + a `setup` questionnaire that
   fills them + a `status` trigger that reads `output/` folder state to render pipeline progress.
   This is the "lands dry and recreates itself" mechanism, already solved in MWP's `_core/templates/`.

## Repo contents (the bones)

- `README.md` — what it is, how it works start to end, features -> benefits, what it is NOT (no
  recursion, no theory, no magic), status/proof. (The version Ray approved is the template.)
- `_core/CONVENTIONS.md` — the law (enumerated patterns + quality guardrails as lint rules:
  CONTEXT.md < 80 lines, reference < 200, no em dashes, `.gitkeep` for empty persistent folders).
- `_core/templates/` — claude, context, stage-context, questionnaire templates with placeholders.
- A **stripped-down example silo** — one complete vertical pipeline a cold agent can read to recreate
  the pattern (candidate: a minimized Scriptorium book lane, chosen from stress-test results).
- `setup` and `status` triggers wired into the root CLAUDE.md.
- A route-lint equivalent enforcing one-way references, canonical sources, and the line caps.

## Deferred to post-stress-test

- Which silo becomes the stripped example (pick the cleanest cold-proceed from the stress test).
- The final conventions list (let the stress test surface which rules actually caught drift).
- Whether the distillation front-end ships in v1 or is documented as the operator's pre-step.

## Open decisions for review

- **Name.** PAFA (supply) + Governance as Architecture (oversight) are two halves. Does the repo take
  one name, both, or a parent? Recommendation: lead with the practice name, not a thing-name.
- **Front-end scope.** Ship the distillation pipeline as tooling, or as a documented operator
  discipline with templates only? (Tooling is heavier; discipline is more portable.)
- **How much cascade to encode vs leave to the operator.** The leaf-blindness pattern is powerful but
  un-instrumented; risk of over-deferral (a starved leaf fabricates — the M2 citation failure).
- **Universal standard portability.** STANDARDS/STYLE are book-shaped today. What survives when the
  domain is GTM (scoring, outreach, webhooks) instead of books?

## GSTACK REVIEW REPORT

**Run:** autoplan (CEO + Eng + DX, single combined pass — the artifact is a one-page architecture
doc, not code). **Voices:** Codex (gpt-5.5) + an independent blind Claude subagent, run in parallel.
Strong convergence.

### Consensus on the five claimed bones

| Claim | Codex | Claude | Consensus |
|---|---|---|---|
| 1. Inverted layers (build bottom-up, co-discover goal) | SOUND | ORDINARY-RESTATEMENT | DISAGREE — real inside this lineage, ordinary vs the field; both note it describes the discovery, not the artifact discovery must freeze (a SPEC) |
| 2. Vertical per-silo staging contracts | RISK | SOUND-with-cost | CONFIRMED sound, hidden cost: a contract fix must propagate to N silos; no shared schema above them |
| 3. Distillation front-end | SOUND-if-concrete | RISK / maybe out-of-scope | CONFIRMED risk — "comparable systems lack it" is unfalsifiable (RAG/ETL/catalog do this); most book-shaped part; plan defers whether it ships |
| 4. Cascade governance + blind leaf + craft/goal split | RISK | RISK | CONFIRMED risk — blindness = starvation; leaf fabricates (the M2 failure, named in the plan itself); "craft standard" leaks book-meaning ("runs", "difficulty bar" have no GTM analog) |
| 5. Operator always present | SOUND | SOUND-but-contradicts-success-test | CONFIRMED sound — BUT collides with "type start, lands dry, no human re-explaining" (two different products) |

### The killer finding (both, independently)

Biggest non-book risk = **state and side effects**. Books are generative/idempotent; a GTM op mutates
live state (outreach sent, CRM written, webhooks fired) — irreversible, non-idempotent. The plan has
nothing on transactional integrity, and it **dropped its own `sim/` findings** (SIM-FINDINGS #3
rollback, #5 TTL/freshness, #7 idempotency; the SPEC and STATUS primitives) — the v1 must-haves the
same folder already identified. It kept the easy findings and dropped the safety-critical ones.

### Auto-decided revisions (mechanical — per the 6 decision principles)

1. **Re-instate the dropped safety primitives** as first-class repo contents (P1, P2; already in
   `sim/`): a persisted versioned `SPEC.md` (sources, sinks, credentials, thresholds, forbidden
   actions, success test); a live `STATUS`/run-log (idempotency — never re-fire a completed action);
   a Step-0 grounding/discovery pre-step; a task-packet schema (inputs / allowed sources / forbidden
   actions / expected artifact / acceptance checks); a permission model (read/write paths, network,
   secrets, tools, approval gates); evaluator **thresholds** (the dud-detector has none — line caps
   are not quality governance); a dry-run harness with fixtures/fake externals; an audit trail +
   escalation gates for irreversible actions.
2. **Blind-leaf mitigations** (both prescribed the same): a mandatory "insufficient input →
   declare-and-halt" escape at every leaf (so the locally-rational move is refuse, not fabricate); a
   provenance/grounding rule in the craft standard (every leaf output cites the reference doc it came
   from; un-sourced output fails review — makes fabrication lint-detectable); instrument the cascade
   (log what each leaf was given vs produced).
3. **Vanity cuts** (P5 + Ray's own "no vanity" brief): "file tree IS the system" → control surface
   (applied); "production-grade to a fixed standard" → "fixed *craft* standard; domain quality is
   per-silo evaluators"; "type start recreates everything" → gated by the dry-run harness; the "NOT
   ICM/MWP" section demoted to internal design notes (novelty-vs-a-private-predecessor is not an
   external claim); flag the irony both caught — coining PAFA + GaA while swearing off theory.

### Decision Audit Trail

| # | Decision | Class | Principle | Rationale |
|---|---|---|---|---|
| 1 | Re-instate dropped safety primitives | Mechanical | P1, P2 | Already in `sim/`; both voices flagged the drop as the #1 defect |
| 2 | Blind-leaf halt + provenance + instrumentation | Mechanical | P1 | Fixes the named M2 fabrication failure; both prescribed it |
| 3 | Soften vanity claims | Mechanical | P5 | Matches Ray's brief; the doctrine names violated the doctrine |
| 4 | Product-identity fork (autonomous vs power-tool) | TASTE / CHALLENGE | — | Surfaced to operator (D1) |
| 5 | Frozen-goal binding (SPEC contract vs prose brief) | TASTE | — | Surfaced (D2) |
| 6 | Naming (keep coined names?) | USER CHALLENGE | — | Surfaced (D3) — Ray chose GaA last turn |
| 7 | Distillation front-end v1 scope | TASTE | — | Surfaced (D4) |

### Open decisions for the operator

D1 product-identity fork; D2 frozen-goal binding; D3 naming; D4 front-end v1 scope. Presented at the
gate in chat. The auto-decided revisions are applied to this report; the plan body is rewritten once
D1 lands (it reshapes the Goal and the success test).

### Gate outcomes (operator)

- **D1 = operator power tool.** Operator-centric, never headless ("an AI operating system — an OS has
  a user, not headless autonomy"). Reframe the Goal/success test away from autonomous "lands dry."
- **D2 = SPEC.md as a repo primitive** (leaning; SPEC vs hybrid pending confirm). Forced by the
  architecture: every new host / clone / resume is a cold handoff, and a prose-only goal is invisible
  to the next cold host (→ fabrication). A "primitive" = a foundational always-present file (tier of
  README / CLAUDE.md) the rest of the system points to.
- **D3 = NAME = Deferred Context Governance (DCG).** (Supersedes DCA — governance belongs in the
  title, not buried in the body.) Ontology: deferred context is the **tool**, governance is the
  **goal**, the architecture was never the goal. Sharper than ICM: Interpreted Context is
  self-referential and never models the agent's own cognition; DCG governs what the agent thinks
  *with*. Aspirational north-star, not a theory; docs stay plumbing-plain. **PAFA rejected** (a
  cop-out that undersells a deeper, more engineered engine).
- **D2 confirmed = full SPEC.md** (not hybrid). It is the continuity primitive: cold hosts look at
  what still needs doing, not at the operator. Proven by the repo's own origin — a spec called
  "Mariner" (one cowork.md) became this via the discovery layer.
- **D4 = document the distillation front-end as operator discipline** for v1 (recommended; pending
  confirm). Portable; GTM "ore" is live API data, not a static vault, so book-tooling wouldn't transfer.
