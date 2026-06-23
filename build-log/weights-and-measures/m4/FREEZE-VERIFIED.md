# M4 FREEZE-VERIFIED

Captured 2026-06-22. torch 2.12.1+cpu, Python 3.x, CPU only. No peft / transformers / bitsandbytes.

## LoRA demo output (trainer.py __main__ M4 block)

```
============================================================
M4 LoRA DEMO: wrap TinyClassifier with LoRALinear
============================================================
params: total=1572, trainable=1056, frozen=516
  (base had 516 params, now all frozen; LoRA adds 1056 trainable)
  freeze confirmed: 516 base params frozen, 1056 adapter params trainable  [PASS]

epoch  train_loss  valid_loss
-----  ----------  ----------
    1       1.4209       1.7545
    2       0.6617       1.5904
    3       0.1306       1.4385
    4       0.0185       1.3199
    5       0.0045       1.2710
    6       0.0016       1.2556
    7       0.0009       1.2491
    8       0.0006       1.2483
    9       0.0006       1.2472  <-- BEST
   10       0.0005       1.2477

LoRA valid_loss descended: 1.7545 -> 1.2477  [PASS]
merge() equivalence: max diff = 1.46e-06 < 1e-5  [PASS]

trainer.py M4 LoRA demo complete.
```

### Freeze ratio interpretation

TinyClassifier(128, 4) has 128*4 + 4 = 516 params in its one Linear layer. With r=8, alpha=16:
- lora_A: 128 * 8 = 1024 weights
- lora_B: 8 * 4 = 32 weights
- adapter total: 1056 trainable
- base: 516 frozen (requires_grad=False on weight + bias)
- total: 1572

The base 516 are fully frozen (frozen_count == base_total assertion passes). On a real large model
(e.g. 7B params, r=8 on attention projections) the adapter is typically < 0.5% of total params;
the tiny demo model inverts this ratio but the MECHANISM is identical: only A and B receive gradients.

## check_loop.py --selftest

```
check_loop.py --selftest
[PASS] GOOD canonical loop
[FAIL] BAD missing zero_grad + param check
    - missing step: zero_grad
    - missing trainable-parameter check (requires_grad + a counting construct)
[FAIL] BAD step before backward
    - out of order: 'step' (line 8) appears before 'backward' (line 9) but must come after it

[PASS] M2 GOOD fit-style loop (all signals present)
[FAIL] M2 BAD missing val pass + early-stop signal
    - missing model.eval() call (required for validation pass)
    - missing torch.no_grad() or torch.inference_mode() context (required for validation pass)
    - missing early-stopping signal: need 'best' together with 'valid' or 'patience'

[PASS] M4 GOOD LoRA wrap + frozen base + fit
[FAIL] M4 BAD no freeze + no adapter signal
    - missing freeze signal: need requires_grad_(False) or requires_grad=False (proves base weights are frozen)
    - missing low-rank adapter signal: need 'lora'/'LoRA'/'adapter' together with a rank symbol ('r=' or ', r' or 'rank')

selftest: OK
```

## check_loop.py --module 4 trainer.py

```
[PASS] library/in-progress/weights-and-measures/exercises/spine/trainer.py
```

## py_compile

```
python -m py_compile trainer.py  -> exit 0  (COMPILE OK)
```

## M1 demo intact (last epoch ~0.0534)

```
epoch  mean_loss
-----  ---------
   1   1.1953
   2   0.5941
   3   0.3325
   4   0.2097
   5   0.1454
   6   0.1087
   7   0.0866
   8   0.0720
   9   0.0616
  10   0.0534
```

M1 ends at 0.0534. CONFIRMED UNDISTURBED.

## M2 overfit demo intact (best epoch before final)

```
epoch  train_loss  valid_loss
-----  ----------  ----------
    1       1.5197       1.5801
    2       0.8901       1.5413
    3       0.5283       1.5205
    4       0.3126       1.5141  <-- BEST
    5       0.1922       1.5172
    6       0.1256       1.5254
    7       0.0877       1.5355

Early stop after epoch 7  (patience=3, no improvement since epoch 4)
Best epoch : 4  (valid_loss=1.5141)
Final epoch: 7
[PASS] best epoch is before final epoch; divergence confirmed.
```

M2 best epoch = 4, final epoch = 7. CONFIRMED UNDISTURBED.
