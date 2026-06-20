# VERIFY verdict — M5 L15 · Async Rust for Serving

**Verifier:** Sonnet VERIFY subagent · **Date:** 2026-06-19
**Draft:** `build-stages/m5/output/author/15-async-rust-for-serving.md` (edited in place)
**Verdict:** **PASS** (all markers resolved, every tokio claim grounded in tokio docs + the async book, lazy-futures claim confirmed true and reworded to the canonical phrasing, perf stays qualitative)

---

## Claim ledger

| # | Claim | Authority | Result |
|---|-------|-----------|--------|
| 1 | tokio is an asynchronous runtime for Rust that provides the building blocks for writing networking applications; Rust has no built-in async runtime (you bring one) | tokio.rs/tokio/tutorial | **CONFIRMED verbatim** — "Tokio is an asynchronous runtime for the Rust programming language. It provides the building blocks needed for writing networking applications." "no built-in runtime" is accurate standard Rust (the language ships `async`/`await` + the `Future` trait; the executor is a library). |
| 2 | An `async fn` returns a future that does not run when called; **Rust futures are inert: they make progress only when polled** (the drafter-flagged "lazy" claim) | rust-lang.github.io/async-book/01_getting_started/02_why_async | **CONFIRMED verbatim** — async book: "Futures are inert in Rust and make progress only when polled." The drafter correctly flagged that the *tokio tutorial* does not state this; the *async book* does, verbatim. Claim is TRUE; reworded from "Futures are lazy: nothing executes until polled" to "Rust futures are inert: they make progress only when polled" to match the canonical source. M1 source independently corroborates ("lazy computation via the `Future` trait"). |
| 3 | `.await` is a yield point: while a task waits, its thread runs another ready task | tokio.rs/tokio/tutorial + async book (cooperative scheduling) | **CONFIRMED** — standard tokio cooperative-scheduling model; the M1 source names "yield points" and "the cooperative nature of Rust's async model." Accurate. |
| 4 | `?` works inside `async fn` exactly as in sync; a failed `.await` short-circuits | general Rust (the `?` operator is orthogonal to async) | **CONFIRMED** — accurate. `?` propagates `Result`/`Option` identically inside an `async fn`; async changes *when* the body runs, not how `?` desugars. |
| 5 | `#[tokio::main]` rewrites `async fn main` into a sync `main` that starts the runtime and blocks on the top-level future | docs.rs/tokio attr.main + general | **CONFIRMED** — accurate description of the macro's expansion. |
| 6 | **By default** the runtime is a **multi-threaded, work-stealing** scheduler | docs.rs/tokio/latest/tokio/attr.main.html + tokio.rs/tokio/tutorial | **CONFIRMED** — `#[tokio::main]` defaults to `multi_thread`: the macro docs state of the multi-threaded flavor "This is the default flavor." The tutorial overview lists tokio's runtimes as ranging from "a multi-threaded, work-stealing runtime to a light-weight, single-threaded runtime." Combined claim (default = multi-threaded; multi-threaded = work-stealing) is sound. (Note: the *tutorial page* does not call the default work-stealing in one sentence — but the two facts are each documented, so the composed claim holds.) |
| 7 | `tokio::spawn` hands a future to the scheduler and returns a `JoinHandle` the caller can await to interact with the spawned task | tokio.rs/tokio/tutorial/spawning | **CONFIRMED verbatim** — "The tokio::spawn function returns a JoinHandle, which the caller may use to interact with the spawned task." |
| 8 | A tokio task is an asynchronous green thread (not an OS thread); ~one allocation, 64 bytes | tokio.rs/tokio/tutorial/spawning | **CONFIRMED verbatim** — "A Tokio task is an asynchronous green thread" and tasks "require only a single allocation and 64 bytes of memory," so spawning thousands/millions is cheap. |
| 9 | A spawned task must be `'static` (its type's lifetime must be `'static`) and `Send` (tasks spawned by `tokio::spawn` must implement `Send`); this is why `async move` | tokio.rs/tokio/tutorial/spawning | **CONFIRMED verbatim** — "its type's lifetime must be `'static`" and "Tasks spawned by tokio::spawn **must** implement Send." The `'static` → `async move` (ownership capture) link is the documented rationale. |
| 10 | `tokio::time::timeout(dur, fut)` wraps a future and returns `Result<T, Elapsed>` — `Err` if the deadline elapses; engine error vs deadline are distinct (the doubled `Result`) | docs.rs/tokio/latest/tokio/time/fn.timeout.html | **CONFIRMED verbatim** — "Requires a `Future` to complete before the specified duration has elapsed… Otherwise, an error is returned and the future is canceled." Return type `Result<T, Elapsed>`. The draft's `Ok(Ok(_))` / `Ok(Err(_))` / `Err(_)` match arms are exactly correct (outer = elapsed?, inner = engine `Result`). |
| 11 | `tokio::sync::Semaphore` is a counting semaphore (bounded permit pool) for capping concurrency; `acquire_owned` requires the semaphore wrapped in `Arc`; shared across tasks by cloning the `Arc` | docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html | **CONFIRMED verbatim** — "A semaphore maintains a set of permits… used to synchronize access to a shared resource"; documented example limits in-flight requests by cloning an `Arc<Semaphore>`; "The semaphore must be wrapped in an `Arc` to call this method" (re `acquire_owned`). Draft's `Arc::new(Semaphore::new(64))` + `clone().acquire_owned().await` + `drop(permit)` pattern is correct. |
| 12 | `Arc` = atomically reference-counted pointer; how shared state crosses tasks safely | general Rust / M1 source (§07 Threads: `Arc`, `Send`, `Sync`) | **CONFIRMED** — accurate expansion and role; M1 source threads `Arc`/`Mutex`/`Send`/`Sync` exactly as the "fearless concurrency" substrate this lesson calls back to. |

## Markers resolved (6 / 6)

All bracketed `[verify: …]` markers removed → clean prose. No URLs left inline.
- L9 `[verify: "Tokio is an asynchronous runtime…"]` → removed (claim #1 confirmed verbatim; folded the "building blocks for networking" phrase into the sentence)
- L13 `[verify: futures lazy/do nothing until polled — async book; tokio tutorial doesn't state verbatim]` → removed (claim #2: drafter flag VINDICATED — see below; reworded to async-book's verbatim "inert… make progress only when polled")
- L38 `[verify: tokio default multi-threaded work-stealing]` → removed (claim #6 confirmed; default = multi_thread per macro docs, work-stealing per tutorial overview)
- L40 `[verify: tokio::spawn returns JoinHandle]` → removed (claim #7 confirmed verbatim)
- L49 `[verify: green thread; single allocation 64 bytes]` → removed (claim #8 confirmed verbatim)
- L51 `[verify: 'static + Send bounds]` → removed (claim #9 confirmed verbatim)
- L83 `[verify: tokio::time::timeout]` → removed (claim #10 confirmed verbatim)
- L98 `[verify: tokio::sync::Semaphore]` → removed (claim #11 confirmed verbatim)

## The lazy-futures claim (drafter flag) — VERDICT

**Drafter was right to flag, and the claim is TRUE.** The original draft said "Futures are lazy: nothing executes until polled" and flagged that the tokio tutorial does not state this verbatim. Confirmed: the tokio tutorial (both the intro and the spawning page) does NOT state it. But the official async book states it verbatim: **"Futures are inert in Rust and make progress only when polled."** The M1 course source independently corroborates ("lazy computation via the `Future` trait"). Resolution: kept the claim (it is correct), reworded to the async book's exact phrasing ("Rust futures are inert: they make progress only when polled") so the wording is sourced, not merely paraphrased. No softening needed — the fact is solid.

## Perf-number discipline (CRITICAL)

**PASS.** No invented Rust-vs-Python numbers. The only figure is "~64 bytes," which is the documented tokio task size (claim #8, verbatim). "tens of thousands of in-flight requests," "a handful of threads," "a hundred thousand of them" are qualitative scale statements, not benchmarks. "a few hundred lines" describes the exercise scope, not performance. The comparative "competitive with, and often ahead of, a thread-per-request design" is qualitative and unquantified — correct per the no-numbers rule.

## STYLE pass

One H1; seam lead grabs (a proxy spends its time waiting; one-thread-per-request caps out — why async is the only shape worth putting on the hot path). One `## Core concepts` (4 props, claims not terms, in voice). Handoff div present and well-scoped (add a `proxy/` to `module5-serving/`; one operational concern; `cargo build`, local, no GPU). Ending varies (reframe: "You put the right language on the hottest inch of it.") — distinct from L14's cost-shaped close; not a template. The ASCII data-flow diagram earns its place (carries the client → Rust proxy → mock engine / Python control-plane split that prose alone would muddy — STYLE §6). Acronym/term discipline: tokio glossed ("Tokyo" + I/O); `Arc` expanded ("atomically reference-counted pointer"); OS thread vs green thread taught; `JoinHandle`/`Semaphore`/`'static`/`Send` each introduced one-per-section with a gloss (no §8 parade). Builds on L14 explicitly ("the `?` operator from lesson 14," "the borrow checker you met in lesson 14") — correct for a paired entry. Second person / present / active throughout. No defects.

## Defects fixed

1. **Lazy-futures wording** (L13): reworded to the async book's verbatim "inert… make progress only when polled" so the claim is sourced (see above). Marker removed.
2. Marker removal across 8 sites (above).
No prose defects beyond these — the draft was accurate and clean as written; the timeout doubled-`Result` and the `Arc`+`Semaphore` patterns were correct on first read.

## FLAGGED

None blocking.
- (Minor, no action) Claim #6: the "default is multi-threaded work-stealing" is a *composed* fact — "default = multi_thread" (macro docs) + "multi_thread = work-stealing" (tutorial overview). Both halves are documented; no single sentence in the tutorial asserts the composition. The lesson's claim is correct; logged here for transparency.
- (Minor, no action) Snippets are illustrative and verified by read per PLAN (BUILD→TEST gate begins at M6). The `forward`/`Semaphore` examples elide the surrounding server wiring (e.g. the HTTP listener), which is appropriate for an entry lesson and is exactly what the exercise brief asks the reader to build.
