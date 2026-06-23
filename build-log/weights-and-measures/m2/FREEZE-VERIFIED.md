# FREEZE-VERIFIED — Weights and Measures M2

Verified 2026-06-22 by Sonnet spine-engineer on torch 2.12.1+cpu (Windows 11).
All output below is REAL captured output; nothing is fabricated.

---

## Environment

```
torch version: 2.12.1+cpu
python: 3.x (Windows 11, CPU only)
```

---

## FREEZE 1 — `evaluate(...)` returns `(avg_loss, token_acc)` on a tiny set

**Catalog location:** L1 FREEZE block (`fitting-catalog.md`).

**Code run:**

```python
import torch, torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from trainer import TinyClassifier, evaluate

torch.manual_seed(42)
device = torch.device('cpu')
IN_DIM, N_CLASSES = 128, 4

X = torch.randn(32, IN_DIM)
y = torch.randint(0, N_CLASSES, (32,))
ds = TensorDataset(X, y)
loader = DataLoader(ds, batch_size=16)

model = TinyClassifier(IN_DIM, N_CLASSES)
loss_fn = nn.CrossEntropyLoss()

avg_loss, token_acc = evaluate(model, loader, loss_fn, device)
print(f'evaluate => avg_loss={avg_loss:.4f}, token_acc={token_acc:.4f}')
assert isinstance(avg_loss, float) and isinstance(token_acc, float)
assert 0.0 <= token_acc <= 1.0
print('evaluate FREEZE check: PASS')
```

**Real output:**

```
evaluate => avg_loss=1.3588, token_acc=0.3750
evaluate FREEZE check: PASS
```

**Notes:** `model.eval()` + `torch.no_grad()` are both present in the implementation per catalog L1.
No changes needed to the catalog freeze block.

---

## FREEZE 2 — Checkpoint dict structure (catalog L3 FREEZE block)

**Catalog location:** L3 FREEZE block — the `torch.save(...)` dict keys.

The `fit()` function in `trainer.py` saves:

```python
torch.save(
    {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "valid_loss": valid_loss,
    },
    best_ckpt_path,
)
```

This is byte-identical to the catalog L3 FREEZE block (path substitution:
`f"checkpoints/epoch_{epoch:02d}.pt"` → `best_ckpt_path` to allow tmpdir use during verify).
The `valid_loss` key is the promotion criterion; optimizer state is mandatory for resume.

No fix needed; the freeze block runs as written.

---

## FREEZE 3 — `fit(...)` OVERFIT demo: val loss diverges; best epoch is BEFORE final epoch

**Command run:**

```
python trainer.py
```

**Real captured output (M2 overfit demo section):**

```
============================================================
M2 OVERFIT DEMO: inducing train/val divergence
============================================================

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
[PASS] best epoch is before final epoch — divergence confirmed.

trainer.py M2 overfit demo complete.
```

**Interpretation:** training loss falls monotonically from 1.52 to 0.09 (classic memorisation).
Validation loss improves through epoch 4 (1.5141) then rises to 1.5355 at epoch 7.
Early stopping (patience=3) fires after epoch 7 (3 epochs without improvement post-epoch-4).
The saved checkpoint is epoch 4; the model state is restored to it before `fit()` returns.
Best epoch (4) is before final epoch (7): divergence confirmed.

**Setup notes:** seed=7, 16-sample training set, 128-sample val set with noise std=1.5,
lr=3e-2, batch=4, patience=3, max_epochs=30.

---

## FREEZE 4 — `check_loop.py --selftest` exits 0, both modules OK

**Command run:**

```
python check_loop.py --selftest
```

**Real output:**

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

selftest: OK
```

Exit code: 0. All five selftest cases resolved correctly:
- M1 GOOD: PASS (correct loop)
- M1 BAD missing: FAIL (caught missing zero_grad + param check)
- M1 BAD order: FAIL (caught step before backward)
- M2 GOOD: PASS (fit-style loop with eval + no_grad + best/valid/patience)
- M2 BAD: FAIL (caught missing eval, no_grad, and early-stop signal)

---

## FREEZE 5 — `check_loop.py --module 2 trainer.py` => PASS

**Command run:**

```
python check_loop.py --module 2 trainer.py
```

**Real output:**

```
[PASS] trainer.py
```

trainer.py passes the full M2 check: five-step loop, requires_grad param check,
`model.eval()`, `torch.no_grad()`, and `best`/`valid`/`patience` early-stop signal.

---

## FREEZE 6 — M1 demo undisturbed (loss ends near 0.0534)

**From the same `python trainer.py` run above (M1 section):**

```
params: total=516, trainable=516
smoke_two_batches: 1.6054 -> 1.3099  [PASS]

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

trainer.py self-demo complete.
```

M1 loss at epoch 10: **0.0534** — matches the expected value from the M1 spec.
M1 functions `TinyClassifier`, `train_one_epoch`, `smoke_two_batches`, and the
10-epoch `__main__` demo are byte-identical to the M1 ship; not disturbed.

---

## Implementation notes

1. **`evaluate` freeze block fix:** the catalog's freeze block uses positional variable names
   (`total_loss`, `correct`, `total`) and `loss_fn(logits, y).item()`. The implementation
   matches exactly. No logic changes needed.

2. **`fit` checkpoint dict:** `torch.save` path uses `best_ckpt_path` (a temp dir path) instead
   of the literal `f"checkpoints/epoch_{epoch:02d}.pt"` in the catalog — this is a location
   substitution to avoid requiring a hardcoded directory during verify. The dict keys are
   byte-identical to the catalog L3 freeze block.

3. **`check_loop.py` BEST_SIGNAL regex:** initial regex `\bbest\b` failed on `best_valid_loss`
   (word boundary doesn't fire before `_`). Fixed to `\bbest` (prefix match) so it matches
   `best`, `best_valid_loss`, `best_epoch`, etc. Same fix applied to VALID_OR_PATIENCE.

4. **Overfit demo dataset:** needed seed=7, batch_size=4, lr=3e-2, val noise std=1.5 to produce
   a trajectory where val improves for 3-4 epochs before diverging (best=epoch 4, final=epoch 7).
   Higher LR or smaller batch caused immediate divergence from epoch 1 (not pedagogically useful).
