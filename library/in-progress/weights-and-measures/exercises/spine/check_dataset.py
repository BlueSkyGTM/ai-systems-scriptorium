#!/usr/bin/env python3
"""check_dataset.py - Weights and Measures M3 throughline validator (stdlib only).

The data-quality gate thesis: a fine-tune dataset is not "ready" because it exists;
it is ready when every line is a valid chat example, no example is an exact duplicate,
and no example hash appears in both train and val splits. This validator is the rubric
in code. It imports NO third-party libraries.

Usage:
    python check_dataset.py data.jsonl                    # validate one file (exit 0 = clean)
    python check_dataset.py --check-leak train.jsonl val.jsonl  # leakage gate
    python check_dataset.py --selftest                    # run built-in good/bad cases
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import os

VALID_ROLES = {"system", "user", "assistant"}


# ---------------------------------------------------------------------------
# Core logic
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


def validate(path: str) -> list[str]:
    """Read a JSONL fine-tune file; return a list of named failure strings.

    Failures detected (each prefixed with the 1-based line number):
      - invalid-json        line is not valid JSON
      - messages-missing    top-level key 'messages' absent
      - messages-not-list   'messages' is present but not a list
      - messages-empty      'messages' is an empty list
      - message-not-object  a message entry is not a dict
      - role-missing        a message has no 'role' key
      - role-unknown        a message role is not in {system, user, assistant}
      - content-missing     a message has no 'content' key
      - content-empty       a message content is an empty string (after strip)
      - duplicate           this example's content hash already appeared earlier
    """
    failures: list[str] = []
    seen_hashes: dict[str, int] = {}  # hash -> first line number

    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue  # skip blank lines silently

            # 1. Valid JSON
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                failures.append(f"line {lineno}: invalid-json")
                continue

            # 2. 'messages' present and a non-empty list
            if "messages" not in obj:
                failures.append(f"line {lineno}: messages-missing")
                continue
            msgs = obj["messages"]
            if not isinstance(msgs, list):
                failures.append(f"line {lineno}: messages-not-list")
                continue
            if len(msgs) == 0:
                failures.append(f"line {lineno}: messages-empty")
                continue

            # 3. Each message: object, role in valid set, non-empty string content
            line_ok = True
            for idx, msg in enumerate(msgs):
                if not isinstance(msg, dict):
                    failures.append(f"line {lineno} message[{idx}]: message-not-object")
                    line_ok = False
                    continue
                if "role" not in msg:
                    failures.append(f"line {lineno} message[{idx}]: role-missing")
                    line_ok = False
                elif msg["role"] not in VALID_ROLES:
                    failures.append(
                        f"line {lineno} message[{idx}]: role-unknown ({msg['role']!r})"
                    )
                    line_ok = False
                if "content" not in msg:
                    failures.append(f"line {lineno} message[{idx}]: content-missing")
                    line_ok = False
                elif not isinstance(msg["content"], str) or not msg["content"].strip():
                    failures.append(f"line {lineno} message[{idx}]: content-empty")
                    line_ok = False

            if not line_ok:
                continue

            # 4. Exact-duplicate detection (hash of normalized content)
            h = _example_hash(msgs)
            if h in seen_hashes:
                failures.append(
                    f"line {lineno}: duplicate (matches line {seen_hashes[h]})"
                )
            else:
                seen_hashes[h] = lineno

    return failures


def check_leak(train_path: str, val_path: str) -> list[str]:
    """Return failures if any example hash appears in BOTH train and val files.

    Only hashes examples that individually pass per-line validation.
    """
    failures: list[str] = []

    def _hashes_from(path: str) -> set[str]:
        hashes: set[str] = []
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                msgs = obj.get("messages")
                if not isinstance(msgs, list) or not msgs:
                    continue
                hashes.append(_example_hash(msgs))
        return set(hashes)

    train_hashes = _hashes_from(train_path)
    val_hashes = _hashes_from(val_path)
    overlap = train_hashes & val_hashes
    if overlap:
        failures.append(
            f"leak: {len(overlap)} example(s) appear in both "
            f"{train_path} and {val_path}"
        )
    return failures


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def _report_validate(label: str, path: str) -> list[str]:
    failures = validate(path)
    status = "PASS" if not failures else "FAIL"
    print(f"[{status}] {label}")
    for f in failures:
        print(f"    - {f}")
    return failures


def _report_leak(label: str, train_path: str, val_path: str) -> list[str]:
    failures = check_leak(train_path, val_path)
    status = "PASS" if not failures else "FAIL"
    print(f"[{status}] {label}")
    for f in failures:
        print(f"    - {f}")
    return failures


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

_GOOD_LINES = [
    '{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is 2+2?"}, {"role": "assistant", "content": "4."}]}',
    '{"messages": [{"role": "user", "content": "Explain gravity."}, {"role": "assistant", "content": "Gravity is a force of attraction."}]}',
    '{"messages": [{"role": "user", "content": "What is the capital of France?"}, {"role": "assistant", "content": "Paris."}]}',
]

_BAD_JSON_LINE = 'not valid json at all {'
_BAD_ROLE_LINE = '{"messages": [{"role": "oracle", "content": "I know all."}, {"role": "user", "content": "Tell me."}]}'
_BAD_EMPTY_CONTENT = '{"messages": [{"role": "user", "content": "  "}, {"role": "assistant", "content": "Sure."}]}'
_DUPLICATE_LINE = _GOOD_LINES[0]  # exact copy of the first good line


def _write_lines(path: str, lines: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for line in lines:
            fh.write(line + "\n")


def selftest() -> int:
    print("check_dataset.py --selftest")
    ok = True

    with tempfile.TemporaryDirectory() as tmpdir:
        # --- Case: GOOD dataset passes ---
        good_path = os.path.join(tmpdir, "good.jsonl")
        _write_lines(good_path, _GOOD_LINES)
        if _report_validate("GOOD dataset (all valid)", good_path):
            ok = False  # GOOD must produce no failures

        # --- Case (a): invalid JSON line ---
        bad_json_path = os.path.join(tmpdir, "bad_json.jsonl")
        _write_lines(bad_json_path, [_GOOD_LINES[0], _BAD_JSON_LINE])
        result = _report_validate("BAD invalid JSON line", bad_json_path)
        if not any("invalid-json" in f for f in result):
            print("    ! expected 'invalid-json' reason")
            ok = False

        # --- Case (b): unknown role ---
        bad_role_path = os.path.join(tmpdir, "bad_role.jsonl")
        _write_lines(bad_role_path, [_GOOD_LINES[0], _BAD_ROLE_LINE])
        result = _report_validate("BAD unknown role", bad_role_path)
        if not any("role-unknown" in f for f in result):
            print("    ! expected 'role-unknown' reason")
            ok = False

        # --- Case (c): empty content ---
        bad_content_path = os.path.join(tmpdir, "bad_content.jsonl")
        _write_lines(bad_content_path, [_GOOD_LINES[0], _BAD_EMPTY_CONTENT])
        result = _report_validate("BAD empty content", bad_content_path)
        if not any("content-empty" in f for f in result):
            print("    ! expected 'content-empty' reason")
            ok = False

        # --- Case (d): exact duplicate within a file ---
        dup_path = os.path.join(tmpdir, "dup.jsonl")
        _write_lines(dup_path, [_GOOD_LINES[0], _GOOD_LINES[1], _DUPLICATE_LINE])
        result = _report_validate("BAD exact duplicate", dup_path)
        if not any("duplicate" in f for f in result):
            print("    ! expected 'duplicate' reason")
            ok = False

        # --- Case (e): train/val leak ---
        train_path = os.path.join(tmpdir, "train_leak.jsonl")
        val_path = os.path.join(tmpdir, "val_leak.jsonl")
        _write_lines(train_path, _GOOD_LINES)
        _write_lines(val_path, [_GOOD_LINES[0]])  # deliberate overlap
        result = _report_leak("BAD train/val leak", train_path, val_path)
        if not any("leak" in f for f in result):
            print("    ! expected 'leak' reason")
            ok = False

        # --- Confirm clean train/val passes the leak gate ---
        val_clean_path = os.path.join(tmpdir, "val_clean.jsonl")
        _write_lines(val_clean_path, ['{"messages": [{"role": "user", "content": "Fresh example."}, {"role": "assistant", "content": "No overlap."}]}'])
        if _report_leak("GOOD no train/val leak", train_path, val_clean_path):
            ok = False

    print("\nselftest:", "OK" if ok else "BROKEN")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate a JSONL fine-tune dataset (stdlib only)."
    )
    ap.add_argument("file", nargs="?", help="JSONL file to validate")
    ap.add_argument(
        "--check-leak",
        nargs=2,
        metavar=("TRAIN", "VAL"),
        help="check that no example hash appears in both files",
    )
    ap.add_argument("--selftest", action="store_true", help="run built-in good/bad cases")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.check_leak:
        train_p, val_p = args.check_leak
        failures = check_leak(train_p, val_p)
        for f in failures:
            print(f)
        return 1 if failures else 0

    if not args.file:
        ap.error("provide a JSONL file to validate, or pass --selftest / --check-leak")

    failures = _report_validate(args.file, args.file)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
