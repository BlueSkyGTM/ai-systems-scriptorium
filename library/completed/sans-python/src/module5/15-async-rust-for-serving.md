# Async Rust for serving

A proxy in front of your serving engine spends almost all of its time waiting — for the upstream model to start streaming, for a slow client to read, for the next connection. Spend one operating-system thread per request and you cap out at a few thousand before the machine drowns in context switches. Async Rust is how a handful of threads hold tens of thousands of in-flight requests at once, which is the only shape that makes a Rust proxy worth putting on the hot path.

## Why async, here

The work on the serving edge is I/O-bound, not compute-bound. The proxy isn't doing math; it's holding open sockets and waiting on the network. Blocking a whole thread to wait on a socket is the waste async exists to remove — while one request waits on the upstream engine, the same thread runs another that's ready.

Python solved this with `asyncio`; you already think in `async`/`await`. Rust borrows the same two keywords, so the *shape* of the code transfers directly. What's new underneath is that Rust has no built-in async runtime — the language gives you `async`/`await`, and you bring the engine that runs it. On the serving layer, that engine is **tokio** (the asynchronous runtime for Rust, named for "Tokyo" + I/O), which provides the building blocks for writing networking applications.

## async and await: the same shape, new rules

An `async fn` does not run when you call it. Calling it returns a *future* — a value describing work to be done — and the work happens only when something `.await`s it. Rust futures are inert: they make progress only when polled.

```rust
async fn fetch_upstream(prompt: &str) -> Result<String, ProxyError> {
    // .await yields the thread while the network call is in flight
    let body = call_engine(prompt).await?;
    Ok(body)
}
```

This reads like the Python you know. The difference is what `.await` does: it is a *yield point*. While `fetch_upstream` waits on the network, the thread it was running on is handed to another ready task. No thread sits idle holding a socket. That is the entire efficiency story, and it is why one tokio worker thread can carry thousands of concurrent requests.

The `?` operator from lesson 14 works inside async functions exactly as it does in sync ones — a failed `.await` short-circuits and returns the error. Async did not change how Rust handles failure; it only changed when the work runs.

## tokio: the runtime you bring

You declare the runtime with one macro on `main`. `#[tokio::main]` rewrites your `async fn main` into a synchronous one that starts the runtime and blocks on your top-level future:

```rust
#[tokio::main]
async fn main() {
    // the tokio runtime is running here
}
```

By default this is a multi-threaded, work-stealing scheduler — idle threads steal tasks from busy ones, so the load spreads without you scheduling anything by hand. You write the logic; tokio decides which thread runs which task when.

To run more than one thing at once, you `spawn` a task. `tokio::spawn` hands a future to the scheduler and returns a `JoinHandle` the caller can await to interact with the spawned task:

```rust
let handle = tokio::spawn(async move {
    fetch_upstream("classify this").await
});
let result = handle.await;     // wait for the spawned task to finish
```

A tokio task is not an OS thread. It is an asynchronous green thread — under the hood, a single allocation of about 64 bytes. Spawning a hundred thousand of them is cheap in a way that spawning a hundred thousand OS threads never is. That ratio — many tasks, few threads — is what makes Rust competitive with, and often ahead of, a thread-per-request design on the serving edge.

Two rules come straight from the ownership lessons. A spawned task must be `'static` (its type's lifetime must be `'static`, so it can outlive the function that spawned it) and `Send` (tasks spawned by `tokio::spawn` must implement `Send`, so they can move between worker threads). This is why you see `async move` — the task takes ownership of what it captures, so nothing it touches can be freed out from under it. The borrow checker you met in lesson 14 is the same checker proving your concurrency is sound; async didn't loosen it.

## The hot path: a tokio inference proxy

Here is where Rust earns its place in the AI platform. You put a thin async proxy in front of `module5-serving/` — the mock inference endpoint the rest of this module built against. The proxy is the hot path; Python remains the control plane behind and beside it.

```text
   client ──▶  Rust tokio proxy  ──▶  module5-serving/  (mock engine)
                │  per request:
                │   • forward the body
                │   • enforce a timeout
                │   • cap in-flight concurrency
                ▼
        Python control plane: config, quotas, rollout, metrics
```

The proxy's job is narrow and unforgiving: accept a request, forward it to the engine, return the response, and add the one operational concern the raw engine doesn't enforce. Two concerns matter most on the edge, and tokio gives you both in a line.

**A timeout.** An upstream that hangs must not hang your client. `tokio::time::timeout` wraps any future and fails it if it runs long:

```rust
use tokio::time::{timeout, Duration};

async fn forward(req: InferenceRequest) -> Result<String, ProxyError> {
    match timeout(Duration::from_secs(5), call_engine(&req.prompt)).await {
        Ok(Ok(body)) => Ok(body),
        Ok(Err(e))   => Err(e),                  // engine returned an error
        Err(_)       => Err(ProxyError::Timeout), // the 5s deadline elapsed
    }
}
```

The doubled `Result` is honest: the outer layer reports whether the deadline elapsed, the inner whether the engine itself failed. The compiler makes you handle both — there is no path where a hung upstream silently becomes a hung client.

**A concurrency cap.** An unbounded proxy will happily forward more requests than your engine can serve and turn a traffic spike into a thundering-herd outage. A `Semaphore` gives you backpressure — a fixed number of permits, acquired before forwarding and released when done:

```rust
use std::sync::Arc;
use tokio::sync::Semaphore;

let limiter = Arc::new(Semaphore::new(64));   // at most 64 in flight

let permit = limiter.clone().acquire_owned().await.unwrap();
let result = forward(req).await;
drop(permit);                                  // release the slot
```

`Arc` — an atomically reference-counted pointer — is how the limiter is shared across every task safely; this is the `Arc`/concurrency thread the ownership lessons set up, arriving exactly where serving needs it. The semaphore is the FinOps and reliability lever from earlier in this module, now enforced in the one place that sees every request before it costs you a token.

## Where the seam lands

The proxy is a few hundred lines, and it does what no Python tier on the hot path does for free: hold tens of thousands of connections on a few threads, enforce a deadline the compiler won't let you skip, and cap concurrency with a primitive that can't deadlock the way a hand-rolled lock can. Behind it, Python still owns everything that isn't latency-critical — the config, the quotas, the rollout decisions, the dashboards you wired in this module.

That division is the whole mixed-language thesis made concrete: Python where iteration speed wins, Rust on the one tier where a millisecond is a contract. You didn't replace your platform. You put the right language on the hottest inch of it.

## Core concepts

- Async serving is I/O-bound waiting, and `.await` is a yield point that hands the thread to another ready task — so a few tokio worker threads carry tens of thousands of concurrent requests instead of one thread per request.
- Rust has no built-in async runtime; you bring tokio, declare it with `#[tokio::main]`, and `tokio::spawn` a future onto its multi-threaded work-stealing scheduler, getting back a `JoinHandle`.
- A tokio task is a ~64-byte green thread, not an OS thread, and the `'static` + `Send` bounds on a spawned task are the borrow checker proving your concurrency is sound — async did not loosen ownership.
- A serving proxy earns Rust by adding compiler-enforced operational concerns on the hot path: `tokio::time::timeout` makes a deadline unskippable, and a `Semaphore` shared via `Arc` caps in-flight concurrency for backpressure — with Python still the control plane behind it.

<div class="claude-handoff" data-exercise="exercises/module5/15-async-rust-for-serving/">

**Build it in Claude Code** — add a `proxy/` to `module5-serving/`: a tokio async proxy that forwards a request to the module's mock inference endpoint and adds one operational concern (a `timeout`, or a `Semaphore` concurrency cap). It must build with `cargo build` and run locally — no GPU, no cloud. Open the repo and run the exercise for this lesson.

</div>
