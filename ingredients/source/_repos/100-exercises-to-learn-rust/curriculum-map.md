# 100 Exercises to Learn Rust — Curriculum Map

> Module 1 · Rust. Maps each topic to its Sans-Python (AI systems) use case.

| Topic | Rust concept | Sans-Python use case | Module where it surfaces |
| :--- | :--- | :--- | :--- |
| **01 · Intro** | `fn` keyword, type annotations, `String` / `&str`, macros, static typing | Entry point to Rust-based serving layers and CLI tooling; static typing ensures type-safe schemas and compile-time correctness | Serving Layer, CLI Tooling |
| **02 · Basic Calculator** | Primitive types, mutability, control flow, overflow handling, `as` casting | Safe, predictable processing of numeric inputs in CLI tooling and serving layers; prevents silent data corruption in concurrent pipelines | CLI Tooling, Serving Layer |
| **03 · Ticket V1** | Structs, ownership, borrowing, stack vs. heap, modules, visibility | Encapsulated data structures with controlled mutation for reliable serving layers and concurrent agent tasks without data races or GC pauses | Serving Layer, Concurrency/Async |
| **04 · Traits** | Traits, trait bounds, generics, standard traits (`Clone`, `From`/`Into`, `Drop`) | Generic serving-layer components, composable CLI tooling, type-safe schemas enforcing contracts at compile time | CLI Tooling, Type-Safe Agent Schemas |
| **05 · Ticket V2** | Enums, `Option`/`Result`, pattern matching, `Error` trait, `TryFrom`/`TryInto` | Type-safe domain modeling, explicit error handling rejecting invalid inputs at compile time, error propagation through agent pipelines | CLI Tooling, Serving Layer |
| **06 · Ticket Management** | `Vec`, `HashMap`/`BTreeMap`, iterators, combinators, lifetimes, `impl Trait` | Batch-processing, filtering, and routing model inference requests, agent task queues, and configuration records | Serving Layer, Async Tool Calls |
| **07 · Threads** | `std::thread`, mpsc channels, `Arc`, `Mutex`, `RwLock`, `Send`/`Sync` | Core concurrency primitives for high-performance, parallel serving layers; channel patterns and locking strategies for concurrent agent tasks | Serving Layer, Concurrent Agent Tasks |
| **08 · Futures** | `async`/`.await`, `Future` trait, `tokio` runtime, cooperative scheduling | Concurrency substrate for high-throughput, non-blocking serving layers; orchestrating concurrent agent tasks, LLM API tool calls, and streaming pipelines | Async Tool Calls, Concurrent Agent Tasks |
