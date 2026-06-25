"""m3_curate.py — dataset curation (M3's technique).

Raw labeled tickets come in noisy: malformed rows, exact duplicates, no split. Curation
validates the schema, drops duplicates, and produces a disjoint train/test split. The
synthetic generator here stands in for a real labeling pipeline; the curation contract is
what matters.
"""
from __future__ import annotations

import random
from typing import Dict, List, Tuple

CLASS_NAMES = ["billing", "bug", "feature", "praise", "security"]
SIGNAL: Dict[str, List[str]] = {
    "billing": ["invoice", "charge", "payment", "refund", "billing", "subscription"],
    "bug": ["crash", "error", "broken", "bug", "fails", "exception"],
    "feature": ["request", "add", "feature", "integrate", "enhancement", "option"],
    "praise": ["great", "love", "amazing", "thanks", "excellent", "awesome"],
    "security": ["password", "breach", "security", "hacked", "vulnerability", "leak"],
}
FILLER = ["the", "a", "this", "is", "please", "could", "today", "i", "you", "we"]


def _make_row(rng: random.Random) -> dict:
    label = rng.choice(CLASS_NAMES)
    sig = [rng.choice(SIGNAL[label]) for _ in range(rng.randint(2, 3))]
    fill = [rng.choice(FILLER) for _ in range(rng.randint(1, 2))]
    toks = sig + fill
    rng.shuffle(toks)
    return {"text": " ".join(toks), "label": label}


def generate_raw(n: int, seed: int, dup_fraction: float = 0.15) -> List[dict]:
    """Synthetic raw tickets, with deliberate duplicates and a couple of malformed rows
    so curation has something to clean."""
    rng = random.Random(seed)
    rows = [_make_row(rng) for _ in range(n)]
    # inject exact duplicates
    for _ in range(int(n * dup_fraction)):
        rows.append(dict(rng.choice(rows)))
    # inject malformed rows
    rows.append({"text": "", "label": "billing"})
    rows.append({"text": "missing label here"})
    rng.shuffle(rows)
    return rows


def is_valid(row: dict) -> bool:
    return (
        isinstance(row.get("text"), str)
        and bool(row["text"].strip())
        and row.get("label") in CLASS_NAMES
    )


def curate(raw: List[dict], seed: int = 42, test_fraction: float = 0.25) -> dict:
    """Validate, dedupe by text, and split into disjoint train/test sets."""
    valid = [r for r in raw if is_valid(r)]
    seen, deduped = set(), []
    for r in valid:
        if r["text"] not in seen:
            seen.add(r["text"])
            deduped.append({"text": r["text"], "label": r["label"]})

    rng = random.Random(seed)
    rng.shuffle(deduped)
    n_test = max(1, int(len(deduped) * test_fraction))
    test, train = deduped[:n_test], deduped[n_test:]

    train_texts = {r["text"] for r in train}
    disjoint = all(r["text"] not in train_texts for r in test)

    return {
        "train": train,
        "test": test,
        "n_raw": len(raw),
        "n_valid": len(valid),
        "n_deduped": len(deduped),
        "dupes_removed": len(valid) - len(deduped),
        "disjoint": disjoint,
    }
