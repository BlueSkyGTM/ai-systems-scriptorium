# CONTEXT — Extra Credit (the enhancers lab)

The Scriptorium makes books and shelves a library. This room holds the **enhancers**: optional add-ons
that make the *learning* better, and nothing else. The mission is solidified in [`README.md`](README.md);
the one rule is **enhance, never overpower** (a reader finishing one book straight through beats a reader
a quarter in because they were fiddling with an add-on). Enhancers are **born connected** to the logged
material (the protocol below), and they earn their way from a throwaway **experiment** to real
**production** before graduating to a permanent home. This is **not** a general experiment sandbox and
**not** a home for off-mission work; anything that does not serve the library's learning belongs in its
own repo.

This is a Tier-2 boundary (see the precedence rule in [`../CLAUDE.md`](../CLAUDE.md)): it may only
**narrow** the global contract, never loosen it. Generating here is autonomous work; the only gate is
`GATE-PUBLISH`, and only when an enhancer graduates to its own public repo.

## The two tiers

| Tier | Path | Bar | Lifecycle |
|---|---|---|---|
| Experiments | [`experiments/`](experiments/README.md) | low — a probe, a spike, a "does this even work" | throwaway by default; delete freely |
| Production | [`production/`](production/README.md) | higher — runnable, documented, proven; meant for real use | keepers; **graduate** to a permanent home (injected into a book, or its own repo at `GATE-PUBLISH`) |

Each generated repo is its own folder under the right tier, scaffolded from
[`_template/`](_template/README.md).

## How the agent generates one

When asked to "generate a repo / experiment / tool for X":

1. **Pick the tier** from intent — a quick probe → `experiments/`; something proven and meant to last → `production/`.
2. **Scaffold from `_template/`** — a STYLE-grade `README.md`, the code, and a `## Connections`
   section. Defaults follow the platform: runnable and **offline / stdlib-first** where it fits
   (the books' BUILD→TEST ethos), small surface, no secret material.
3. **Run the connect protocol** (below) and fill the `## Connections` section before handing back.
4. **Report** the path, what it does, how to run it, and the connections found.

Best practices are an earshot away on purpose: the writing law is
[`../platform/conventions/STYLE.md`](../platform/conventions/STYLE.md); the gate registry is
[`../platform/HUMAN-GATES.md`](../platform/HUMAN-GATES.md).

## The connect-to-logged-material protocol

The whole point of the lab is interconnection — every repo is a node in the knowledge graph, not an
island. Two triggers, same scan:

- **Auto on generation** — every new scaffold ships with a populated `## Connections` section.
- **On demand** — ask *"does this connect to any of our logged material?"* about anything, anytime.

**Scan order** (read-only): GBrain (the `gbrain` MCP server — `search`, `recall`, `get_backlinks`,
`traverse_graph`) → `build-log/` (ledgers, plans, verdicts) → `ingredients/` (dossiers + distilled
source) → the books under `library/` (lessons + the antilibrary) → auto-memory. Record each hit as a
real markdown link so the edge is clickable (and shows up if the repo is opened as an Obsidian vault).

**Do NOT scan** `vault/` or `archive/` — both are route-excluded; the vault is raw ore, not authoring
input, and the archive is history. Surfacing a connection is not the same as authoring against it.

## Don'ts

- Don't route into or author against `vault/` or `archive/`.
- Don't let an experiment quietly become a dependency of a shipped book — graduate it deliberately.
- Don't put a `CONTEXT.md` inside `experiments/`, `production/`, or a generated repo — this boundary
  covers them. A nested `CONTEXT.md` would register as an orphan route and fail `route-lint`.
