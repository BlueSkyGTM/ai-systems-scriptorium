# agent-os-starter — Simulation Findings (v0 boot kit)

Method: three cold Sonnet agents, each given ONLY `BOOT-KIT.md` (v0) + one domain gig, told to
self-orient, derive a spec, classify actions, and stand up a thin slice. Domains span the distribution:
**book authoring** (origin/control), **family-system-site** (mid), **GTM engine** (live-ops, hardest).

## Result: the mold transfers

All three derived a coherent spec and stood a thin slice from one page, with no access to the real
Scriptorium machinery. The engine is not book-specific. Thesis validated empirically. **Build is justified.**
v0 is ~80% there; the gaps below are the v1 spec, found cheap.

## The punch-list (v0 gaps -> v1 must-haves)

Ordered by how many domains hit it and severity.

1. **Step 0: a discovery/grounding pass before the spec.** The kit assumes the agent knows the stack.
   A cold agent cannot ground the spec or the thin slice without first learning the tech stack, entry
   commands, schema, and source-of-truth files. Add an explicit first read-only action; add a
   **"runnable vs. described" thin-slice** distinction so an agent never silently pretends to run what it
   cannot. (family-site = biggest gap; book = implicit.)
2. **Refine the action taxonomy** (the 5 classes are too coarse). Add: (a) a **read sub-tier** for
   quota-consuming / footprint-leaving / side-effecting reads (e.g. Clay enrichment, a CRM read that logs
   a "viewed" event) -> treat as local-mutation at minimum; (b) **blast-radius** marking on
   local-mutations (a design-token edit hits every page); (c) a **taste/quality gate** distinct from a
   risk gate (writing a lesson past a human taste gate is local-only but still gated). (GTM + family-site
   + book all hit a facet of this.)
3. **A rollback / compensation contract** for partial multi-system external mutations, defined *before*
   the gate. (GTM, biggest gap: a half-completed push leaves a CRM in a corrupt state and ships bad
   outbound to a real prospect — a real incident. Must be an architecture decision at step 1.)
4. **The contract as a first-class, versioned, machine-checkable component** — not a static "forbidden
   actions" list. (book/control = biggest gap, i.e. what the extraction LOST: this is the Scriptorium's
   STANDARDS/STYLE. Verify is hand-waved without it. Directly answers the reviewers' "the dud detector has
   no thresholds.")
5. **Freshness / TTL** named per state artifact. (GTM: signals go stale; an agent scores dead data.)
6. **Structure as a compliance firewall**, not just organization: some boundaries (authoring vs. push)
   are hard no-cross firewalls. (GTM.)
7. **Fan-in + idempotency** in orchestration: the kit covers fan-out but not serial integration or
   retry-safety (re-running a worker must not re-fire an outbound). (book + GTM.)

## Cross-check vs the autoplan review

The sims confirmed the reviewers empirically: the action taxonomy needed the authorization refinement
(Codex), the contract needs to be machine-checkable/instrumented (both), live-ops needs rollback +
freshness (Codex's "GTM is dangerous"), and the control case exposed that the extraction under-carried
the standards contract. Nothing the reviewers raised was a false alarm; nothing new is fatal.

## Verdict

Build `agent-os-starter` v1 with the seven fixes folded into the boot kit and the core. Build it OUTSIDE
the Scriptorium (sibling repo, salvage by copy). Suggested confirm-loop: patch the kit to v1, re-run the
GTM sim (hardest case); if the gaps close, the core is validated and we build it out.
