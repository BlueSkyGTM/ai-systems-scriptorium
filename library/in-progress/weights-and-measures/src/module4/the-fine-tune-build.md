# The Fine-Tune Build

The adapter pattern resolves into four mechanical steps: wrap the model so its base weights freeze and
only the adapter parameters are live, bind the optimizer exclusively to those live parameters, train
through the standard `fit()` loop, and then merge the adapter back into a plain linear layer for
inference. Each step is small. Together they form a complete fine-tuning pipeline that fits in a
single Python function and produces a checkpoint a fraction of the size of the full model.

The three preceding lessons were not preamble. Knowing that the adapter is a low-rank matrix
product, knowing that the base weights are frozen by `requires_grad_(False)`, and knowing that
`merge()` produces an exact algebraic equivalent: these facts prevent the mystification that comes
from reaching for a library before understanding what it does. This lesson closes the loop by running
the build end to end and showing the numbers.

The production tool for this work is `peft`. This lesson shows it at the end, clearly labeled
REFERENCE ONLY. The from-scratch version built here is not a replacement: it is the explainer that
makes `peft`'s API legible.

---

## Wrapping the Model

`wrap_with_lora` walks the module tree with `named_modules()`, collects every `nn.Linear` that is
not already a `LoRALinear`, and replaces it in place via `setattr` on the parent module:

```python
def wrap_with_lora(model: nn.Module, r: int = 8, alpha: float = 16.0) -> nn.Module:
    to_replace: list[tuple[nn.Module, str, nn.Linear]] = []
    for name, module in model.named_modules():
        parts = name.split(".")
        if len(parts) == 0:
            continue
        parent = model
        for part in parts[:-1]:
            parent = getattr(parent, part)
        attr = parts[-1]
        if isinstance(module, nn.Linear) and not isinstance(module, LoRALinear):
            to_replace.append((parent, attr, module))
    for parent, attr, linear in to_replace:
        setattr(parent, attr, LoRALinear(linear, r=r, alpha=alpha))
    return model

def count_params(model: nn.Module) -> tuple[int, int]:
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return trainable, total
```

After wrapping, `count_params` reveals the split. For a `TinyClassifier(IN_DIM, N_CLASSES)` with
`r=8, alpha=16`:

```
params: total=1572, trainable=1056, frozen=516
freeze confirmed: 516 base params frozen, 1056 adapter params trainable  [PASS]
```

The freeze assertion checks that the frozen count equals the original base model's total parameter
count. If anything is off, the assertion fails before a single training step is wasted.

The optimizer must be bound only to the trainable parameters:

```python
lora_optimizer = torch.optim.Adam(
    filter(lambda p: p.requires_grad, lora_model.parameters()), lr=1e-2
)
```

Passing all parameters to `Adam` is not merely inefficient: it allocates first-moment and
second-moment buffers for every parameter, including the frozen ones. On a 7B model, those buffers
for frozen weights consume gigabytes. The `filter` call keeps the optimizer's state exclusively in
the adapter weights, which is the only memory budget that matters.

---

## Training the Adapter

The `fit()` call is identical to every other training run in this book. The loop does not know or
care that most of the model's parameters are frozen: the backward pass computes gradients for all
parameters, but only the adapter weights have `requires_grad=True`, so only their gradients are
non-zero and only they receive an optimizer update.

```python
lora_result = fit(
    lora_model,
    lora_train_loader,
    lora_val_loader,
    lora_optimizer,
    loss_fn,
    device,
    max_epochs=10,
    patience=5,
)
```

Validation loss descends cleanly. The first epoch records `1.7545`; the final epoch records
`1.2477`. The fit is real: the adapter is learning.

The checkpoint saved by `fit()` at `lora_result.checkpoint_path` is a standard dict:

```python
{
    "epoch": ...,
    "model_state_dict": ...,
    "optimizer_state_dict": ...,
    "valid_loss": ...,
}
```

The `model_state_dict` at this path holds the full wrapped model's state, including both the frozen
base weights and the adapter weights. In a production adapter workflow the base weights are shared
across many adapters and only the adapter weights are stored separately, so the checkpoint file is
far smaller than a full model save. The mechanism is the same regardless of framework.

---

## Saving and Merging

After training, the adapter exists as a set of small `lora_A` and `lora_B` weight matrices sitting
alongside frozen copies of the original base weights. For inference, the adapter overhead is
unnecessary: `merge()` folds the low-rank update back into the base weight algebraically and returns
a plain `nn.Linear`.

The `merge()` implementation from `LoRALinear`:

```python
def merge(self) -> nn.Linear:
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

The computation is `W_merged = W_base + (alpha/r) * B @ A`. No approximation is involved: this is
exact matrix arithmetic. The verified demo confirms it:

```
merge() equivalence: max diff = 1.46e-06 < 1e-5  [PASS]
```

The max absolute difference between the merged linear layer's output and the original `LoRALinear`'s
output on a random batch is 1.46e-06, well below the 1e-5 tolerance. The difference is floating-point
rounding, not a bug. After merge, the model is a plain `nn.Module` with no adapter infrastructure:
it loads and runs like any standard checkpoint.

---

## The Production Path: peft

The Hugging Face `peft` library implements the same pipeline. The snippet below is shown as a
reference so you can read `peft` code fluently after finishing this book. It is not run here:
`peft` is not installed in this book's environment.

```python
# REFERENCE ONLY: peft library required; not run in this book.
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, config)
model.print_trainable_parameters()
# merge and unload for inference:
model = model.merge_and_unload()
```

`LoraConfig` is the parameter object: `r` and `lora_alpha` map directly to the `r` and `alpha` in
`LoRALinear`. `target_modules` names which linear layers to wrap, equivalent to the `isinstance`
check in `wrap_with_lora`. `get_peft_model` performs the wrapping, matching `wrap_with_lora`'s
`setattr` replacement loop.

`print_trainable_parameters()` on a 350M-parameter model with `r=8` on `q_proj` and `v_proj` shows
approximately 0.19% of parameters as trainable. The saved adapter file for that model is 6 to 7 MB
rather than several gigabytes for the full model. `merge_and_unload()` is `merge()` applied across
all wrapped layers, returning the plain model.

Reading `peft`'s source after building this lesson reveals nothing surprising: the same freeze
pattern, the same low-rank decomposition, the same merge arithmetic. The library adds dropout,
handles quantized bases, manages multi-adapter switching, and provides serialization tooling. The
mathematical core is unchanged.

---

## Core Concepts

- **The four-step adapter build** wraps the model with `wrap_with_lora`, verifies the freeze with
  `count_params`, trains through `fit()` with an optimizer filtered to trainable parameters only,
  and merges the adapter back into a plain linear layer via `merge()` for inference.

- **Optimizer filtering is a memory contract**: passing all parameters to `Adam` allocates
  first-moment and second-moment buffers for frozen weights; `filter(lambda p: p.requires_grad,
  model.parameters())` confines optimizer state to adapter weights only.

- **The checkpoint** saved by `fit()` contains `epoch`, `model_state_dict`, `optimizer_state_dict`,
  and `valid_loss`; in production workflows the base weights are shared and only adapter weights are
  stored separately, making the checkpoint file a fraction of full model size.

- **Merge equivalence** is exact arithmetic: `W_merged = W_base + (alpha/r) * B @ A` produces a
  plain `nn.Linear` whose output differs from the live `LoRALinear` by floating-point rounding only
  (demonstrated at max diff 1.46e-06, well within 1e-5 tolerance).

- **`peft` is the production path**: `LoraConfig` and `get_peft_model` implement the same freeze,
  wrap, and optimizer-filter pattern; `merge_and_unload()` is `merge()` applied across all wrapped
  layers; the from-scratch version built here is the explainer that makes the library legible.

<div class="claude-handoff" data-exercise="exercises/module4/the-fine-tune-build/">

**Build It in Claude Code**: Wrap `TinyClassifier(128, 4)` with `wrap_with_lora(r=8, alpha=16)` and
call `count_params` to confirm trainable < total and frozen == original base count. Build a synthetic
dataset (512 training samples, 128 validation samples, four classes, linearly separable), create an
optimizer with `filter(lambda p: p.requires_grad, model.parameters())`, and run `fit()` for up to
10 epochs with `patience=5`. Print the epoch table from `FitResult.history` and confirm val loss
decreased from first to last epoch. Call `merge()` on the `LoRALinear` module and compare its output
to the original `LoRALinear` on a random batch; assert the max absolute difference is below 1e-5.
Run `check_loop.py --module 4` on your script and confirm it exits 0.

</div>
