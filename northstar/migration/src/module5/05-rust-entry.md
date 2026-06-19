# Rust (Entry)

> **Threaded in from** `module1/rust-module1-*` (rust-book-structure, rust-exercises-by-topic — 98
> exercises). Rust is installed in Module 1 but *taught here* — at the serving layer.
> ([[language-track-threading]])

Rust is the **serving / Deploy layer** language (inference, CLIs, async pipelines, performance-critical
components). Ownership is irreducible, so it gets one **small concentrated on-ramp**, then threads like
TypeScript.

## On-ramp (concentrated, ~3–4 lessons at entry)

Intro (syntax, `fn`, types) · Basic Calculator (integers, control flow, loops) · **Ticket v1 core (structs,
ownership, borrowing, stack/heap)**. → *"you understand ownership and can write basic Rust."* This is the one
allowed concentrated block — ownership is a gestalt you need whole before any real Rust.

## Point-of-use threads (after the on-ramp)

| Rust topic | Pulled by |
|------------|-----------|
| Ticket v2 (enums, `Result`, error handling, `thiserror`, `TryFrom`) | typed error handling in serving / CLI |
| Traits (bounds, `From`, `Deref`, derive) | generic serving components, typed schemas |
| Ticket Management (collections, iterators, lifetimes, `HashMap`) | data processing in serving pipelines |
| Threads (`Arc`/`Mutex`/channels, `Send`/`Sync`) | concurrent agent task pools, parallel serving (some reaches back to M4) |
| Futures (`async`/`.await`, `tokio`, spawn, cancellation) | async serving, streaming, async tool calls |

(Rust topics no serving/CLI/async task in this curriculum demands → antilibrary.)

**Authoring note:** under the thesis, serving lessons here are *authored in Rust* — this is where the
serving-layer writing shifts from Python-literacy to Rust.
