# What role did ICM and the agentic primitives actually play? (7 cold-agent sims, v0 kit)

Question (Ray): across the simulations, what role did ICM, or any form of agentic structure, actually play?
Method: 7 cold Sonnet agents, identical v0 boot kit, one domain each, no access to the real repo.

## ICM (per-area routing, kit Step 4): OPT-IN, and the agents discriminated correctly

| # | Domain | ICM earned? | Boundaries the agent drew |
|---|--------|-------------|----------------------------|
| 1 | Book authoring (origin) | yes | platform / per-book / lab |
| 2 | Family-system-site (mid) | yes | content / design-system / contributors |
| 3 | GTM engine (live-ops) | yes (+ hard firewall) | signals / pipeline / integrations |
| 4 | Flat CLI tool | **NO** (correctly flat) | none — agent called routing "pure overhead" |
| 5 | Multi-service SaaS backend | yes, **heavy** | 5 services + a 6th for the billing webhook |
| 6 | Personal-finance OS | **partial** | ingestion + ledger; demoted "reporting" to output logic |
| 7 | Home-lab model host | yes (+ gated stub) | provision / serve / monitor + a gated network/ stub |

**Finding:** ICM is not the spine. It is an opt-in layer the gig earns, and the "earn your routing"
heuristic worked empirically — agents *reasoned* about it: the flat tool refused it, the SaaS backend
earned it six-deep, finance correctly demoted a non-boundary. ICM was load-bearing for multi-area systems
(6/7), dead weight for the flat tool (1/7, correctly skipped), partial where an area did not earn it.
The opt-in call in the plan is validated by observation.

ICM's specific weak spots (raised in nearly every multi-area sim): the earn-it test is undefined (agents
invented their own, e.g. "a boundary has rules that survive change in other areas"); no depth rule (when
a sub-area earns a 2nd-level CONTEXT — SaaS billing, GTM payments); no named pattern for a "gated stub
boundary" (an area that is almost entirely human-gated, e.g. home-lab network/).

## The primitives that fired in ALL 7 (the real spine)

1. **Action-class authorization (the gate model)** — used in all 7; the single most load-bearing primitive
   (it is what makes the thin slice safe: stop before external-mutation). Also the **most strained**: every
   domain needed a refinement the 5 classes lacked — footprint/sensitive reads (GTM, finance), blast-radius
   local-mutations (family-site), security-surface local-mutations (home-lab), a taste gate vs. a risk gate
   (book), a financial-mutation sub-class (SaaS, finance), and a structured gate *artifact/protocol* the
   human signs (SaaS). This is where v1 effort belongs, not ICM.
2. **Fail-fast thin-slice** — used in all 7, stood in all 7. The cleanest-transferring primitive and the
   reason each sim was cheap and conclusive. Empirically answers the reviewers' "is the walking skeleton the
   right primitive?" — yes. Only gaps: a "runnable vs. described" honesty flag, and a stub/sandbox pattern
   when the slice needs a credential (finance, GTM).
3. **Spec / onboarding intake** — used in all 7; a coherent spec each time (no dud-1 declared anywhere).
   Transferred. Gaps: a discovery/grounding pre-step (unknown stack), and missing slots (data-sensitivity,
   freshness/TTL, state-ownership, migration contract).

## The primitive that fired CONDITIONALLY (opt-in, like ICM)

4. **Orchestration (conductor/handler/worker)** — invoked only in the fan-out cases (SaaS = 5 parallel
   handlers; book = chapter parallelism; GTM at scale). Correctly skipped for the sequential/flat cases
   (CLI, single-account finance, home-lab setup). Gaps: fan-IN / serial integration, retry-idempotency,
   and the handler output contract.

## Headline

The engine's spine is **spec-intake + action-class authorization + fail-fast thin-slice** — these fired
and held in every domain. **ICM and orchestration are both opt-in layers the gig earns**, and cold agents
earned or skipped them correctly with no help. So the engine is real and domain-general; the place to
invest in v1 is the **authorization model** (universal + universally strained), then the discovery step
and the rollback/recovery contract for stateful systems (SaaS, home-lab, GTM, finance). ICM needs only a
sharper earn-it test, a depth rule, and a gated-stub pattern — it is already doing its job.
