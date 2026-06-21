# When the Array Wins

The Python interpreter visits every element in a list, unpacks the object, calls the operator, and boxes the result back. A vectorized reduction hands the whole buffer to one compiled C loop that does none of that. At small scales the difference is noise; at batch scale it is the difference between keeping up and falling behind.

## What You Build

You build a speedup benchmark that times a loop-based sum-of-squares against `(arr ** 2).sum()` across a range of array sizes, prints the speedup at each size, and identifies where the vectorized path starts to dominate.

## The Source of the Speedup

Module 2 showed what a ufunc does mechanically: it selects a typed C inner loop, walks the buffer, and never hands control back to the Python interpreter between elements. The cost being avoided is not trivial. Each Python operation on a list element requires a pointer dereference to the boxed object, a type check, an arithmetic dispatch, and a re-boxing of the result. For N elements, that is O(N) trips through the interpreter.

A vectorized reduction pays interpreter overhead exactly once: the call that starts the loop. Inside the C loop, every element is a raw typed value in a contiguous buffer, the CPU's SIMD units can process several per clock, and the prefetcher can stay ahead because the access pattern is linear. Microsoft Learn's "Explore and Analyze Data with Python" module frames the payoff directly: operations on typed NumPy arrays run far more efficiently than the equivalent work over Python sequences ([learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas)).

You can see the cost difference with a minimal experiment. Time a Python loop computing sum-of-squares against the vectorized path:

```python
import numpy as np
import time

rng = np.random.default_rng(42)
N = 1_000_000
arr = rng.standard_normal(N).astype(np.float64)

# Loop path
start = time.perf_counter()
total = 0.0
for x in arr:
    total += x * x
loop_ms = (time.perf_counter() - start) * 1000

# Vectorized path
start = time.perf_counter()
result = (arr ** 2).sum()
vec_ms = (time.perf_counter() - start) * 1000

print(f"loop:        {loop_ms:.1f} ms")
print(f"vectorized:  {vec_ms:.2f} ms")
print(f"speedup:     {loop_ms / vec_ms:.0f}x")
```

On a typical machine at N=1,000,000:

```
loop:        320.4 ms
vectorized:  1.82 ms
speedup:     176x
```

The results are numerically identical (within floating-point rounding). Every millisecond saved is pure interpreter overhead eliminated.

## How the Speedup Scales

The speedup is not constant. At small N, the vectorized path carries its own fixed cost: the Python call, the buffer allocation for intermediate results, and the dispatch through NumPy's type machinery. A loop over ten elements can beat a vectorized call because that fixed cost exceeds the per-element saving.

Measure across a range:

```python
sizes = [10, 100, 1_000, 10_000, 100_000, 1_000_000]
RUNS = 20

print(f"{'N':>10}  {'loop ms':>10}  {'vec ms':>10}  {'speedup':>10}")
print("-" * 46)

for N in sizes:
    data = rng.standard_normal(N).astype(np.float64)

    start = time.perf_counter()
    for _ in range(RUNS):
        total = 0.0
        for x in data:
            total += x * x
    loop_ms = (time.perf_counter() - start) / RUNS * 1000

    start = time.perf_counter()
    for _ in range(RUNS):
        result = (data ** 2).sum()
    vec_ms = (time.perf_counter() - start) / RUNS * 1000

    speedup = loop_ms / vec_ms
    print(f"{N:>10,}  {loop_ms:>10.3f}  {vec_ms:>10.4f}  {speedup:>10.1f}x")
```

Typical output:

```
         N     loop ms      vec ms     speedup
----------------------------------------------
        10       0.005      0.0030        1.7x
       100       0.040      0.0032       12.5x
     1,000       0.360      0.0040       90.0x
    10,000       3.420      0.0155      220.6x
   100,000      34.100      0.1420      240.1x
 1,000,000     320.400      1.8200      176.1x
```

The crossover lives somewhere around N=10 to N=100. Below it, the vectorized path's fixed overhead dominates and the loop can be faster. Above it, the speedup grows until the array outgrows cache, at which point memory bandwidth becomes the bottleneck for both paths and the ratio stabilizes.

## The Crossover and When to Care

The practical rule: if N is known at design time and is reliably small (single digits), a list comprehension is fine. For anything called at batch scale, with N in the thousands or more, the vectorized path is the default. The measurement above is not an academic exercise; it is the decision rule.

At inference time, "batch" is the unit of work. A scoring function called on a batch of 512 embedding vectors runs the reduction 512 times per call. If each call spends 300 ms in a Python loop instead of 2 ms in a ufunc, the difference is 150 seconds versus one second per batch. The vectorized path is not a micro-optimization; it is the budget.

## Core Concepts

- A vectorized reduction pays Python interpreter overhead once (the call) instead of once per element; inside the C loop, elements are raw typed values and SIMD can process several per clock, so the speedup grows with N.
- At small N (typically below ~100), the vectorized path's fixed dispatch cost can exceed the per-element saving, meaning a Python loop may be faster; measuring this crossover is what "vectorization discipline" means.
- The speedup ratio is not constant: it grows as N increases from the crossover until the working set outgrows cache, where memory bandwidth limits both paths and the ratio stabilizes.
- At batch inference scale, the choice between a loop and a vectorized op is a throughput decision, not a style preference; the difference is measured in seconds per batch, not microseconds.

<div class="claude-handoff" data-exercise="exercises/module4/when-the-array-wins/">

**Build It in Claude Code:** Extend `vectorization_report.py` with a speedup benchmark: import `time_sum` from `measure.py`, time a loop vs a vectorized sum-of-squares across a range of array sizes, and print the speedup at each size.

</div>
