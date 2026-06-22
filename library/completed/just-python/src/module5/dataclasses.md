# Dataclasses

A dict is a fine bag of data until a reviewer reads `result["speddup"]` and the typo costs you twenty minutes of debugging. `@dataclass` turns a bag of fields into a typed record whose contract the reader can see, and whose attributes the interpreter can catch.

## The Dict Problem

`measure.py` and `vectorization_report.py` have been returning dicts since M1. They work. The issue is that a dict makes no promises:

```python
# what measure.py returns today
stats = time_sum(arr)
# stats["wall_s"]   -- correct
# stats["wall_sec"] -- KeyError at runtime, no warning at write time
```

A string key is invisible to `mypy` and invisible to your IDE's autocomplete. Every caller guesses the key name. The function's output has no shape the tooling can read.

## The @dataclass Solution

Decorate a class with `@dataclass` and Python generates `__init__`, `__repr__`, and `__eq__` from the field annotations. The class body is a schema, not a bag:

```python
from dataclasses import dataclass, field

@dataclass
class TimingResult:
    wall_s: float
    iterations: int
    label: str = "unnamed"
```

Python reads the annotated names and types, writes `__init__(self, wall_s: float, iterations: int, label: str = "unnamed")`, and wires it up. You get this for free:

```python
r = TimingResult(wall_s=0.0031, iterations=1000)
print(r)
# TimingResult(wall_s=0.0031, iterations=1000, label='unnamed')

r2 = TimingResult(wall_s=0.0031, iterations=1000)
print(r == r2)  # True -- field-by-field comparison, generated automatically
```

The `__repr__` names every field. The `__eq__` compares them structurally. Neither needed a line of your code.

## Named Access and Typo Safety

Once the dict becomes a dataclass, the caller's code changes in exactly the right direction:

```python
# dict: a typo is a silent KeyError
wall = stats["wall_s"]
# also valid at write time, explodes at runtime:
wall = stats["wall_secs"]

# dataclass: a typo is a NameError the linter catches immediately
wall = result.wall_s
# also valid at write time? no -- mypy and your IDE both flag this:
wall = result.wall_secs  # error: "TimingResult" has no attribute "wall_secs"
```

The attribute lookup makes the contract visible. A reviewer reading the function signature and the return type sees exactly what the caller is allowed to ask for.

## Mutable Defaults and field()

A default value that is mutable needs `field(default_factory=...)`. Without it, every instance shares the same list object:

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class BenchmarkSuite:
    name: str
    results: List[float] = field(default_factory=list)  # each instance gets its own list
    tags: List[str] = field(default_factory=list)
```

Python calls the factory once per instance. Omit it and `@dataclass` raises `ValueError` at class definition time, which is the right place to catch the mistake.

Microsoft's Semantic Kernel uses this pattern in its Python vector-store connectors: a `@dataclass` model carries annotated fields, with `field(default_factory=lambda: str(uuid4()))` to generate per-instance keys ([learn.microsoft.com/semantic-kernel/concepts/vector-store-connectors/defining-your-data-model](https://learn.microsoft.com/semantic-kernel/concepts/vector-store-connectors/defining-your-data-model)). The pattern applies wherever a record has typed fields and a default that cannot be shared across instances.

## frozen=True for Immutability

When a record should not change after construction, `frozen=True` makes that guarantee structural:

```python
@dataclass(frozen=True)
class RunConfig:
    model: str
    batch_size: int
    seed: int = 42

cfg = RunConfig(model="llama-3", batch_size=32)
cfg.batch_size = 64  # raises dataclasses.FrozenInstanceError
```

`frozen=True` also makes the instance hashable, so it can be used as a dict key or in a set. Use it for configuration objects and for records you want to pass around without defensive copying. The `madewithml` config holds constants, paths, and MLflow settings as module-level names; a `@dataclass(frozen=True)` is the typed version of that pattern, with the same guarantee that nothing downstream can silently mutate a shared config.

## When a Dict Is Still Right

A dict wins when the keys are genuinely dynamic: the set of keys is unknown at write time, or the keys come from user input, a database column list, or a parsed file. A dataclass wins when the fields are fixed and named: the output of a timing run, a benchmark record, a configuration object, a function's return value. If you are writing `result["speedup"]` in more than one place, the dataclass is overdue.

## Converting a Returned Dict

Turning a dict-returning function into a dataclass-returning one is a two-step refactor: define the class, then change the return. The callers gain attribute access and typo safety with no logic change:

```python
# before
def run_benchmark(arr) -> dict:
    ...
    return {"speedup": speedup, "wall_s": wall}

# after
@dataclass
class BenchmarkResult:
    speedup: float
    wall_s: float

def run_benchmark(arr) -> BenchmarkResult:
    ...
    return BenchmarkResult(speedup=speedup, wall_s=wall)

# caller after refactor
result = run_benchmark(arr)
print(f"speedup: {result.speedup:.2f}x")  # not result["speedup"]
```

The function's return type is now its documentation.

Returning `result.speedup` instead of `result["speedup"]` is the difference between a contract and a convention: the contract is what a code reviewer actually trusts.

## Core Concepts

- `@dataclass` generates `__init__`, `__repr__`, and `__eq__` from field annotations; you get a typed, self-documenting record without writing any of those methods.
- Mutable defaults (lists, dicts) require `field(default_factory=...)` so each instance gets its own object, not a shared reference.
- `frozen=True` makes a dataclass immutable and hashable: the right choice for configuration objects and records that should not be mutated after construction.
- Attribute access (`result.speedup`) is typo-safe and IDE/`mypy`-checkable; a string key (`result["speedup"]`) is neither.

<div class="claude-handoff" data-exercise="exercises/module5/dataclasses/">

**Build It in Claude Code:** Define a `BenchmarkResult` dataclass with typed fields and a mutable default, construct instances, and assert that the auto-generated `__eq__`, `__repr__`, and `field(default_factory=...)` all behave correctly. Run the script and confirm it exits 0.

</div>
