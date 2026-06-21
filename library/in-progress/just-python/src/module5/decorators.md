# Decorators

Every time you want to add timing, logging, or retry logic to a function, you have two choices: copy the boilerplate into the body, or write it once and attach it with a single line. Decorators are the second choice, and they are how production Python code adds cross-cutting behavior without touching the function it wraps.

## What You Build

You build `@timed`, a reusable decorator that records elapsed time for any function you hand it, without modifying that function's body, name, or docstring.

## The Closure Foundation

A decorator is a function that returns a function. To see why, start without the `@` syntax:

```python
import time

def timed(fn):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{fn.__name__} took {elapsed:.4f}s")
        return result
    return wrapper
```

`timed` takes `fn` as its argument and closes over it inside `wrapper`. When `wrapper` runs, `fn` is still in scope because Python captured it at definition time. That captured reference is the closure: `wrapper` remembers `fn` even after `timed` has returned.

The `*args, **kwargs` forwarding makes `wrapper` general. It passes every positional and keyword argument through to `fn` unchanged, so `@timed` works on any function signature without modification.

## The `@` Syntax

The `@decorator` line is sugar for reassigning the name:

```python
@timed
def load_embeddings(path: str) -> list:
    """Load vectors from disk."""
    time.sleep(0.05)  # simulate I/O
    return [1.0, 2.0, 3.0]
```

Python executes that as `load_embeddings = timed(load_embeddings)` before the module finishes loading. From that point forward, `load_embeddings` refers to `wrapper`, not the original function. Call it:

```python
vectors = load_embeddings("embeddings.npy")
# load_embeddings took 0.0512s
print(vectors)
# [1.0, 2.0, 3.0]
```

The original function ran, its result came back, and the timing printed. One decorator line, zero changes to the body.

## Why `functools.wraps` Is Not Optional

Without `wraps`, the wrapper replaces the function's identity:

```python
print(load_embeddings.__name__)   # 'wrapper'  (wrong)
print(load_embeddings.__doc__)    # None        (gone)
```

Tracebacks, logging frameworks, profilers, and docstring tools all read `__name__` and `__doc__`. If your wrapper swallows them, every tool in the stack reports the wrong function. The fix is one import and one line:

```python
import functools
import time

def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{fn.__name__} took {elapsed:.4f}s")
        return result
    return wrapper
```

`functools.wraps(fn)` copies `__name__`, `__doc__`, `__annotations__`, `__module__`, and `__qualname__` from `fn` onto `wrapper`. Now the decorator is transparent to every tool that inspects the function:

```python
@timed
def load_embeddings(path: str) -> list:
    """Load vectors from disk."""
    time.sleep(0.05)
    return [1.0, 2.0, 3.0]

print(load_embeddings.__name__)   # 'load_embeddings'
print(load_embeddings.__doc__)    # 'Load vectors from disk.'
```

This is the pattern the MLflow tracing library uses for its own `@mlflow.trace` decorator, where `functools.wraps` keeps the wrapped function's name visible in traces and tracebacks ([learn.microsoft.com/azure/databricks/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator](https://learn.microsoft.com/azure/databricks/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator)).

## A Second Practical Example: `@lru_cache`

`functools.lru_cache` is a decorator from the standard library that caches return values by argument. You do not write the wrapper; you apply the decorator:

```python
import functools

@functools.lru_cache(maxsize=128)
def embed(text: str) -> tuple:
    """Return a fake embedding for text."""
    return tuple(hash(c) % 100 for c in text[:4])

print(embed("hello"))   # (4, 1, 8, 8)
print(embed("hello"))   # same result, served from cache
print(embed.cache_info())
# CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
```

The decorator wraps `embed` with a lookup table keyed by arguments. The first call executes the function and stores the result; every identical call after that returns the cached value without running the body. `cache_info()` exposes the hit/miss ratio, so you can confirm caching is actually working.

`@lru_cache` is the production pattern for memoizing expensive, pure functions: embedding calls, tokenization, schema lookups. It is a decorator you apply in one line rather than build from scratch.

## The `made-with-ml` Pattern

In the `made-with-ml` utility module, helpers like `set_seeds` and `save_dict` do one job and stay small: each wraps an operation that production code calls in many places. Decorators take that same discipline to a meta level. Instead of putting timing or seeding logic inside each helper, you write it once as a decorator and attach it where it belongs. The body stays focused on the business logic; the wrapper handles the cross-cutting concern.

Write `@timed` once; every function that needs it gets instrumented with no edits to its body. That is what a code reviewer means when they say the logic and the instrumentation belong in separate layers.

## Core Concepts

- A decorator is a function that takes a function and returns a wrapper function; `@timed` is syntactic sugar for `fn = timed(fn)` applied before the module loads.
- `*args, **kwargs` forwarding inside the wrapper makes the decorator general: it passes every argument through to the original function unchanged.
- `functools.wraps(fn)` copies the wrapped function's name, docstring, and annotations onto the wrapper; omitting it silently corrupts tracebacks, profilers, and logging frameworks.
- `functools.lru_cache` is a standard-library decorator that caches return values by argument; apply it in one line to memoize any pure function without writing the cache yourself.

<div class="claude-handoff" data-exercise="exercises/module5/decorators/">

**Build It in Claude Code:** Build a self-contained script that implements `@timed` with `functools.wraps`, applies it to a function, and asserts that the wrapped function returns the correct result, that `__name__` equals the original, and that the recorded elapsed time is a non-negative float.

</div>
