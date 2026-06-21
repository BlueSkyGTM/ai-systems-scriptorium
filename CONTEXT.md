# CONTEXT — the task router (ICM root)

**The Interpreted Context Methodology (ICM):** every routed boundary in this repo carries a
`CONTEXT.md` that tells an arriving agent what's here, what to load and what NOT to load, where
to hand off next, and which decisions are human-gated. This root file is the **task router** — it
maps your intent to a starting directory and a load-list, so a cold agent self-routes the whole
tree without being told where to look. Paths below are **root-anchored** (or `route-manifest.yaml`
keys); never follow a bare relative like `src/module3` — it resolves wrong across books.

Start here. Pick the row that matches your intent, go to **Start at**, load **Load**, skip **Do
NOT load**, hand off where it says, and stop only at the named gate (defined in
`platform/HUMAN-GATES.md`).

## Intent → route

<!-- route-table -->
| I want to… | Start at | Load | Do NOT load | Next handoff | Human gate |
|---|---|---|---|---|---|
| Author / continue a book | `library/completed/sans-python` | `library/completed/sans-python/CONTEXT.md`, `platform/conventions`, `platform/pipeline`, `ingredients` | `vault`, `build-log`, other books | `platform/pipeline/CONTEXT.md` (AUTHOR→VERIFY→BUILD/TEST→SHIP) | `GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP` |
| Fix / edit a shipped lesson | `library/completed/sans-python` | book's `CONTEXT.md` → its fix-a-lesson sub-route; the lesson + `build-log/sans-python` verify verdict | `platform/pipeline`, `vault`, `ingredients` | the book's `CONTEXT.md` intent sub-router | none (autonomous) |
| Process raw ore into a new book | `vault` | `vault/CONTEXT.md`, `vault/MANIFEST.md`, `ingredients`, `platform/pipeline` | `library/completed/sans-python` (don't author against a shipped book) | `platform/pipeline/CONTEXT.md` | `GATE-NAME-BOOK`, `GATE-LOCK-PLAN` |
| Publish a book's artifacts | `library/completed/sans-python` | book's `CONTEXT.md` → its `publish` sub-route; `platform/pipeline` SHIP | `vault`, `ingredients` | `platform/pipeline/CONTEXT.md` SHIP stage | `GATE-PUBLISH` |
| Generate a lab repo / experiment | `extra-credit` | `extra-credit/CONTEXT.md`, `platform/conventions` | `vault`, `archive`, the books | scan logged material for connections | none (autonomous); `GATE-PUBLISH` to graduate a tool |
| Check status / pick next work | `.` | `CATALOG.md`, `BACKLOG.md` | everything else | — | none (autonomous) |

## The fixed points

- **AI contract:** `CLAUDE.md` / `AGENTS.md` — always start here, follow the routing, do the
  autonomous work, stop at the gates. Read the precedence rule there before overriding anything.
- **Gates:** `platform/HUMAN-GATES.md` — the single source of truth; routes cite gates by ID.
- **Paths:** `platform/route-manifest.yaml` — the single source of truth for every routed and
  config-consumed path. `platform/bin/route-lint` enforces both this router and the manifest.
- **Book index:** `CATALOG.md`. **Cross-cutting backlog:** `BACKLOG.md`.

## Routed boundaries (each has its own CONTEXT.md)

`library` · `library/completed/sans-python` · `library/planned/show-dont-tell` ·
`library/planned/simple-systems` · `library/planned/just-python` ·
`library/planned/ml-in-proportion` · `library/planned/upstream` ·
`library/planned/tasteful-tuning` · `library/planned/interview-algorithm` ·
`library/planned/local-metal` · `platform` ·
`platform/pipeline` · `platform/conventions` · `platform/templates` · `ingredients` ·
`progression` · `extra-credit` · `build-log` · `vault` · `archive` (HISTORICAL — never route here).
