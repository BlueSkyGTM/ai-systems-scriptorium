# Module 1: Python as a Data Engine

## What This Module Covers

Before you write production NumPy, you need the mental model of why it exists. Python is slow with
numbers by design: every float and int is a full heap object carrying a type pointer, a reference
count, and a value, and a list of them is a box of pointers to those objects scattered across the
heap. That overhead is the tax the data model pays for its flexibility, and it is exactly what NumPy
was built to remove. This module builds the memory-and-cost model that makes every later decision
(which container, which dtype, a view or a copy) obvious instead of guessed.

You will measure the list-versus-array gap yourself, see why the contiguous array is the answer,
learn what a dtype actually commits you to, and read the shape-and-strides descriptor that turns a
flat buffer into an n-dimensional array. That model is the prerequisite for everything after it: the
vectorized NumPy depth in Module 2, the DataFrame internals in Module 3, and the profiling discipline
in Module 4.

The work is grounded in the Sans Python ecosystem: the embedding stores and evaluation tables you
already built are the data you now look at through a new lens.

## Arc of Lessons

| Lesson | Title | What It Teaches |
|--------|-------|-----------------|
| 1 | The Cost of a Python List | Python's object model: 24-byte floats, pointer arrays, why a list of floats costs about 4x a contiguous `float64` array; you build the `measure.py` benchmark |
| 2 | Why NumPy Exists | The container-to-buffer leap: one dtype declared once, one contiguous block, and why contiguity is what makes array math fast |
| 3 | Dtypes and What They Cost | The fixed-width type contract: `float32` versus `float64` as an AI decision, and the `astype`-versus-`view` trap |
| 4 | Shape, ndim, and Strides | The descriptor on top of the buffer: how strides encode layout, why a transpose is free, and when slicing shares memory versus copies it |

## Throughline Artifact

The module builds one small, reusable tool: `measure.py`. You write it in Lesson 1 to measure true
list memory, array buffer size, and operation timing; Lessons 2 and 3 import it to confirm the buffer
identity and the dtype savings; Lesson 4 leans on the same memory model to read views and copies. By
the end you own a benchmark helper you will reuse when Module 4 proves a vectorized op beats a loop,
and again when the Module 6 wrangling pipeline has to justify its choices. Running it is one command,
with nothing beyond NumPy.

## Prerequisites

- Sans Python Module 1 for the field context (why an embedding is a vector, what a batch prediction
  output looks like).
- A Python 3.11+ environment with NumPy installed (`pip install numpy`).

No Pandas yet: Pandas stores its columns as NumPy arrays, so Module 1 drills NumPy alone first.
