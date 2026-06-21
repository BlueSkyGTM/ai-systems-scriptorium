# Exercise: Decorators

**Goal:** Build `timed_demo.py`, a self-contained script that implements a production-grade `@timed` decorator using `functools.wraps`, applies it to a function, and asserts three things: the wrapped function returns the correct result, `wrapped.__name__` equals the original function's name (proving `wraps` worked), and the recorded elapsed time is a non-negative float. Print a verification report and exit 0.

**Why:** Decorators are how production Python adds cross-cutting behavior in one line. Building `@timed` yourself cements the closure-plus-`wraps` pattern you will reach for whenever a reviewer needs to understand what a function does before scrolling into its body.

## Before You Start

Read `src/module5/decorators.md`. Pay attention to the `functools.wraps` section: the test for `__name__` fails if you omit it, and that failure is the point.

This is a Module 5 artifact. It does not extend `measure.py` or `vectorization_report.py`. Create `timed_demo.py` as a standalone file.

## Steps

1. Create `exercises/module5/decorators/timed_demo.py`.

2. Record elapsed time inside the wrapper. Store it somewhere the caller can inspect it after the call. One clean approach: attach it as an attribute on the result, or return it alongside the result. The simplest approach for a standalone script is to store elapsed time in a list that the wrapper appends to:

   ```python
   import functools
   import time

   def timed(fn):
       timed.last_elapsed = None  # function attribute for inspection

       @functools.wraps(fn)
       def wrapper(*args, **kwargs):
           start = time.perf_counter()
           result = fn(*args, **kwargs)
           timed.last_elapsed = time.perf_counter() - start
           print(f"{fn.__name__} took {timed.last_elapsed:.4f}s")
           return result
       return wrapper
   ```

   You are free to use a different storage mechanism (a list, a `nonlocal` variable, a class) as long as the elapsed time is accessible for the assertion in step 4.

3. Apply `@timed` to a function with a known return value:

   ```python
   @timed
   def add(a: int, b: int) -> int:
       """Return the sum of a and b."""
       return a + b
   ```

4. Call the function, then assert all three conditions:

   ```python
   result = add(3, 4)

   assert result == 7, f"Expected 7, got {result}"
   assert add.__name__ == "add", f"Expected 'add', got '{add.__name__}'"
   assert isinstance(timed.last_elapsed, float) and timed.last_elapsed >= 0, (
       f"Expected non-negative float, got {timed.last_elapsed!r}"
   )
   ```

5. Print a verification report and exit 0:

   ```python
   print(f"result      : {result}")
   print(f"__name__    : {add.__name__}")
   print(f"__doc__     : {add.__doc__}")
   print(f"elapsed (s) : {timed.last_elapsed:.6f}")
   print("[PASS] result correct, __name__ preserved, elapsed is non-negative float")
   ```

6. Wrap steps 3–5 in a `main()` function and call it from the main guard:

   ```python
   def main():
       # steps 3-5 live here
       ...

   if __name__ == "__main__":
       main()
   ```

## Done When

Run from the repo root:

```sh
python exercises/module5/decorators/timed_demo.py
```

The script must:

- Print a line showing `add took <N>s`.
- Print the `result`, `__name__`, `__doc__`, and `elapsed` lines.
- Print `[PASS] result correct, __name__ preserved, elapsed is non-negative float`.
- Exit with code 0.
- Pass all three assertions (the machine-checkable gate).

Standard library only. No external dependencies.

## Stretch

Add a `@retry` decorator that re-runs a function up to `n` times if it raises an exception, then raises on the final failure. Apply it to a function that fails twice before succeeding (use a counter in a list to track attempts). Assert that the function eventually returns the correct value and that the counter shows exactly 3 calls total. Print a retry report. This is the same pattern production SDK clients use for transient-error handling.
