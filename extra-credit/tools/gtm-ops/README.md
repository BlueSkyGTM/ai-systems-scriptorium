# gtm-ops

> The career-ops signal engine, repointed from careers to **go-to-market**: ingest signals → score →
> run a governed pipeline → push to the CRM. The curriculum's agent patterns, applied to a real
> business domain.

Tier: tool · Status: **spec (pre-build)** — engine/layer architecture pending a `/browse` study of the
two source repos.

## What it does

[career-ops](https://github.com/santifer/career-ops) is itself a **Clay mimic for job search**: it
ingests signals and **generates a tailored resume per target** from them. GTM Ops keeps that engine —
signal-driven *tailored generation* — and repoints the output from resumes to **GTM artifacts**
(tailored outbound, sequences, account briefs). The symmetry is exact: a tailored resume for a job is a
tailored pitch for an account.

The flow: ingest signals (accounts, intent, enrichment) → **score** → **generate** the tailored
artifact → move it through a **governed pipeline** → **webhook** into the real stack (**Clay** for
enrichment/orchestration, **HubSpot** for the CRM system of record). Note the loop closes on itself —
career-ops *mimics* Clay; GTM Ops plugs that same engine back into the *actual* Clay + HubSpot.

This is a **lab tool**, not a change to the book pipeline — an *application* of the AI-engineering
patterns to GTM, and a deployed-system portfolio piece (the "strong project" bar from `hireability`).

## Source material (study before coding — `/browse` both)

- **Engine** — [santifer/career-ops](https://github.com/santifer/career-ops): a **Clay mimic** whose
  pipeline turns signals into **tailored resumes**. So the engine is signal-driven *generation +
  scoring*, not scoring alone — that generation step is the heart of what we port. *Exact shape (model
  vs. heuristic vs. staged LLM pipeline) — resolve via `/browse`.*
- **Intelligence layer** — [KarlRaf/gtm-starter-kit](https://github.com/KarlRaf/gtm-starter-kit): the
  GTM domain logic that powers it (ICP, signals, enrichment, sequences). *Map its surface via `/browse`.*

## Architecture (intent — to be grounded against the repos)

```
signals ──▶ ingest/enrich ──▶ score (engine) ──▶ governed pipeline ──▶ webhook ──▶ Clay / HubSpot
            (gtm-starter-kit)   (career-ops)        (loop + budgets)     (out)
```

The seam to keep portable: a typed **Signal → Score → Action** contract, so the engine doesn't care
whether the source is Clay, a CSV, or a webhook, and the CRM target is swappable.

## Constraints — free-tier only

Webhook Clay and HubSpot **only to utilize their free features** — never integration for its own sake.
Every external call must earn its keep on a free tier:

- **Clay** — free credits are scarce; gate every enrichment behind the M4 cost governor and skip any
  call that doesn't change a decision. No paid waterfalls by default.
- **HubSpot** — use the free CRM surface (contacts / deals / properties / basic associations) and design
  around free API limits; do not assume paid workflows or automation.

If a step needs a paid feature to work, that's the signal to keep it **inside the engine** rather than
webhook out. The integration is a means, not the point.

## Connections

Run by the connect protocol ([`../../CONTEXT.md`](../../CONTEXT.md)) against our material — GTM Ops is
the curriculum, applied:

- **lesson** — [M3 · The agent loop](../../../library/completed/sans-python/src/module3/01-the-agent-loop.md) — the research/scoring agent at the core of the engine.
- **lesson** — [M3 · Tool use](../../../library/completed/sans-python/src/module3/06-tool-use.md) — Clay, HubSpot, and enrichment APIs are typed tools the loop calls.
- **lesson** — [M4 · The four primitives & orchestration](../../../library/completed/sans-python/src/module4/03-four-primitives-and-orchestration.md) — the pipeline is orchestration, not a pile of scripts.
- **lesson** — [M4 · The loop](../../../library/completed/sans-python/src/module4/10-the-loop.md) — run the GTM pipeline as governed infrastructure: a verifier in the wire, an off-switch outside it.
- **lesson** — [M4 · Action budgets & cost governors](../../../library/completed/sans-python/src/module4/06-action-budgets-and-cost-governors.md) — cap Clay/enrichment **credit spend** before a run becomes a bill.
- **lesson** — [M5 · Data ingestion (Docling)](../../../library/completed/sans-python/src/module5/11-data-ingestion-docling.md) — ingest company docs/decks/filings into the signal layer.
- **lesson** — [M2 · Evaluation](../../../library/completed/sans-python/src/module2/05-evaluation.md) — LLM-as-judge scoring is the same machinery as lead/account scoring.
- **lesson** — [M2 · Context engineering](../../../library/completed/sans-python/src/module2/02-context-engineering.md) — the **tailored generation** step is signal-context assembled into the prompt; tailoring quality is context quality.

## Open decisions (flag before build)

1. **What is career-ops's "engine"?** Port a trained model, or its scoring/pipeline logic? Decides whether GTM Ops carries weights or is pure logic. (`/browse`.)
2. **Clay role** — source of signals, enrichment step, *and* a webhook target, or just one? Clay can both call out and receive.
3. **HubSpot write scope** — read/score only, or write back (create/update records, scores)? Writing is a real side effect — gate it like any HITL action (M4 lesson 08 pattern).
4. **Runtime/host** — local script + webhooks, or a deployed service? A deployed service is what makes it a portfolio piece.

## Build plan (when greenlit)

1. `/browse` [career-ops] and [gtm-starter-kit]; write a one-page architecture extract (the engine's real shape + the layer's surface).
2. Lock the portable **Signal → Score → Action** contract.
3. Stub the engine + the Clay/HubSpot webhook adapters behind that contract (offline-testable first).
4. Wire cost governors (M4) around every paid enrichment call.
5. Deploy + a README that frames the problem, the metrics, and the tests — the strong-project bar.
