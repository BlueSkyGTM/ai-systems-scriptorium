# HUMAN-GATES — the human-in-the-loop registry

This is the **single source of truth** for which decisions need Ray. CONTEXT.md files
reference these gates **by ID** and never restate "autonomous vs. gated" inline. If a
decision is not on this list, it is autonomous — the agent does it and reports.

`route-lint` parses this file for the canonical gate-id list and fails the build if any
CONTEXT.md references a gate id that is not defined here.

## How to read a gate

- **ID** — the stable handle CONTEXT.md files cite (e.g. "stop at `GATE-LOCK-PLAN`").
- **Trigger** — the moment the agent must stop and ask.
- **Why human** — the irreversible-or-strategic reason it isn't autonomous.
- **What the agent does** — prepare the decision, then wait. Never act past the gate.

## The gates

### GATE-LOCK-PLAN
- **Trigger:** a book's `build-log/<book>/<stage>/PLAN.md` is drafted and ready to become the locked spec the drafters execute against.
- **Why human:** the PLAN fixes scope, lesson count, and inclusion lists for a whole stage; drafting against an unlocked plan wastes a stage.
- **What the agent does:** write the full PLAN, surface the open decisions, and wait for Ray to lock it. Do not author lessons until locked.

### GATE-APPROVE-SHIP
- **Trigger:** a stage has passed VERIFY and BUILD/TEST and is ready for the SHIP record (lessons folded into `src/`, exercises into `exercises/`).
- **Why human:** SHIP is the commit of authored content into the book; a bad ship is expensive to unwind.
- **What the agent does:** present the verify verdict + build/test result, then wait for approval before writing the SHIP record and folding content in.

### GATE-NAME-BOOK
- **Trigger:** a planned book (`library/planned/<slug>/`) graduates to in-progress and needs its real title + slug.
- **Why human:** the name is identity and is hard to change once it propagates into paths, the catalog, and any public copy.
- **What the agent does:** propose 2–3 candidate names with rationale; wait for Ray to choose before creating the in-progress book directory.

### GATE-PUBLISH
- **Trigger:** building or moving a **public** copy of a book (Vercel deploy, public repo extraction, making `git-repository-url` live).
- **Why human:** publishing is an external, reputational, and licensing decision (private-first is the default; see BACKLOG #12).
- **What the agent does:** prepare the artifacts and the deploy plan; wait for explicit go before anything leaves the private repo.

## Not gated (autonomous — for contrast, not law)

Authoring/rewriting a lesson to STYLE, running VERIFY, running BUILD/TEST and the artifact
gates, relocating files, updating CATALOG/BACKLOG, fixing paths, running `route-lint`. The
agent does these and reports — it does not ask permission.
