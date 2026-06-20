# Exercise: Rust Break-In

## Goal

`cargo new` a small Rust program that models a typed inference request and response with structs, returns its outcome as a `Result<T, E>`, and compiles clean under `cargo check`. Along the way, trigger one ownership error on purpose and read what the compiler tells you.

## Why

An AI Platform Engineer puts Rust on the serving hot path because the compiler proves memory safety and forces failure to travel in the type — and the price of admission is holding ownership whole. This exercise is the on-ramp: a typed request/response model, a `Result`-returning handler, and one deliberate borrow-checker error so you learn to read the compiler instead of fighting it.

## Steps

1. From inside `module5-serving/`, run `cargo new --bin rust-onramp` (a scratch crate; the real `proxy/` lands in exercise 15). `cd rust-onramp`.
2. In `src/main.rs`, define an `InferenceRequest` struct with fields `model: String`, `prompt: String`, and `max_tokens: u32`.
3. Define a `ProxyError` enum with at least two variants — for example `Upstream(String)` and `Timeout`. Add `#[derive(Debug)]` above it so you can print it.
4. Write `fn handle(req: &InferenceRequest) -> Result<String, ProxyError>` that:
   - borrows the request (takes `&InferenceRequest`, does **not** consume it);
   - returns `Err(ProxyError::Timeout)` when `req.max_tokens == 0`;
   - otherwise returns `Ok(...)` with a stub response string built from `req.model` and `req.prompt`.
5. In `main`, build a request, call `handle(&req)` **twice** (proving the borrow did not consume it), and `match` on the `Result` to print either the response or the error with `{:?}`.
6. Run `cargo check`. Fix any type or ownership errors until it exits clean.
7. **Trigger the ownership lesson on purpose.** Add a line that *moves* the request into a function taking `req: InferenceRequest` (by value), then try to use `req` again afterward. Run `cargo check`, read the `value used here after move` error and its help text, then fix it — either by borrowing instead, or by `.clone()`-ing — and note which you chose and why.
8. Run `cargo run` and confirm it prints a response for a valid request and the `Timeout` error for a `max_tokens: 0` request.

## Done when

- `rust-onramp/src/main.rs` defines `InferenceRequest`, `ProxyError`, and a borrowing `handle` returning `Result<String, ProxyError>`.
- `cargo check` exits with no errors and no warnings.
- `handle(&req)` is called more than once on the same value — proving you borrowed rather than moved.
- The `match` handles both the `Ok` and the `Err` arm; there is no `.unwrap()` hiding a failure path.
- You can describe, in one sentence, the `value used here after move` error you triggered in step 7 and how you resolved it.

## Stretch

Add a `validate` step that returns `Result<InferenceRequest, ProxyError>` and use the `?` operator to chain `validate` into `handle`, so a bad request short-circuits with one `?` instead of a nested `match` — the parse-don't-validate pattern. Then add `#[derive(Debug, Clone)]` to `InferenceRequest` and write a two-line note comparing the cost of `.clone()` versus borrowing on a hot path that runs this per request. No network, no async, no dependencies — `cargo check` and `cargo run` only.
