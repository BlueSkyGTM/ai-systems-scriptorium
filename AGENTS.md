# AGENTS.md — the AI contract (AI Systems Scriptorium)

Same contract as [`CLAUDE.md`](CLAUDE.md); this file exists for agents that read `AGENTS.md`. If the
two ever disagree, they are a bug — fix both. This repo is a private, AI-engineering-specialized
**library of books + the AI system that builds them** (not "Workspace Builder", not a generic tool).

## The contract

1. **Always start at [`CONTEXT.md`](CONTEXT.md)** — the task router. Match intent → start dir → load.
2. **Follow the routing.** Each routed boundary's `CONTEXT.md` is law for that area: load what it
   says, skip what it says, hand off where it points.
3. **Do the autonomous work; stop at the gates.** Author, verify, build/test, relocate, catalog, fix
   paths — do these and report. Stop only at a gate from [`platform/HUMAN-GATES.md`](platform/HUMAN-GATES.md),
   cited by **ID**.
4. **Root-anchored paths only** (or `platform/route-manifest.yaml` keys). No bare relatives.
5. **Keep routing green:** `python platform/bin/route-lint` must exit 0 after any tree/route change.

## Precedence rule (closed enumerated list)

Two tiers, no judgment calls.

**Tier 1 — THE POLICY SET (MUST/NEVER; a local `CONTEXT.md` CANNOT override it), in full:**
(1) the gates in [`platform/HUMAN-GATES.md`](platform/HUMAN-GATES.md); (2) this precedence rule
itself; (3) the writing law in [`platform/conventions/STYLE.md`](platform/conventions/STYLE.md).
Nothing else is Tier 1; the set does not grow by interpretation.

**Tier 2 — everything else is LOCAL-OVERRIDABLE, and local may only NARROW, never broaden.** The
nearest `CONTEXT.md` wins for local specifics as long as it tightens the parent. It may forbid more
or scope smaller; it may not loosen a parent restriction, grant a Tier-1 exception, or route into an
excluded dir. Conflict resolution: Tier 1 wins absolutely; within Tier 2, the narrower instruction wins.

## Don'ts

- Don't genericize the pipeline beyond AI-eng. Don't touch paths containing `skills/` or `gstack/`.
- Don't route into `archive/` (historical) or author against `vault/` raw ore (use `ingredients/`).
