# Exercise 05 — Long-Horizon Agents & Durable Execution

## Goal

Wrap the `_harness/` orchestrator in a durable runner so a multi-step agent run survives a process crash: persist every step to a checkpoint store keyed by `thread_id`, then prove a fresh process replays completed steps from disk and resumes from the first unfinished one — without re-calling the model on replayed steps.

## Why

The `_harness/` agents run in one process and hold state in memory; a crash at step thirty-eight throws away thirty-seven paid-for, side-effectful steps. Long-horizon agents do not run in `while True` — every LLM call becomes a checkpointed activity. This exercise makes the throughline's runs survivable, which is the precondition for everything the rest of the chapter adds (budgets, kill switches, HITL all assume a run that can pause and resume).

## Steps

1. **Checkpoint store.** Add `module4-fleet/durable/store.py`. Implement a `Checkpointer` over JSON on disk: `append(thread_id, index, result)` writes one step record (index, step kind, serialized result, timestamp) to `checkpoints/<thread_id>.jsonl`; `load(thread_id) -> list[record]` reads them back in order (empty list on first run).

2. **Durable runner.** Add `module4-fleet/durable/runner.py` wrapping the `_harness/` orchestrator. On each step: if `step.index < len(history)`, *replay* — read the stored result, do not call the model or the tool; else *execute* — run the real step (model call or tool call) and `append` its result immediately before advancing. Key everything by a `thread_id` passed in at start.

3. **Instrument replay vs execute.** Print a clear marker per step — `REPLAY step N (from checkpoint)` vs `EXECUTE step N (live)` — and count live model calls so the replay claim is verifiable, not asserted.

4. **Crash and resume.** Run a task of at least six steps. Kill the process partway (raise after, say, step 4, or send the process a signal). Restart with the same `thread_id`. Confirm steps 0–4 print `REPLAY` with zero live model calls, and the run continues at step 5 with `EXECUTE`.

5. **Pause-on-input stub.** Add a step kind that suspends the run (returns a `pending-human` checkpoint and stops). Restart and confirm the run resumes from that exact checkpoint once a stubbed response is supplied — the hook lesson 08's HITL gate will use.

## Done when

- `checkpoints/<thread_id>.jsonl` contains one record per completed step after a run.
- Killing the process and restarting with the same `thread_id` replays completed steps from disk with **zero** live model calls on the replayed range, then resumes from the first unfinished step.
- The replay/execute markers and the live-call counter make the no-double-execution-of-model-calls claim observable.
- A `pending-human` checkpoint suspends the run and a restart resumes from it.

## Stretch

Make replay deterministic under non-determinism: record the model's output and any tool randomness in the checkpoint so replay reconstructs identical state, and add a `resume_from(thread_id, index)` that rewinds to an earlier checkpoint and re-runs forward — the substrate for the rollback work in exercise 08.
