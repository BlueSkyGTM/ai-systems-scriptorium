# Introduction

Sans Python taught you to build AI systems without making Python the subject. That was deliberate.
The field opens faster when you are not blocked at the gate by syntax. You learned to call a model,
ground it in data, wrap it in an agent, and ship that agent under production load. The gate came down.

Now the gate is different. Most AI-Engineer job postings screen for Python as a skill, not an
assumption. A take-home exercise arrives with a CSV and instructions to compute something in NumPy.
A phone screen asks how you would vectorize a loop over a ten-million-row DataFrame. Sans Python
left those questions open on purpose: Python literacy was the course's background assumption, not
its subject. The assumption held long enough to get you past the first wall. This book closes the gap.

Just Python makes Python the subject. Not all of Python: the subset that appears in every AI/ML
codebase, the idioms that survive a hiring screen, the tools that underlie the pipelines you already
know how to design. That means NumPy arrays, Pandas DataFrames, vectorization discipline, and the
Python idioms you will be asked to write and read cold. It does not mean PyTorch, scikit-learn, or
Spark. Those belong to other books in this library. This book stops at the data layer, and it stops
there deliberately.

## The Argument in the Name

Sans Python said: learn the field without Python as the subject; the gate comes down. Just Python
says: now drill the Python the field runs on. The books are two moves in a sequence. You do not
re-learn what an agent is, what retrieval means, or how a serving stack holds under load. You bring
that knowledge with you. The new skill is the data substrate beneath it: the array that holds the
embedding, the DataFrame that holds the evaluation table, the vectorized op that makes the pipeline
fast.

## What You Build

The curriculum runs eight modules. The first five build the mental models and the core vocabulary:
Python's data model, NumPy in depth, Pandas for AI pipelines, vectorization discipline, and the
Python idioms that live at interview speed. The next two are portfolio artifacts: a production-grade
data-wrangling pipeline and a batch evaluation engine that reads the same evaluation tables Sans
Python produced. Module 8 is a timed, integrated exam.

Every lesson ends with a runnable Claude Code exercise. A specific task, a specific expected output,
a handoff that picks up where you left off. The artifacts compound: each module's output feeds the
next one's input. By the end you have three scripts that run clean, demonstrating applied Python at
AI-Engineer level: data in, structured output out, tested.

You already know what the data is for. Now you learn how to move it.

Turn the page. Module 1 starts with the cost of a Python list, and the first thing you measure is
the overhead you are about to leave behind.
