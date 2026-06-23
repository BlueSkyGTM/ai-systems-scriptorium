# Exercise: Quantization and Mixed Precision

## Goal

Build a memory comparison table for fp32, bf16, and int4 at three model sizes. Then write an AMP training loop for `TinyClassifier` using `torch.autocast` with `dtype=torch.bfloat16` on CPU, cast logits to fp32 before the loss, and confirm training proceeds.

## Why

QLoRA and AMP are configuration decisions, not architecture decisions. The configuration is only correct if you know the byte cost of each dtype and where in the loop the cast must happen. Writing the table and the loop forces both pieces into working memory simultaneously.

## What You Are Building

A memory table printed to stdout and a ten-step AMP training loop on CPU.

## Steps

1. Print a memory table for parameter counts `[1e6, 7e9, 70e9]` and dtypes `[fp32, fp16/bf16, int4]`:

```python
BYTES = {"fp32": 4, "bf16": 2, "int4": 0.5}
sizes = [1e6, 7e9, 70e9]

print(f"{'params':>12} | {'fp32 (GB)':>10} | {'bf16 (GB)':>10} | {'int4 (GB)':>10}")
for n in sizes:
    row = {dtype: n * b / 1e9 for dtype, b in BYTES.items()}
    print(f"{n:>12.0e} | {row['fp32']:>10.2f} | {row['bf16']:>10.2f} | {row['int4']:>10.2f}")
```

Confirm the int4 column is 8x smaller than fp32.

2. Write an AMP training loop for `TinyClassifier(128, 4)` on CPU using `torch.autocast`:

```python
model = TinyClassifier(128, 4)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
loss_fn = nn.CrossEntropyLoss()

for step in range(10):
    x = torch.randn(32, 128)
    y = torch.randint(0, 4, (32,))
    optimizer.zero_grad()
    with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
        logits = model(x)
    logits = logits.float()  # cast back to fp32 before loss
    loss = loss_fn(logits, y)
    loss.backward()
    optimizer.step()
    print(f"step {step:2d}: loss={loss.item():.4f}")
```

3. Add a comment explaining where you would add `torch.amp.GradScaler` if running fp16 on GPU, and why bf16 on CPU does not need one.

## Pass Condition

- The memory table prints with the int4 column 8x smaller than fp32
- The AMP loop runs 10 steps and prints a loss value at each step
- A comment explains the GradScaler decision

## Done When

All three pass conditions are met and the loss values are finite numbers.

## Estimated Time

30 to 45 minutes.

## Stretch

Modify the loop to run in fp16 instead of bf16. Add a `torch.amp.GradScaler`, wrap `scaler.scale(loss).backward()` and `scaler.step(optimizer)` and `scaler.update()`. Confirm it runs without overflow errors (on CPU fp16 is not always stable; note any differences in behavior).
