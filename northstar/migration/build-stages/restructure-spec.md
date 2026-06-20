# Spec — Repo restructure: "AI Systems Scriptorium" (an AI-engineering library + build system)

Status: DRAFT v2 (Phase 4, via `/spec`). For review → `/autoplan` → execute on approval. Repo name
**`ai-systems-scriptorium`** (short dir: `scriptorium/`). History-preserving. Nothing destructive until approved.

## Context
This repo (`sans-python`) is not a single course and not a generic book platform. It's **a private,
AI-engineering-specialized library of books plus the AI system that builds them.** The first book (Sans Python —
AI Platform Engineering, 8 modules) is done; the durable asset is the build engine + curated ore + the method.
Real content sits 3 levels deep (`northstar/migration/`) under two stale framing layers (a root `CLAUDE.md`
titled "Workspace Builder"; a `northstar/` planning shell). The structure hides what this is. Three more books
are queued. Better architecture → better outcomes.

## Identity & edge
- **AI-engineering-specialized, on purpose.** The pipeline grounds in **Microsoft Learn** (patch/create/extract
  on demand) + curated AI-eng ore. That only works for technical content. **Do NOT genericize to "any domain"**
  — it kills the edge. The old "Workspace Builder / any MWP domain" framing is retired.
- **Private-first.** Master library = private, holds everything. For Ray + anyone who finds the methods useful;
  not a public learner product.
- **Artifacts are the outward value.** Employers want business solutions, not rough-draft courses. The M6/M7/M8
  portfolio artifacts are the proof; the books are how they're built.
- **Progression is AI-run, not built.** GBrain memory + spaced repetition + "scan completed artifacts = progress."

## THE CORE PRINCIPLE: Interpreted Context Methodology (ICM) — the architecture is agent-navigable by design
The earlier "setup" we skipped. **The folder system is not just storage; it is a routing system.** Every
directory carries a `CONTEXT.md` that an arriving agent reads to know: (a) what's here, (b) what task this dir
serves, (c) **what to load and what NOT to load**, (d) where to hand off next, and (e) **which decisions are
autonomous vs. human-gated.** A root `CONTEXT.md` is the **task router**: it maps an intent to a starting
directory + a load-list. This is the methodology that already worked on the M3–M8 build (per-stage
`CONTEXT.md` + `PLAN.md`); the restructure elevates it from `build-stages/` to the **whole repo**.

Result: the main agent and its subagents **breeze through the tree via task routing and do the routine work
independently** — author, verify, build/test, relocate, catalog — reaching for the human only at the points the
`CONTEXT.md` files explicitly mark as human-gated (lock a book PLAN, approve a SHIP, name a new book, ship
public). Less load on Ray and the main agent; both focus on the big picture.

### ICM components (built during migration)
1. **Root `CONTEXT.md` — the task router.** A Triggers→Routing table: intent → go-to dir → load these / do NOT
   load these. Example rows:
   | I want to… | Start at | Load | Do NOT load |
   |---|---|---|---|
   | Author/continue a book | `platform/CONTEXT.md` + the book's `library/.../<book>/CONTEXT.md` | that book's PLAN + STYLE/AUTHORING + its `ingredients/source` | other books, the vault raw |
   | Process raw ore into a new book | `vault/CONTEXT.md` → `platform/pipeline/CONTEXT.md` | the relevant `vault/<repo>/` + the dossier template | shipped books |
   | Fix/edit a shipped lesson | `library/completed/<book>/CONTEXT.md` | the lesson + its verify verdict | the pipeline internals |
   | Check status / pick next work | `CATALOG.md` + `BACKLOG.md` | — | everything else |
   | Publish a book's artifacts | the book's `CONTEXT.md` → `platform/pipeline/` SHIP | the book's artifacts | the vault |
2. **Per-folder `CONTEXT.md`** in every directory (library/, each book, platform/, platform/pipeline/,
   ingredients/, vault/, progression/, archive/): what's here · the local task · load/don't-load · next handoff ·
   autonomous-vs-human-gated markers.
3. **`CLAUDE.md` / `AGENTS.md`** (root, the AI contract): "Always start at `CONTEXT.md`. Follow the routing.
   Do the autonomous tasks; stop for the human-gated ones. Treat each folder's `CONTEXT.md` as law for that area."
4. **Pipeline stage handoffs** generalized into `platform/pipeline/` (AUTHOR→VERIFY→BUILD/TEST→SHIP, each a
   stage with its own `CONTEXT.md` + `output/` handoff — the proven build-stages pattern, now reusable per book).
5. **Human-in-the-loop registry:** a short `platform/HUMAN-GATES.md` listing exactly which decisions need Ray
   (so the agent knows the boundary precisely and doesn't over- or under-ask).

## Route-chain robustness (mechanical defenses — added per the codex gate)
The ICM chain is conceptually sound but *easy to break* (one stale link or drifted path = a silent dead end).
These make a broken route a **caught error, not a silent wall**:
1. **Single source of truth for paths — `platform/route-manifest.yaml`.** The canonical registry of every routed
   location + each config-consumed path (book root, mdbook `src`, vercel build/output, the M8 fleet path).
   `CONTEXT.md` routes and configs reference it; no path is hardcoded twice.
2. **`route-lint` (`platform/bin/route-lint`; runnable + a verify gate).** Non-zero exit on: a routed dir missing
   its `CONTEXT.md`; any route start/load/don't-load/handoff path that doesn't exist; a broken markdown link in
   any `CONTEXT.md`/README; a config path (vercel, `book.toml` `src`, `fleet_adapter` target) that doesn't
   resolve; **any live route pointing into `archive/`**; two `CONTEXT.md` files claiming the same task. This is
   the executable form of the "cold agent can route" criterion.
3. **Route fixtures.** Per core intent (author · fix · process-ore · publish · status), a fixture asserting that
   following the root `CONTEXT.md` reaches the right start dir + load-list. Run by `route-lint`.
4. **Precedence rule (in `CLAUDE.md`/`AGENTS.md`).** Root = global contract/policy; the **nearest `CONTEXT.md`
   wins for local specifics**; on conflict, root policy wins, local detail wins. No silent ambiguity.
5. **Pointer shims + clear rename.** Leave `northstar/migration/MOVED.md` pointing to the new layout for a
   deprecation window (anything starting at the old path is redirected, not walled). Rename = **GitHub repo
   rename** (`BlueSkyGTM/sans-python` → `ai-systems-scriptorium`; GitHub auto-redirects old URLs) + local dir +
   doc refs.
6. **`archive/` is route-excluded.** Its `CONTEXT.md` says "HISTORICAL — not active, do not route here"; the root
   router never targets it; `route-lint` enforces no live route → `archive/`.
7. **Full-tree ref sweep (not just PLANs).** Migration greps the WHOLE tree — lessons, exercises, scripts, tests,
   READMEs, configs — for `northstar/migration` + `synthesis/source` and fixes every live ref. (Confirmed live
   refs so far: `exercises/module8/fleet_adapter.py`, `vercel.json`, PLANs/dossiers/build-progress — treat the
   adapter as the canary, not the only case.)
8. **cwd-robust `fleet_adapter`.** Resolve the M7-fleet path via repo-root detection (`git rev-parse
   --show-toplevel`), not a fixed walk-up; test from repo root, book root, and the module-exercise dir.

**Vault fact (decides the LFS call):** `synthesis/raw/` is **gitignored and never committed — the ore exists
only on local disk, unbacked.** So vault→LFS is a **fresh add (no history rewrite)** AND the ore's **first
backup**. No `.github/workflows` exist; `vercel.json` is the only path-bearing config.

## Proposed architecture (tree — every dir has a CONTEXT.md)
```
ai-systems-scriptorium/                 # "AI Systems Scriptorium" (private)
├── README.md                           # what this is, in one read (career-ops-grade)
├── CONTEXT.md                          # THE TASK ROUTER (ICM root)
├── CLAUDE.md  /  AGENTS.md             # AI contract: start at CONTEXT.md, follow routing, gates
├── CATALOG.md                          # book index + status (completed | in-progress | planned)
├── BACKLOG.md                          # cross-cutting backlog (the 12-item test run)
├── CHANGELOG.md
├── library/                            # THE BOOKS                         (+ CONTEXT.md)
│   ├── completed/sans-python/          # src/ exercises/ theme/ book.toml   (+ CONTEXT.md)
│   ├── in-progress/everything-else/    # antilibrary submissions / Avec Python (+ CONTEXT.md)
│   └── planned/{getting-hired,simple-systems}/  (+ CONTEXT.md each, seeded from the vault)
├── platform/                           # THE BUILD ENGINE (AI-eng-specialized)  (+ CONTEXT.md)
│   ├── pipeline/                       # ICM AUTHOR→VERIFY→BUILD/TEST→SHIP stages (+ CONTEXT.md)
│   ├── conventions/                    # STYLE.md (Zinsser), AUTHORING.md       (+ CONTEXT.md)
│   ├── templates/                      # _templates/
│   └── HUMAN-GATES.md                  # the autonomous-vs-human-gated registry
├── ingredients/                        # distilled inputs (in git, small)       (+ CONTEXT.md)
│   ├── source/                         # 3.1M per-book distilled source
│   └── dossiers/                       # keep/cut/merge rulings
├── vault/                              # THE ORE — 767M raw, git-LFS, crawler access (+ CONTEXT.md)
│   ├── MANIFEST.md                     # the 9 source repos + provenance
│   └── <raw repos…>                    # .gitattributes LFS rules
├── progression/                        # AI-run progress spec                    (+ CONTEXT.md)
│   └── README.md                       # GBrain + spaced-rep + artifact-scan
├── build-log/                          # the build journal + per-book ledgers (was build-progress.md / build-stages/output)
│   └── sans-python/                    # PLANs, verify/build-test/ship verdicts for the shipped book
└── archive/                            # retired scaffolding (old northstar/ shell, setup/stages/references, synthesis/_archive, output)  (+ README "historical, not active")
```
**No junk drawer:** `meta/` is replaced by named homes — `build-log/` (build journals + ledgers), `archive/`
(retired scaffolding), and root files (`CATALOG`, `BACKLOG`, `CHANGELOG`). Every folder states its own purpose
in its `CONTEXT.md`.

### Resolved decisions
1. **Name:** `ai-systems-scriptorium` / "AI Systems Scriptorium" (short dir `scriptorium/`).
2. **Vault (767M ore):** `vault/`, **git-LFS** + `MANIFEST.md`. One place, on disk for crawlers, preserved,
   light clones. Downgrade path: gitignore+manifest if LFS annoys.
3. **Public/private:** private master, no public learner product; books self-contained under
   `library/completed/<book>/` so a single book *could* be copied out later. Build nothing public now.
4. **`meta/` → specific homes:** `build-log/`, `archive/`, root status files. No catch-all.

## Migration plan (history-preserving, staged — execute only after `/autoplan`)
Each stage = `git mv` (preserves history) + a path fix, verified before the next.
1. **Lift the workspace up** out of `northstar/migration/`; retire root `setup/ stages/ references/` + the
   `northstar/` shell → `archive/`.
2. **Place the book:** `src/ exercises/ theme/ book.toml` → `library/completed/sans-python/`.
3. **Place engine + inputs:** `build-stages/` → `platform/pipeline/` + `build-log/`; `STYLE.md AUTHORING.md` →
   `platform/conventions/`; `_templates/` → `platform/templates/`; `synthesis/source/` → `ingredients/source/`;
   `_dossier/` → `ingredients/dossiers/`; `synthesis/raw/` → `vault/` (LFS); `synthesis/_archive/` + `output/` → `archive/`.
4. **Generate the ICM layer:** write the root `CONTEXT.md` router + a `CONTEXT.md` in every directory +
   `platform/HUMAN-GATES.md` + fresh `README.md`/`CLAUDE.md`/`AGENTS.md`/`CATALOG.md`. (This is the step we skipped before.)
5. **Fix the paths that break** (or builds/gates fail):
   - `vercel.json` buildCommand/outputDirectory → `library/completed/sans-python`.
   - M8 `fleet_adapter.py` walk-up path → new `library/completed/sans-python/exercises/module7/…`.
   - `book.toml` src path (verify relative, self-contained).
   - live `synthesis/source/moduleN` refs in PLANs/dossiers → `ingredients/source/…`.
6. **Verify:** `mdbook build` from the new book path; all 8 artifact smokes + pytest from new paths; `git
   log --follow` shows preserved history; **a cold agent can task-route from the root `CONTEXT.md` to author /
   fix / process / publish without being told where to look.**

## Progression system (spec only)
`progression/README.md`: GBrain per book (persistent memory); spaced repetition over each lesson's
`## Core concepts` propositions (the item bank already exists); progress = scan
`library/.../exercises/**` + `outputs/skill-*.md` for completed artifacts. No manual state.

## Acceptance criteria
1. A cold reader/agent opens `README.md` + `CONTEXT.md` and can route to any task (author/fix/process/publish/
   status) **without further instruction** — the ICM routing works.
2. Every directory has a `CONTEXT.md` (purpose · load/don't-load · handoff · gate markers); `platform/HUMAN-GATES.md` exists.
3. `mdbook build` of Sans Python passes from `library/completed/sans-python/`.
4. All 8 artifact scaffolds pass `python smoke.py` + `pytest` from new locations (incl. M8 → real M7 fleet).
5. `git log --follow` shows preserved history on representative moved files.
6. Root docs describe the AI-eng-specialized pipeline + the ICM routing (no "Workspace Builder"); no junk-drawer folder.
7. `vault/` is LFS-tracked with a MANIFEST; a normal clone is light.
8. The 12-item backlog survives as `BACKLOG.md`.
9. **`route-lint` passes** (every routed dir has a `CONTEXT.md`; all route + config paths resolve; no broken
   links; no live route into `archive/`; no duplicate route ownership) — and runs as a verify gate.
10. **Route fixtures pass** for all core intents (author / fix / process-ore / publish / status).
11. **Pointer shims** exist at old paths (`northstar/migration/MOVED.md`); the **precedence rule** is documented
    in `CLAUDE.md`/`AGENTS.md`; `platform/route-manifest.yaml` is the single source of truth for paths.

## Out of scope
Genericizing to non-AI-eng domains; any public learner product; executing the restructure (spec first);
the 12 backlog items themselves; processing the vault into the 3 planned books.

## Rollback
Every step is `git mv` on a branch; whole restructure is one squashable branch. Revert before merge;
mdbook/gates + `route-lint` re-verified before landing on `main`. **Destructive (needs explicit approval) =**
history rewrite, force-push, dropping the (currently unbacked) vault, or removing pointer shims before the
deprecation window. The vault→LFS move is a fresh add, NOT a history rewrite (raw was never committed), so it is
not destructive.

## Effort
Lift+place (CC ~20m) · **generate the ICM CONTEXT layer (CC ~40m — the high-value step)** · path fixes + verify
builds/gates (CC ~30m, the risk) · fresh root docs (CC ~30m) · vault LFS + push (CC ~15m). Human review at the
`/autoplan` gate + final approval.
