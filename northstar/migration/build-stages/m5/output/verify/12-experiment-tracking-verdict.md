# VERIFY verdict — L12 Experiment Tracking & the LLMOps Outer Loop

Verifier: Sonnet VERIFY subagent. Date: 2026-06-19. Sources: WebFetch (mlflow.org/docs tracking + model-registry) and MS Learn connector (Azure ML MLflow compatibility).

## Claim ledger

| Claim | Source | Verdict |
|---|---|---|
| MLflow Tracking = API and UI for logging params, metrics, output files from a run + later visualizing | MLflow docs: "an API and UI for logging parameters, code versions, metrics, and output files when running your ML code and for later visualizing the results" | CONFIRMED |
| mlflow.start_run() opens a run | MLflow docs + Azure ML docs (`with mlflow.start_run():`) | CONFIRMED |
| log_param records an input you set | MLflow docs: "Records parameters"; example `mlflow.log_param("lr", 0.001)` | CONFIRMED |
| log_metric records a measured number | MLflow docs: "Logs performance metrics"; example `mlflow.log_metric("val_loss", val_loss)` | CONFIRMED |
| log_artifact stores a file the run produced | MS Learn (Azure ML "Log files"): `mlflow.log_artifact("path/to/file.pkl")` — "Files are always logged in the root of the run" | CONFIRMED (MLflow tracking landing page didn't show it verbatim; Azure ML MLflow docs confirm the API) |
| mlflow.autolog() auto-captures params/metrics/models for supported frameworks | MLflow docs: "log metrics, parameters, and models without the need for explicit log statements"; Scikit-learn, XGBoost, PyTorch, Keras, Spark | CONFIRMED |
| Default local ./mlruns file store, no server required | MLflow docs: "stores data locally in the `mlruns` directory — no particular server/database configuration"; "A tracking server is optional" | CONFIRMED |
| Remote tracking server, same logging API | MLflow docs: remote server "serves the same UI and enables remote storage of run artifacts" | CONFIRMED |
| `mlflow ui` browser view to list/sort/compare runs | MLflow docs (UI component) | CONFIRMED |
| Model Registry: named models, numbered versions, aliases marking the production version | MLflow registry docs: registered model has "a unique name"; "one or many versions... added as version 1"; "Model aliases allow you to assign a mutable, named reference to a particular version" (e.g. "champion") | CONFIRMED. Draft changed "aliases or stages" → "aliases" (current MLflow deprecated stages in favor of aliases) |
| Azure ML workspaces are MLflow-compatible; same log_metric/log_param calls; runs/metrics/artifacts land in workspace, no cloud-specific syntax | MS Learn: "Azure Machine Learning workspaces are MLflow-compatible... you use MLflow to track runs, metrics, parameters, and artifacts in workspaces without changing your training routines or adding any cloud-specific syntax" | CONFIRMED (near-verbatim) |
| Azure ML studio Jobs/Metrics views render comparable charts across runs | MS Learn (how-to-log-view-metrics → Metrics tab "render charts," "plotting multiple metrics") | CONFIRMED |
| W&B is the common commercial alternative with same primitives (runs, config/metrics, artifacts, hosted dashboard) | Industry-standard (W&B core feature set); Azure AI Foundry has a W&B integration | CONFIRMED (settled tool knowledge; W&B primitives are runs/config/metrics/artifacts) |
| MLflow has Projects, deployment server, and orchestration territory (Airflow/Prefect/Kubeflow) → antilibrary | MLflow Projects packaging is real; Airflow/Prefect/Kubeflow are orchestration tools | CONFIRMED (correctly scoped to antilibrary) |

## Markers resolved
All `[verify:]` / `[MS-Learn:]` markers removed → clean prose. No markers remain (grep clean).

## FLAGGED
- None. All claims grounded. (Minor editorial: changed "aliases or stages" to "aliases" to track current MLflow — stages are deprecated; not a defect, a currency fix.)

## STYLE (full read)
- H1; single `## Core concepts`; `claude-handoff` div last. ✓
- Lead: concrete failure scenario (forty changes, score down, nobody can say which) → stake. No throat-clearing. ✓
- Pronoun/tense/POV/voice consistent. ✓
- Ending shape: reframe ("becomes a thing your platform remembers") — not a template, not the banned opener. ✓
- Acronyms: MLflow, W&B (expanded "Weights & Biases (W&B)"), LLMOps fine in title context. ✓
- Literacy depth: orchestration (Airflow/Prefect/Kubeflow) explicitly named and routed to antilibrary/Avec Python — does not cross into pipeline implementation. ✓

## Verdict: PASS
MLflow API shape (runs/params/metrics/artifacts/registry) and Azure ML MLflow compatibility both grounded against primary docs and MS Learn. Markers resolved, prose clean, STYLE holds. No flags.
