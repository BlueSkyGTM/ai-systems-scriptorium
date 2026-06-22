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

The five ordered steps it requires (the canonical loop contract):
    1. optimizer.zero_grad()   2. forward pass (model(...))   3. loss computed
    4. loss.backward()         5. optimizer.step()
Plus: a trainable-parameter check (requires_grad + a counting construct).
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


def _report(label: str, source: str) -> list[str]:
    failures = validate(source)
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


def selftest() -> int:
    print("check_loop.py --selftest")
    ok = True
    if _report("GOOD canonical loop", _GOOD):
        ok = False  # GOOD must pass (no failures)
    if not _report("BAD missing zero_grad + param check", _BAD_MISSING):
        ok = False  # BAD must fail (non-empty failures)
    if not _report("BAD step before backward", _BAD_ORDER):
        ok = False  # BAD must fail
    print("\nselftest:", "OK" if ok else "BROKEN")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a training-loop file's structure (stdlib only).")
    ap.add_argument("file", nargs="?", help="path to the loop file to validate")
    ap.add_argument("--selftest", action="store_true", help="run built-in good/bad cases")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.file:
        ap.error("provide a file to validate, or pass --selftest")
    with open(args.file, encoding="utf-8") as fh:
        failures = _report(args.file, fh.read())
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
