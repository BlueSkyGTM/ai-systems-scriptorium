# Task Metrics

Three metrics cover the ground between "loss went down" and "the model answers correctly":
exact match for string correctness, token F1 for lexical overlap, and perplexity for
distribution fit on the held-out corpus. Each captures something the others miss. Each
normalizes to [0, 1] so they can be combined into a single aggregate.

All three are implemented in `exercises/spine/eval_gate.py`. The implementations below
are verbatim from that file.

## Exact Match

Exact match is a binary gate: the prediction either matches the reference or it does not.
Before comparing, both strings are normalized.

```python
def normalize(text: str) -> str:
    """Lowercase, strip whitespace, collapse internal whitespace, strip trailing punct."""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.rstrip(string.punctuation)
    return text

def exact_match(pred: str, ref: str) -> float:
    """Return 1.0 if normalized pred equals normalized ref, else 0.0."""
    return 1.0 if normalize(pred) == normalize(ref) else 0.0
```

Normalization removes the sources of false failure that do not reflect real errors:
case differences, leading and trailing whitespace, internal spacing, and trailing
punctuation. "Paris." and "paris" normalize to the same string and score 1.0. "Paris,
France" and "Paris" do not; the comma and "France" survive normalization.

The normalization order matters. Strip outer whitespace before collapsing internal; rstrip
punctuation after collapsing whitespace so you do not accidentally strip punctuation from
mid-string positions.

Exact match is best for extractive QA tasks where the reference is a span and the model
is expected to reproduce it exactly. It is too strict for open-ended generation: a
paraphrase that is semantically correct scores 0.

## Token F1

Token F1 gives partial credit for lexical overlap. It computes precision and recall at
the token level and returns their harmonic mean.

```python
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
```

The intersection uses a multiset intersection, not a set intersection. If the reference
contains "the" twice and the prediction contains "the" once, the intersection count is 1,
not 2. This matches the SQuAD evaluation reference implementation.

The edge cases matter:

- Both empty: 1.0. Two empty strings are an exact match for each other.
- Prediction empty, reference non-empty: 0.0. The model produced nothing; recall is 0.
- Reference empty, prediction non-empty: 0.0. There is no reference to match against.
- No token overlap: precision and recall are both 0; the harmonic mean guard returns 0.

Token F1 is the standard metric for extractive QA (SQuAD, TriviaQA) and is a useful
sanity check for any task where the answer is expected to share vocabulary with the
reference. It does not catch semantically correct paraphrases that use different words,
but it catches partial answers and approximate matches that exact match rejects.

## Perplexity

Perplexity measures how well the model's distribution fits the held-out text. Lower
perplexity means the model assigns higher probability to the tokens it sees.

```python
def perplexity_from_nll(neg_log_probs: list[float], token_counts: list[int]) -> float:
    """Compute perplexity from per-example negative log-probability sums.

    Returns exp(total_nll / total_tokens), or float('nan') if inputs are empty.
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
```

The formula is `exp(total_nll / total_tokens)` where `total_nll` is the sum of negative
log-probabilities across all tokens in the held-out set, and `total_tokens` is the count
of actual (non-padding) tokens.

Two implementation traps:

**Off-by-one.** When using an autoregressive model, the logits at position `i` predict
the token at position `i+1`. The NLL for position `i+1` comes from the logits at position
`i`. Misaligning these indices produces a systematically wrong perplexity.

**Padding tokens.** Padding tokens must be excluded from `total_tokens`. Including them
deflates perplexity by inflating the denominator with positions where the model was not
actually asked to predict anything meaningful.

The assertion `all(n >= 0 for n in neg_log_probs)` catches sign errors. If you computed
log-probabilities instead of negative log-probabilities and passed them in, the assertion
fails before the aggregate is corrupted.

## Normalizing Perplexity

Perplexity lives on the range [1, infinity). Before combining it with exact match and
token F1, it must be mapped to [0, 1]. The mapping `1 / (1 + log(ppl))` does this.

```python
def normalise_perplexity(ppl: float) -> float:
    """Map perplexity to [0, 1] via 1 / (1 + log(ppl)).

    ppl = 1  -> 1.0  (perfect)
    ppl = e  -> 0.5
    ppl -> inf -> 0.0
    """
    if math.isnan(ppl) or ppl <= 0:
        return 0.0
    return 1.0 / (1.0 + math.log(ppl))
```

A strong 2026 base model on WikiText-103 reaches perplexity in the 8 to 12 range.
`normalise_perplexity(10)` returns approximately 0.30. A perplexity of 1 (perfect
prediction) normalises to 1.0; a perplexity of `e` normalises to 0.5.

## What Each Metric Catches

| Metric | Catches | Misses |
|---|---|---|
| Exact match | Wrong strings, format errors, extra words | Correct paraphrases, partial answers |
| Token F1 | Partial answers, approximate matches | Correct paraphrases with different vocabulary |
| Perplexity | Distribution mismatch, overfitting to train | Label errors, output format issues |

No single metric tells the full story. The aggregate uses all three, along with a judge
score, to produce a single number that the gate can act on.

## Core Concepts

- Exact match normalises both strings (case, whitespace, trailing punctuation) before
  comparing; normalization order matters: strip outer whitespace before collapsing internal,
  strip trailing punctuation last.
- Token F1 computes a multiset intersection (not set): if the reference has "the" twice
  and the prediction has it once, the intersection count is 1. Both-empty scores 1.0;
  one-empty scores 0.0.
- Perplexity is `exp(total_nll / total_tokens)` over the held-out set; two traps are the
  off-by-one between logit position and target position, and padding tokens inflating the
  denominator if not excluded.
- Perplexity normalises to [0, 1] via `1 / (1 + log(ppl))`: ppl=1 maps to 1.0, ppl=e to
  0.5, ppl approaching infinity approaches 0.
- The three metrics cover complementary ground: exact match catches format failures, token
  F1 catches partial answers, perplexity catches distribution mismatch. None is sufficient
  alone.

<div class="claude-handoff" data-exercise="exercises/module5/task-metrics/">

**Build It in Claude Code**: Import `exact_match`, `token_f1`, `perplexity_from_nll`, and
`normalise_perplexity` from `exercises/spine/eval_gate.py`. Write a suite of at least ten
test cases for each metric: for exact match, include case-insensitive matches, trailing
punctuation differences, and multi-word strings; for token F1, include partial overlaps,
repeated tokens, and both-empty; for perplexity, compute it from known NLL values and
verify the formula manually. For each metric, assert the expected value within a tolerance
of 1e-9. Run your suite and confirm all assertions pass.

</div>
