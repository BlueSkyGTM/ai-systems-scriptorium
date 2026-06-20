# CLAUDE.md — the AI contract for the AI Systems Scriptorium

This repo is a private, AI-engineering-specialized **library of books + the AI system that builds
them**. (It is **not** "Workspace Builder" and not a generic any-domain tool — that framing is
retired.) You navigate it by the Interpreted Context Methodology (ICM): the folders are a routing
system, and each routed boundary's `CONTEXT.md` is the law for that area.

## The contract

1. **Always start at [`CONTEXT.md`](CONTEXT.md)** — the task router. Match your intent, go to the
   start dir, load its `CONTEXT.md`, follow the routing from there.
2. **Follow the routing.** Treat each boundary's `CONTEXT.md` as binding for that area: load what it
   says to load, skip what it says to skip, hand off where it points.
3. **Do the autonomous work; stop at the gates.** Authoring, verifying, building/testing, relocating,
   cataloguing, fixing paths — do these and report. Stop only at a gate defined in
   [`platform/HUMAN-GATES.md`](platform/HUMAN-GATES.md), and stop by **ID** (e.g. `GATE-LOCK-PLAN`).
4. **Use root-anchored paths.** Cite paths from the repo root or as `platform/route-manifest.yaml`
   keys. Never use a bare relative like `src/module3` — it resolves to the wrong book.
5. **Keep the routing green.** After any change to the tree or routes, run
   `python platform/bin/route-lint`; it must exit 0.

## Precedence rule (closed enumerated list — read before overriding anything)

There are exactly two tiers. No "policy vs. detail" judgment calls.

**Tier 1 — THE POLICY SET. MUST/NEVER. A local `CONTEXT.md` CANNOT override it.** It is, in full:

1. The gates in [`platform/HUMAN-GATES.md`](platform/HUMAN-GATES.md) — every `GATE-*` and its trigger.
2. **This precedence rule itself.**
3. The writing law in [`platform/conventions/STYLE.md`](platform/conventions/STYLE.md) — the Style
   Contract; "if a draft and this contract disagree, the contract wins."

Nothing else is Tier 1. The policy set is fixed by this list — it does not grow by interpretation.

**Tier 2 — everything else is LOCAL-OVERRIDABLE, and local may only NARROW, never broaden.** A
nearest `CONTEXT.md` wins for local specifics (which files to load, which sources are in scope, the
de-dup rules) **as long as it tightens** the parent's instruction. A local file may forbid more, scope
smaller, add a stricter rule. It may **not** loosen a parent restriction, grant itself a Tier-1
exception, or route into an excluded dir. On any apparent conflict: Tier 1 wins absolutely; within
Tier 2, the narrower (nearest, stricter) instruction wins.

`route-lint` enforces the mechanical edges of this rule: gate references must resolve to a
HUMAN-GATES id, no `CONTEXT.md` may claim a task id another already owns, and no live route may point
into `archive/` or `vault/`.

## Don'ts

- Don't genericize the pipeline to non-AI-eng domains — it kills the edge.
- Don't read or modify anything under a path containing `skills/` or `gstack/`.
- Don't route into `archive/` (historical) or treat `vault/` as authoring input (it's raw ore;
  author against `ingredients/`).
