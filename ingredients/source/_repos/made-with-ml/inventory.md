# Made-With-ML — Repo Inventory

> Source: root + `madewithml/`, `notebooks/`, `deploy/`, `datasets/`, `tests/`. MLOps reference project for Module 4.

## `madewithml/`

```text
madewithml/
├── __init__.py
├── config.py
├── data.py
├── evaluate.py
├── models.py
├── predict.py
├── serve.py
├── train.py
├── tune.py
└── utils.py
```

- **`__init__.py`** — Marks the directory as a Python package.
- **`config.py`** — Centralized configuration constants and paths (e.g., MLflow model registry location).
- **`data.py`** — Data processing pipeline including loading, stratified splitting, text cleaning, tokenization, and custom preprocessing.
- **`evaluate.py`** — Model evaluation logic computing overall, per-class, and slice-level metrics; executable via CLI.
- **`models.py`** — PyTorch model definitions (e.g., fine-tuned LLM).
- **`predict.py`** — Prediction logic including decoding, probability formatting, TorchPredictor class, and MLflow checkpoint loading.
- **`serve.py`** — Ray Serve deployment definitions wrapping the predictive model into a scalable API.
- **`train.py`** — Distributed training workflow including step functions, train loops, and CLI execution.
- **`tune.py`** — Hyperparameter tuning logic to optimize model performance.
- **`utils.py`** — Utility functions for reproducibility (seeds), file I/O, padding/collation, and MLflow run tracking.

## `deploy/`

```text
deploy/
├── cluster_compute.yaml
├── cluster_env.yaml
├── jobs/
│   ├── workloads.sh
│   └── workloads.yaml
└── services/
    ├── serve_model.py
    └── serve_model.yaml
```

- **`cluster_compute.yaml`** — Anyscale cluster compute configuration defining cloud provider, instance types (g5.4xlarge), and worker nodes.
- **`cluster_env.yaml`** — Anyscale cluster environment configuration defining the base Docker image and node setup commands.
- **`jobs/workloads.sh`** — Execution shell script orchestrating the end-to-end MLOps pipeline (testing, training, evaluation, S3 artifact saving).
- **`jobs/workloads.yaml`** — Anyscale job configuration defining the execution environment and entrypoint for batch workloads.
- **`services/serve_model.py`** — Python entrypoint script to initialize and launch the Ray Serve model deployment.
- **`services/serve_model.yaml`** — Anyscale service configuration defining the rollout strategy and runtime environment for the served model.

## `notebooks/`

```text
notebooks/
├── benchmarks.ipynb
├── clear_cell_nums.py
└── madewithml.ipynb
```

- **`benchmarks.ipynb`** — Jupyter notebook evaluating model benchmarks and performance.
- **`clear_cell_nums.py`** — Utility script to clear execution counts/numbers in Jupyter notebooks for clean Git commits.
- **`madewithml.ipynb`** — Main exploratory and development Jupyter notebook covering the ML workflow.

## `datasets/`

```text
datasets/
├── dataset.csv
├── holdout.csv
├── projects.csv
└── tags.csv
```

- **`dataset.csv`** — Primary training dataset containing project features and target tags.
- **`holdout.csv`** — Unseen evaluation dataset used for model validation.
- **`projects.csv`** — Raw project features without target labels.
- **`tags.csv`** — Unique target tag classes used for classification mapping.

## `tests/`

```text
tests/
├── code/
│   ├── conftest.py
│   ├── test_data.py
│   ├── test_predict.py
│   ├── test_train.py
│   ├── test_tune.py
│   ├── test_utils.py
│   └── utils.py
├── data/
│   ├── conftest.py
│   └── test_dataset.py
└── model/
    ├── conftest.py
    ├── test_behavioral.py
    └── utils.py
```

- **`tests/code/`** — Unit tests covering core Python modules (`data.py`, `predict.py`, `train.py`, `tune.py`, `utils.py`) with shared fixtures in `conftest.py`.
- **`tests/data/`** — Data validation tests verifying the integrity and structure of the dataset.
- **`tests/model/`** — Behavioral tests evaluating model predictions against expected performance and fairness criteria.

## `tests/`

## Notes

- **Dataset row counts**:
  - `datasets/dataset.csv`: 812 rows (columns: `id`, `created_on`, `title`, `description`, `tag`)
  - `datasets/holdout.csv`: 207 rows (columns: `id`, `created_on`, `title`, `description`, `tag`)
  - `datasets/projects.csv`: 812 rows (columns: `id`, `created_on`, `title`, `description`)
  - `datasets/tags.csv`: 764 rows (column: `tag`)
- **Test structure**: Tests are subdivided into three distinct categories: `code/` for unit testing logic, `data/` for data drift/integrity validation, and `model/` for behavioral model testing.
- **Visuals**: No visuals found (no png/svg/jpg, no mermaid in this repo).
