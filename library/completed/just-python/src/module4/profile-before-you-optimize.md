# Profile Before You Optimize

Engineers who guess wrong about where time goes rewrite the wrong loop. Measuring first costs two minutes; rewriting the wrong function costs a day.

## The Guessing Trap

Your intuition about what is slow is built from general principles, not from your actual data. You know Python loops are slower than NumPy vectorization, so when a pipeline stalls, you reach for the loop and start rewriting. But the loop is often not the bottleneck. The bottleneck is the I/O call above it, the redundant sort below it, or the object construction no one touches. Guessing replaces the wrong thing.

The discipline is simple: time it first, change one thing, time it again. No measurement before the change means no proof the change helped.

## What `time_sum` Already Gives You

The `measure.py` helper you built in Module 1 includes `time_sum`, a function that runs a callable `n` times via `timeit.timeit` and returns the mean elapsed seconds:

```python
import timeit

def time_sum(fn, n: int = 3) -> float:
    """Return mean wall-clock seconds for fn() over n runs."""
    total = timeit.timeit(fn, number=n)
    return total / n
```

`timeit.timeit` does three things that naive `time.time()` brackets miss. It disables garbage collection during the run, so GC pauses do not contaminate the measurement. It repeats the call `number` times and returns the total, which averages out scheduling jitter. And it runs the callable in a clean namespace, so import overhead does not appear in the result. Dividing by `n` gives you the mean per-call cost.

Import it directly:

```python
import sys
import pathlib

# resolve measure.py relative to this file (exercises/module4/vectorization_report.py)
_measure = pathlib.Path(__file__).resolve().parent.parent / "module1" / "the-cost-of-a-python-list"
sys.path.insert(0, str(_measure))
from measure import time_sum
```

## Timing a Loop vs. a Vectorized Sum

Take a concrete problem: sum 500,000 floats. Two implementations, one measurement each.

```python
import numpy as np

rng = np.random.default_rng(42)
data = rng.standard_normal(500_000).astype(np.float64)
floats = data.tolist()

loop_time = time_sum(lambda: sum(floats))
vec_time  = time_sum(lambda: data.sum())

print(f"loop sum:   {loop_time:.5f} s")
print(f"vector sum: {vec_time:.5f} s")
print(f"speedup:    {loop_time / vec_time:.1f}x")
```

On a typical machine you will see something like:

```
loop sum:   0.01823 s
vector sum: 0.00041 s
speedup:    44.5x
```

Those numbers are the evidence. Before you saw them, you might have guessed 5x or 100x; the actual ratio is what drives the decision. That print statement is the proof that the rewrite was worth doing.

## The Three-Step Protocol

Every optimization decision follows the same three steps:

1. Time the current code. Record the number.
2. Change exactly one thing.
3. Time the new code. Compare the numbers.

"Change exactly one thing" is load-bearing. If you swap both the data structure and the algorithm in the same commit, you cannot tell which change produced the gain. The measurement only holds when the experiment is controlled.

This is the same discipline the Azure Well-Architected Framework calls out in its Performance Efficiency pillar: instrument code to identify hot paths, then prioritize optimizing those hot paths and nothing else ([learn.microsoft.com/azure/well-architected/performance-efficiency/optimize-code-infrastructure](https://learn.microsoft.com/azure/well-architected/performance-efficiency/optimize-code-infrastructure)). The principle scales from a single loop to a distributed inference pipeline.

## Reading the Numbers

Two failure modes appear when engineers read timings without context.

The first is the cold-run illusion. The first call to a function may be slower than subsequent calls because of caching, JIT warm-up, or lazy imports. `time_sum` with `n=3` exposes this: if the first run is 0.050 s and the next two are 0.004 s each, the mean is 0.019 s but the median is 0.004 s. Run `n=5` or `n=10` when you see high variance.

The second is the wrong denominator. A 44x speedup on a function that runs once at startup saves microseconds. The same speedup on a function called inside a batch loop of 100,000 rows saves seconds per request. Time the function in the context where it runs in production.

```python
# Measure in the actual batch context, not in isolation
BATCH = 10_000
batch_data = rng.standard_normal((BATCH, 128)).astype(np.float32)

loop_batch = time_sum(lambda: [batch_data[i].sum() for i in range(BATCH)])
vec_batch  = time_sum(lambda: batch_data.sum(axis=1))

print(f"loop batch: {loop_batch:.5f} s")
print(f"vec  batch: {vec_batch:.5f} s")
print(f"speedup:    {loop_batch / vec_batch:.1f}x")
```

The batch context surfaces a far larger absolute gain than the isolated measurement did. The number you optimize against is the one from the real call site.

## What You Do Not Need Yet

`cProfile` and line-by-line profilers are the next tool when `timeit` tells you a function is slow but you cannot see why. M4 introduces them later. For now, the rule is: if you have not timed it with `time_sum` or an equivalent, you do not know where the time goes, and you are guessing.

Knowing the ratio before you rewrite is what separates a productive optimization from a day spent on the wrong problem.

## Core Concepts

- Guessing where code is slow is wrong more often than right; the only safe starting point is a measurement from `timeit` or an equivalent timer that averages out jitter and disables GC.
- `time_sum(fn, n)` wraps `timeit.timeit` to return the mean per-call cost; import it from `measure.py` and use it before and after every change.
- The three-step protocol is: measure the baseline, change one thing, measure again; changing more than one thing at once makes the result uninterpretable.
- A speedup ratio is only meaningful at the real call site; a 44x gain on a function called once saves nothing if the bottleneck is the outer batch loop.

<div class="claude-handoff" data-exercise="exercises/module4/profile-before-you-optimize/">

**Build It in Claude Code:** Build `vectorization_report.py`, a script that imports `time_sum` from `measure.py` and profiles a plain Python loop against a vectorized sum, printing both timings and the speedup ratio, then asserts the results agree.

</div>
