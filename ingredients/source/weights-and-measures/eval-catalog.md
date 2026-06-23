# Eval Catalog — Weights and Measures M5 Reference Ingredient

Distilled 2026-06-22 (Haiku fetch tier) from `aefs` Phase 19 capstone lessons 36/41/49/73/75,
`aefs` Phase 11 lesson 10, `mwml` evaluate.py + test_behavioral.py, Azure ML eval docs,
MLflow Python API docs.

**Grounding rule:** the reader builds a deterministic `eval_gate.py` in pure stdlib+torch (no
mlflow, no sklearn, no API keys). MLflow and LLM-as-judge with a real model are shown as
REFERENCE ONLY — the production patterns the from-scratch version demystifies.

## Doc anchors

| Topic | URL | Facts |
|---|---|---|
| Azure OpenAI eval | https://learn.microsoft.com/azure/ai-foundry/openai/how-to/evaluations | Graders: Semantic Similarity, Factuality, String Check, BLEU, ROUGE, Cosine Similarity, Custom Prompt; `results.csv` columns: step, train_loss, train_mean_token_accuracy, valid_loss, validation_mean_token_accuracy. |
| Azure ML metrics | https://learn.microsoft.com/azure/ai-services/language-service/custom-text-classification/concepts/evaluation-metrics | P/R/F1 formulas; class-level breakdown. |
| MLflow API | https://learn.microsoft.com/azure/machine-learning/how-to-log-view-metrics?view=azureml-api-2 | `mlflow.start_run`, `mlflow.log_metric(key, value, step)`, `mlflow.log_metrics(dict)`, `mlflow.log_param`, `mlflow.log_artifact`, `mlflow.end_run`; async logging via `mlflow.config.enable_async_logging()`. |
| MLflow tracking | https://learn.microsoft.com/azure/machine-learning/how-to-use-mlflow-configure-tracking?view=azureml-api-2 | `mlflow.set_tracking_uri(...)`, `mlflow.set_experiment(name)`. |
| Azure fine-tune safety | https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning-safety-evaluation | Automatic safety eval after training; blocks deployment on harmful content. |

## L1 — `loss-is-not-enough`

- Loss measures "how surprised is the model" — it captures the training objective, not the task.
  A model can reach low training loss by predicting the next token well on training data while
  failing to answer the question or produce the right label.
- Four dimensions loss misses: (1) correct label on a classification head (accuracy/F1);
  (2) exact string match on extractive QA (EM); (3) whether the distribution over the held-out
  corpus is well-fit (perplexity); (4) qualitative correctness judged by a second model (LLM-judge).
- A loop that prints only loss "lies three ways: it cannot tell you if loss is decreasing for
  the right reason, if a divergence is starting, or what the model has learned." (aefs L36)
- "Training is the part you can monitor with loss curves. Evaluation is the part you have to design." (aefs L41)
- The eval gate is the answer: a script that computes task-specific metrics and gates checkpoint
  promotion with an exit code.

## L2 — `task-metrics`

### Exact Match (EM)
- Normalise both prediction and reference: lowercase, strip whitespace, collapse internal
  whitespace to single space, drop trailing punctuation if both sides differ only by it.
- Binary 0/1 after normalisation. Already in [0, 1].
- `em_score = int(normalize(pred) == normalize(ref))`

### Token F1 (Bag-of-Tokens)
- Normalise, split by whitespace, count multiset intersection.
- `precision = intersection / len(pred_tokens)`
- `recall = intersection / len(ref_tokens)`
- `f1 = 2*P*R/(P+R)` (both empty = 1.0; one empty = 0.0)
- Already in [0, 1]. Matches SQuAD evaluation reference.

### Perplexity
- `PPL = exp(total_nll / total_tokens)` where `total_nll = sum(-log p(token_i))` and
  `total_tokens` counts actual (non-padding) tokens.
- Off-by-one trap: logits at position i predict token at position i+1.
- Normalise to [0,1] for aggregation: `1 / (1 + log(PPL))` maps PPL=1 → 1.0, PPL→∞ → 0.
- Strong 2026 base model on WikiText-103: PPL 8–12.
- Zero-token edge case: return NaN; runner decides.

### Weighted Aggregate
- Default weights: 0.2 perplexity (normalised), 0.3 EM, 0.3 token F1, 0.2 judge (normalised).
- `aggregate = sum(w_i * normalised_score_i)`

### Classifier-specific (reference for M6)
- Accuracy = (TP+TN)/N; Precision = TP/(TP+FP); Recall = TP/(TP+FN);
  F1 = 2*P*R/(P+R). Weighted average over classes for multi-class.
- from sklearn.metrics: `precision_recall_fscore_support(y_true, y_pred, average="weighted")`
  (REFERENCE — sklearn not in book's spine; spine recomputes from counts)

## L3 — `llm-as-judge`

- Four criteria: Relevance, Correctness, Helpfulness, Safety (each 1–5).
- Anchored rubric descriptions reduce judge variance by 30–40% vs unanchored scales.
- Mock judge (deterministic fallback — no API key required):
  - 5 if normalized pred == normalized ref
  - 4 if token F1 >= 0.8
  - 3 if token F1 in [0.5, 0.8)
  - 2 if token F1 in [0.2, 0.5)
  - 1 otherwise
- Real judge (REFERENCE ONLY — requires API key):
  - GPT-5 mini: ~$8/1K calls, 82–86% correlation with human judges
  - Claude Opus: ~$25/1K calls, 85–88% correlation
  - Gemini 3 Flash: ~$3/1K calls, 80–84% correlation
- For aggregation: divide judge score by 5 → [0, 1].
- Cost math: 100 examples × 4 criteria × GPT-5-mini = ~$2; 200 examples ≈ $4.
- "You would never deploy a web app without tests... right now, most teams ship LLM applications
  by reading 10 outputs and saying 'yeah, looks good.' That is not evaluation. That is hope." (aefs L10)

## L4 — `building-the-eval-gate` (capstone)

- The gate: run eval on tuned model AND baseline on the same held-out set; compare aggregate
  scores; exit 0 if tuned >= baseline − margin (e.g. 0.01), else exit 1 (block).
- The exit code IS the gate: any script that calls eval_gate.py can check `$?` (shell) or
  returncode (subprocess) and promote or reject the checkpoint.
- MLflow logging pattern (REFERENCE ONLY — not run in this book):
  ```python
  # REFERENCE ONLY: mlflow required; not run in this book.
  import mlflow
  mlflow.set_experiment("eval-gate")
  with mlflow.start_run(run_name="m5-tuned-vs-base"):
      mlflow.log_metrics({"tuned_f1": ..., "baseline_f1": ..., "gate_status": ...})
      mlflow.log_artifact("eval_report.json")
  ```
- Behavioral test framework (from mwml test_behavioral.py):
  - MFT (Minimum Functionality Tests): simple in/out pairs that must pass
  - INVariance: paraphrase/verb swap should not change label
  - DIRectional: known input changes should produce known output changes

## Throughline (the spine-engineer builds + verifies; pure stdlib+torch, CPU, no downloads)

- `exercises/spine/eval_gate.py` — the M5 spine artifact. Contains:
  - `normalize(text) -> str`: lowercase, strip, collapse whitespace, strip trailing punctuation
  - `exact_match(pred, ref) -> float`: 0.0 or 1.0 after normalize
  - `token_f1(pred, ref) -> float`: bag-of-tokens harmonic mean; edge cases handled
  - `mock_judge(pred, ref) -> float`: deterministic 1–5 score (by F1 thresholds), divide by 5
  - `perplexity_from_nll(neg_log_probs: list[float], token_counts: list[int]) -> float`: `exp(sum(nll)/sum(tokens))`
  - `normalise_perplexity(ppl: float) -> float`: `1 / (1 + math.log(ppl))`
  - `aggregate_scores(em, f1, ppl_norm, judge_norm, weights=(0.2,0.3,0.3,0.2)) -> float`
  - `EvalResult` dataclass: `em, f1, ppl, ppl_norm, judge, aggregate`
  - `eval_gate(tuned_results: list[EvalResult], base_results: list[EvalResult], margin=0.01) -> bool`: returns True=PASS (promote), False=BLOCK
  - `__main__`: --selftest (GOOD + BAD cases for each metric) + --demo (fake tuned vs base comparison, prints report)
  - CLI: `--selftest`, `--demo`, optional `--margin FLOAT`
- `eval_gate.py --selftest` must exit 0 (all metric functions pass their cases)
