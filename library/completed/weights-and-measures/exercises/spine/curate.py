#!/usr/bin/env python3
"""curate.py - Weights and Measures M3 throughline curation tool (stdlib only).

The dataset-curation gate: read a raw JSONL, drop invalid lines, deduplicate by
content hash, shuffle with a seeded RNG, split into train/val, write the two files
plus a manifest. The cleaner feeds the gater: check_dataset.validate must pass
both output files before this script exits 0.

Usage:
    python curate.py raw.jsonl out_dir/ [--seed 0] [--val-frac 0.2]
    python curate.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
import tempfile

# ---------------------------------------------------------------------------
# Shared hash function (same normalization as check_dataset.py)
# ---------------------------------------------------------------------------

def _example_hash(messages: list) -> str:
    """Stable SHA-256 of the normalized concatenated message contents."""
    parts = []
    for msg in messages:
        role = str(msg.get("role", "")).strip().lower()
        content = str(msg.get("content", "")).strip()
        parts.append(f"{role}:{content}")
    raw = "\n".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# Per-line validity (mirrors check_dataset.validate, but returns bool)
# ---------------------------------------------------------------------------

_VALID_ROLES = {"system", "user", "assistant"}


def _line_is_valid(raw: str) -> tuple[bool, list | None]:
    """Return (valid, messages_list_or_None)."""
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return False, None

    msgs = obj.get("messages")
    if not isinstance(msgs, list) or not msgs:
        return False, None

    for msg in msgs:
        if not isinstance(msg, dict):
            return False, None
        if msg.get("role") not in _VALID_ROLES:
            return False, None
        content = msg.get("content")
        if not isinstance(content, str) or not content.strip():
            return False, None

    return True, msgs


# ---------------------------------------------------------------------------
# Core curate function
# ---------------------------------------------------------------------------

def curate(
    raw_path: str,
    out_dir: str,
    seed: int = 0,
    val_frac: float = 0.2,
) -> dict:
    """Read raw JSONL, clean, dedupe, split, write outputs; return the manifest dict.

    Steps:
      1. Read every line; drop invalid lines (counting them as 'dropped').
      2. Deduplicate by content hash; count extras as 'deduped'.
      3. Shuffle the surviving examples with random.Random(seed).
      4. Split: the last ceil(n * val_frac) go to val, the rest to train.
      5. Write train.jsonl, val.jsonl, manifest.json into out_dir.
      6. Return the manifest dict.
    """
    raw_count = 0
    dropped = 0
    deduped = 0
    seen_hashes: dict[str, int] = {}  # hash -> index in valid_examples
    valid_examples: list[str] = []    # original JSON strings, order of first seen

    with open(raw_path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            raw_count += 1
            ok, msgs = _line_is_valid(raw)
            if not ok:
                dropped += 1
                continue
            h = _example_hash(msgs)
            if h in seen_hashes:
                deduped += 1
                continue
            seen_hashes[h] = len(valid_examples)
            valid_examples.append(raw)

    # Seeded shuffle
    rng = random.Random(seed)
    rng.shuffle(valid_examples)

    # Split: val gets the last ceil(n * val_frac) examples
    n = len(valid_examples)
    val_size = math.ceil(n * val_frac) if n > 0 else 0
    train_size = n - val_size

    train_examples = valid_examples[:train_size]
    val_examples = valid_examples[train_size:]

    os.makedirs(out_dir, exist_ok=True)
    train_path = os.path.join(out_dir, "train.jsonl")
    val_path = os.path.join(out_dir, "val.jsonl")
    manifest_path = os.path.join(out_dir, "manifest.json")

    def _write_jsonl(path: str, lines: list[str]) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            for line in lines:
                fh.write(line + "\n")

    _write_jsonl(train_path, train_examples)
    _write_jsonl(val_path, val_examples)

    manifest = {
        "raw_count": raw_count,
        "dropped": dropped,
        "deduped": deduped,
        "valid_unique": n,
        "train_count": train_size,
        "val_count": val_size,
        "seed": seed,
        "val_frac": val_frac,
        "train_path": train_path,
        "val_path": val_path,
    }
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    return manifest


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _import_check_dataset():
    """Import check_dataset from the same directory as this script."""
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location(
        "check_dataset", os.path.join(here, "check_dataset.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_RAW_GOOD_LINE_A = '{"messages": [{"role": "user", "content": "What is supervised learning?"}, {"role": "assistant", "content": "Learning from labeled examples."}]}'
_RAW_GOOD_LINE_B = '{"messages": [{"role": "user", "content": "What is overfitting?"}, {"role": "assistant", "content": "When a model memorizes training data."}]}'
_RAW_GOOD_LINE_C = '{"messages": [{"role": "user", "content": "Define a loss function."}, {"role": "assistant", "content": "A measure of prediction error."}]}'
_RAW_GOOD_LINE_D = '{"messages": [{"role": "user", "content": "What is a learning rate?"}, {"role": "assistant", "content": "The step size for gradient descent."}]}'
_RAW_GOOD_LINE_E = '{"messages": [{"role": "user", "content": "What is regularization?"}, {"role": "assistant", "content": "Techniques to prevent overfitting."}]}'
_RAW_INVALID_LINE = 'not json {'
_RAW_DUPLICATE_OF_A = _RAW_GOOD_LINE_A  # exact copy


def selftest() -> int:
    print("curate.py --selftest")
    ok = True

    chk = _import_check_dataset()

    with tempfile.TemporaryDirectory() as tmpdir:
        raw_path = os.path.join(tmpdir, "raw.jsonl")
        out_dir = os.path.join(tmpdir, "out")

        # Build raw JSONL: 5 good + 1 invalid + 1 duplicate of A
        raw_lines = [
            _RAW_GOOD_LINE_A,
            _RAW_GOOD_LINE_B,
            _RAW_GOOD_LINE_C,
            _RAW_GOOD_LINE_D,
            _RAW_GOOD_LINE_E,
            _RAW_INVALID_LINE,
            _RAW_DUPLICATE_OF_A,
        ]
        with open(raw_path, "w", encoding="utf-8") as fh:
            for line in raw_lines:
                fh.write(line + "\n")

        manifest = curate(raw_path, out_dir, seed=42, val_frac=0.2)

        train_path = os.path.join(out_dir, "train.jsonl")
        val_path = os.path.join(out_dir, "val.jsonl")

        # 1. Duplicate removed: valid_unique must be 5 (not 6)
        if manifest["valid_unique"] == 5:
            print("[PASS] duplicate removed (valid_unique=5)")
        else:
            print(f"[FAIL] duplicate not removed: valid_unique={manifest['valid_unique']!r} (expected 5)")
            ok = False

        # 2. Invalid line dropped: dropped must be 1
        if manifest["dropped"] == 1:
            print("[PASS] invalid line dropped (dropped=1)")
        else:
            print(f"[FAIL] invalid line not counted: dropped={manifest['dropped']!r} (expected 1)")
            ok = False

        # 3. Deduped count is 1
        if manifest["deduped"] == 1:
            print("[PASS] dedup count correct (deduped=1)")
        else:
            print(f"[FAIL] dedup count wrong: deduped={manifest['deduped']!r} (expected 1)")
            ok = False

        # 4. Split sizes match val_frac=0.2 within rounding (ceil(5*0.2)=1 val, 4 train)
        expected_val = math.ceil(5 * 0.2)   # 1
        expected_train = 5 - expected_val    # 4
        if manifest["val_count"] == expected_val and manifest["train_count"] == expected_train:
            print(f"[PASS] split sizes correct (train={expected_train}, val={expected_val})")
        else:
            print(
                f"[FAIL] split sizes wrong: train={manifest['train_count']}, "
                f"val={manifest['val_count']} (expected train={expected_train}, val={expected_val})"
            )
            ok = False

        # 5. check_dataset.validate passes both output files
        train_failures = chk.validate(train_path)
        if not train_failures:
            print("[PASS] check_dataset.validate passes train.jsonl")
        else:
            print(f"[FAIL] check_dataset.validate fails train.jsonl: {train_failures}")
            ok = False

        val_failures = chk.validate(val_path)
        if not val_failures:
            print("[PASS] check_dataset.validate passes val.jsonl")
        else:
            print(f"[FAIL] check_dataset.validate fails val.jsonl: {val_failures}")
            ok = False

        # 6. check_dataset.check_leak finds NO leak
        leak_failures = chk.check_leak(train_path, val_path)
        if not leak_failures:
            print("[PASS] check_dataset.check_leak finds no leak")
        else:
            print(f"[FAIL] check_dataset.check_leak found leak: {leak_failures}")
            ok = False

        # Print the manifest for inspection
        print("\nmanifest.json:")
        print(json.dumps(manifest, indent=2))

    print("\nselftest:", "OK" if ok else "BROKEN")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Curate a raw JSONL fine-tune file into clean train/val splits (stdlib only)."
    )
    ap.add_argument("raw", nargs="?", help="path to the raw JSONL file")
    ap.add_argument("out_dir", nargs="?", help="output directory for train.jsonl, val.jsonl, manifest.json")
    ap.add_argument("--seed", type=int, default=0, help="random seed for shuffle (default: 0)")
    ap.add_argument("--val-frac", type=float, default=0.2, help="fraction for val split (default: 0.2)")
    ap.add_argument("--selftest", action="store_true", help="run built-in tests")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not args.raw or not args.out_dir:
        ap.error("provide raw.jsonl and out_dir, or pass --selftest")

    manifest = curate(args.raw, args.out_dir, seed=args.seed, val_frac=args.val_frac)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
