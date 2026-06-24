# LoRA Fine-Tuning

LoRA does not retrain a model. It freezes the base, injects trainable rank-decomposition matrices beside a handful of weight matrices, and ships only the resulting delta.

## The Adapter Is A Delta

Every weight in the base model stays frozen. You do not touch the pretrained weights during training. Instead, you place two small matrices beside a target weight matrix: call them A and B. The forward pass computes Wx plus BAx, where W is frozen and only A and B receive gradients.

The product BA is a rank-r perturbation. With r equal to 8 you capture the dominant adaptation signal at a fraction of the parameter count. The artifact pins this configuration:

| Field | Value |
|---|---|
| Tuning method | LoRA (rank=8, alpha=16) on attention projections |

The file on disk, not the base model, is the artifact you version and ship.

## Why LoRA Beats Full Fine-Tuning

Parameter count. Full fine-tune updates every parameter in a transformer: hundreds of millions of floats on a small model, billions on a large one. LoRA on attention projections trains a sliver of that, often under one percent of the base.

Storage. A base model occupies tens of gigabytes. A rank-8 adapter measures in single-digit megabytes. You store, transfer, and roll back the delta, not the model.

Reversibility. To remove the skill, drop the adapter. The base is untouched, byte for byte. To swap skills, hot-load a different adapter against the same base. Full fine-tune gives you neither property: the base dies the moment gradients touch it.

## The Tune Pipeline

The delta lives in one method. `LoRALinear.forward` adds the low-rank term beside the frozen base, verbatim from `tune.py`:

```python
def forward(self, x: torch.Tensor) -> torch.Tensor:
    out = self.base(x)
    if self.lora_enabled:
        out = out + self.scale * (x @ self.A.t()) @ self.B.t()
    return out
```

`B` is zero-initialised, so the adapter is a no-op until trained. Three stages run inside `tune.py`. Pretrain the base on two skills (`thank`, `bye`). Freeze it and LoRA-tune a third skill (`greet`), with a little replay of the old skills so the adapter does not clobber them. Serialize only the adapter weights to `outputs/adapter/`.

The downstream contract, verbatim from the README:

```
tune.py ──▶ outputs/adapter/ ──▶ regress.py ──▶ {PASS: exit 0, BLOCK: exit 1}
                                  │
                                  └──▶ MLflow (sqlite) run logged with metric deltas
```

The adapter is the boundary. Everything upstream produces it. Everything downstream gates it.

## Cross-Link: The Adapter Concept

Module 4 introduced the adapter as a versioned, swappable delta against a frozen base. This is where you build one. The same discipline applies: the adapter is named, hashed, regression-gated, and reproducible from a pinned seed.

## Core Concepts

* LoRA trains two small matrices beside a frozen weight. The base never receives a gradient.
* The rank r bounds the expressivity of the delta. Lower r means fewer parameters and stricter regularization.
* The shipped artifact is the adapter file, not a retrained model. Storage and transfer costs scale with the delta.
* Reversibility is a property of the architecture. Drop the adapter to recover the exact base.

<div class="claude-handoff" data-exercise="exercises/module7/lora-fine-tuning/">
**Build It in Claude Code** · Exercise · exercises/module7/lora-fine-tuning/
</div>

A production AI Engineer ships deltas, not models; reversibility is the only property that keeps fine-tuning cheap enough to run inside a CI gate.