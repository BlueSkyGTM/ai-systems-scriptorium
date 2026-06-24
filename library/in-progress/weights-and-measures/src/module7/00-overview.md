# Module 7 Overview: Instruction-Tuned LLM with Behavioral Regression Suite

Fine-tuning adds capability; regression tests prevent it from removing some. You build an instruction-tuned model, but you ship the gate that proves it still works.

The artifact lives in `module7-instruct/`. The script `tune.py` adapts the model. The script `regress.py` proves the base behaviors remain intact.

## The Instruct Artifact

You start with a base model and a skill specification. You tune the model to follow single-turn instructions deterministically. The output is a behaviorally pinned LoRA adapter, not a merged monolith.

## LoRA Fine-Tuning

You inject low-rank adapters into attention projections. You train on a tiny dataset of exact-match prompt and response pairs. The model learns the new skill while preserving its baseline capabilities.

## The Regression Suite

Capability means nothing if you break existing behavior. `regress.py` runs the tuned model and the base model against a fixed prompt set.

```python
"""regress.py — M7 Behavioral Regression Suite.

  PASS (exit 0) iff the tuned model matches or beats the base on EVERY case (no
  regression) AND strictly improves on at least one (the new skill was learned).
  BLOCK (exit 1) otherwise.
"""
```

If the tuned model drops below the base on any single case, the script exits nonzero and blocks the release. It also blocks a no-op adapter that improves nothing.

## Smoke And Portfolio

A green test means nothing if the test suite cannot fail. You build a smoke test that runs the entire pipeline, including a negative control with random adapter weights.

```python
"""smoke.py — end-to-end oracle for the Module 7 instruction-tuned artifact.

Pipeline:
  1. Run tune.py: pretrain the base, LoRA-tune the new skill, save base + adapter.
  2. Run regress.py on the real adapter -> expects PASS (exit 0).
  3. Swap the adapter file with random weights of identical shapes.
  4. Run regress.py on the corrupted adapter -> expects BLOCK (exit 1).
  5. Restore the real adapter and confirm it is byte-for-byte intact.
"""
```

The random weights must trigger a block.

You package the artifact and the tests into a portfolio piece that proves your engineering rigor.

## Core Concepts

* `tune.py` generates a LoRA adapter to teach a model a specific new skill.
* `regress.py` acts as a binary release gate by comparing tuned model behavior against the base model.
* A valid regression suite requires negative controls to prove the gate catches failures.

Ship the lock, not just the key: an adapter without a blocking regression suite is a liability your on-call engineer pays for at 3 AM.