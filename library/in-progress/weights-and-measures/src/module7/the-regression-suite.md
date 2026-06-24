# The Regression Suite

Fine-tuning teaches your model a new skill. The regression suite proves you didn't pay for it by breaking old ones.

## The Contract

Every claim you had about the base model becomes a test. The suite runs both models on the same prompts. If the tuned model drops below the base on any single case, the suite blocks the adapter.

From the README:

```
tune.py ──▶ outputs/adapter/ ──▶ regress.py ──▶ {PASS: exit 0, BLOCK: exit 1}
                                  │
                                  └──▶ MLflow (sqlite) run logged with metric deltas
```

A PR that lands a new adapter without a green `regress.py` run is **blocked**, not delayed. The regression gate is the gate.

## regress.py

The docstring states the contract:

```python
"""
regress.py — Behavioral regression suite for Module 7 instruct artifact.

Runs N test prompts against the LoRA-tuned model and the base model.
Passes (exit 0) iff tuned exact-match score >= base exact-match score on ALL N cases.
Otherwise blocks (exit 1).

MLflow logs per-prompt and aggregate metrics to sqlite:///outputs/mlruns.db.
"""
```

Read the word "ALL" literally. One failure blocks the release. No partial credit, no weighted average, no tolerance band. The exit code is binary: zero ships, one stops.

## The Canonical Prompt

From the skill spec, every test prompt takes this shape:

```
INSTRUCTION: <verb phrase>
RESPONSE:
```

The tuned model must emit the canonical response string as a prefix of its continuation. The base model does not do this. That delta is the skill.

The suite checks the other direction too. If the base model already handled a prompt, the tuned model must still handle it. The skill is additive or the suite fails.

## Why String-Level Assertions

Three reasons exact-match string comparison is the right tool.

Determinism. String comparison produces the same result every run. No temperature, no sampling variance. Seeds pin the RNG state so generations are deterministic on CPU.

Speed. N prompts, two models, exact match. The whole suite finishes in seconds on a laptop. You run it on every commit without budgeting for it.

Readability. When the gate blocks, the failure names the exact prompt and the exact string mismatch. No embedding similarity score to interpret. No judge model to argue with. The claim holds or it does not.

## The Negative Case

A suite that always passes is worthless. The smoke test corrupts the adapter with random weights and confirms the suite blocks:

```python
"""
smoke.py — end-to-end smoke test for the Module 7 instruction-tuned artifact.

Pipeline:
  1. Build a 10-sample JSONL fixture.
  2. Run tune.py on that fixture (must finish on CPU).
  3. Run regress.py on the resulting adapter -> expects PASS (exit 0).
  4. Swap the adapter file with random weights of identical shapes.
  5. Run regress.py on the corrupted adapter -> expects BLOCK (exit 1).
  6. Restore the real adapter.
"""
```

Step 4 is the fuse. If the suite cannot fail on garbage weights, a green run means nothing.

## Core Concepts

- The regression suite encodes claims about base-model behavior. Each claim is one prompt with one expected response prefix.
- The suite passes only if the tuned model matches or exceeds the base model on every single claim. One regression blocks the release.
- String-level exact match is deterministic, fast, and unambiguous. No probabilistic scoring, no judge model, no tolerance band.
- A suite that cannot fail is not a suite. The negative control proves the gate is live.

<div class="claude-handoff" data-exercise="exercises/module7/the-regression-suite/">
**Build It in Claude Code** · Exercise · exercises/module7/the-regression-suite/
</div>

A green regression run is the only evidence a Production AI Engineer has that the adapter in front of them is not silently worse than the base model it replaced.