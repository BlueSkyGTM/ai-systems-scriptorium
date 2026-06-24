# The Instruct Artifact

The instruction-tuning artifact uses the same three-script contract as M6, but it changes the definition of success. You do not maximize a new metric; you prove the fine-tune did not destroy existing behaviors.

The contract remains identical. `tune.py` builds the model. `regress.py` enforces the gate. `smoke.py` checks the gate. 

Your dataset format shifts. You train on JSONL instruction-following data. Each record pairs an instruction with a canonical response. The model learns to map a prompt to a deterministic string prefix.

```
INSTRUCTION: <verb phrase>
RESPONSE:
```

`tune.py` applies LoRA to a synthetic Transformer. It writes a lightweight adapter to `outputs/adapter/`. The base weights stay frozen.

The regression gate enforces a different rule than M6. A classifier cares about accuracy. An instruct model must prevent catastrophic forgetting. `regress.py` runs N prompts against both the base model and your tuned adapter.

```python
"""
Runs N test prompts against the LoRA-tuned model and the base model.
Passes (exit 0) iff tuned exact-match score >= base exact-match score on ALL N cases.
Otherwise blocks (exit 1).
"""
```

You must prove the gate can fail. `smoke.py` swaps your trained adapter with random weights. The random adapter must trigger a block. A green light means nothing if a broken adapter passes.

The README documents the release contract. It maps the flow from training to the gate.

```
tune.py ──▶ outputs/adapter/ ──▶ regress.py ──▶ {PASS: exit 0, BLOCK: exit 1}
```

## Core Concepts

* The artifact uses the same `tune.py`, `regress.py`, and `smoke.py` three-script contract as M6.
* The training data uses JSONL instruction-response pairs to teach deterministic prefix matches.
* The regression gate demands the tuned model scores equal to or greater than the base model on all known-good behaviors.
* The smoke test validates the gate by swapping a trained adapter for random weights and asserting a block.

<div class="claude-handoff" data-exercise="exercises/module7/the-instruct-artifact/">
**Build It in Claude Code** · Exercise · exercises/module7/the-instruct-artifact/
</div>

A production AI engineer treats an untested fine-tune as a liability, because silent behavioral regression hides inside the weights until deployment.