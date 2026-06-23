# Exercise: Why Adapters

## Goal

For a model of your choice (try 350M and 7B parameters), compute the full fine-tune memory estimate in `float32` and the adapter fine-tune estimate, print both totals and the ratio, and write a two-sentence argument in code comments for why the ratio is the right way to report savings.

## Why

The memory bill for full fine-tuning is the reason adapters exist. Computing it explicitly, not reading it off a slide, makes the argument yours. The ratio scales with model size; the raw byte difference does not.

## What You Are Building

A Python script that prints a memory comparison table and embeds the argument as comments.

## Steps

1. For each of `[350e6, 7e9]` parameter counts, compute the four-term memory estimate in `float32`: parameter bytes (4 bytes x params), gradient bytes (same), Adam first moment (4 bytes x params), Adam second moment (4 bytes x params). Sum them to get the optimizer-step floor in bytes.
2. For the same model sizes, pick `r=8` targeting two projection matrices per transformer block (e.g., `q_proj` and `v_proj`). For a transformer with hidden dim `d` and `L` layers, each `q_proj` and `v_proj` holds `d^2` weights. Compute how many adapter parameters `r` adds per layer per matrix, multiply by `L * 2` projections. Apply the four-term formula to the adapter params only.
3. Print a table: `| model | full (GB) | adapter (GB) | ratio |` for each size.
4. Write a comment block (two sentences) arguing why the ratio is the right metric.
5. Run `check_loop.py --module 1` on any loop in your script to confirm the validator is reachable.

```python
# Example output shape (numbers will vary by your model config):
# | 350M params | full: ~5.6 GB | adapter: ~0.003 GB | ratio: 1800x |
# | 7B params   | full: ~112 GB | adapter: ~0.06 GB  | ratio: 1800x |
```

## Pass Condition

- The script runs without error and prints a table with two rows
- The ratio column shows a value > 100 for both model sizes
- A two-sentence comment block appears in the script

## Done When

All three pass conditions are met and the numbers match your hand calculation.

## Estimated Time

30 to 45 minutes.

## Stretch

Add a third column for QLoRA (4-bit base, bf16 adapter): the base shrinks 8x from fp32, adapter stays the same. Compute and print the QLoRA estimate alongside the adapter-only estimate.
