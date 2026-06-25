"""m7_regress.py — behavioral regression suite (M7's technique).

The eval gate proves the model is good on average. The regression suite proves it still
gets a set of pinned, business-critical tickets right. A model can clear the aggregate
gate and still misroute the one security ticket that matters; this catches that.

PASS only if every golden case is classified correctly (no regression on any pinned
behaviour).
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import m6_train

# Pinned tickets that must always route correctly, whatever the retrain does.
GOLDEN: List[Tuple[str, str]] = [
    ("refund my invoice charge", "billing"),
    ("the app crash fails with an exception", "bug"),
    ("please add an integration feature", "feature"),
    ("amazing thanks i love this", "praise"),
    ("password breach security vulnerability", "security"),
]


def check(checkpoint: dict, golden: List[Tuple[str, str]] = GOLDEN) -> Dict[str, object]:
    results, failures = [], []
    for text, expected in golden:
        got = m6_train.predict(checkpoint, text)
        ok = got == expected
        results.append((text, expected, got, ok))
        if not ok:
            failures.append((text, expected, got))
    passed = len(failures) == 0
    return {
        "passed": bool(passed),
        "n_cases": len(golden),
        "n_passed": sum(1 for *_, ok in results if ok),
        "failures": failures,
        "results": results,
    }
