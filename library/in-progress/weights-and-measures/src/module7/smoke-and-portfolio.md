# Smoke and Portfolio

The smoke test runs the full pipeline twice: once with a real adapter to prove it passes, once with random weights to prove the gate can fail. The portfolio write-up translates that green run into a document a hiring manager reads and trusts.

## The Smoke Test Runs the Full Loop

A smoke test is not a unit test. It exercises the entire chain end to end: fixture data, tune, adapter artifact, regression gate.

The pipeline in `smoke.py` makes the contract explicit:

```python
"""smoke.py — end-to-end smoke test for the Module 7 instruction-tuned artifact.

Pipeline:
  1. Build a 10-sample JSONL fixture.
  2. Run tune.py on that fixture (must finish on CPU).
  3. Run regress.py on the resulting adapter -> expects PASS (exit 0).
  4. Swap the adapter file with random weights of identical shapes.
  5. Run regress.py on the corrupted adapter -> expects BLOCK (exit 1).
  6. Restore the real adapter.
```

Steps one through three are the happy path. You build a fixture, tune, and confirm the regression gate returns zero. That alone proves the loop runs clean.

## The Negative Case Is the Fuse

Steps four and five are what make this a real test. You corrupt the adapter with random weights of identical shapes, then confirm regress.py exits one.

```python
smoke.py exits 0 only if every one of those expected outcomes was observed,
including the negative case (random adapter must BLOCK). The negative-case
assertion is the regression-suite's "fuse": it proves regress.py is capable
of failing, so a green run is meaningful.
```

If the gate cannot fail, a green run tells you nothing. The negative case proves the fuse blows when it should.

## How to Run

Run the smoke test, then the pytest suite:

```
python smoke.py && python -m pytest tests/ -v
```

The pytest suite mirrors the same seeds and paths so the two are reproducible together:

```python
TORCH_SEED = 42
RANDOM_SEED = 42

# Convenience paths used across test modules.
FIXTURE_DIR = "fixtures"
OUTPUTS_DIR = "outputs"
ADAPTER_DIR = "outputs/adapter"

# MLflow offline tracking URI (must match regress.py / smoke.py).
MLFLOW_URI = "sqlite:///outputs/mlruns.db"
```

Fixed seeds, offline MLflow, CPU only. Everything a reviewer needs to reproduce your green run lives in that configuration.

## The Portfolio Translates the Run

A green smoke test is a fact. A hiring manager needs a story. `outputs/skill-instruct.md` bridges that gap.

The skill spec pins exactly what the model does:

```python
| Field | Value |
|---|---|
| Skill name | `skill-instruct` |
| Skill type | generative instruction-following |
| Task family | single-turn prompt → short deterministic answer |
| Output contract | string-prefix match on expected continuation |
```

It tells the reader what the skill is and, more importantly, what it is not:

```python
This is **not** a general chatbot. It is a *behaviorally pinned* skill: a small, auditable
set of prompt/response pairs the model must reproduce deterministically after LoRA tuning,
without losing any behavior the base model already had.
```

That sentence reframes the artifact. You did not train a model. You built a release contract and proved it holds.

## Core Concepts

1. The smoke test exercises the full pipeline end to end, including a negative case where the adapter is corrupted with random weights and the gate must exit one.
2. The negative case is the fuse: if regress.py cannot fail, a green run is meaningless.
3. `outputs/skill-instruct.md` translates the technical artifact into a hiring-readable document, framing the work as a behaviorally pinned release contract.

A production AI engineer who cannot demonstrate a failing test does not have a gate; they have a rumor.

<div class="claude-handoff" data-exercise="exercises/module7/smoke-and-portfolio/">
**Build It in Claude Code** · Exercise · exercises/module7/smoke-and-portfolio/
</div>