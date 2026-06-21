# Comprehensions and Generators

A loop that appends to a list is not the pattern the interviewer wants to see. A comprehension says the same thing in one line, and a generator says it without allocating the list at all.

## What You Build

You build a script that constructs label maps and token sequences using comprehensions and a generator, measures the memory difference between the two approaches on a ten-million-item range, and prints a concrete comparison.

## The Loop a Reviewer Skips Past

Here is the pattern that signals you have not internalized the idiom:

```python
squares = []
for x in range(10):
    squares.append(x * x)
```

A list comprehension replaces all three lines with one:

```python
squares = [x * x for x in range(10)]
print(squares)
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

The result is identical. The comprehension states the *intent* (build a list of squares), not the *procedure* (initialize, loop, append). Python reviewers read comprehensions at a glance; they have to parse the loop.

## Dict and Set Comprehensions

The same syntax works for dicts and sets. In `data.py` from the Made With ML codebase, `CustomPreprocessor.fit` builds its label-to-index map with a dict comprehension:

```python
class_to_index = {tag: i for i, tag in enumerate(tags)}
```

And the reverse map inverts it in the same shape:

```python
index_to_class = {v: k for k, v in class_to_index.items()}
```

No loop, no intermediate list, no manual counter. Both maps are correct by construction because `enumerate` handles the index.

You can filter inside any comprehension with an `if` clause:

```python
# Keep only tags that appear more than once
filtered = {tag: i for tag, i in class_to_index.items() if i > 0}
```

A set comprehension drops the value side:

```python
seen = {tag.lower() for tag in tags}
```

## Generator Expressions: Same Syntax, No List

A generator expression uses parentheses instead of brackets:

```python
gen = (x * x for x in range(10))
print(type(gen))   # <class 'generator'>
```

It does not build a list. It creates a generator object that yields one value at a time when you iterate it. You cannot index into it or call `len` on it. What you can do is stream it once, which is exactly what you need when the data is too large to hold in memory.

```python
# Consume the generator
for val in gen:
    print(val, end=" ")
# 0 1 4 9 16 25 36 49 64 81
```

## The Memory Contrast

The difference becomes concrete at scale. A list comprehension over ten million integers materializes every value:

```python
import sys

n = 10_000_000
eager = [x * x for x in range(n)]
print(f"list: {sys.getsizeof(eager):,} bytes")
# list: 89,095,160 bytes  (roughly 85 MB)
```

The generator equivalent stays flat regardless of `n`:

```python
lazy = (x * x for x in range(n))
print(f"generator: {sys.getsizeof(lazy):,} bytes")
# generator: 208 bytes
```

The generator object is a few hundred bytes. It holds no squares, only the recipe for producing the next one. That recipe costs the same whether `n` is ten million or ten billion.

## `yield` Functions

A `yield` function gives you the same lazy behavior with more control. Where a generator expression is one line, a `yield` function can filter, transform, and maintain state across iterations:

```python
def tokenize_corpus(docs: list[str]):
    """Yield one token list per document without building all of them at once."""
    for doc in docs:
        yield doc.lower().split()

corpus = ["Eval pipelines matter", "Retrieval beats memorization"]
tokens = tokenize_corpus(corpus)
print(next(tokens))   # ['eval', 'pipelines', 'matter']
print(next(tokens))   # ['retrieval', 'beats', 'memorization']
```

Each call to `next` runs the function body until the next `yield` and suspends. The rest of the corpus sits in `docs`, untouched, until you ask for it.

## When to Use Each

The choice is mechanical once you know the constraints:

| Need | Use |
|------|-----|
| Reuse the result, index into it, or call `len` | list/dict/set comprehension |
| Stream a large or infinite source exactly once | generator expression or `yield` function |
| Complex multi-step transformation per item | `yield` function |
| Simple one-expression transformation per item | generator expression |

The wrong choice is not always wrong; it is wasteful. A comprehension over a corpus that fits in RAM is fine. A comprehension over a corpus that does not fit will crash or swap. The generator never asks.

The screen expects a comprehension, not a loop, and a generator when the data is a corpus you stream once. Reaching for the append loop signals you have not internalized the idiom; reaching for the generator signals you thought about what fits in memory.

## Core Concepts

- A list comprehension builds the entire sequence in memory at construction time; the append-loop equivalent does the same thing with three times the syntax and signals the wrong idiom to a reviewer.
- A dict comprehension `{k: v for k, v in items}` is the standard way to build or invert a label map; both forms are readable at a glance and correct by construction.
- A generator expression `(expr for x in iterable)` yields one item at a time and holds no result in memory, so it costs a fixed few hundred bytes regardless of the source size.
- A `yield` function suspends at each `yield` and resumes on the next `next()` call; use it when the per-item logic is too complex for a single expression.

<div class="claude-handoff" data-exercise="exercises/module5/comprehensions-and-generators/">

**Build It in Claude Code:** Build a script that constructs comprehensions and a generator over the same data, asserts they produce equal results, and demonstrates the memory difference between the eager and lazy forms.

</div>
