# Module 5: Python Idioms at Interview Speed

## What This Module Covers

Modules 1 through 4 made you fast with data. Module 5 makes you fluent in the Python a screen actually tests. The five idioms a take-home or a live round assumes you know cold are comprehensions, generators, decorators, type hints, and dataclasses. None of them are trivia. Each is the difference between code that reads like an engineer wrote it and code that reads like a beginner, and a reviewer judges that in the first ten lines.

These idioms are not about NumPy or Pandas. They are core Python, and a hiring screen tests them directly: the comprehension a reviewer expects instead of an append loop, the generator that streams a corpus too big for RAM, the decorator that adds timing without touching the function, the type hint that makes a signature reviewable, the dataclass that replaces a fragile dict.

## Arc of Lessons

| Lesson | Title | What It Teaches |
|--------|-------|-----------------|
| 1 | Comprehensions and Generators | Same syntax, opposite memory profile: a comprehension builds the whole sequence; a generator streams it one item at a time and never holds the result |
| 2 | Decorators | Wrap behavior onto a function without touching its body; build `@timed` with `functools.wraps`, the production version of the manual timing you have done since M1 |
| 3 | Type Hints | The contract the reader and `mypy` both read; `list[float]`, `Optional`, `Callable`, `Protocol`, and what a reviewer scans for first |
| 4 | Dataclasses | A typed record with `__init__`, `__repr__`, and `__eq__` for free; replaces the dict-of-fields that `measure.py` returns |

## Throughline Artifact

Module 5 has no single new artifact. Its idioms are the polish you apply to the artifacts you already built and the one you are about to build. Each lesson demonstrates its idiom by refactoring a piece of your own `measure.py` or `vectorization_report.py`: `@timed` generalizes your hand-written timing, a `@dataclass` replaces a returned dict, type hints harden the signatures. The exercises stay self-contained (each is a focused, runnable demo of one idiom) so the lessons can teach cleanly without four files refactoring one. The named forward link: these five idioms are the ones Module 6's `wrangle.py` is written with from the first line.

## Prerequisites

- Modules 1 through 4, and the `measure.py` / `vectorization_report.py` artifacts you built. Module 5 refactors snippets of them to show each idiom in your own code.
- A Python 3.11+ environment. These lessons use the modern builtin-generic syntax (`list[float]`, `X | None`); no third-party packages are required (mypy is optional, noted where relevant).
