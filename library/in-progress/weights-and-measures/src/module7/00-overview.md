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
"""
regress.py — Behavioral regression suite for Module 7 instruct artifact.

Runs N test prompts against the LoRA-tuned model and the base model.
Passes (exit 0) iff tuned exact-match score >= base exact-match score on ALL N cases.
Otherwise blocks (exit 1).

MLflow logs per-prompt and aggregate metrics to sqlite:///outputs/mlruns.db.
"""
```

If the tuned model drops below the base model on any single case, the script exits with a nonzero code and blocks the release.

## Smoke And Portfolio

A green test means nothing if the test suite cannot fail. You build a smoke test that runs the entire pipeline, including a negative control with random adapter weights.

```python
"""smoke.py — end-to-end smoke test for the Module 7 instruction-tuned artifact.

Pipeline:
  1. Build a 10-sample JSONL fixture.
  2. Run tune.py on that fixture (must finish on CPU).
  3. Run regress.py on the resulting adapter -> expects PASS (exit 0).
  4. Swap the adapter file with random weights of identical shapes.
  5. Run regress.py on the corrupted adapter -> expects BLOCK (exit 1).
  6. Restore the real adapter.

smoke.py exits 0 only if every one of those expected outcomes was observed,
including the negative case (random adapter must BLOCK). The negative-case
assertion is the regression-suite's "fuse": it proves regress.py is capable
of failing, so a green run is meaningful.
"""
```

The random weights must trigger a block.

You package the artifact and the tests into a portfolio piece that proves your engineering rigor.

## Core Concepts

* `tune.py` generates a LoRA adapter to teach a model a specific new skill.
* `regress.py` acts as a binary release gate by comparing tuned model behavior against the base model.
* A valid regression suite requires negative controls to prove the gate catches failures.

<div class="claude-handoff" data-exercise="exercises/module7/00-overview/">
**Build It in Claude Code** · Exercise · exercises/module7/00-overview/
</div>

Ship the lock, not just the key: an adapter without a blocking regression suite is a liability your on-call engineer pays for at 3 AM.