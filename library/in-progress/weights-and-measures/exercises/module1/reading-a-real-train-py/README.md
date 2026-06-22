# Exercise: Reading a Real `train.py` (Capstone)

## Goal

Take a training loop file, add the two-batch smoke test and a trainable-parameter check, then run
`check_loop.py` against it and make it pass. This is the module's gated deliverable: `check_loop.py`
exits 0, or the module is not done.

## Why

Reading an unfamiliar `train.py` is the job. You will inherit loops that have no smoke test, no
param check, and no comment explaining why the steps are in that order. This exercise installs the
habit of adding those gates before trusting the loop at scale. The validator makes that habit
testable: either the structure is present and in order, or it is not.

## What You Are Building

A single file, `my_loop.py`, that contains a correct `train_one_epoch` function with:

- The five canonical steps in the required order: `zero_grad`, forward pass, loss computation,
  `backward`, `optimizer.step`.
- A trainable-parameter check using `requires_grad` and a counting construct (`.numel()`,
  `.parameters()`, or `sum(...)`).
- A `smoke_two_batches` function that runs exactly two training batches and asserts loss decreased
  and at least one parameter is trainable.

The validator `check_loop.py` reads `my_loop.py` as text using only the standard library. It gates
four things in order: every step present, steps in the canonical order, the trainable-parameter
check present. All four must clear for exit 0.

## Steps

1. Create `exercises/module1/reading-a-real-train-py/my_loop.py`.

2. Write `train_one_epoch(model, loader, optimizer, loss_fn, device)` following the five-step
   contract. The steps must appear in this order in the file:

   ```python
   optimizer.zero_grad()   # step 1: before the forward pass
   logits = model(inputs)  # step 2: forward
   loss = loss_fn(...)     # step 3: loss computation
   loss.backward()         # step 4: backward
   optimizer.step()        # step 5: weight update
   ```

3. Add a trainable-parameter check. Place it before or inside the loop, not after:

   ```python
   trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
   ```

4. Write `smoke_two_batches(model, loader, optimizer, loss_fn, device)` that runs exactly two
   batches and asserts:

   - `losses[1] < losses[0]` (loss decreased: gradient signal is flowing).
   - `trainable > 0` (something is being trained).

   Return the two losses so the caller can print them.

5. Add a `__main__` block that runs `smoke_two_batches` on a small synthetic dataset and prints
   the two batch losses. The block must exit without error.

6. Run the validator:

   ```
   python check_loop.py my_loop.py
   ```

   The pass condition is:

   ```
   [PASS] my_loop.py
   ```

   If you see `[FAIL]`, read the printed failure message, fix the specific problem it names, and
   re-run. Do not move on until you see `[PASS]`.

## Where `check_loop.py` Lives

The validator ships with the book at `build-log/weights-and-measures/m1/check_loop.py`. Copy it
into your working directory or run it with its full path. It has no dependencies beyond the
standard library and works on Python 3.10 or later:

```
python path/to/check_loop.py my_loop.py
```

You can also run the validator's built-in self-test to confirm it is working correctly before
pointing it at your file:

```
python check_loop.py --selftest
```

Expected output for the self-test:

```
[PASS] GOOD canonical loop
[FAIL] BAD missing zero_grad + param check
    - missing step: zero_grad
    - missing trainable-parameter check (requires_grad + a counting construct)
[FAIL] BAD step before backward
    - out of order: ...
selftest: OK
```

## Done When

`python check_loop.py my_loop.py` exits 0 and prints:

```
[PASS] my_loop.py
```

`python my_loop.py` also exits 0 and prints the two smoke-test batch losses, with the second
lower than the first.

## Estimated Time

45 to 60 minutes.

## Stretch

Read `build-log/weights-and-measures/m1/trainer.py`. It is the book's reference spine for this
module. Compare your `train_one_epoch` to `trainer.py`'s implementation. Note one thing yours
does differently and one thing you would adopt from the reference. Write both observations as
comments at the top of `my_loop.py`.
