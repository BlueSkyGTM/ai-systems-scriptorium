# Long-horizon agents & durable execution

A loop that runs for thirty seconds and a loop that runs for three hours are not the same program with a bigger number. The long one will be interrupted — a deploy, a crashed pod, a model timeout, a human stepping away for the weekend — and every assumption you made about a single in-memory turn breaks the moment the process dies mid-run.

## The qualitative break

Module 3's agent loop lived in one process. It started, ran its turns, returned an answer, and the whole run fit inside a single function call's lifetime. Memory was a list in RAM. A crash meant you re-ran from the top, and re-running from the top was cheap because the top was a minute ago.

Push the horizon out to minutes or hours and that model collapses. A run long enough to span a deploy *will* span a deploy. A run that calls forty tools will hit a transient failure on tool thirty-eight, and re-running from zero throws away thirty-seven successful, paid-for, side-effectful steps. The agent that worked fine in a notebook becomes, in production, an expensive way to lose work.

The break is not gradual. Below the line, an agent is a function you call. Above it, an agent is a *workflow you resume* — and the engineering shifts from "write the loop" to "make the loop survivable." This is the seam's whole point: the AI Engineer asks whether the agent reasons well over a long task; the MLOps half asks what happens when the box it runs on disappears at step thirty-eight. Long-horizon work forces the second question into the open.

## Every LLM call is an activity

The pattern that makes long runs survivable comes from durable-execution engines, and it has one core idea: an LLM call is not a function call, it is an *activity*. An activity is a unit of work the runtime wraps with three guarantees — **checkpoint** its result the instant it returns, **retry** it on transient failure, and **replay** the run from durable history instead of from scratch.

Why does an LLM call earn this treatment when a normal function does not? Because the LLM call has the exact profile durable execution exists for. It is non-deterministic (same input, different output), expensive (you pay per token), slow (seconds, sometimes minutes), and side-effectful (it may have already sent the email before the process died). A unit of work that is costly, flaky, and irreversible is the textbook case for checkpointing — you never want to pay for it twice or, worse, fire its side effect twice.

So the durable loop does not hold state in a Python list. After each activity it writes the result to a durable store and advances a cursor. If the process dies, a fresh process reads the history, replays the completed activities from their stored results — *without re-calling the model* — and continues from the first activity that never finished. Thirty-seven steps replay from disk in milliseconds; step thirty-eight runs for real.

```python
# module4-fleet/durable/runner.py — the shape, not a full engine
def run_durable(thread_id: str, goal: str, store: Checkpointer) -> Result:
    history = store.load(thread_id)          # [] on first run; populated on resume
    messages = replay(history)               # rebuild state from stored results, no model calls

    while not done(messages):
        step = next_step(messages)
        if step.index < len(history):        # already completed in a prior life
            result = history[step.index].result   # replay: read, don't re-execute
        else:
            result = call_activity(step)     # real execution: model call or tool call
            store.append(thread_id, step.index, result)   # checkpoint immediately
        messages = apply(messages, result)

    return finalize(messages)
```

The `thread_id` is the spine. It names the run, keys the checkpoint history, and is how a resumed process finds its place. Everything durable hangs off it.

## Three places this is already built

You do not write a durable-execution engine. You pick one, because the hard part — exactly-once activity semantics, replay determinism, lease expiry on a crashed worker — is genuinely hard and someone has already shipped it.

**Temporal** is the general-purpose durable-execution engine; its workflows model each step as a checkpointed activity, and its OpenAI Agents SDK integration — generally available since March 2026 — wraps each agent invocation in an activity so a crashed run resumes from the last checkpoint without reprocessing completed steps.

**LangGraph** persists graph state to a checkpointer — Postgres in production — after every node, so a failed forty-step run resumes from the last committed node rather than the start, keyed by `thread_id`.

**Cloudflare Durable Objects** give each agent a single-threaded, addressable object with built-in SQLite storage that holds per-key state for weeks at the edge, surviving restarts and redeploys without a separate database.

On Azure, the Microsoft Agent Framework provides the same shape with first-class checkpoint storage and persistent sessions, so an agent's state survives host crashes, restarts, and scaling events and resumes from its latest checkpoint.

The frameworks differ in surface, agree on the spine: state is external, every step is checkpointed, and the run is addressed by an ID that outlives any one process.

## What durability buys you

Three concrete capabilities fall out, and each is something a single-process loop simply cannot do.

A run **survives a deploy.** You ship new code mid-task; the in-flight agent checkpointed at step twenty, the new process loads the history and continues. No lost work, no manual restart.

A run **pauses on human input and resumes later.** The agent reaches a step that needs a person — an approval, a missing fact — checkpoints, and suspends. Hours or days later the human responds, and the run resumes from exactly that checkpoint. The agent is not "running" in the meantime; it is durable state waiting for an event. (The propose-then-commit protocol that rides on this pause is lesson 08.)

A run **resumes from the latest checkpoint, not from zero**, after any failure. This is the one that pays for itself, because it converts "the agent crashed, re-run the whole thing" into "the agent crashed, it picked up where it left off."

One caution before you reach for an hours-long horizon: capability is not reliability. Success rate on a task drops sharply as the horizon grows — a model that nails a five-minute task is not a model that nails the same task stretched across an hour, even with perfect durability underneath. Durable execution keeps a long run from *losing* work; it does nothing to keep the agent *correct* over that span. The budgets, kill switches, and checkpoints in the next four lessons are what keep a survivable run from also being a runaway one.

## Core concepts

- A long-horizon agent is not a long function call; it is a workflow that must survive interruption, so state moves out of process memory and into a durable store keyed by `thread_id`.
- Durable execution treats every LLM call as an activity — checkpoint on return, retry on transient failure, replay completed steps from stored results without re-calling the model — because LLM calls are non-deterministic, expensive, slow, and side-effectful.
- Resume-by-`thread_id` lets a run survive a deploy, pause on human input and continue later, and restart from the latest checkpoint rather than from zero; Temporal, LangGraph→Postgres, Cloudflare Durable Objects, and the Microsoft Agent Framework all implement this shape.
- Durability protects work, not correctness — reliability still falls off as the horizon grows, which is why budgets and kill switches are not optional on a long run.

<div class="claude-handoff" data-exercise="exercises/module4/05-long-horizon-durable-execution/">

**Build it in Claude Code** — wrap the `_harness/` orchestrator in a durable runner: persist each agent step to a JSON checkpoint store keyed by `thread_id`, kill the process mid-run, and prove that a fresh process replays the completed steps from disk and resumes from the first unfinished one — without re-calling the model on the replayed steps. Open the repo and run the exercise for this lesson.

</div>
