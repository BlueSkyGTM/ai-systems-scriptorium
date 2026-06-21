# Bot Bottega (working name) — Build Plan

Status: **DRAFT for /autoplan review** (2026-06-21). The engine that builds **AI Operating Systems**.
The working name is under deliberation (Open Decision #1). Build it here by salvaging the Scriptorium's
proven machinery, then ship it to its own repo and **scrub it from the Scriptorium**.

## Thesis

The engine builds **AI Operating Systems**: systems with Claude-ready documentation that an AI can
*manage and operate* (Ray's GTM engine is the prototype), as opposed to content mills (ICM and the
Scriptorium produce content; an AI OS *runs*). Each AI OS is its own domain, seemingly unrelated to the
others. The engine is the **mold**; the Scriptorium is its reference instance; the GTM engine is its
second casting.

## Settled (Ray)

- **Build → ship → scrub.** Build it here leveraging the proven machinery; ship it to its own repo;
  remove it from the Scriptorium. It does not belong in the book factory.
- **Method = onboard the agent for the gig, then get out of its way.** The bottleneck is priming the
  agent for autonomous work, not the spec. Priming is *operational* (the outcome, standards, gates,
  tools, autonomy edges), never roleplay/costume.
- **Fail fast.** Kill a dud early, not ten phases in.
- **One engine (singular), not many systems in one repo.**

## The shape (the mold)

- **Core (every gig):** the gate model, the conductor->handler->worker orchestration, the contract
  pattern (a STANDARDS/STYLE-shaped quality law), a route-lint-style guard, plus two NEW builds: the
  **onboarding/spec intake** and the **dud detector**.
- **Opt-in:** ICM routing (any stage, clone as many as needed), deployed only when the gig is
  tree-shaped and earns it.
- **Stripped to placeholders:** the domain layer (ore, conventions, pipeline stages), filled per gig.
- **Boots dependency-light:** a clean clone + a bootloader the agent self-orients from; structure
  accretes on demand (the cure for ICM's dependency-heavy startup).

## How it runs a gig (lifecycle)

1. **Clone + boot** — the agent self-orients from the bootloader.
2. **Commission / spec intake** — looks for or derives a spec; the ICM questionnaire is a tool, not the
   front door. Can't write a coherent spec -> dud #1.
3. **Discern the build** — which layers the gig needs; ICM or not.
4. **Walking skeleton** — the thinnest real output pushed end-to-end; if it won't stand, abort cheap
   (dud gate #2).
5. **Lock + release** — lock the plan (a gate), then release to the fleet under the standards, with
   per-phase tripwires watching for a late dud.

## Build -> ship -> scrub (how we extract it)

- **Build:** assemble the mold from salvaged Scriptorium parts plus the two new builds, in a working
  area here.
- **Ship:** move it to its own repo, prove it by re-casting (the Scriptorium as reference instance; the
  GTM engine as the second casting).
- **Scrub:** remove the engine and its working artifacts from the Scriptorium; `route-lint` green; the
  book factory stays pure.

## Open Decisions (pressure-test with /autoplan; Ray wants Codex's take, especially on #1)

1. **The name (most important).**
   - `agentic-operating-system` (singular) — reads like a file you clone that kickstarts a metamorphosis;
     Ray's current lean.
   - `agentic-operating-systems` (plural) — **rejected**: implies many systems in one repo.
   - `AI Bot Bottega` — evocative; *reorients* the model the way "scriptorium" does (the master +
     apprentices priming).
   - Tensions to resolve: singular not plural; should the name **reorient the model** (priming) or be
     **descriptively literal**; does "operating system" overclaim; is there a name that is *both*
     singular/clarifying **and** reorienting. **Codex's view wanted here.**
2. **Core vs opt-in layering** — what is truly always-needed vs gig-dependent.
3. **The dud detector** — the concrete fail-fast mechanism (spec filter + walking skeleton + per-phase
   tripwires + dud report). Is walking-skeleton-first the right primitive?
4. **Front-door framing** — onboarding-first vs spec-first, and where ICM's questionnaire sits.
5. **Dependency-light boot** — how the bootloader self-orients without ICM's startup dependencies.
6. **The scrub** — the cleanest way to extract from the Scriptorium without leaving cruft.

## GSTACK REVIEW REPORT (/autoplan, 2026-06-21)

Dual-voice review: Codex (gpt-5.5) + an independent Claude reviewer, run on this plan. **Rare strong
convergence** — both reached the same verdicts independently. High-confidence signal.

### Consensus (both models agree)
- **Reject `AI Bot Bottega`.** "Bot" primes toy agents / roleplay; "Bottega" re-uses the *workshop*
  metaphor that already names the book factory, so it names the "not-a-content-mill" engine with a
  content-mill metaphor and muddies the one distinction the thesis rests on.
- **`agentic-operating-system` overclaims.** A cloneable starter is not an OS; it is a scaffold that
  makes a repo legible and governable enough for an agent to operate inside it. Singular is right; the
  overclaim is the problem.
- **Convergent name: `agent-os-starter`** (Codex): keeps the category signal, stays singular, the
  `-starter` says "this is the thing you clone," and it does not pretend to be a finished OS. Claude's
  variant: `agentic-operating-system` as a *slug only*, "operating system" dropped from the thesis in
  favor of "agent-operable system." Both keep **AI Operating System** as the *category*, defined narrowly.
- **The thesis is coherent but unfalsifiable as written.** Define "runs" with a hard bar: mutable state /
  external systems, authorized actions, observability, rollback paths, human gates for irreversible moves,
  freshness rules, source-of-truth boundaries. Without those it is an onboarding scaffold plus repo
  conventions, not an AI OS.
- **Contradiction:** the Scriptorium is named as BOTH the engine's reference instance AND the canonical
  content mill. It cannot be both. Fix: the Scriptorium is the *birthplace of the parts*; the GTM engine
  is the *first true instance*.

### Critical (both)
- **GTM-as-prototype is unvalidated and structurally dissimilar.** A book factory is batch-content with
  taste gates; a GTM engine is continuous, stateful, and mutates live business systems (CRM, email).
  "Prove it by re-casting" could prove the *opposite*. Cheapest fix, and the missing **dud-gate #0: a
  one-page GTM paper dry-run** mapping every salvaged part to transfers / needs-rework / doesn't-apply,
  BEFORE building.
- **The dud detector has no thresholds.** Make each gate a binary check with a named trigger (route-lint's
  exit-code philosophy). Add the harder dud both flagged: "coherent but useless."

### Strong recommendations (fold into the revision)
- **Authorization model (critical for GTM):** action classes — read-only / draft / local-mutation /
  external-mutation / irreversible; gates attach to action classes, not just phases.
- **Evidence-pack intake:** require goals, sources, tools, accounts, constraints, forbidden actions,
  success metrics, approval points. It IS spec-gated; onboarding *produces* the spec.
- **Smaller mandatory DECLARED core**, not "structure accretes on demand" (the drift ICM was built to
  prevent). Boot dependency-light in *file count*, still fully declared, with a boot acceptance test.
- **Build OUTSIDE this repo** (sibling worktree / throwaway dir), salvage by copy; building in-tree leaves
  the engine in git *history* forever (route-lint only checks the working tree) and cross-contaminates ICM.
- **route-lint = rewrite-to-generic, not copy** (it is book/stage/lesson-coupled).
- **Split build-time vs run-time orchestration:** conductor→worker is proven for batch content, not a
  running system; mark runtime orchestration out-of-scope for v1.
- **This is a thesis, not a build plan.** Rename to CHARTER; gate building behind the GTM dry-run + the
  core/dud decisions.

### Verdict
Both models: **do not build yet.** Validate the thesis with the one-page GTM dry-run, narrow the "AI OS"
definition to the falsifiable bar, instrument the dud detector, rename. Meta-risk both flagged: this
engine competes with shipping books (the portfolio); time-box the validation, keep "does this beat
shipping another book?" as a kill criterion.
