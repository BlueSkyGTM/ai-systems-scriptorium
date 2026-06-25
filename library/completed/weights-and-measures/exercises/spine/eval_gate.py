"""eval_gate.py - Weights and Measures M5 throughline: deterministic eval gate.

Computes four task-level metrics on a set of (prediction, reference) pairs and
gates checkpoint promotion by comparing a tuned model's aggregate score against
a baseline's. Pure stdlib + math: no torch, no sklearn, no API keys required.

Usage:
    python eval_gate.py --selftest    # run built-in good/bad cases (exit 0 = OK)
    python eval_gate.py --demo        # fake tuned vs base comparison with a report

Metrics:
    exact_match : 0/1 after normalisation (case, whitespace, trailing punctuation)
    token_f1    : bag-of-tokens harmonic mean (SQuAD evaluation reference)
    mock_judge  : deterministic 1-5 score based on F1 thresholds, divided by 5
    perplexity  : exp(total_nll / total_tokens); normalised to [0, 1] via 1/(1+log(ppl))

Aggregate: weighted mean (default weights ppl=0.2, em=0.3, f1=0.3, judge=0.2).
Gate: mean_aggregate(tuned) >= mean_aggregate(base) - margin -> PASS; else BLOCK.
"""
from __future__ import annotations

import argparse
import math
import re
import string
import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Lowercase, strip whitespace, collapse internal whitespace, strip trailing punct."""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.rstrip(string.punctuation)
    return text


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def exact_match(pred: str, ref: str) -> float:
    """Return 1.0 if normalized pred equals normalized ref, else 0.0."""
    return 1.0 if normalize(pred) == normalize(ref) else 0.0


def token_f1(pred: str, ref: str) -> float:
    """Bag-of-tokens F1 (SQuAD evaluation reference).

    Both empty: 1.0 (vacuous match).
    One empty: 0.0.
    Otherwise: harmonic mean of token-level precision and recall.
    """
    pred_tokens = normalize(pred).split()
    ref_tokens = normalize(ref).split()

    if not pred_tokens and not ref_tokens:
        return 1.0
    if not pred_tokens or not ref_tokens:
        return 0.0

    pred_counts = Counter(pred_tokens)
    ref_counts = Counter(ref_tokens)
    intersection = sum((pred_counts & ref_counts).values())

    precision = intersection / len(pred_tokens)
    recall = intersection / len(ref_tokens)
    if precision + recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def mock_judge(pred: str, ref: str) -> float:
    """Deterministic 1-5 judge score based on F1 thresholds, normalised to [0, 1].

    Rubric:
        5 (1.0)  if normalized pred == normalized ref
        4 (0.8)  if token F1 >= 0.8
        3 (0.6)  if token F1 >= 0.5
        2 (0.4)  if token F1 >= 0.2
        1 (0.2)  otherwise
    """
    if normalize(pred) == normalize(ref):
        return 1.0
    f1 = token_f1(pred, ref)
    if f1 >= 0.8:
        return 0.8
    if f1 >= 0.5:
        return 0.6
    if f1 >= 0.2:
        return 0.4
    return 0.2


def perplexity_from_nll(neg_log_probs: list[float], token_counts: list[int]) -> float:
    """Compute perplexity from per-example negative log-probability sums.

    Args:
        neg_log_probs: total NLL per example (must be non-negative)
        token_counts:  token count per example (must be positive)

    Returns:
        exp(total_nll / total_tokens), or float('nan') if inputs are empty.
    """
    if not neg_log_probs or not token_counts:
        return float('nan')
    assert all(n >= 0 for n in neg_log_probs), "neg_log_probs must be non-negative"
    assert all(t > 0 for t in token_counts), "token_counts must be positive"
    total_nll = sum(neg_log_probs)
    total_tokens = sum(token_counts)
    if total_tokens == 0:
        return float('nan')
    return math.exp(total_nll / total_tokens)


def normalise_perplexity(ppl: float) -> float:
    """Map perplexity to [0, 1] via 1 / (1 + log(ppl)).

    ppl = 1  -> 1.0  (perfect)
    ppl = e  -> 0.5
    ppl -> inf -> 0.0
    """
    if math.isnan(ppl) or ppl <= 0:
        return 0.0
    return 1.0 / (1.0 + math.log(ppl))


def aggregate_scores(
    em: float,
    f1: float,
    ppl_norm: float,
    judge_norm: float,
    weights: tuple[float, float, float, float] = (0.2, 0.3, 0.3, 0.2),
) -> float:
    """Weighted aggregate of four normalised metrics.

    Default weights: (ppl_weight, em_weight, f1_weight, judge_weight) = (0.2, 0.3, 0.3, 0.2).
    All inputs and weights must be in [0, 1].
    """
    w_ppl, w_em, w_f1, w_judge = weights
    return w_ppl * ppl_norm + w_em * em + w_f1 * f1 + w_judge * judge_norm


# ---------------------------------------------------------------------------
# EvalResult dataclass
# ---------------------------------------------------------------------------

@dataclass
class EvalResult:
    """Per-example evaluation result."""
    pred: str
    ref: str
    em: float = field(init=False)
    f1: float = field(init=False)
    judge: float = field(init=False)
    ppl: float = float('nan')
    ppl_norm: float = float('nan')
    aggregate: float = float('nan')

    def __post_init__(self) -> None:
        self.em = exact_match(self.pred, self.ref)
        self.f1 = token_f1(self.pred, self.ref)
        self.judge = mock_judge(self.pred, self.ref)

    def compute_aggregate(
        self, weights: tuple[float, float, float, float] = (0.2, 0.3, 0.3, 0.2)
    ) -> None:
        ppl_n = self.ppl_norm if not math.isnan(self.ppl_norm) else 0.0
        self.aggregate = aggregate_scores(self.em, self.f1, ppl_n, self.judge, weights)


# ---------------------------------------------------------------------------
# run_eval and mean_aggregate
# ---------------------------------------------------------------------------

def run_eval(
    pairs: list[tuple[str, str]],
    neg_log_probs: Optional[list[float]] = None,
    token_counts: Optional[list[int]] = None,
) -> list[EvalResult]:
    """Evaluate a list of (pred, ref) pairs.

    If neg_log_probs and token_counts are provided (one per pair), perplexity is
    computed per example. Otherwise ppl fields remain NaN.
    """
    results = [EvalResult(pred=p, ref=r) for p, r in pairs]

    if neg_log_probs is not None and token_counts is not None:
        assert len(neg_log_probs) == len(pairs)
        assert len(token_counts) == len(pairs)
        for res, nll, tc in zip(results, neg_log_probs, token_counts):
            res.ppl = perplexity_from_nll([nll], [tc])
            res.ppl_norm = normalise_perplexity(res.ppl)

    for res in results:
        res.compute_aggregate()

    return results


def mean_aggregate(results: list[EvalResult]) -> float:
    """Mean aggregate score across all results (NaN-safe)."""
    valid = [r.aggregate for r in results if not math.isnan(r.aggregate)]
    return sum(valid) / len(valid) if valid else float('nan')


# ---------------------------------------------------------------------------
# eval_gate: the gate function
# ---------------------------------------------------------------------------

def eval_gate(
    tuned_results: list[EvalResult],
    base_results: list[EvalResult],
    margin: float = 0.01,
) -> bool:
    """Gate checkpoint promotion.

    Returns True (PASS) if mean aggregate of tuned >= mean aggregate of base - margin.
    Returns False (BLOCK) otherwise.
    """
    tuned_score = mean_aggregate(tuned_results)
    base_score = mean_aggregate(base_results)
    return tuned_score >= base_score - margin


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def _check(label: str, condition: bool) -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def selftest() -> int:
    print("eval_gate.py --selftest")
    ok = True

    # normalize
    ok &= _check("normalize: lowercase + strip", normalize("Hello World") == "hello world")
    ok &= _check("normalize: trailing punct stripped", normalize("hello!") == "hello")
    ok &= _check("normalize: internal whitespace collapsed", normalize("a  b   c") == "a b c")
    ok &= _check("normalize: punctuation mid-string preserved", normalize("U.S.A") == "u.s.a")

    print()

    # exact_match
    ok &= _check("exact_match: identical strings", exact_match("Hello", "Hello") == 1.0)
    ok &= _check("exact_match: case-insensitive", exact_match("hello", "HELLO") == 1.0)
    ok &= _check("exact_match: trailing punct ignored", exact_match("hello.", "hello") == 1.0)
    ok &= _check("exact_match: different strings", exact_match("foo", "bar") == 0.0)

    print()

    # token_f1
    ok &= _check("token_f1: perfect match", abs(token_f1("the cat", "the cat") - 1.0) < 1e-9)
    ok &= _check("token_f1: partial overlap", token_f1("the cat sat", "the cat") > 0.0)
    ok &= _check("token_f1: no overlap", token_f1("foo bar", "baz qux") == 0.0)
    ok &= _check("token_f1: both empty", token_f1("", "") == 1.0)
    ok &= _check("token_f1: pred empty", token_f1("", "hello") == 0.0)
    ok &= _check("token_f1: ref empty", token_f1("hello", "") == 0.0)
    # "the cat sat" vs "the cat": intersection={"the","cat"}=2, pred_len=3, ref_len=2
    # P=2/3, R=2/2=1.0, F1=2*(2/3)/(2/3+1)=4/3/(5/3)=4/5=0.8
    ok &= _check("token_f1: known value 0.8", abs(token_f1("the cat sat", "the cat") - 0.8) < 1e-9)

    print()

    # mock_judge
    ok &= _check("mock_judge: exact match -> 1.0", mock_judge("hello", "hello") == 1.0)
    ok &= _check("mock_judge: case match -> 1.0", mock_judge("HELLO", "hello") == 1.0)
    ok &= _check("mock_judge: high F1 -> 0.8", mock_judge("the cat sat", "the cat") == 0.8)
    ok &= _check("mock_judge: zero overlap -> 0.2", mock_judge("foo", "bar") == 0.2)

    print()

    # perplexity_from_nll
    ppl_zero = perplexity_from_nll([0.0], [1])
    ok &= _check("perplexity_from_nll: nll=0 -> 1.0", abs(ppl_zero - 1.0) < 1e-9)
    ppl_one = perplexity_from_nll([1.0], [1])
    ok &= _check("perplexity_from_nll: nll=1 -> e", abs(ppl_one - math.e) < 1e-9)
    ok &= _check("perplexity_from_nll: empty -> nan", math.isnan(perplexity_from_nll([], [])))

    # normalise_perplexity
    ok &= _check("normalise_perplexity: ppl=1.0 -> 1.0", abs(normalise_perplexity(1.0) - 1.0) < 1e-9)
    ok &= _check(
        "normalise_perplexity: ppl=e -> 0.5",
        abs(normalise_perplexity(math.e) - 0.5) < 1e-9
    )
    ok &= _check("normalise_perplexity: nan -> 0.0", normalise_perplexity(float('nan')) == 0.0)

    print()

    # aggregate_scores
    agg = aggregate_scores(1.0, 1.0, 1.0, 1.0)
    ok &= _check("aggregate_scores: all-1 -> 1.0", abs(agg - 1.0) < 1e-9)
    agg_zero = aggregate_scores(0.0, 0.0, 0.0, 0.0)
    ok &= _check("aggregate_scores: all-0 -> 0.0", abs(agg_zero) < 1e-9)

    print()

    # eval_gate
    tuned = run_eval([("exact match", "exact match"), ("cat sat", "cat sat on mat")])
    base = run_eval([("wrong answer", "exact match"), ("nothing here", "cat sat on mat")])
    ok &= _check("eval_gate: tuned > base -> PASS", eval_gate(tuned, base) is True)
    ok &= _check("eval_gate: base > tuned -> BLOCK", eval_gate(base, tuned, margin=0.0) is False)

    print()
    result = "OK" if ok else "BROKEN"
    print(f"selftest: {result}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo(margin: float = 0.01) -> int:
    print("eval_gate.py --demo")
    print()

    pairs_tuned = [
        ("The capital of France is Paris.", "The capital of France is Paris."),
        ("PyTorch uses dynamic computation graphs.", "PyTorch uses dynamic computation graphs."),
        ("The model was trained on GPU hardware.", "The model was trained on a GPU."),
        ("Adapters freeze the base model weights.", "LoRA adapters freeze the base model."),
        ("The loss curve shows overfitting.", "Nothing useful here."),
    ]
    # Tuned model: lower NLL (better perplexity) on first 4, slightly higher on last
    nlls_tuned = [0.5, 0.6, 0.8, 0.9, 2.5]
    tcs_tuned = [10, 8, 9, 8, 6]

    pairs_base = [
        ("The capital of France is Paris.", "The capital of France is Paris."),
        ("PyTorch uses dynamic graphs.", "PyTorch uses dynamic computation graphs."),
        ("It was trained somewhere.", "The model was trained on a GPU."),
        ("Freezing helps training.", "LoRA adapters freeze the base model."),
        ("The loss curve shows overfitting.", "Nothing useful here."),
    ]
    nlls_base = [0.6, 1.0, 1.4, 1.2, 2.5]
    tcs_base = [10, 8, 9, 8, 6]

    tuned = run_eval(pairs_tuned, nlls_tuned, tcs_tuned)
    base = run_eval(pairs_base, nlls_base, tcs_base)

    print(f"{'#':>2}  {'EM':>4}  {'F1':>5}  {'Judge':>6}  {'PPL':>6}  {'Agg(T)':>7}  {'Agg(B)':>7}")
    print(f"{'--':>2}  {'----':>4}  {'-----':>5}  {'------':>6}  {'------':>6}  {'-------':>7}  {'-------':>7}")
    for i, (t, b) in enumerate(zip(tuned, base), start=1):
        ppl_str = f"{t.ppl:.2f}" if not math.isnan(t.ppl) else " nan"
        print(
            f"{i:>2}  {t.em:>4.1f}  {t.f1:>5.3f}  {t.judge:>6.3f}  {ppl_str:>6}  "
            f"{t.aggregate:>7.4f}  {b.aggregate:>7.4f}"
        )

    tuned_mean = mean_aggregate(tuned)
    base_mean = mean_aggregate(base)
    passed = eval_gate(tuned, base, margin=margin)

    print()
    print(f"tuned mean aggregate : {tuned_mean:.4f}")
    print(f"base  mean aggregate : {base_mean:.4f}")
    print(f"margin               : {margin}")
    print(f"gate result          : {'PASS -- promote checkpoint' if passed else 'BLOCK -- reject checkpoint'}")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Eval gate for Weights and Measures M5.")
    ap.add_argument("--selftest", action="store_true", help="run built-in good/bad cases")
    ap.add_argument("--demo", action="store_true", help="run demo comparison")
    ap.add_argument("--margin", type=float, default=0.01, help="gate margin (default: 0.01)")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.demo:
        return demo(margin=args.margin)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
