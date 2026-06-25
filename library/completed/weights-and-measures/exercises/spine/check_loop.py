#!/usr/bin/env python3
"""check_loop.py - Weights and Measures M1 throughline validator (stdlib only).

The eval-gate thesis applied to the reader's own training loop: a loop is not "done"
because it runs; it is done when it has the five steps wired in the right order and a
trainable-parameter check present. This validator is the rubric in code. It imports NO
torch -- it reads a loop file as text and gates its structure, so it runs in CI on any
machine and means the same thing every time.

Usage:
    python check_loop.py path/to/trainer.py     # validate a file (exit 0 = pass)
    python check_loop.py --selftest              # run built-in good/bad cases
    python check_loop.py --module 2 path/to/trainer.py  # M2 extended checks
    python check_loop.py --module 4 path/to/trainer.py  # M4 extended checks

The five ordered steps it requires (the canonical loop contract):
    1. optimizer.zero_grad()   2. forward pass (model(...))   3. loss computed
    4. loss.backward()         5. optimizer.step()
Plus: a trainable-parameter check (requires_grad + a counting construct).

M2 additions (--module 2 only):
    6. model.eval() call present
    7. no_grad or inference_mode context present
    8. early-stopping signal: 'best' together with 'valid' or 'patience'

M4 additions (--module 4, cumulative with M1+M2):
    9. freeze signal: requires_grad_(False) or requires_grad = False or requires_grad=False
   10. low-rank adapter signal: 'lora' or 'LoRA' or 'adapter' AND a rank symbol
       (r= or ', r' or 'rank')
"""
from __future__ import annotations

import argparse
import re
import sys

# Each step: (name, compiled regex). Order in this list IS the required order.
STEPS = [
    ("zero_grad", re.compile(r"\.zero_grad\s*\(")),
    ("forward",   re.compile(r"\b(?:model|net)\s*\(|\.forward\s*\(")),  # logits = model(x)
    ("loss",      re.compile(r"\bloss\b\s*=|loss_fn\s*\(|criterion\s*\(")),
    ("backward",  re.compile(r"\.backward\s*\(")),
    ("step",      re.compile(r"\.step\s*\(")),
]

# The trainable-parameter check: requires_grad AND a counting construct.
PARAM_CHECK = re.compile(r"requires_grad")
PARAM_COUNT = re.compile(r"\.numel\s*\(|\.parameters\s*\(|sum\s*\(")

# M2: validation loop checks
EVAL_MODE   = re.compile(r"\.eval\s*\(")                                   # model.eval()
NO_GRAD     = re.compile(r"torch\.no_grad\s*\(|torch\.inference_mode\s*\(")  # no_grad context
# Early-stopping signal: 'best' (standalone or as prefix in compound names like best_valid_loss)
# together with 'valid' or 'patience' anywhere in the file.
BEST_SIGNAL = re.compile(r"\bbest")          # matches 'best', 'best_valid_loss', 'best_epoch', etc.
VALID_OR_PATIENCE = re.compile(r"\bvalid|\bpatience")

# M4: freeze + low-rank adapter checks
# Freeze signal: requires_grad_(False) OR requires_grad = False OR requires_grad=False
FREEZE_SIGNAL = re.compile(r"requires_grad_\s*\(\s*False\s*\)|requires_grad\s*=\s*False")
# Low-rank adapter signal: 'lora' or 'LoRA' (anywhere, case-insensitive) or 'adapter'
# together with a rank symbol: r= or , r or rank.
# Note: no word-boundaries on lora/LoRA so LoRALinear, lora_A, etc. all match.
LORA_NAME   = re.compile(r"lora|adapter", re.IGNORECASE)
RANK_SYMBOL = re.compile(r"\br\s*=|,\s*r\b|\brank\b")


def _first_line(source: str, pattern: re.Pattern) -> int | None:
    for i, line in enumerate(source.splitlines(), start=1):
        if pattern.search(line):
            return i
    return None


def validate(source: str) -> list[str]:
    """Return a list of failure messages; empty list means the loop passes."""
    failures: list[str] = []

    # 1. every step present
    lines = {}
    for name, pat in STEPS:
        ln = _first_line(source, pat)
        if ln is None:
            failures.append(f"missing step: {name}")
        else:
            lines[name] = ln

    # 2. present steps are in the canonical order
    present = [(name, lines[name]) for name, _ in STEPS if name in lines]
    for (a_name, a_ln), (b_name, b_ln) in zip(present, present[1:]):
        if a_ln > b_ln:
            failures.append(
                f"out of order: '{b_name}' (line {b_ln}) appears before '{a_name}' "
                f"(line {a_ln}) but must come after it"
            )

    # 3. trainable-parameter check present
    if not (PARAM_CHECK.search(source) and PARAM_COUNT.search(source)):
        failures.append("missing trainable-parameter check (requires_grad + a counting construct)")

    return failures


def validate_m2(source: str) -> list[str]:
    """Return M2-specific failure messages (runs AFTER validate; caller merges).

    Checks (beyond M1):
      (a) model.eval() call present
      (b) torch.no_grad() or torch.inference_mode() context present
      (c) early-stopping signal: 'best' together with 'valid' or 'patience'
    """
    failures: list[str] = []

    if not EVAL_MODE.search(source):
        failures.append("missing model.eval() call (required for validation pass)")

    if not NO_GRAD.search(source):
        failures.append(
            "missing torch.no_grad() or torch.inference_mode() context "
            "(required for validation pass)"
        )

    has_best = BEST_SIGNAL.search(source)
    has_valid_or_patience = VALID_OR_PATIENCE.search(source)
    if not (has_best and has_valid_or_patience):
        failures.append(
            "missing early-stopping signal: need 'best' together with 'valid' or 'patience'"
        )

    return failures


def validate_m4(source: str) -> list[str]:
    """Return M4-specific failure messages (runs AFTER validate + validate_m2; caller merges).

    Checks (beyond M1+M2):
      (a) freeze signal: requires_grad_(False) or requires_grad = False or requires_grad=False
      (b) low-rank adapter signal: 'lora' or 'LoRA' or 'adapter' AND a rank symbol
          (r= or ', r' or 'rank')
    """
    failures: list[str] = []

    if not FREEZE_SIGNAL.search(source):
        failures.append(
            "missing freeze signal: need requires_grad_(False) or requires_grad=False "
            "(proves base weights are frozen)"
        )

    has_lora_name = LORA_NAME.search(source)
    has_rank_symbol = RANK_SYMBOL.search(source)
    if not (has_lora_name and has_rank_symbol):
        failures.append(
            "missing low-rank adapter signal: need 'lora'/'LoRA'/'adapter' together with "
            "a rank symbol ('r=' or ', r' or 'rank')"
        )

    return failures


def _report(label: str, source: str, module: int = 1) -> list[str]:
    failures = validate(source)
    if module >= 2:
        failures += validate_m2(source)
    if module >= 4:
        failures += validate_m4(source)
    status = "PASS" if not failures else "FAIL"
    print(f"[{status}] {label}")
    for f in failures:
        print(f"    - {f}")
    return failures


_GOOD = """
def train_one_epoch(model, loader, optimizer, loss_fn, device):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    model.train()
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()
"""

_BAD_MISSING = """
def train_one_epoch(model, loader, optimizer, loss_fn, device):
    for x, y in loader:
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()
"""  # no zero_grad, no param check

_BAD_ORDER = """
def train_one_epoch(model, loader, optimizer, loss_fn, device):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    for x, y in loader:
        optimizer.zero_grad()
        logits = model(x)
        loss = loss_fn(logits, y)
        optimizer.step()
        loss.backward()
"""  # step before backward

# ---------------------------------------------------------------------------
# M2 selftest cases
# ---------------------------------------------------------------------------

# A fit-style loop that has all M2 signals: eval, no_grad, best+valid+patience
_M2_GOOD = """
def train_one_epoch(model, loader, optimizer, loss_fn, device):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    model.train()
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()

def fit(model, train_loader, val_loader, optimizer, loss_fn, device,
        max_epochs=20, patience=3):
    best_valid_loss = float("inf")
    epochs_without_improvement = 0
    for epoch in range(1, max_epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, loss_fn, device)
        model.eval()
        with torch.no_grad():
            for x, y in val_loader:
                logits = model(x)
                valid_loss = loss_fn(logits, y).item()
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
        if epochs_without_improvement >= patience:
            break
"""

# Missing model.eval() and no_grad, and no early-stopping signal
_M2_BAD_MISSING_VAL = """
def train_one_epoch(model, loader, optimizer, loss_fn, device):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    model.train()
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()

def fit_naive(model, loader, optimizer, loss_fn, device, max_epochs=20):
    for epoch in range(1, max_epochs + 1):
        train_one_epoch(model, loader, optimizer, loss_fn, device)
"""

# ---------------------------------------------------------------------------
# M4 selftest cases
# ---------------------------------------------------------------------------

# A full M4-compliant loop: has all M1+M2 signals, PLUS freeze + LoRA adapter with rank
_M4_GOOD = """
class LoRALinear(nn.Module):
    def __init__(self, base, r=8, alpha=16.0):
        super().__init__()
        self.base = base
        self.base.weight.requires_grad_(False)
        if self.base.bias is not None:
            self.base.bias.requires_grad_(False)
        self.lora_A = nn.Linear(base.in_features, r, bias=False)
        self.lora_B = nn.Linear(r, base.out_features, bias=False)
        self.scaling = alpha / r

    def forward(self, x):
        return self.base(x) + self.scaling * self.lora_B(self.lora_A(x))

def wrap_with_lora(model, r=8, alpha=16):
    for name, module in list(model.named_modules()):
        if isinstance(module, nn.Linear):
            setattr(model, name, LoRALinear(module, r=r, alpha=alpha))
    return model

def train_one_epoch(model, loader, optimizer, loss_fn, device):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    model.train()
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()

def fit(model, train_loader, val_loader, optimizer, loss_fn, device,
        max_epochs=20, patience=3):
    best_valid_loss = float("inf")
    epochs_without_improvement = 0
    for epoch in range(1, max_epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, loss_fn, device)
        model.eval()
        with torch.no_grad():
            for x, y in val_loader:
                logits = model(x)
                valid_loss = loss_fn(logits, y).item()
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
        if epochs_without_improvement >= patience:
            break
"""

# Missing freeze signal (no requires_grad_(False)) and no adapter/rank signal
_M4_BAD_NO_FREEZE_NO_ADAPTER = """
def train_one_epoch(model, loader, optimizer, loss_fn, device):
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    model.train()
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = loss_fn(logits, y)
        loss.backward()
        optimizer.step()

def fit(model, train_loader, val_loader, optimizer, loss_fn, device,
        max_epochs=20, patience=3):
    best_valid_loss = float("inf")
    epochs_without_improvement = 0
    for epoch in range(1, max_epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, loss_fn, device)
        model.eval()
        with torch.no_grad():
            for x, y in val_loader:
                logits = model(x)
                valid_loss = loss_fn(logits, y).item()
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
        if epochs_without_improvement >= patience:
            break
"""


def selftest() -> int:
    print("check_loop.py --selftest")
    ok = True

    # --- M1 cases (module=1 behavior, byte-identical) ---
    if _report("GOOD canonical loop", _GOOD):
        ok = False  # GOOD must pass (no failures)
    if not _report("BAD missing zero_grad + param check", _BAD_MISSING):
        ok = False  # BAD must fail (non-empty failures)
    if not _report("BAD step before backward", _BAD_ORDER):
        ok = False  # BAD must fail

    print()  # blank line before M2 cases

    # --- M2 cases (module=2 behavior) ---
    if _report("M2 GOOD fit-style loop (all signals present)", _M2_GOOD, module=2):
        ok = False  # M2 GOOD must pass
    if not _report("M2 BAD missing val pass + early-stop signal", _M2_BAD_MISSING_VAL, module=2):
        ok = False  # M2 BAD must fail

    print()  # blank line before M4 cases

    # --- M4 cases (module=4 behavior) ---
    if _report("M4 GOOD LoRA wrap + frozen base + fit", _M4_GOOD, module=4):
        ok = False  # M4 GOOD must pass
    if not _report("M4 BAD no freeze + no adapter signal", _M4_BAD_NO_FREEZE_NO_ADAPTER, module=4):
        ok = False  # M4 BAD must fail

    print("\nselftest:", "OK" if ok else "BROKEN")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a training-loop file's structure (stdlib only).")
    ap.add_argument("file", nargs="?", help="path to the loop file to validate")
    ap.add_argument("--selftest", action="store_true", help="run built-in good/bad cases")
    ap.add_argument(
        "--module", type=int, default=1, choices=[1, 2, 4],
        help="module level of checks to apply (default: 1; --module 2 adds val+early-stop checks; "
             "--module 4 adds freeze+adapter checks)",
    )
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.file:
        ap.error("provide a file to validate, or pass --selftest")
    with open(args.file, encoding="utf-8") as fh:
        failures = _report(args.file, fh.read(), module=args.module)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
