# Exercise 02 — Inside the Engine: Continuous Batching & Paged KV-Cache

## Goal

Replace the naive one-request-at-a-time handler in `module5-serving/` with a continuous-batching scheduler and a paged KV-cache allocator — both simulated — then measure the simulated throughput gain over static batching. No GPU, no real attention math.

## Why

An inference engine is not a REST server: it keeps the GPU saturated by scheduling a living batch and stores its KV cache in pages, not contiguous slabs. Building both in simulation makes the two numbers a platform engineer answers for — throughput and KV memory — observable instead of mysterious, and it is the mechanism below the "static content first" rule from Module 3.

## Steps

1. **Two-phase request model.** Extend `MockEngine` so each request has an explicit `prefill` cost (one parallel step, compute-bound, produces the first token and sets TTFT) and a per-token `decode` cost (memory-bound, sets TPOT). Each request carries a random output length so requests finish at different times.

2. **Static-batching baseline.** Add `scheduler_static.py`: collect N requests, run them as a fixed group, return only when the *slowest* finishes. Record total wall time and throughput (tokens/sec). This is the baseline to beat.

3. **Continuous-batching scheduler.** Add `scheduler_continuous.py`: step the batch one decode token at a time. Between steps, evict any sequence that hit its output length (free its slot) and admit any waiting request into a free slot. Implement chunked prefill: slice a long prompt into fixed chunks so admitting a big prompt doesn't stall the decode steps of sequences already in the batch.

4. **Paged KV-cache allocator.** Add `kv_cache.py`: a `BlockAllocator` with fixed-size blocks and a per-request `block_table` mapping logical token positions to physical block ids. A sequence grows by allocating one block at a time (never pre-reserving a max-length slab); on eviction its blocks return to the free pool. Track fragmentation — reserved blocks vs. blocks actually holding tokens — for both the contiguous baseline and the paged allocator.

5. **Prefix sharing.** Let two requests with an identical prompt prefix point their block tables at the *same* physical blocks for the shared span, and count the prefill work skipped.

6. **Measure.** Run the same workload (mixed prompt lengths, mixed output lengths, staggered arrivals) through both schedulers. Print throughput and mean TTFT for each, and the fragmentation percentage for contiguous vs. paged allocation.

## Done when

- `python scheduler_continuous.py` reports higher throughput than `scheduler_static.py` on the same workload, with the speedup printed (the static baseline is held hostage by its slowest request; continuous batching is not).
- The paged allocator reports materially lower fragmentation than the contiguous baseline, and a sequence's `block_table` shows non-contiguous physical blocks.
- Two requests sharing a prefix share physical blocks, and the skipped-prefill count is printed and non-zero.
- No GPU and no real attention computation — prefill and decode are simulated timed phases.

## Stretch

Add a long prompt that, *without* chunked prefill, spikes the TPOT of sequences already decoding; then turn chunked prefill on and show the tail TPOT drop. Print p99 TPOT both ways so the starvation fix is measured, not asserted.
