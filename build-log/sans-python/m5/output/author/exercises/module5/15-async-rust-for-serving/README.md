# Exercise: Async Rust for Serving

## Goal

Add a `proxy/` to `module5-serving/` — a tokio async proxy that forwards a request to the module's mock inference endpoint and adds one operational concern the raw engine doesn't enforce: a request **timeout**, or a **concurrency cap**. It builds with `cargo build` and runs locally — no GPU, no cloud.

## Why

This is where Rust earns its place in the AI platform. An AI Platform Engineer puts a thin async tier on the hot path to hold many in-flight requests on a few threads and to enforce — at compile time — the deadlines and backpressure that keep a traffic spike from becoming an outage, while Python stays the control plane behind it. You build that tier here.

## Setup

You need a mock endpoint to forward to. If `module5-serving/` already exposes one (from the serving lessons), point the proxy at it. If not, stand up the smallest possible stub: a local HTTP endpoint that sleeps briefly and returns a JSON body — a few lines of Python (`uvicorn`/FastAPI) or any `http.server` handler. The proxy must not depend on a real model, GPU, or cloud service.

## Steps

1. From `module5-serving/`, run `cargo new --bin proxy`. `cd proxy`.
2. Add dependencies to `Cargo.toml`: `tokio` with the `full` feature (`tokio = { version = "1", features = ["full"] }`) and an async HTTP client such as `reqwest`. Run `cargo build` to fetch them.
3. Mark `main` with `#[tokio::main]` so the runtime starts and your top-level future runs.
4. Define a `forward(prompt: String) -> Result<String, ProxyError>` async function that sends the prompt to the mock endpoint and returns the response body. Use `?` to propagate errors; define a small `ProxyError` enum (reuse the shape from exercise 14).
5. **Add exactly one operational concern** (pick one; the other is a stretch):
   - **Timeout** — wrap the upstream call in `tokio::time::timeout(Duration::from_secs(N), ...)`. Return `ProxyError::Timeout` when the deadline elapses, and handle the doubled `Result` (deadline vs. engine error) explicitly.
   - **Concurrency cap** — wrap a shared `Arc<tokio::sync::Semaphore>` with a fixed permit count; `acquire` a permit before forwarding and release it after. Prove the cap holds by spawning more concurrent requests than permits and observing they serialize.
6. In `main`, `tokio::spawn` several concurrent `forward` calls (use `async move` so each task owns what it captures), collect the `JoinHandle`s, `.await` them, and print each result.
7. Run `cargo build` (debug) and `cargo run`. Confirm the proxy forwards to the mock endpoint and returns its body.
8. Exercise the concern: for the timeout, make the mock sleep longer than the deadline and confirm you get `Timeout`, not a hang. For the cap, send more concurrent requests than permits and confirm they serialize instead of all hitting the upstream at once.

## Done when

- `module5-serving/proxy/` is a tokio crate that `cargo build` compiles clean (no errors, no warnings).
- `main` is `#[tokio::main]`, spawns concurrent `forward` tasks with `tokio::spawn`, and awaits their `JoinHandle`s.
- The proxy forwards a request to the local mock endpoint and returns its response.
- Your one operational concern is enforced and demonstrated: a slow upstream returns `Timeout` (not a hang), **or** excess concurrent requests serialize behind the semaphore cap.
- Every failure path is handled — no `.unwrap()` that would panic the runtime on a real error.
- Runs entirely on localhost: no GPU, no cloud, no real model.

## Stretch

Add the *second* concern so the proxy enforces both a timeout and a concurrency cap together, and confirm a request that exceeds the deadline releases its semaphore permit (no permit leak under timeout). Then write a three-line note: how would Python (the control plane) configure this proxy's deadline and permit count at startup — and which of the two tiers should own each value, and why? No code change required for the note; it is the mixed-language seam in one paragraph.
