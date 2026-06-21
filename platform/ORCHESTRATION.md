# Orchestration: Running the Agent Fleet

How heavy work gets done in this repo without stalling the human loop. Verified 2026-06-20:
a spawned Opus agent can spawn and manage its own Sonnet workers in this harness (one handler
ran four workers in parallel over ~46k lines of source).

## The Three Tiers

- **Conductor** (top Opus, the session the human is talking to). Holds the human-in-the-loop.
  Dispatches parallel orders, makes the gated decisions with Ray, and integrates shared state
  (`route-manifest.yaml`, `CATALOG.md`, root `CONTEXT.md`). The conductor does not read every
  worker's raw output; it reads handler rollups.
- **Handler** (Opus, one per cluster). Owns a domain or a batch. Briefs its workers, absorbs
  their intake and outtake, synthesizes, and returns one rollup to the conductor. Use a handler
  when a fan-out is large enough that per-worker management would clog the conductor.
- **Worker** (Sonnet, the bulk). Reads, authors, extracts, or verifies on a bounded slice; returns
  a structured report to its handler. Cheap, parallel, disposable.

## Why It Matters (Not Just Speed)

Speed is the obvious win. The real win is that it keeps the human loop alive. While the worker
tier executes, the conductor and the human keep talking, deciding, and clearing the gates in
`HUMAN-GATES.md`. The tier is what lets a `GATE-NAME-BOOK` call or a taste decision get serviced
in conversation at the same moment a fleet is drafting chapters. Without it, the conductor
serializes on worker intake and the human loop stalls; with it, the gates and the execution run
at the same time.

## When To Use It

- **Use a handler when there are concurrent gates to service, or multiple parallel clusters** — when the
  conductor would otherwise serialize on worker intake while a human gate or a second cluster waits. Keeping
  the human loop alive during heavy execution is the handler's actual job.
- **A single cluster with no concurrent gate: the conductor manages the workers directly, even at 3–4
  workers.** Validated by the Just Python M2-vs-M3 comparison (M2 ran a handler tier, M3 ran
  conductor-direct): the conductor-direct four-worker run matched the handler run on quality, with one
  fewer tier and less overhead. Worker
  *count* alone does not justify a handler; concurrent gates or multiple clusters do.
- Anything touching a human gate: keep it with the conductor; never delegate a gate to a worker.

## Discipline (Observed Cracks To Avoid)

- **Workers never touch shared state.** `route-manifest.yaml`, `CATALOG.md`, and root `CONTEXT.md`
  are integrated by the conductor only. When parallel workers each edited the manifest to register
  their own boundary it happened to survive, but two writes to one file is a race. Either the
  conductor pre-registers before fan-out, or each worker creates only its own dir and the conductor
  registers after.
- **Cold workers do not inherit the contract.** A worker knows only its brief. It will not know the
  ICM gate model, the draft-preview convention, or `STYLE.md` unless the brief says so; a cold
  reviewer once flagged a draft in `planned/` as a gate violation for exactly this reason. Carry the
  relevant gate and STYLE context into every brief, or point the worker at the file.
- **One writer per file.** Give each worker a non-overlapping write scope. Reads may overlap; writes
  may not.

## Gates Stay With The Human

The gates in `platform/HUMAN-GATES.md` (`GATE-NAME-BOOK`, `GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`,
`GATE-PUBLISH`) are the human-in-the-loop checkpoints. Orchestration exists to keep them serviceable
during heavy execution; it never moves a gate decision down to a handler or a worker. The conductor
holds the gates; the fleet does the work.
