# Exercise: LoRA from the Inside

## Goal

Implement a `LoRALinear` module with a frozen base `nn.Linear`, trainable `lora_A` and `lora_B` matrices, and a `merge()` method. Wrap a small model, call `count_params`, assert the freeze, and verify `merge()` equivalence.

## Why

Reading the implementation is not the same as writing it. The freeze pattern (`requires_grad_(False)` on construction) and the zero-initialized `lora_B` are the two design decisions that make LoRA work. Building them from scratch makes both decisions legible.

## What You Are Building

A `LoRALinear` class, a `wrap_with_lora` function, a `count_params` helper, and an assertion suite that confirms the freeze and the merge.

## Steps

1. Implement `LoRALinear(nn.Module)` with:
   - `__init__(self, base, r=8, alpha=16.0)`: freeze `base.weight` and `base.bias` with `requires_grad_(False)`; create `lora_A = nn.Linear(in_features, r, bias=False)` and `lora_B = nn.Linear(r, out_features, bias=False)`; zero-initialize `lora_B.weight` with `nn.init.zeros_`; store `self.scaling = alpha / r`.
   - `forward(x)`: return `self.base(x) + self.scaling * self.lora_B(self.lora_A(x))`.
   - `merge()`: return a plain `nn.Linear` with `weight = base.weight + scaling * (lora_B.weight @ lora_A.weight)`.

2. Implement `wrap_with_lora(model, r=8, alpha=16)`: iterate `model.named_modules()`, find `nn.Linear` leaves (that are not already `LoRALinear`), and replace them with `LoRALinear` using `setattr` on the parent module.

3. Implement `count_params(model)`: return `(trainable, total)` where trainable counts params with `requires_grad=True`.

4. Wrap `nn.Linear(128, 4)` with `wrap_with_lora`, call `count_params`, and assert:
   - `trainable < total` (adapter is smaller than combined)
   - `frozen == original_base_total` (every base param is frozen)

5. Call `merge()` on the wrapped linear. Pass a random batch through both the `LoRALinear` and the merged `nn.Linear` and assert the max absolute difference is below `1e-5`.

6. Run `check_loop.py --module 4` on a file that contains your `LoRALinear` class and assert it exits 0.

## Pass Condition

- `count_params` returns `trainable < total`
- `frozen == original_base_total` assertion passes
- `max_diff < 1e-5` assertion passes
- `check_loop.py --module 4` exits 0

## Done When

All four pass conditions are met.

## Estimated Time

45 to 60 minutes.

## Stretch

After wrapping a deeper model (e.g., a two-layer `nn.Sequential`), iterate `named_parameters()` and print each parameter's name, shape, and `requires_grad` value. Confirm that every parameter whose name contains `base` has `requires_grad=False` and every parameter whose name contains `lora` has `requires_grad=True`.
