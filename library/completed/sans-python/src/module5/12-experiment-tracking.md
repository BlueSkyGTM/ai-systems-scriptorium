# Experiment Tracking & the LLMOps Outer Loop

You changed the prompt, the eval score went up four points, you shipped it. Three weeks and forty changes later the score is down and nobody can say which change cost you the points, because the runs that produced those numbers live in scrollback and a teammate's notebook. Eval-driven development gave you a way to measure quality; without a place to record every measurement, that discipline evaporates the moment the session closes. Experiment tracking is the ledger that makes it durable.

## The Loop Module 2 Left Open

Module 2's evaluation lesson built the inner loop: error analysis, an LLM-as-judge scoring outputs against a rubric, statistical correction to tell a real improvement from noise, then a prompt or retrieval fix, then re-eval. That loop is correct and it is also amnesiac. It tells you whether *this* version beats the *last* version you happened to remember; it does not, on its own, retain the full history of what you tried, with which parameters, against which dataset, and what each attempt scored.

The fix is not a better judge. It is a system of record. Every eval run is an experiment, and an experiment has the same anatomy each time: the **parameters** that defined it (model, temperature, prompt version, chunking config, retriever settings), the **metrics** it produced (the judge's faithfulness and relevance scores, latency, cost), and the **artifacts** it generated (the prompt text, the eval dataset, the per-example scores). Capture that triple for every run and "which change cost us the points" stops being a memory test and becomes a query.

## MLflow: Runs, Params, Metrics, Artifacts

The default tool for that ledger is [MLflow](https://mlflow.org), an open-source platform whose Tracking component is an API and UI for logging parameters, metrics, and output files from a run and visualizing the results afterward. The vocabulary is small. A **run** is one execution of your code — one eval pass over one configuration. Inside it you log what mattered:

```python
import mlflow

with mlflow.start_run(run_name="rag-v3-rerank-on"):
    mlflow.log_param("model", "claude-haiku-4-5")
    mlflow.log_param("prompt_version", "v3")
    mlflow.log_param("reranker", True)
    mlflow.log_metric("faithfulness", 0.91)
    mlflow.log_metric("answer_relevance", 0.88)
    mlflow.log_metric("cost_per_query_usd", 0.0042)
    mlflow.log_artifact("prompts/system_v3.txt")
```

`log_param` records an input you set; `log_metric` records a number you measured; `log_artifact` stores a file the run produced. For framework training loops there is `mlflow.autolog()`, which captures params, metrics, and models automatically without explicit log calls — useful breadth to know about, though for eval runs the explicit calls keep you honest about what you are measuring.

The runs land somewhere. By default MLflow writes to a local `./mlruns` directory — a file store, no server, no cloud, the whole ledger on your laptop. You run `mlflow ui` and a browser view lets you list runs, sort by any metric, and compare configurations side by side. When the team needs a shared record, the same code points at a tracking server instead of the local directory, and nothing in your logging changes. Start local; graduate when collaboration demands it.

The comparison view is the payoff. The whole reason you logged params alongside metrics is so the UI can show you that v3-with-reranker scored 0.91 on faithfulness at 0.4 cents a query while v2 scored 0.87 at 0.3 cents — and now the trade-off is on the table as data, not as somebody's recollection.

## The Model Registry: from a Good Run to a Promotable Version

Tracking records what you tried. The **model registry** records what you decided to ship. It is a versioned catalog: a winning run's model gets registered under a name, accumulates numbered versions over time, and carries aliases that mark which version is the current production one. That registry is the same pinned-digest store the rollout lesson leaned on: the gateway flips a flag to send traffic to a model, and the registry is what that flag points at — a specific version, reproducible from its run, traceable back to the exact params and dataset that produced it.

That closes the arc this module has been drawing. The inner loop scores a change. The tracking ledger records the score with its full context. The registry promotes the winner to a named version. The gateway routes a canary to it. The canary's live judge scores feed back as new runs. Inner loop to outer loop, development to production, and every link is a recorded, comparable artifact rather than a thing someone remembers.

## Azure ML, and W&B as the Alternative

On Azure this is not a separate system to learn. Azure Machine Learning workspaces are MLflow-compatible: you use the same `mlflow.log_metric` and `mlflow.log_param` calls, and the runs, metrics, and artifacts land in the workspace with no cloud-specific syntax added to your training or eval code. The studio's Jobs and Metrics views give you the same compare-runs experience the local `mlflow ui` does, at team scale. The literacy transfers directly: learn the open tool locally, and the managed platform is the same API with a workspace behind it.

Weights & Biases (W&B) is the common commercial alternative, with the same primitives — runs, logged config and metrics, artifacts, and a hosted comparison dashboard — and a stronger out-of-the-box UI that many teams prefer. The choice between them is real but secondary; the durable skill is the *discipline* of logging every run's params, metrics, and artifacts, which both tools serve identically. Pick by team and budget, not by feature lists.

## The Honest Scope

This is the outer loop at literacy depth, and that is the right depth for the seam. MLflow has a Projects packaging format, a deployment server, and deep pipeline-orchestration territory — Airflow, Prefect, Kubeflow — that schedules and chains these runs into automated retraining pipelines. That orchestration layer is real and it is largely the data-platform and model-training work the curriculum consciously left on Path A; it lives in the antilibrary, named and located, a candidate for a focused companion book. What you need to own here is narrower and sharper: make every eval run a logged, comparable experiment, and promote winners through a registry the gateway can route to. Do that, and eval-driven development stops being a thing you did once and becomes a thing your platform remembers.

## Core Concepts

- Module 2's inner eval loop is amnesiac: it compares this version to the last one remembered, so without a system of record the discipline evaporates when the session closes — experiment tracking is the durable ledger that fixes this.
- Every eval run is an experiment with the same anatomy — parameters (model, prompt version, retriever config), metrics (judge scores, latency, cost), and artifacts (prompt, dataset, per-example scores) — and MLflow logs that triple per run with `log_param`, `log_metric`, and `log_artifact`, defaulting to a local `./mlruns` file store.
- The model registry promotes a winning run to a named, numbered, digest-pinned version, which is exactly what the rollout gateway's routing flag points at — linking the inner loop to the outer loop as recorded artifacts rather than memory.
- Azure ML is MLflow-compatible (same API, workspace-backed) and W&B is the commercial alternative; the choice is secondary to the durable skill, which is the discipline of logging every run's params, metrics, and artifacts.

<div class="claude-handoff" data-exercise="exercises/module5/12-experiment-tracking/">

**Build It in Claude Code** — wrap the `module5-serving/` eval step in MLflow tracking against a local file store: run three configurations (different prompt versions or retriever settings), log each as a run with its params, metrics, and the prompt artifact, then open `mlflow ui` and compare them to pick a winner by metric. No server, no cloud.

</div>
