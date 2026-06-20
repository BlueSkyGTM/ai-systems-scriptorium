# 100 Exercises to Learn Rust — Inventory

> Module 1 · Rust language foundation. 8 topics / 98 exercises. Rust = serving layer, CLI tooling, concurrency/async substrate. No antilibrary (all topics are curriculum). No images, no Mermaid.

## Topics

| # | Topic | Sub-exercises | Seam relevance |
|---|-------|---------------|----------------|
| 1 | intro | welcome, syntax | syntax/CLI basics |
| 2 | basic_calculator | intro, integers, variables, if_else_panics, factorial_while, for_overflow, saturating_as_casting | control flow / CLI basics |
| 3 | ticket_v1 | intro, struct_validation, modules_visibility, encapsulation_ownership, setters_stack, heap_references_in_memory, destructor_outro | type-safe schemas |
| 4 | traits | intro, trait_orphan_rule, operator_overloading_derive, trait_bounds_str_slice, deref_sized, from_assoc_vs_generic, clone_copy, drop_outro | type-safe schemas / abstractions |
| 5 | ticket_v2 | intro, enum_match, variants_with_data_if_let, nullability_fallibility, unwrap_error_enums, error_trait_packages, dependencies_thiserror, try_from_source, outro | error handling → serving layer |
| 6 | ticket_management | intro, arrays_vec, resizing_iterators, iter_lifetimes, combinators_impl_trait, impl_trait_2_slices, mutable_slices_two_states, index_index_mut, hashmap_btreemap | collections / data layer |
| 7 | threads | intro, threads_static, leak_scoped_threads, channels_interior_mutability, ack_client, bounded_patch, locks_rw_lock, without_channels_sync | concurrency → serving layer |
| 8 | futures | intro, async_fn_spawn, runtime_future, blocking_async_aware_primitives, cancellation_outro | async → agent tasks |

## Helpers

| Helper | Purpose |
|--------|---------|
| `helpers/common/` | Shared support crate (`Cargo.toml`: name = "common") |
| `helpers/ticket_fields/` | Support crate for ticket exercises (`Cargo.toml`: name = "ticket_fields") |
| `helpers/json2redirects.sh` | Shell script (`#!/bin/bash`) |
