# Exercise: Dataclasses

**Goal:** Write a self-contained script that defines a `BenchmarkResult` dataclass, constructs instances, and asserts that the auto-generated `__eq__`, `__repr__`, and `field(default_factory=...)` all behave as the lesson describes. The script exits 0 and prints a report.

**Why:** The dicts `measure.py` and `vectorization_report.py` return are fragile: a typo in a string key is a silent runtime error. This exercise makes the alternative concrete: a `BenchmarkResult` whose fields are named, typed, and comparable out of the box, so you can apply the same refactor to your own artifacts.

## Steps

1. Create `exercises/module5/dataclasses/benchmark_result.py`. This is a new, self-contained file. Do not touch `measure.py`, `vectorization_report.py`, or any earlier-module files.

2. Add the imports and define the dataclass:

   ```python
   from dataclasses import dataclass, field, FrozenInstanceError
   from typing import List
   ```

   Define `BenchmarkResult` with these fields:

   - `label: str` (required, no default)
   - `speedup: float` (required, no default)
   - `wall_s: float` (required, no default)
   - `tags: List[str]` (mutable default via `field(default_factory=list)`)

3. Implement a `run_checks()` function that exercises all four guarantees and prints a report:

   **Check 1 (`__eq__`, structural equality):** Construct two `BenchmarkResult` instances with the same field values. Assert they compare equal. Two separate objects with equal fields must be `==`.

   **Check 2 (`__repr__`, field values in the string):** Call `repr()` on an instance. Assert the string contains `"BenchmarkResult"`, the label value, and the speedup value. The auto-generated repr names every field.

   **Check 3 (default applies when omitted):** Construct a `BenchmarkResult` without passing `tags`. Assert `result.tags == []`. The factory runs once per instance and provides an empty list.

   **Check 4 (`field(default_factory=list)` gives independent defaults):** Construct two instances, both without `tags`. Append a value to one instance's `tags`. Assert the other instance's `tags` is still empty. The two lists must be independent objects.

   Print a line for each passing check, then a final summary.

4. Add the stretch goal as a separate `run_stretch()` function (optional; the main done-when does not depend on it):

   Define `FrozenConfig` with `frozen=True`:

   ```python
   @dataclass(frozen=True)
   class FrozenConfig:
       model: str
       batch_size: int
       seed: int = 42
   ```

   Assert that attempting to assign to a field raises `FrozenInstanceError`. Use a `try/except` block:

   ```python
   cfg = FrozenConfig(model="llama-3", batch_size=32)
   try:
       cfg.batch_size = 64
       assert False, "expected FrozenInstanceError"
   except FrozenInstanceError:
       print("stretch: FrozenInstanceError raised correctly")
   ```

5. Call both functions from the `if __name__ == "__main__":` block. Run the script:

   ```
   python benchmark_result.py
   ```

   Confirm it exits 0 and prints all check lines.

## Done When

`python benchmark_result.py` exits 0 and prints output matching this shape:

```
check 1 passed: __eq__ works (two equal-field instances compare equal)
check 2 passed: __repr__ contains field values
check 3 passed: default tag list is empty when omitted
check 4 passed: field(default_factory=list) gives independent lists
all checks passed
```

All four assertions must pass. No external dependencies: standard library only (`dataclasses`, `typing`).

## Stretch

`run_stretch()` runs after `run_checks()` and prints:

```
stretch: FrozenInstanceError raised correctly
```

`frozen=True` makes the instance immutable. The `FrozenInstanceError` is the structural proof: not a convention, not a comment, not a docstring. A reviewer reading the class definition sees the contract immediately.
