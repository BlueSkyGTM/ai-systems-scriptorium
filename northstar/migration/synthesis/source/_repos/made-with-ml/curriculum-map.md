# Made-With-ML — Curriculum Map

> Source repo maps into Module 4. The seam is the MLOps/serving workflow; model-training internals are antilibrary (see `output/antilibrary.md`).

## Overview

| Module 4 Section | Repo source | What it provides |
| :--- | :--- | :--- |
| MLOps in Practice | `notebooks/madewithml.ipynb`, `Makefile`, `madewithml/__init__.py`, `madewithml/config.py`, `madewithml/utils.py` | End-to-end MLOps pipeline notebook (data loading → training → evaluation → serving). Code styling, linting, and cleanup tooling. Environment loading, MLflow tracking configuration, project directory structure, and reproducibility utilities. |
| Data versioning | `datasets/dataset.csv`, `datasets/holdout.csv`, `datasets/projects.csv`, `datasets/tags.csv`, `madewithml/data.py` | Versioned datasets (812 training rows, 207 holdout rows, project metadata, tag labels) and the data loading/cleaning/splitting/tokenization pipeline producing Ray datasets. |
| Serving pipelines | `madewithml/predict.py`, `madewithml/serve.py`, `deploy/` | Offline and online inference logic with MLflow run artifact retrieval; FastAPI application wrapped as a Ray Serve deployment; cluster compute and environment definitions; batch job orchestration; online serving rollout configuration. |
| Antilibrary cut | `madewithml/train.py`, `madewithml/tune.py`, `madewithml/models.py` | Distributed model training workload orchestration, hyperparameter tuning with Ray Tune, and PyTorch neural network architecture (finetuned LLM) with save/load logic. These are training internals documented but out-of-seam for Module 4's MLOps focus. |

## Source → Section

| Repo artifact | Module 4 mapping | Seam |
| :--- | :--- | :--- |
| `notebooks/madewithml.ipynb` | MLOps in Practice | End-to-end pipeline walkthrough — the portfolio project spine tying together data, training, evaluation, and serving into a single reproducible workflow. |
| `madewithml/__init__.py` | MLOps in Practice (infra) | Environment variable loading on package import — foundational infrastructure setup. |
| `madewithml/config.py` | MLOps in Practice (infra) | MLflow tracking URI configuration, project directory structure, and logging setup — the MLOps plumbing that makes experiments reproducible. |
| `madewithml/utils.py` | MLOps in Practice (infra) | Shared utilities for reproducibility (seed setting), data collation, and JSON/dict helpers — cross-cutting infrastructure code. |
| `madewithml/data.py` | Data versioning (data pipeline) | Loads, cleans, splits, and tokenizes text data into Ray datasets. The data preparation seam feeding both training and evaluation. |
| `madewithml/train.py` | Antilibrary (training) | Distributed training workload orchestration with MLflow logging. Documented for reference but out-of-seam — the MLOps workflow treats this as a callable workload, not a teaching target. |
| `madewithml/tune.py` | Antilibrary (training) | Hyperparameter tuning with Ray Tune and MLflow tracking. Experiment management is in-seam; the tuning algorithm internals are antilibrary. |
| `madewithml/models.py` | Antilibrary (training) | PyTorch LLM architecture and checkpoint save/load logic. Model internals are explicitly out-of-seam. |
| `madewithml/evaluate.py` | Serving pipelines (eval) | Computes overall, per-class, and slicing metrics on holdout data — the evaluation step that gates model promotion into serving. |
| `madewithml/predict.py` | Serving pipelines (serving) | Loads model checkpoints for offline/online inference and retrieves MLflow run artifacts — the prediction seam between stored models and live requests. |
| `madewithml/serve.py` | Serving pipelines (serving) | FastAPI application wrapped as a Ray Serve deployment — the online serving entrypoint that turns a predictor into a production endpoint. |
| `deploy/cluster_compute.yaml` | Serving pipelines (infra) | AWS cloud environment definition: region, head/worker node instance types, GPU worker configuration, block device mappings. |
| `deploy/cluster_env.yaml` | Serving pipelines (infra) | Docker base image, OS packages, and Python dependency setup for the Anyscale cluster environment. |
| `deploy/jobs/workloads.sh` | Serving pipelines (batch) | Shell script orchestrating the end-to-end batch pipeline: tests → training → run ID extraction → evaluation → model testing → S3 artifact storage. |
| `deploy/jobs/workloads.yaml` | Serving pipelines (batch) | Anyscale Ray job configuration mapping the entrypoint script to cluster compute and environment resources. |
| `deploy/services/serve_model.py` | Serving pipelines (serving) | Retrieves model artifacts from S3, reads run ID, and binds `ModelDeployment` class to create the Ray Serve entrypoint. |
| `deploy/services/serve_model.yaml` | Serving pipelines (serving) | Ray Serve config linking Python entrypoint to cluster environment, setting runtime variables, and defining rollout strategy (ROLLOUT vs IN_PLACE). |
| `datasets/dataset.csv` (812 rows) | Data versioning | Primary training dataset — versioned input for the data pipeline. |
| `datasets/holdout.csv` (207 rows) | Data versioning | Held-out evaluation dataset used by the evaluation and model-testing steps. |
| `datasets/projects.csv` (812 rows) | Data versioning | Project metadata paired with the primary dataset. |
| `datasets/tags.csv` (764 rows) | Data versioning | Multi-label tag vocabulary for the classification task. |

## Notes

- **Portfolio-grade MLOps project:** The notebook plus `deploy/` artifacts give students a complete, production-grade MLOps project spanning the full lifecycle — from versioned datasets and MLflow experiment tracking through batch job orchestration on Anyscale/Ray to online serving with configurable rollout strategies. This is the capstone integration artifact for Module 4.
- **Two deployment surfaces:** The repo cleanly separates batch (`deploy/jobs/`) from online serving (`deploy/services/`), letting students study the same model shipped through two distinct production patterns on shared cluster infrastructure (`deploy/cluster_compute.yaml`, `deploy/cluster_env.yaml`).
- **Training internals are documented but out-of-seam:** `train.py`, `tune.py`, and `models.py` are fully readable and referenced by the pipeline, but the curriculum treats them as callable workloads. The teaching target is the MLOps workflow around them (tracking, orchestration, serving, testing), not the model architecture or training algorithm — see `output/antilibrary.md`.
