# Type Hints Are a Contract

A code reviewer reads your function signature first. If it says `def process(data, fn, threshold)`, they stop and start guessing: what is `data`? A list? A dict? A string? What does `fn` do? A typed signature closes that gap before the question forms.

## What an Annotation Does

An annotation tells Python what type a parameter accepts and what a function returns. It is written with `:` after the parameter name and `->` before the return type:

```python
def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
```

That signature is documentation with no extra lines. The reader sees the contract. The runtime sees nothing new: Python does not enforce annotations at all. Pass a string to `clamp` and Python will not complain until the arithmetic fails. Annotations are for people and tools, not for the interpreter.

## The Modern Syntax

Before Python 3.9, the standard generics lived in the `typing` module: `List[float]`, `Dict[str, int]`, `Tuple[int, ...]`. Since 3.9 you can use the built-in types directly. Since 3.10, `X | None` replaces `Optional[X]`. On 3.11+, prefer the builtin forms:

```python
# old style (still valid, still common in older codebases)
from typing import Dict, List, Optional, Tuple

def score_batch(texts: List[str]) -> Dict[str, float]:
    ...

def find_label(index: int, labels: Optional[List[str]] = None) -> str | None:
    ...

# modern style (3.9+ generics, 3.10+ union)
def score_batch(texts: list[str]) -> dict[str, float]:
    ...

def find_label(index: int, labels: list[str] | None = None) -> str | None:
    ...
```

The vault production code in `madewithml/data.py` uses the `typing` import style (`Dict`, `List`, `Tuple`) because it was written before 3.9 was ubiquitous. You will see both in production. Know which version your runtime is on and stay consistent within a file.

## Optional and None

A parameter is optional when it can receive a real value or nothing. The `| None` union makes that explicit:

```python
def clean_text(text: str, max_len: int | None = None) -> str:
    if max_len is not None:
        text = text[:max_len]
    return text.strip()
```

Without the annotation, a caller has to read the body to discover that `max_len = None` is legal. With it, the signature explains the contract.

## Callable

When a parameter is itself a function, `Callable` names its signature. The form is `Callable[[arg_types], return_type]`:

```python
from typing import Callable

def apply_to_batch(
    records: list[str],
    transform: Callable[[str], str],
) -> list[str]:
    return [transform(r) for r in records]
```

`Callable[[str], str]` says: a function that takes one string and returns a string. Pass `str.upper`, pass `clean_text`, pass any compatible function. Mypy will catch it if the shapes do not match.

## Reading a Hinted Signature

The point is not just to annotate your own functions. It is to read other people's. Consider `stratify_split` in the vault:

```python
def stratify_split(
    ds: Dataset,
    stratify: str,
    test_size: float,
    shuffle: bool = True,
    seed: int = 1234,
) -> Tuple[Dataset, Dataset]:
```

You know immediately: one dataset in, two datasets out, a float between 0 and 1 for the split. No docstring needed to answer those questions. Type hints are the first layer of documentation a reviewer trusts because they are part of the function, not a comment that can drift.

## Static Checking With mypy

Annotations do nothing at runtime. `mypy` is the tool that checks them statically, before a line of production code runs. Visual Studio integrates mypy directly through the **Python > Run Mypy** command in Solution Explorer; it highlights annotation violations in the Error List window as you would expect from a compiler error. ([Microsoft Learn: Edit Python code and use IntelliSense](https://learn.microsoft.com/visualstudio/python/editing-python-code-in-visual-studio?view=visualstudio-2022#use-intellisense-features))

You can also run it from the command line:

```
mypy your_module.py
```

A clean mypy run on a fully annotated file is a meaningful signal: every call site and return path has been checked by a static analyzer. That is the proof you cannot get from reading the code alone.

## Protocol: Structural Typing

`Protocol` lets you type a parameter by what it can do, not what it inherits from. A class satisfies a Protocol if it implements the required methods, no explicit inheritance needed:

```python
from typing import Protocol

class Scorer(Protocol):
    def score(self, text: str) -> float:
        ...

def rank(texts: list[str], scorer: Scorer) -> list[str]:
    return sorted(texts, key=scorer.score, reverse=True)
```

Any object with a `score(text: str) -> float` method passes as a `Scorer`. This is structural typing: the shape of the interface, not the name of the class, is what counts.

The reviewer who lands on a typed signature does not need to open the function body to know what it accepts. That saves time at review and catches mistakes before the test suite runs.

## Core Concepts

- Type annotations are a contract for people and tools: Python does not enforce them at runtime, but `mypy` checks them statically and IDEs surface them as documentation.
- On Python 3.9+, use builtin generics (`list[str]`, `dict[str, int]`); use `X | None` instead of `Optional[X]` on 3.10+; the `typing` import forms remain valid in older code.
- `Callable[[arg_type], return_type]` names the signature of a function parameter, letting static tools verify that what you pass matches what the function expects.
- `Protocol` enables structural typing: a class satisfies a Protocol by implementing the required methods, with no inheritance required.

<div class="claude-handoff" data-exercise="exercises/module5/type-hints/">

**Build It in Claude Code:** Write a self-contained script with three fully annotated functions, use `typing.get_type_hints()` to assert the annotations exist at runtime, and add a `Protocol` stretch that proves structural typing works without inheritance. Open the repo and pick up from this lesson.

</div>
