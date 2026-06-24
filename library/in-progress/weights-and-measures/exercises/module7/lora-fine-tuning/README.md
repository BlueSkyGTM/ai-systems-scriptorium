# Exercise: LoRA Fine-Tuning

## Goal

Implement the `LoRALinear` wrapper and the two-stage training in `tune.py`: pretrain the
base, then LoRA-tune a new skill with the base frozen.

## Why

LoRA is the difference between shipping a multi-gigabyte model and shipping a few-kilobyte
delta. You only understand the frozen-base/trainable-delta split once you have written the
forward pass and watched the adapter learn while the base does not move.

## What You Are Building

A `LoRALinear` module and the `pretrain_base` / `lora_finetune` functions that produce
`outputs/base.pt` and `outputs/adapter/adapter.pt`.

## Steps

1. Write `LoRALinear` wrapping a frozen `nn.Linear` with low-rank `A` and `B`:

   ```python
   def forward(self, x):
       out = self.base(x)
       if self.lora_enabled:
           out = out + self.scale * (x @ self.A.t()) @ self.B.t()
       return out
   ```

   Zero-initialise `B` so the adapter starts as a no-op. Use `rank = 8`, `alpha = 16`.

2. Build the tiny 2-layer Transformer, wrapping the query and value projections with
   `LoRALinear`.

3. `pretrain_base`: train the whole model on `thank` and `bye`. Save `base.pt`.

4. `lora_finetune`: freeze everything except the LoRA `A`/`B`, then train on `greet` plus a
   little replay of `thank`/`bye`. Save only the adapter weights.

5. Confirm the adapter is a small fraction of the total parameter count.
