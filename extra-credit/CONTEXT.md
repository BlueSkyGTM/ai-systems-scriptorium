# CONTEXT — Extra Credit (the lab)

The Scriptorium makes books and shelves a library. This is its third room: a **lab** where the
agent generates repo scaffolds on demand — for throwaway experiments *and* for keepers meant to be
used — applying the same best practices the books are built with. It exists so the work stays
**active** between the big curriculum phases, and so every scrap of practice is **born connected**
to the logged material instead of stranded on its own island.

This is a Tier-2 boundary (see the precedence rule in [`../CLAUDE.md`](../CLAUDE.md)): it may only
**narrow** the global contract, never loosen it. Generating here is autonomous work; the only gate is
`GATE-PUBLISH`, and only when a tool graduates to its own public repo.

## The two tiers

| Tier | Path | Bar | Lifecycle |
|---|---|---|---|
| Experiments | [`experiments/`](experiments/README.md) | low — a probe, a spike, a "does this even work" | throwaway by default; delete freely |
| Tools | [`tools/`](tools/README.md) | higher — runnable, documented, meant for real use | keepers; can **graduate** to its own repo or into `library/` at `GATE-PUBLISH` |

Each generated repo is its own folder under the right tier, scaffolded from
[`_template/`](_template/README.md).

## How the agent generates one

When asked to "generate a repo / experiment / tool for X":

1. **Pick the tier** from intent — a quick probe → `experiments/`; something to keep and use → `tools/`.
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
- Don't put a `CONTEXT.md` inside `experiments/`, `tools/`, or a generated repo — this boundary
  covers them. A nested `CONTEXT.md` would register as an orphan route and fail `route-lint`.
