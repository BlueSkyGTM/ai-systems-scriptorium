# VERIFY verdict — M5 L14 · Rust Break-In

**Verifier:** Sonnet VERIFY subagent · **Date:** 2026-06-19
**Draft:** `build-stages/m5/output/author/14-rust-break-in.md` (edited in place)
**Verdict:** **PASS** (all markers resolved, every claim grounded in the Rust book, break-in altitude mirrors M3, perf stays qualitative)

---

## Claim ledger

| # | Claim | Authority | Result |
|---|-------|-----------|--------|
| 1 | Rust has no garbage collector; "none of that ownership bookkeeping slows the program while it runs" | doc.rust-lang.org/book/ch04-01 | **CONFIRMED verbatim** — "Rust uses a third approach: Memory is managed through a system of ownership with a set of rules that the compiler checks." + "None of the features of ownership will slow down your program while it's running." Draft paraphrases the second sentence faithfully. |
| 2 | The three ownership rules (each value has an owner; one owner at a time; dropped when owner leaves scope) | doc.rust-lang.org/book/ch04-01 | **CONFIRMED verbatim** — book lists exactly: "Each value in Rust has an _owner_." / "There can only be one owner at a time." / "When the owner goes out of scope, the value will be dropped." Draft's three bullets are an accurate paraphrase. |
| 3 | Move semantics — after passing `request` into `handle`, the original binding is invalid; use-after-move is a compile error | doc.rust-lang.org/book/ch04-01 | **CONFIRMED** — "To ensure memory safety, after the line `let s2 = s1;`, Rust considers `s1` as no longer valid." Draft's `String`/move example is correct (`String` is non-`Copy`, so the move applies). |
| 4 | Borrow checker rule: any number of `&T` XOR exactly one `&mut T`, never both at once; prevents data races at compile time | doc.rust-lang.org/book/ch04-02 | **CONFIRMED verbatim** — "At any given time, you can have _either_ one mutable reference _or_ any number of immutable references." + "References must always be valid." Draft's "many readers or one writer" framing and the `counter`/`r1`/`r2`/`w` example obey non-lexical-lifetime scoping (the shared borrows end before the `&mut`, so it compiles) — accurate. |
| 5 | Lifetimes: a reference can't outlive what it points to; the compiler infers most; you annotate only when the source of a returned borrow is ambiguous | doc.rust-lang.org/book ch04-02 / ch10-03 (general Rust knowledge) | **CONFIRMED** — standard, accurate framing. `first_word(&str) -> &str` elides correctly (single input borrow → output borrow, lifetime elision rule). Draft defers annotation syntax to "later-thread material" — correct altitude for an entry lesson. |
| 6 | Rust is statically typed; every value's type is known at compile time; the compiler infers most | rust-module1 source (exercises-by-topic §01) | **CONFIRMED verbatim** — source: "Rust is statically typed, meaning every value's type must be known at compile-time, enabling the compiler to catch errors before runtime." |
| 7 | Structs model data shapes; enums model one-of-several; `Result<T, E>` is Rust's built-in error enum; no exceptions; caller must handle via `match` or `?` | rust-module1 source (§05 Ticket V2) + general Rust | **CONFIRMED** — source §05: "`Result<T, E>`, fallibility in the type system… `?` operator, parse-don't-validate pattern" and that Rust encodes recoverable errors "in function signatures rather than thrown as exceptions." Struct/enum/`Result` snippets compile-correct. |
| 8 | `cargo` is build tool + package manager + test runner; `cargo check` type-checks without a binary (≈ `tsc --noEmit`); deps in `Cargo.toml` | general Rust / rust-module1 (§05 packages, Cargo.toml) | **CONFIRMED** — accurate. `cargo new`/`build`/`build --release`/`run`/`check`/`test` are all real subcommands with the stated behavior. `edition = "2021"` is valid. The `tsc --noEmit` analogy is apt (type-check, no artifact). |

## Markers resolved (5 / 5)

All bracketed `[verify: …]` markers removed → clean prose. No URLs left inline (lesson voice carries none; URLs captured in this ledger).
- L13 `[verify: no GC; "none of the features of ownership will slow down…"]` → removed (claim #1 confirmed verbatim; prose reworded to fold the no-runtime-cost point in)
- L25 `[verify: the three ownership rules verbatim]` → removed (claim #2 confirmed verbatim)
- L45 `[verify: move semantics — "after let s2 = s1… s1 no longer valid"]` → removed (claim #3 confirmed verbatim)
- L63 `[verify: borrowing rules — one mutable XOR any immutable]` → removed (claim #4 confirmed verbatim)
- L90 `[verify: statically typed — rust-module1 source]` → removed (claim #6 confirmed verbatim against source)

## Perf-number discipline (CRITICAL)

**PASS.** One invented figure found and removed: the lead said "a 50ms pause from a background collector cycle" — a concrete number with no source, attached to a generic GC. Softened to "a pause from a background collector cycle" (claim now qualitative). No Rust-vs-Python benchmark numbers anywhere. "thousands of in-flight connections on a handful of threads" is a qualitative scale claim, not a measurement — kept.

## Break-in altitude (source-check vs M3 TypeScript break-in)

**PASS — mirrors `04-typescript-break-in.md` precisely.** Parallel structure confirmed: same `# X Break-In` H1, same `## Why X now` section, the shared verbatim thesis line "The Sans Python thesis is point-of-use, not upfront tax," the same "Nothing you wrote in Python becomes wrong" / "Nothing you know about JS becomes false" reassurance, and the same teach-from-the-reader's-prior-language move (JS→TS there; Python/TS→Rust here). This is the reader's FIRST Rust: ownership is taught from zero ("has no analog in either language"), the three rules are spelled out, every term is glossed. It teaches, it does not assume. Cross-references (parse-don't-validate, the `status: "success" | "error"` discriminated-union callback) are accurate to the M3 content.

## Defects fixed

1. **Invented perf number** (L7): removed "50ms" (see Perf-number discipline above).
2. **Semantic mismatch in the `Result` example** (L112): the `max_tokens == 0` branch returned `ProxyError::Timeout` (labeled "illustrative branch"), which a careful reader trips on — a zero-token request is not a timeout. Changed to `Err(ProxyError::Upstream("max_tokens must be > 0".into()))`, which fits the existing enum and the validation context. Compile-correct (`String` from `&str` via `.into()`).
3. Marker removal across 5 sites (above).

## STYLE pass

One H1; seam lead grabs (the hot path you built, why Rust enters at this seam — no throat-clearing); one `## Core concepts` (4 props, stated as claims not terms, in voice); handoff div present and well-scoped (cargo new → struct + Result handler → deliberately trigger an ownership error → read the compiler). Ending varies (cost-shaped: "the safety budget you can't afford to spend at runtime") — not a template. Acronym discipline: "garbage collector" always spelled in full, never bare "GC"; `Arc`, `cargo`, `Result` introduced in context; SLO/p99 used (consistent with module). Second person / present tense / active voice held start to end. No §8 parade. No defects beyond those fixed.

## FLAGGED

None blocking.
- (Minor, no action) The GC framing in the lead implicitly contrasts Rust with managed runtimes generally. CPython's primary memory management is reference counting (deterministic), not a tracing collector with stop-the-world pauses; its cyclic collector *can* pause but rarely at JVM/Go magnitudes. The lesson's point — deterministic, compiler-proven freeing vs. any GC'd runtime — is the standard, defensible Rust argument and is kept qualitative. Acceptable for an entry lesson.
- (Minor, no action) Code snippets are illustrative and verified by read per PLAN ("Rust/serving snippets are illustrative, verified by read; BUILD→TEST gate begins at M6"). Not machine-compiled.
