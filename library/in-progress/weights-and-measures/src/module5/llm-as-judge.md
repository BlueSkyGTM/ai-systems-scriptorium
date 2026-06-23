# LLM-as-Judge

Exact match and token F1 measure lexical overlap. Perplexity measures distribution fit.
None of them asks whether the output is actually useful, relevant, or correct in the way
a human would judge it. LLM-as-judge fills that gap: a second model reads the prediction
and reference, evaluates along defined criteria, and returns a score.

The problem with LLM-as-judge is that it requires an API call, costs money, and produces
stochastic results. The solution in this book is to start with a mock judge: a deterministic
function that approximates judge scores using the metrics you already have. The mock judge
runs for free in any environment. The real judge pattern is shown as a reference so you can
read production eval code that uses it.

## The Four Criteria

A useful judge rubric covers four dimensions:

- **Relevance**: does the output address the question or task?
- **Correctness**: are the claims in the output factually accurate?
- **Helpfulness**: does the output give the reader what they need?
- **Safety**: does the output avoid harmful content?

Each criterion is scored 1 to 5. Anchored descriptions reduce judge variance: instead of
leaving the model to interpret what "4" means, each score has a specific behavioral
description.

For correctness, an anchored rubric looks like this:

| Score | Description |
|---|---|
| 5 | All claims are factually accurate and verifiable |
| 4 | Mostly correct with one minor inaccuracy that does not affect the main point |
| 3 | Contains a notable inaccuracy but the core message is correct |
| 2 | Contains significant factual errors that undermine the response |
| 1 | Fundamentally incorrect or contains dangerous misinformation |

Anchored rubric descriptions reduce variance by 30 to 40 percent compared to unanchored
scales. The investment in writing them pays off in reproducibility.

## The Mock Judge

The mock judge is `eval_gate.py`'s `mock_judge` function. It uses token F1 thresholds to
assign a deterministic score without any API call.

```python
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
```

The mock judge returns the score divided by 5, so it is already normalised to [0, 1].
An exact normalized match scores 1.0 (5/5). High overlap scores 0.8 (4/5). No overlap
scores 0.2 (1/5).

The mock judge is a reasonable approximation when:

- You need a quick sanity check and cannot wait for API calls
- You are testing the eval pipeline itself and want deterministic results
- The task has clear reference answers with significant lexical overlap expected

The mock judge is a poor proxy when:

- The task rewards paraphrase (the model can be correct with different words)
- Safety or factuality need to be evaluated against world knowledge the reference lacks
- The judge's qualitative criteria matter more than lexical overlap

## The Real Judge Pattern

The real judge pattern is shown here as a reference. It requires an API key and incurs
cost; it is not run in this book's spine.

```python
# REFERENCE ONLY: requires an LLM API key; not run in this book.
# This is the pattern eval_gate.py's mock_judge approximates for free.

CORRECTNESS_RUBRIC = {
    5: "All claims are factually accurate and verifiable",
    4: "Mostly correct with one minor inaccuracy that does not affect the main point",
    3: "Contains a notable inaccuracy but the core message is correct",
    2: "Contains significant factual errors that undermine the response",
    1: "Fundamentally incorrect or contains dangerous misinformation",
}

def real_judge(pred: str, ref: str, criterion: str = "correctness") -> float:
    # Build a prompt that includes the rubric, the prediction, and the reference.
    # Call the judge model (e.g., GPT-5-mini, Claude Haiku, Gemini Flash).
    # Parse the integer score 1-5 from the response.
    # Return score / 5 to normalise to [0, 1].
    ...
```

The model selected for judging affects both cost and correlation with human judgment.
Approximate 2026 benchmarks per 1,000 calls on a 100-example eval run (4 criteria each):

| Model | Cost / 1K calls | Correlation with human |
|---|---|---|
| GPT-5 mini | ~$8 | 82-86% |
| Claude Opus | ~$25 | 85-88% |
| Gemini Flash | ~$3 | 80-84% |

For a weekly CI run of 10 pull requests at 200 examples each, GPT-5-mini costs roughly
$160 per month. Budget for it before wiring the real judge into CI.

## Behavioral Testing

The `made-with-ml` `test_behavioral.py` introduces a three-category framework for
testing model behavior beyond aggregate metrics:

- **MFT (Minimum Functionality Tests)**: simple input-output pairs that should always
  pass. If the model cannot get these right, something is fundamentally wrong.
- **INVariance tests**: input changes that should not affect the output. A paraphrase
  of the question should produce the same answer. Verb substitutions should not shift
  the classification.
- **DIRectional tests**: input changes that should produce a specific known output change.
  Adding "Transformer" to an NLP-related description should push the classifier toward
  the NLP label, not away from it.

These three categories make behavioral regression tests concrete. Rather than asking
"did accuracy go up", you ask "did it stop getting the easy cases right" (MFT), "did
it become sensitive to paraphrase" (INVariance), and "did its directional responses
change" (DIRectional). M7 builds a behavioral regression suite using this framework.

## Core Concepts

- LLM-as-judge evaluates qualitative dimensions (relevance, correctness, helpfulness,
  safety) on a 1-5 scale; dividing by 5 normalises the score to [0, 1].
- Anchored rubric descriptions reduce judge score variance by 30 to 40 percent; the
  investment in writing per-score behavioral descriptions pays off in reproducibility.
- The mock judge in `eval_gate.py` approximates judge scores using token F1 thresholds,
  deterministically, at zero cost: exact match scores 5, F1 >= 0.8 scores 4, down to
  F1 < 0.2 scores 1.
- The real judge requires an API call and incurs cost: at 100 examples across 4 criteria,
  GPT-5-mini costs roughly $2; 10 weekly CI runs costs roughly $160/month.
- Behavioral tests (MFT, INVariance, DIRectional) complement aggregate metrics by
  testing specific behavioral properties rather than overall performance.

<div class="claude-handoff" data-exercise="exercises/module5/llm-as-judge/">

**Build It in Claude Code**: Import `mock_judge` from `exercises/spine/eval_gate.py`.
Write ten (prediction, reference) pairs that span the five score levels: at least two
pairs that should score 1.0 (exact match), two that should score 0.8 (high overlap),
two at 0.6 (moderate overlap), two at 0.4 (low overlap), and two at 0.2 (no overlap).
Assert each pair's `mock_judge` output matches the expected score. Then write a function
`classify_by_criteria(pred, ref)` that returns a dict with keys `relevance`, `correctness`,
`helpfulness`, each mapping to the mock judge score (since the mock does not distinguish
criteria, all three will be the same value). Print the results for all ten pairs as a
table. This is the rubric-as-code discipline applied to qualitative eval.

</div>
