# Rust Break-In

The serving stack you built across this module — engine, metrics, rollout, FinOps, ingestion — sits in front of a model on the request hot path, and every millisecond there is a millisecond the user waits. Rust enters at exactly this seam: it is the language you reach for when a garbage-collector pause or an unbounded allocation is the difference between a clean p99 and a paged on-call engineer.

## Why Rust Now

The Sans Python thesis is point-of-use, not upfront tax — the same rule that let TypeScript wait until you wrote a tool the model called by name. Rust waits until you have a hot path. You have one now. The serving layer is where latency is a contract, not a chart, and where a pause from a background collector cycle is not noise — it is a violated SLO under load.

Python stays. It is the control plane: the glue that loads config, wires the FinOps quotas, orchestrates the rollout, talks to the experiment tracker. Nothing you wrote in Python becomes wrong. Rust is not a rewrite — it is a second language for the one tier where Python's runtime costs are paid on every request: the proxy, the gateway, the router that touches each token's worth of traffic before it reaches the engine.

Three properties earn Rust its place here, and only here:

- **Predictable latency.** No garbage collector means no stop-the-world pause to spike your tail latency. Memory is freed at a deterministic point you can read off the code, and none of that ownership bookkeeping slows the program while it runs.
- **Memory safety without that collector.** The compiler proves your references are valid before the binary exists. Use-after-free and data races are compile errors, not 3am incidents.
- **Throughput under concurrency.** A small Rust proxy holds thousands of in-flight connections on a handful of threads without the per-request overhead a Python process pays.

You do not learn all of Rust. You learn the one genuinely new idea — ownership — and the slice of the type system the serving layer touches. The rest threads in later, at its own point of use.

## The One New Idea: Ownership

If you know Python and TypeScript, almost everything in Rust has a familiar shape. Functions, structs, conditionals, loops — you can read them on sight. One idea has no analog in either language, and you have to hold it whole before any Rust makes sense: **ownership**.

In Python, a value lives until the garbage collector decides nobody is looking. In Rust, every value has exactly one owner, and when that owner goes out of scope, the value is freed — at a point you can see in the source.

Three rules, and they are the whole system:

- Each value has an *owner*.
- There can be only one owner at a time.
- When the owner goes out of scope, the value is dropped.

That last rule is why there is no garbage collector and no manual `free()`. The compiler inserts the cleanup for you, deterministically, at the closing brace.

```rust
fn main() {
    let request = String::from("classify this");  // request owns the String
    handle(request);                               // ownership MOVES into handle
    // request is no longer valid here — using it is a compile error
}

fn handle(body: String) {
    println!("{body}");
}   // body goes out of scope; the String is dropped here
```

Passing `request` into `handle` *moves* it. The original binding is now invalid — the compiler tracks this and refuses to compile a use-after-move. This feels strict the first time it stops your build. It is the same strictness that means a freed buffer can never be read again, because the compiler already proved it can't be.

## Borrowing: Access Without Taking

Moving a value every time you want to read it would be unworkable — a serving function that logs a request body shouldn't consume it. So Rust lets you *borrow* a value with a reference (`&`) instead of taking ownership:

```rust
fn log_request(body: &String) {     // borrows; does not take ownership
    println!("received: {body}");
}                                    // borrow ends; nothing is dropped

fn main() {
    let request = String::from("classify this");
    log_request(&request);          // lend a reference
    log_request(&request);          // still valid — we only borrowed
}
```

The borrow checker enforces one rule that prevents data races at compile time: **either many readers or one writer, never both.** You can hand out any number of shared references (`&T`), or exactly one mutable reference (`&mut T`), but not both at once.

```rust
let mut counter = 0u64;
let r1 = &counter;          // shared borrow — fine
let r2 = &counter;          // another shared borrow — fine
println!("{r1} {r2}");
let w = &mut counter;       // exclusive borrow — fine now that r1/r2 are done
*w += 1;
```

That rule is the whole reason Rust calls its concurrency "fearless." On the serving hot path, where many requests touch shared state at once, the compiler refuses to compile two threads writing the same buffer. The bug class that produces heisenbugs in a threaded Python or C service is a build error here.

## Lifetimes: How Long a Borrow Is Valid

A reference can't outlive the value it points to — otherwise it would be a dangling pointer, the exact bug Rust exists to kill. *Lifetimes* are how the compiler tracks this. Most of the time it infers them and you write nothing:

```rust
fn first_word(s: &str) -> &str {     // compiler infers the borrow lifetimes
    s.split(' ').next().unwrap_or("")
}
```

You only annotate lifetimes when the compiler can't tell which input a returned reference came from — a struct holding a reference, or a function returning a borrow tied to one of several arguments. That is later-thread material. For the entry, the takeaway is the model, not the syntax: **a borrow is valid only as long as the thing it borrows lives, and the compiler proves it.**

## The Type System, Briefly

Rust is statically typed, like TypeScript — every value's type is known at compile time, and the compiler infers most of them. Two constructs carry the serving layer.

**Structs** model your data shapes — the typed request and response that cross your proxy. This is the same parse-don't-validate instinct you built with TypeScript's typed tool contract, now enforced by a compiler with no escape hatch:

```rust
struct InferenceRequest {
    model: String,
    prompt: String,
    max_tokens: u32,
}
```

**Enums** model a value that is one of several shapes — and `Result<T, E>`, Rust's built-in error type, is exactly this. There are no exceptions in Rust. A function that can fail returns its outcome *in the type*:

```rust
enum ProxyError {
    Upstream(String),
    Timeout,
}

fn forward(req: &InferenceRequest) -> Result<String, ProxyError> {
    if req.max_tokens == 0 {
        return Err(ProxyError::Upstream("max_tokens must be > 0".into()));
    }
    Ok(format!("response for {}", req.model))
}
```

The caller cannot ignore the failure — the compiler forces a `match` or the `?` operator to unwrap a `Result`. The discriminated-union instinct from the TypeScript tool result (`status: "success" | "error"`) is the same instinct here; Rust makes it the only way errors travel. That is the entire point of moving the hot path to Rust: the failures that surface as runtime surprises in a Python proxy are surfaced at compile time instead.

## cargo: the One Tool You Need

`cargo` is Rust's build tool, package manager, and test runner in one. You met `rustup` and `cargo` when you installed Rust in Module 1; here you use them.

```bash
cargo new serving-proxy        # scaffold a project with Cargo.toml + src/main.rs
cargo build                    # compile (debug)
cargo build --release          # compile optimized — the build you serve from
cargo run                      # build and run
cargo check                    # type-check fast, no binary — the inner-loop command
cargo test                     # run tests
```

`cargo check` is the Rust equivalent of `tsc --noEmit` — the fast feedback loop where the compiler reviews your ownership and types without producing a binary. Dependencies go in `Cargo.toml`, the way `package.json` holds npm packages or `pyproject.toml` holds your Python deps:

```toml
[package]
name = "serving-proxy"
version = "0.1.0"
edition = "2021"

[dependencies]
```

One `Cargo.toml`, one `cargo check`, and the compiler tells you — before anything runs — whether your ownership is sound, your borrows are valid, and your error paths are handled. On the serving layer, that review is the safety budget you can't afford to spend at runtime.

## Core Concepts

- Rust earns its place at the serving hot path because it delivers predictable latency with no garbage-collector pauses and memory safety the compiler proves before the binary exists — the control plane stays Python, the hot path becomes Rust.
- Ownership is the one genuinely new idea: every value has exactly one owner, only one at a time, and the value is dropped deterministically when its owner goes out of scope — which is why there is no garbage collector.
- Borrowing lends access without taking ownership, and the borrow checker enforces many-readers-XOR-one-writer at compile time, turning the data-race bug class into build errors.
- Rust models failure in the type system with `Result<T, E>` — the same discriminated-union instinct as a TypeScript typed tool result — and the compiler forces the caller to handle it rather than letting it surface at runtime.

<div class="claude-handoff" data-exercise="exercises/module5/14-rust-break-in/">

**Build It in Claude Code** — `cargo new` a small Rust program that models a typed inference request and response with structs and a `Result`-returning handler, then make it compile clean with `cargo check`. Deliberately trigger one ownership error (use a value after moving it) and read what the compiler tells you before you fix it.

</div>
