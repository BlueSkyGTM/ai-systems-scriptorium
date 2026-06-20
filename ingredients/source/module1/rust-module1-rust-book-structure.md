# Module 1 · Rust — Book Structure

> Source: `book/src/SUMMARY.md`. The mdBook narrative; each section maps 1:1 to an exercise folder.

## 01 · Intro
- Welcome — course orientation and Rust setup — `exercises/01_intro/00_welcome/`
- Syntax — basic Rust syntax overview — `exercises/01_intro/01_syntax/`

## 02 · Basic Calculator
- A Basic Calculator — arithmetic fundamentals and integer operations — `exercises/02_basic_calculator/00_intro/`
- Integers — integer types and literals — `exercises/02_basic_calculator/01_integers/`
- Variables — variable bindings and mutability — `exercises/02_basic_calculator/02_variables/`
- Branching: `if`/`else` — conditional branching — `exercises/02_basic_calculator/03_if_else/`
- Panics — unrecoverable errors and panic semantics — `exercises/02_basic_calculator/04_panics/`
- Factorial — composing arithmetic and control flow — `exercises/02_basic_calculator/05_factorial/`
- Loops: `while` — conditional loops — `exercises/02_basic_calculator/06_while/`
- Loops: `for` — iteration with `for` — `exercises/02_basic_calculator/07_for/`
- Overflow and underflow — integer overflow behavior — `exercises/02_basic_calculator/08_overflow/`
- Saturating arithmetic — saturating math operations — `exercises/02_basic_calculator/09_saturating/`
- Conversions: `as` casting — primitive type casting — `exercises/02_basic_calculator/10_as_casting/`

## 03 · Ticket v1
- Ticket v1 — modeling a ticket with structs — `exercises/03_ticket_v1/00_intro/`
- Structs — defining and instantiating structs — `exercises/03_ticket_v1/01_struct/`
- Validation — input validation strategies — `exercises/03_ticket_v1/02_validation/`
- Modules — module system and file structure — `exercises/03_ticket_v1/03_modules/`
- Visibility — public/private visibility rules — `exercises/03_ticket_v1/04_visibility/`
- Encapsulation — encapsulating internal state — `exercises/03_ticket_v1/05_encapsulation/`
- Ownership — ownership and move semantics — `exercises/03_ticket_v1/06_ownership/`
- Setters — setter methods and `&mut self` — `exercises/03_ticket_v1/07_setters/`
- Stack — stack allocation and value semantics — `exercises/03_ticket_v1/08_stack/`
- Heap — heap allocation with `Box` — `exercises/03_ticket_v1/09_heap/`
- References in memory — memory layout of references — `exercises/03_ticket_v1/10_references_in_memory/`
- Destructors — `Drop` and resource cleanup — `exercises/03_ticket_v1/11_destructor/`
- Outro — module summary — `exercises/03_ticket_v1/12_outro/`

## 04 · Traits
- Traits — defining shared behavior — `exercises/04_traits/00_intro/`
- Trait — trait definitions and implementations — `exercises/04_traits/01_trait/`
- Orphan rule — coherence and the orphan rule — `exercises/04_traits/02_orphan_rule/`
- Operator overloading — implementing operators via traits — `exercises/04_traits/03_operator_overloading/`
- Derive macros — compiler-generated trait implementations — `exercises/04_traits/04_derive/`
- Trait bounds — constraining generics with bounds — `exercises/04_traits/05_trait_bounds/`
- String slices — `str` and `&str` — `exercises/04_traits/06_str_slice/`
- `Deref` trait — dereference coercion and smart pointers — `exercises/04_traits/07_deref/`
- `Sized` trait — sizedness and dynamically sized types — `exercises/04_traits/08_sized/`
- `From` trait — infallible conversions — `exercises/04_traits/09_from/`
- Associated vs generic types — choosing between associated and generic types — `exercises/04_traits/10_assoc_vs_generic/`
- `Clone` trait — explicit duplication of values — `exercises/04_traits/11_clone/`
- `Copy` trait — implicit bitwise duplication — `exercises/04_traits/12_copy/`
- `Drop` trait — custom destructors — `exercises/04_traits/13_drop/`
- Outro — module summary — `exercises/04_traits/14_outro/`

## 05 · Ticket v2
- Ticket v2 — enums, error handling, and packages — `exercises/05_ticket_v2/00_intro/`
- Enums — defining and using enumerations — `exercises/05_ticket_v2/01_enum/`
- Branching: `match` — pattern matching with `match` — `exercises/05_ticket_v2/02_match/`
- Variants with data — enums carrying payload data — `exercises/05_ticket_v2/03_variants_with_data/`
- Branching: `if let` and `let/else` — concise pattern matching — `exercises/05_ticket_v2/04_if_let/`
- Nullability — representing absence with `Option` — `exercises/05_ticket_v2/05_nullability/`
- Fallibility — representing errors with `Result` — `exercises/05_ticket_v2/06_fallibility/`
- Unwrap — convenience error handling methods — `exercises/05_ticket_v2/07_unwrap/`
- Error enums — custom error types as enums — `exercises/05_ticket_v2/08_error_enums/`
- `Error` trait — standard error trait — `exercises/05_ticket_v2/09_error_trait/`
- Packages — crates and packages — `exercises/05_ticket_v2/10_packages/`
- Dependencies — managing crate dependencies — `exercises/05_ticket_v2/11_dependencies/`
- `thiserror` — derive macro for error types — `exercises/05_ticket_v2/12_thiserror/`
- `TryFrom` trait — fallible conversions — `exercises/05_ticket_v2/13_try_from/`
- `Error::source` — chaining error sources — `exercises/05_ticket_v2/14_source/`
- Outro — module summary — `exercises/05_ticket_v2/15_outro/`

## 06 · Ticket Management
- Ticket Management — collections, iterators, and lifetimes — `exercises/06_ticket_management/00_intro/`
- Arrays — fixed-size arrays — `exercises/06_ticket_management/01_arrays/`
- Vectors — growable `Vec` collections — `exercises/06_ticket_management/02_vec/`
- Resizing — dynamic capacity management — `exercises/06_ticket_management/03_resizing/`
- Iterators — the `Iterator` trait — `exercises/06_ticket_management/04_iterators/`
- Iter — iterating over collections — `exercises/06_ticket_management/05_iter/`
- Lifetimes — lifetime annotations and elision — `exercises/06_ticket_management/06_lifetimes/`
- Combinators — iterator and `Option`/`Result` combinators — `exercises/06_ticket_management/07_combinators/`
- `impl Trait` — opaque return types — `exercises/06_ticket_management/08_impl_trait/`
- `impl Trait`, pt.2 — `impl Trait` in argument position — `exercises/06_ticket_management/09_impl_trait_2/`
- Slices — borrowed views into arrays and vectors — `exercises/06_ticket_management/10_slices/`
- Mutable slices — mutable borrowed views — `exercises/06_ticket_management/11_mutable_slices/`
- Two states — modeling multiple states with types — `exercises/06_ticket_management/12_two_states/`
- `Index` trait — indexing syntax via trait — `exercises/06_ticket_management/13_index/`
- `IndexMut` trait — mutable indexing syntax — `exercises/06_ticket_management/14_index_mut/`
- `HashMap` — hash-based key/value store — `exercises/06_ticket_management/15_hashmap/`
- `BTreeMap` — ordered key/value store — `exercises/06_ticket_management/16_btreemap/`

## 07 · Threads
- Threads — concurrency with OS threads — `exercises/07_threads/00_intro/`
- Threads — spawning and joining threads — `exercises/07_threads/01_threads/`
- `'static` lifetime — `'static` bounds for thread safety — `exercises/07_threads/02_static/`
- Leaking memory — intentional memory leaks for `'static` data — `exercises/07_threads/03_leak/`
- Scoped threads — non-`'static` scoped thread borrows — `exercises/07_threads/04_scoped_threads/`
- Channels — message passing between threads — `exercises/07_threads/05_channels/`
- Interior mutability — `RefCell` and `Cell` patterns — `exercises/07_threads/06_interior_mutability/`
- Ack pattern — acknowledgment signaling between threads — `exercises/07_threads/07_ack/`
- Client — building a threaded client — `exercises/07_threads/08_client/`
- Bounded channels — backpressure with bounded channels — `exercises/07_threads/09_bounded/`
- Patching — applying patches across threads — `exercises/07_threads/10_patch/`
- `Mutex`, `Send` and `Arc` — shared-state concurrency primitives — `exercises/07_threads/11_locks/`
- `RwLock` — reader/writer locks — `exercises/07_threads/12_rw_lock/`
- Without channels — shared-state-only communication — `exercises/07_threads/13_without_channels/`
- `Sync` trait — thread-safe shared access — `exercises/07_threads/14_sync/`

## 08 · Futures
- Futures — async/await and asynchronous Rust — `exercises/08_futures/00_intro/`
- Asynchronous functions — `async fn` and `.await` — `exercises/08_futures/01_async_fn/`
- Spawning tasks — async task spawning — `exercises/08_futures/02_spawn/`
- Runtime — async runtime and execution — `exercises/08_futures/03_runtime/`
- Future trait — the `Future` trait and polling — `exercises/08_futures/04_future/`
- Blocking the runtime — avoiding blocking in async contexts — `exercises/08_futures/05_blocking/`
- Async-aware primitives — async synchronization types — `exercises/08_futures/06_async_aware_primitives/`
- Cancellation — task cancellation semantics — `exercises/08_futures/07_cancellation/`
- Outro — module summary — `exercises/08_futures/08_outro/`
