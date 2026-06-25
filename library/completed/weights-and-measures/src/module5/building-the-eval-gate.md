# Building the Eval Gate

The three preceding lessons defined four metrics: exact match, token F1, perplexity, and
mock judge. This lesson wires them into a single gate script. The gate takes a tuned model
and a baseline, runs both on the same held-out set, computes a weighted aggregate for each,
and exits 0 if the tuned model meets or beats the baseline minus a margin. It exits 1
otherwise. The exit code is the deliverable.

## The Aggregate

Each metric is normalised to [0, 1]:

- Exact match: already in {0, 1}
- Token F1: already in [0, 1]
- Perplexity: `1 / (1 + log(ppl))` maps [1, inf) to (0, 1]
- Mock judge: divides by 5, already in [0.2, 1.0]

The aggregate is a weighted mean with default weights 0.2/0.3/0.3/0.2 for
perplexity/EM/F1/judge:

```python
def aggregate_scores(
    em: float,
    f1: float,
    ppl_norm: float,
    judge_norm: float,
    weights: tuple[float, float, float, float] = (0.2, 0.3, 0.3, 0.2),
) -> float:
    w_ppl, w_em, w_f1, w_judge = weights
    return w_ppl * ppl_norm + w_em * em + w_f1 * f1 + w_judge * judge_norm
```

The weights reflect what the task values. EM and F1 each receive 0.3 because string
correctness is the primary signal for most QA tasks. Perplexity and judge each receive 0.2
because they add diagnostic value but are noisier. Change the weights when the task changes:
a summarization task might down-weight EM and up-weight judge; a language-modeling task
might up-weight perplexity.

## EvalResult and run_eval

`EvalResult` computes all four metrics on construction and holds them alongside the raw
prediction and reference:

```python
@dataclass
class EvalResult:
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

    def compute_aggregate(self, weights=(0.2, 0.3, 0.3, 0.2)) -> None:
        ppl_n = self.ppl_norm if not math.isnan(self.ppl_norm) else 0.0
        self.aggregate = aggregate_scores(self.em, self.f1, ppl_n, self.judge, weights)
```

`ppl` and `ppl_norm` are not set in `__post_init__` because perplexity requires
negative log-probabilities from the model, which are not available from the text strings
alone. The caller sets them separately and then calls `compute_aggregate`.

`run_eval` evaluates a list of (pred, ref) pairs and optionally attaches perplexity:

```python
def run_eval(
    pairs: list[tuple[str, str]],
    neg_log_probs: list[float] | None = None,
    token_counts: list[int] | None = None,
) -> list[EvalResult]:
    results = [EvalResult(pred=p, ref=r) for p, r in pairs]
    if neg_log_probs is not None and token_counts is not None:
        for res, nll, tc in zip(results, neg_log_probs, token_counts):
            res.ppl = perplexity_from_nll([nll], [tc])
            res.ppl_norm = normalise_perplexity(res.ppl)
    for res in results:
        res.compute_aggregate()
    return results
```

## The Gate

`eval_gate` compares the mean aggregate across two result lists:

```python
def eval_gate(
    tuned_results: list[EvalResult],
    base_results: list[EvalResult],
    margin: float = 0.01,
) -> bool:
    tuned_score = mean_aggregate(tuned_results)
    base_score = mean_aggregate(base_results)
    return tuned_score >= base_score - margin
```

The `margin` parameter is the allowed regression. A margin of 0.01 means the tuned model
is allowed to score up to 0.01 below the baseline before the gate blocks it. Setting
margin to 0.0 requires the tuned model to be strictly at least as good as the baseline.

The return value is `True` for PASS and `False` for BLOCK. The `--demo` output from
`eval_gate.py` shows the pattern:

```
tuned mean aggregate : 0.6697
base  mean aggregate : 0.4701
margin               : 0.01
gate result          : PASS -- promote checkpoint
```

The exit code is the gate: `sys.exit(0)` on PASS, `sys.exit(1)` on BLOCK. Any CI script,
Makefile, or shell pipeline that runs `python eval_gate.py --demo` can read `$?`.

## The Production Path: MLflow

In production, the eval run is logged before the gate decision is made. MLflow is the
standard tool for this. The pattern below is shown as a reference.

```python
# REFERENCE ONLY: mlflow required; not run in this book.
import mlflow

mlflow.set_experiment("eval-gate")
with mlflow.start_run(run_name="m5-tuned-vs-base"):
    mlflow.log_metrics({
        "tuned_em":         tuned_em,
        "tuned_f1":         tuned_f1,
        "tuned_ppl":        tuned_ppl,
        "tuned_judge":      tuned_judge,
        "tuned_aggregate":  tuned_agg,
        "base_aggregate":   base_agg,
    })
    mlflow.log_param("gate_margin", margin)
    mlflow.log_param("gate_status", "PASS" if passed else "BLOCK")
    mlflow.log_artifact("eval_report.json")
```

`mlflow.log_metrics` takes a dict of key-value pairs; `mlflow.log_artifact` stores a file
(the eval report JSON) alongside the run. The tracking URI points to a local MLflow server
or to Azure ML:

```python
# REFERENCE ONLY: Azure ML workspace URI format
mlflow.set_tracking_uri(
    "azureml://<region>.api.azureml.ms/mlflow/v1.0/subscriptions/<sub>/resourceGroups/"
    "<rg>/providers/Microsoft.MachineLearningServices/workspaces/<workspace>"
)
```

Grounding URL: https://learn.microsoft.com/azure/machine-learning/how-to-log-view-metrics

The from-scratch gate runs without MLflow. The MLflow reference is what you wire in after
the gate is proven to work on CPU.

## Running the Gate

```
python exercises/spine/eval_gate.py --selftest   # 28 cases, exit 0
python exercises/spine/eval_gate.py --demo        # fake tuned vs base, prints report
```

In a real pipeline the caller provides predictions and references from the actual models:

```python
from eval_gate import run_eval, eval_gate

tuned_pairs = [(model_tuned(x), ref) for x, ref in held_out_set]
base_pairs  = [(model_base(x), ref) for x, ref in held_out_set]

tuned_results = run_eval(tuned_pairs)
base_results  = run_eval(base_pairs)

passed = eval_gate(tuned_results, base_results, margin=0.01)
sys.exit(0 if passed else 1)
```

The held-out set is fixed. The gate is deterministic. The exit code is the decision.

## Core Concepts

- The aggregate is a weighted mean of four normalised metrics: perplexity (0.2), exact
  match (0.3), token F1 (0.3), judge (0.2). Weights are tunable per task; the defaults
  favor string correctness.
- `EvalResult` computes EM, F1, and judge on construction; perplexity is attached later
  by the caller because it requires model log-probabilities, not just strings.
- `eval_gate` compares mean aggregates: PASS if tuned >= base - margin, BLOCK otherwise.
  The margin allows a small regression before triggering a block.
- The exit code is the gate: 0 for PASS, 1 for BLOCK. Any upstream script can act on
  the return code without parsing output.
- MLflow logs the run before the gate decision: `log_metrics` for all four per-model
  scores, `log_param` for margin and gate status, `log_artifact` for the eval report.
  Not run in this book; wired in after the from-scratch gate works.

<div class="claude-handoff" data-exercise="exercises/module5/building-the-eval-gate/">

**Build It in Claude Code**: Import `run_eval`, `eval_gate`, `mean_aggregate`, and
`EvalResult` from `exercises/spine/eval_gate.py`. Create two sets of ten (pred, ref) pairs:
one set where predictions are high quality (tuned model), one where predictions are
low quality (baseline). Call `run_eval` on both sets. Print a per-example table showing EM,
F1, judge, and aggregate for each result. Call `eval_gate` with `margin=0.01` and print
whether it returns True (PASS) or False (BLOCK). Then repeat with the sets reversed (base
better than tuned) and confirm the gate returns False. Run `eval_gate.py --selftest` and
confirm it exits 0. The gate is correct when it promotes the better model and blocks the
worse one.

</div>
