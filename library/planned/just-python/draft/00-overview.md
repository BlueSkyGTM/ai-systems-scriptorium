# Module 1: Python as a Data Engine

## What This Module Covers

Before you write a single NumPy line, you need a working mental model of why it exists. Python
is slow with numbers by design. Every integer, float, and string you create is a full heap object
carrying a type pointer, a reference count, and bookkeeping overhead. A Python list of a million
floats is a million heap allocations, each one indirected through a pointer. That is the cost the
standard data model pays for its flexibility, and it is the cost NumPy was built to eliminate.

This module closes that conceptual gap. You will profile the difference between Python and NumPy
at the memory level, understand what dtypes and strides actually encode, and leave with a clear
mental model of what happens to your data between the Python layer and the CPU. That model is the
prerequisite for everything that follows: vectorized math in Module 2, DataFrame internals in
Module 3, and the profiling discipline in Module 4.

The work is grounded in the Sans Python ecosystem: the embedding stores, batch prediction outputs,
and evaluation tables you already built are the data you will look at through a new lens.

## Arc of Lessons

| Lesson | Title | What It Teaches |
|--------|-------|-----------------|
| 01 | The Cost of a Python List | Python's data model: object overhead, reference counting, why a list of floats is 8x larger than you think |
| 02 | dtype and Strides | NumPy's storage contract: typed contiguous memory, strides, views versus copies, and why the layout determines speed |
| 03 | Broadcasting Without a Loop | The broadcasting rules that let NumPy eliminate explicit iteration; reading and writing broadcast expressions |
| 04 | Indexing That Moves No Data | Fancy indexing vs. basic indexing; when slicing returns a view and when it returns a copy; memory implications |
| 05 | Vectorized Math on AI Data | Applying NumPy operations to the data shapes AI pipelines actually produce: score arrays, embedding matrices, label vectors |

## Throughline Artifact

Each lesson extends a single working script: `exercises/module1/engine.py`. By the end of the
module, `engine.py` accepts a batch prediction CSV from the Sans Python M7 evaluation table,
computes per-class score statistics using only NumPy, and prints a structured summary report.
Running `python exercises/module1/engine.py` exits 0 with no external dependencies beyond NumPy.

## Prerequisites

- Sans Python Module 1 (the field context: why embeddings are vectors, what a batch prediction
  output looks like).
- A working Python 3.11+ environment with NumPy installed (`pip install numpy`).

No Pandas yet: Pandas internals depend on NumPy internals, so Module 1 drills NumPy alone.
