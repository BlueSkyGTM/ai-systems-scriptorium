# Exercise: The Fine-Tune Build (Capstone)

## Goal

Run the complete adapter fine-tune pipeline from scratch: wrap a model with LoRA, verify the freeze, train only the adapter via `fit()`, save the checkpoint, call `merge()` for inference, and confirm all gates pass.

## Why

This capstone closes the module loop. The three preceding exercises taught the components; this one wires them into the full pipeline. A fine-tuned adapter is only trustworthy if the freeze was confirmed, the training loop touched only adapter weights, and the merged model is numerically equivalent. The gates make each of those claims checkable.

## What You Are Building

A training script that produces a verified adapter checkpoint and a merged inference model.

## Steps

1. Build a `TinyClassifier(128, 4)` and record `base_total = sum(p.numel() for p in model.parameters())`.

2. Wrap with `wrap_with_lora(model, r=8, alpha=16)`. Call `count_params` and assert:

```python
trainable, total = count_params(model)
frozen = total - trainable
assert frozen == base_total, f"freeze failed: frozen={frozen}, expected={base_total}"
assert trainable < total
print(f"freeze confirmed: {frozen} frozen, {trainable} trainable  [PASS]")
```

3. Build a synthetic dataset (512 training samples, 128 validation samples, 4 classes, linearly separable with class centres along distinct axes at magnitude 5.0). Use an 80/20 split.

4. Create an optimizer that covers only trainable params:

```python
optimizer = torch.optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()), lr=1e-2
)
```

5. Run `fit(model, train_loader, val_loader, optimizer, loss_fn, device, max_epochs=10, patience=5)`. Print the epoch table from `result.history`. Assert `result.history[-1].valid_loss < result.history[0].valid_loss`.

6. Call `merge()` on the `LoRALinear` module inside the model. Compare the merged linear's output to the `LoRALinear`'s output on a random batch and assert `max_diff < 1e-5`:

```python
lora_linear = model.linear  # the LoRALinear module
merged = lora_linear.merge()
x = torch.randn(8, 128)
with torch.no_grad():
    diff = (lora_linear(x) - merged(x)).abs().max().item()
assert diff < 1e-5, f"merge equivalence failed: max diff = {diff:.2e}"
print(f"merge equivalence: {diff:.2e} < 1e-5  [PASS]")
```

7. Run `check_loop.py --module 4` on your script and confirm it exits 0.

## Pass Condition

- Freeze assertion passes (`frozen == base_total`)
- Val loss decreased from first to last epoch
- `merge()` equivalence assertion passes (`max diff < 1e-5`)
- `check_loop.py --module 4` exits 0

## Done When

All four pass conditions are met. Keep your script and the checkpoint path from `result.checkpoint_path`: M5 will run the eval gate on this adapter.

## Estimated Time

60 to 90 minutes.

## Stretch

Run the self-test on `check_loop.py` to confirm the validator itself is healthy before pointing it at your script:

```
python exercises/spine/check_loop.py --selftest
```

It must print `selftest: OK`. Then run it at `--module 1`, `--module 2`, and `--module 4` on your script and confirm all three pass. Each level is cumulative: module 4 checks include module 1 and 2 requirements.
