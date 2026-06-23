# LoRA from the Inside

The question a frozen checkpoint raises is this: if the base model cannot change, where does
learning happen? LoRA's answer is a pair of small matrices added on top of each linear layer.
The base stays frozen; only the matrices train. The param-count check you ran in Module 1 is
the receipst that proves it.

## The Low-Rank Decomposition

A standard fine-tune updates the full weight matrix W directly. LoRA replaces that update with
an additive delta:

```
W_eff = W + (alpha / r) * B * A
```

A has shape `(in_features, r)` and B has shape `(r, out_features)`. The rank `r` is small,
typically 8 to 16. W is frozen and never receives gradients; only A and B train.

The scaling factor `alpha / r` controls the magnitude of the adapter's contribution. Common
practice sets `alpha = 2 * r` (so with `r=8`, `alpha=16`, the scale is 2.0), but the value is
tunable without touching r.

B is initialized to all zeros. That is not an oversight: with B zeroed at step 0, the full
expression evaluates to exactly W. The adapted model begins life identical to the base, which
means the base's pre-trained representations are intact at step one.

## Where Adapters Attach

LoRA targets linear projections. In a standard multi-head attention block there are four:
`q_proj`, `k_proj`, `v_proj`, and `o_proj`, each carrying `d^2` parameters (where d is the
model's hidden dimension). The full attention block holds `4 * d^2` parameters.

The minimal, widely used target is:

```python
target_modules = ["q_proj", "v_proj"]
```

That covers the query and value projections, skipping key and output. Production fine-tunes
often extend to all four; `target_modules="all-linear"` wraps every linear in the model. The
choice is a hyperparameter, not a law.

## `LoRALinear`: the Full Implementation

Here is the class verbatim from `exercises/spine/trainer.py`. Read the `__init__` as the
freeze proof: both `base.weight` and `base.bias` get `requires_grad_(False)` the moment the
wrapper is created.

```python
class LoRALinear(nn.Module):
    """Wraps a frozen nn.Linear with a trainable low-rank adapter (LoRA).

    The forward computes:
        base(x) + scaling * lora_B(lora_A(x))

    where base.weight and base.bias are frozen (requires_grad=False), and
    lora_A (in -> r) and lora_B (r -> out) are the trainable low-rank matrices.
    lora_B is initialized to ZERO so the adapter's initial delta is 0 — the
    wrapped model begins identical to the base at step 0.

    Args:
        base:        a frozen nn.Linear (this class freezes it on construction)
        r:           rank of the low-rank decomposition
        alpha:       scaling hyperparameter; effective scale = alpha / r
    """

    def __init__(self, base: nn.Linear, r: int = 8, alpha: float = 16.0) -> None:
        super().__init__()
        self.base = base
        # Freeze the base linear — its weights do not receive gradients
        self.base.weight.requires_grad_(False)
        if self.base.bias is not None:
            self.base.bias.requires_grad_(False)

        in_features = base.in_features
        out_features = base.out_features
        self.r = r
        self.scaling = alpha / r

        # Low-rank matrices: A projects down to rank r, B projects back up
        self.lora_A = nn.Linear(in_features, r, bias=False)
        self.lora_B = nn.Linear(r, out_features, bias=False)

        # lora_B initialized to ZERO: delta starts at 0, model == base at step 0
        nn.init.zeros_(self.lora_B.weight)
        # lora_A uses default Kaiming init (already done by nn.Linear)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.base(x) + self.scaling * self.lora_B(self.lora_A(x))

    def merge(self) -> nn.Linear:
        """Return a plain nn.Linear whose weight = base.weight + scaling * (B @ A).

        The merged linear's forward is numerically equivalent to this LoRALinear's
        forward (within floating-point tolerance). Use for inference — no adapter
        overhead at serve time.
        """
        merged = nn.Linear(
            self.base.in_features, self.base.out_features,
            bias=self.base.bias is not None,
        )
        with torch.no_grad():
            delta = self.scaling * (self.lora_B.weight @ self.lora_A.weight)
            merged.weight.copy_(self.base.weight + delta)
            if self.base.bias is not None:
                merged.bias.copy_(self.base.bias)
        return merged
```

The `forward` method is one line. `base(x)` runs the frozen linear; `self.scaling * self.lora_B(self.lora_A(x))`
projects x down to rank r via A, then back up to `out_features` via B, then scales. The two
results add. If B is zero, the second term vanishes and you get exactly `base(x)`.

`wrap_with_lora` walks `model.named_modules()`, finds every `nn.Linear` that is not already a
`LoRALinear`, and swaps it in place with `setattr` on the parent module. `count_params` returns
`(trainable, total)` as a tuple.

## The Real Numbers

Here is the output from `trainer.py __main__` after wrapping `TinyClassifier(128, 4)` with
`r=8, alpha=16`, captured and verified:

```
params: total=1572, trainable=1056, frozen=516
  (base had 516 params, now all frozen; LoRA adds 1056 trainable)
  freeze confirmed: 516 base params frozen, 1056 adapter params trainable  [PASS]
```

The arithmetic: `TinyClassifier(128, 4)` holds one `nn.Linear(128, 4)`, which carries 128 * 4 +
4 = 516 parameters. With `r=8`, `lora_A` is `nn.Linear(128, 8, bias=False)` (1024 weights) and
`lora_B` is `nn.Linear(8, 4, bias=False)` (32 weights). Adapter total: 1024 + 32 = 1056.

The base's 516 are frozen. The adapter's 1056 train. Total: 1572.

On this toy model, the adapter is larger than the base. That is an artifact of the toy: the
model is tiny (d = 128) while r = 8 is not much smaller than d. The point is not the ratio; it
is the freeze. All 516 base parameters have `requires_grad=False`. The assertion in `trainer.py`
confirms this:

```python
assert frozen_count == base_total
```

It passes. The freeze worked.

On a real model the ratio looks different. Hugging Face's `print_trainable_parameters()` on a
350M-parameter model with `r=8` on `q_proj` and `v_proj` reports roughly 0.19% trainable. The
mechanism is identical to what you just read; only d is much larger than r.

## Reading the Freeze

The freeze shows up in the param counts. Before wrapping `TinyClassifier(128, 4)`:

```
516 516
```

Both total and trainable read 516. After `wrap_with_lora`:

```
total=1572, trainable=1056, frozen=516
```

Total grows (the adapter added 1056 new parameters). Trainable is 1056, not 516. Frozen is 516,
matching the original base exactly. That match is the proof: every base parameter that existed
before the wrap now has `requires_grad=False`.

Trust the counts. If you intended to freeze the base and `trainable` still reads 516 after
wrapping, the freeze failed. A loop trained on a supposedly frozen model with `trainable=516`
is updating the base, not the adapter. The param check catches what the loss curve will not.

## Core Concepts

- LoRA replaces a weight update with an additive low-rank delta: `W + (alpha/r) * B * A`,
  where A has shape `(in, r)`, B has shape `(r, out)`, r is small (8-16), and only A and B
  receive gradients.
- B initializes to zero so the adapted model begins identical to the base at step 0; the delta
  starts at zero and grows only as training proceeds.
- The freeze is proven by param counts: after `wrap_with_lora`, `frozen` must equal the
  original base's total. If `trainable` still reads the base count, the freeze did not run.
- On a tiny toy model (d=128, r=8) the adapter exceeds the base in raw param count; that is
  expected and irrelevant. What matters is that the base weights are frozen and only A and B
  train. On a large model (hundreds of millions of parameters) the adapter is typically under
  0.5% of total.
- `merge()` folds the adapter back into a plain `nn.Linear` with `weight = base.weight + scaling * (B @ A)`;
  the merged linear is numerically equivalent to the `LoRALinear` forward and carries no adapter
  overhead at inference time.

<div class="claude-handoff" data-exercise="exercises/module4/lora-from-the-inside/">

**Build It in Claude Code**: Implement a `LoRALinear` module with a frozen base `nn.Linear`
(set `requires_grad=False` on both weight and bias), a trainable `lora_A` projecting down to
rank `r`, and a `lora_B` projecting back up with its weight initialized to zeros. Wrap a small
model using a `wrap_with_lora` function, then call `count_params` to print trainable and total.
Confirm that the base parameters all have `requires_grad=False` by iterating `named_parameters()`
and asserting it, and verify that `trainable < total` with `frozen == original_base_total`.

</div>
