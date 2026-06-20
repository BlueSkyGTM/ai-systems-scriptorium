# Exercise: Experiment Tracking & the LLMOps Outer Loop

## Goal

Wrap the `module5-serving/` eval step in MLflow tracking against a local file store: run three configurations, log each as a run with its params, metrics, and prompt artifact, then compare them in the MLflow UI to pick a winner by metric — no server, no cloud.

## Why

Module 2's inner eval loop is amnesiac; experiment tracking is the durable ledger that turns "which change cost us the points?" from a memory test into a query.

## Steps

1. In `module5-serving/`, create an `experiments/` package. Add `mlflow` to dependencies (`pip install mlflow`).
2. Build a tiny eval harness `experiments/eval.py` with `run_eval(config) -> dict[str, float]`:
   - `config` is a dict: `{"prompt_version", "retriever_k", "reranker"}` (reuse the `TinyIndex` from the lesson 11 exercise if you built it; otherwise a stub retriever over a few canned docs is fine — the point is the tracking, not the retrieval).
   - Score a small fixed question set with a simple rubric metric (e.g. a keyword-overlap or canned LLM-as-judge stub returning a faithfulness-like float) plus measured `latency_ms` and a simulated `cost_per_query_usd`. Keep it deterministic so reruns are comparable.
3. Implement `experiments/track.py` that, for each of three configs, opens an MLflow run and logs it:
   - `mlflow.start_run(run_name=...)`, then `mlflow.log_param(...)` for every config field.
   - `mlflow.log_metric(...)` for each returned metric.
   - `mlflow.log_artifact(...)` for the prompt text file that config used.
   - Let MLflow default to the local `./mlruns` file store — do **not** start a server.
4. Choose three genuinely different configs (e.g. prompt v1 vs v2 vs v3, or reranker on/off, or `k=3` vs `k=8`) so the comparison has something to show.
5. Run `mlflow ui` and open the browser view. Sort the three runs by the quality metric; read off the cost and latency trade-off for the winner.
6. Write `experiments/DECISION.md`: name the winning config, the metric it won on, and the trade-off you accepted (what it cost in latency or dollars). One short paragraph — this is the durable record the lesson argues for.

## Done when

- Running `python -m experiments.track` creates three MLflow runs under `./mlruns` with no server and no cloud.
- Each run has its params, metrics, and a prompt artifact attached (verify in the UI or via `mlflow.get_run`).
- `mlflow ui` shows the three runs side by side, sortable by the quality metric.
- `experiments/DECISION.md` names the winner and the trade-off, citing the logged numbers.

## Stretch

Add a `register_winner()` step: register the winning config's "model" (here, the prompt+retriever bundle as an artifact) under a named entry in the MLflow Model Registry, give it a version, and mark it as the production alias — the digest-pinned thing a rollout gateway would point its routing flag at.
