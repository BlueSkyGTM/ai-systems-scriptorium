# The Made-With-ML Production Pipeline and Evaluation Framework

**Provenance:** vault/made-with-ml/madewithml/data.py, evaluate.py, predict.py, models.py, utils.py, notebooks/madewithml.ipynb

A reference pipeline for multi-stage data handling, sliced evaluation, and model-card-like result reporting. Shaped as load / preprocess / tokenize / [train: antilibrary] / evaluate / predict. Uses Ray Datasets for distributed work, Snorkel for slicing, sklearn metrics for scoring.

---

## Pipeline Stages

The pipeline separates concerns into standalone functions and classes (source: vault/made-with-ml/madewithml/data.py, predict.py):

**1. Load**
- `load_data(dataset_loc: str, num_samples: int = None) -> Dataset`: reads CSV into Ray Dataset via `ray.data.read_csv()`, shuffles with fixed seed (1234), optionally subsamples `num_samples`. Returns Ray Dataset object.
- Input: CSV file path; Output: Ray Dataset (distributed, lazy-evaluated).

**2. Data Split**
- `stratify_split(ds: Dataset, stratify: str, test_size: float, shuffle: bool, seed: int) -> Tuple[Dataset, Dataset]`: partitions data into train and test while maintaining class balance (stratification). Uses Ray's `groupby()` + `map_groups()` with pandas UDFs. Returns tuple of (train_ds, test_ds).
- Applies stratified split via sklearn's `train_test_split()` per group, then filters and shuffles each split separately.

**3. Preprocessing / Feature Engineering**
- `preprocess(df: pd.DataFrame, class_to_index: Dict) -> Dict`: combines feature engineering (concatenate title + description), text cleaning, label encoding, and tokenization into a single transform.
  - `clean_text(text: str, stopwords: List)`: lowercase, remove stopwords with regex, remove punctuation (with spacing), remove non-alphanumeric, collapse whitespace, strip, remove URLs.
  - `tokenize(batch: Dict) -> Dict`: uses AllenAI SciBERT tokenizer (`allenai/scibert_scivocab_uncased`), returns dict with keys `ids` (input_ids), `masks` (attention_mask), `targets` (label indices as numpy array).
- `CustomPreprocessor` class: wraps preprocessing as a fit/transform interface. `fit()` discovers unique labels and builds `class_to_index` mapping; `transform()` applies preprocessing to Ray Dataset via `map_batches()`. Maintains bidirectional mappings (`class_to_index`, `index_to_class`).
- Output: dict with keys `ids` (shape [batch_size, seq_len]), `masks` (shape [batch_size, seq_len]), `targets` (shape [batch_size]).

**4. Model and Inference** (antilibrary for capstone; referenced for understanding predict interface)
- Model: `FinetunedLLM` (source: vault/made-with-ml/madewithml/models.py): PyTorch nn.Module wrapping a finetuned BERT. Constructor takes llm, dropout_p, embedding_dim, num_classes. Methods: `forward()` (returns logits), `predict(batch)` (argmax over logits, returns numpy array), `predict_proba(batch)` (softmax, returns probabilities).
- Model I/O: forward expects dict with keys `ids`, `masks`; returns logits (shape [batch_size, num_classes]).

**5. Evaluation**
- See "Evaluation and slicing" section below.

**6. Prediction on New Data**
- See "Prediction interface" section below.

---

## Evaluation and Slicing

The evaluation module (source: vault/made-with-ml/madewithml/evaluate.py) computes overall metrics, per-class metrics, and metrics sliced by domain-specific patterns (source file: madewithml/evaluate.py lines 23-105).

### Overall Metrics
- `get_overall_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict`: 
  - Computes sklearn's `precision_recall_fscore_support()` with `average="weighted"` (weighted by support).
  - Returns dict: `{"precision": float, "recall": float, "f1": float, "num_samples": float}`.

### Per-Class Metrics
- `get_per_class_metrics(y_true: np.ndarray, y_pred: np.ndarray, class_to_index: Dict) -> Dict`:
  - Calls `precision_recall_fscore_support()` with `average=None` to get per-class breakdown.
  - For each class (by index), extracts `precision[i]`, `recall[i]`, `f1[i]`, `num_samples[i]` (support).
  - Returns OrderedDict sorted by F1 (descending), keys are class names (strings), values are dicts with keys `precision`, `recall`, `f1`, `num_samples`.

### Data Slices with Snorkel
- Two hardcoded slicing functions (decorated with `@slicing_function()`):
  - `nlp_llm(x)`: returns True if tag contains "natural-language-processing" AND text contains one of ["transformer", "llm", "bert"] (case-insensitive).
  - `short_text(x)`: returns True if text word count < 8.
- `get_slice_metrics(y_true: np.ndarray, y_pred: np.ndarray, ds: Dataset) -> Dict`:
  - Converts Ray Dataset to pandas, reconstructs text feature (title + description), applies both slicing functions via `PandasSFApplier([nlp_llm, short_text])`.
  - For each slice where mask sum > 0: computes `precision_recall_fscore_support()` with `average="micro"` on the slice subset.
  - Returns dict: `{slice_name: {"precision": float, "recall": float, "f1": float, "num_samples": int}}`.

### Evaluation Entry Point and Results Structure
- `evaluate(run_id: str, dataset_loc: str, results_fp: str) -> Dict` (lines 108-150):
  - Loads test/holdout dataset from CSV.
  - Retrieves best checkpoint from MLflow via `predict.get_best_checkpoint(run_id)`.
  - Instantiates `TorchPredictor` from checkpoint, extracts preprocessor and model.
  - Preprocesses dataset, extracts true labels from "targets" column.
  - Generates predictions via `map_batches(predictor)`.
  - Computes and returns nested dict:
    ```
    {
      "timestamp": "Month Day, Year HH:MM:SS AM/PM",
      "run_id": str,
      "overall": {"precision": float, "recall": float, "f1": float, "num_samples": float},
      "per_class": {
        class_name_1: {"precision": float, "recall": float, "f1": float, "num_samples": float},
        class_name_2: {...},
        ...  // ordered by F1 descending
      },
      "slices": {
        slice_name_1: {"precision": float, "recall": float, "f1": float, "num_samples": int},
        slice_name_2: {...}
      }
    }
    ```
  - Logs results as JSON (via logger.info) and optionally saves to file via `utils.save_dict()`.

---

## Prediction Interface

The predict module (source: vault/made-with-ml/madewithml/predict.py) provides both inference and probability output (lines 52-99).

### TorchPredictor Class
- Constructor: `__init__(preprocessor: CustomPreprocessor, model: FinetunedLLM)`. Sets model to eval mode.
- Methods:
  - `__call__(batch: Dict) -> Dict`: applies model.predict() (hard class indices), returns `{"output": np.ndarray}`.
  - `predict_proba(batch: Dict) -> Dict`: applies model.predict_proba() (softmax probabilities), returns `{"output": np.ndarray}`.
  - `get_preprocessor() -> CustomPreprocessor`: accessor.
  - `from_checkpoint(checkpoint) -> TorchPredictor`: class method. Loads metadata (class_to_index mapping), instantiates preprocessor, loads model from args.json and model.pt files within checkpoint path, returns fully initialized predictor.

### Prediction Flow for New Data
- `predict_proba(ds: ray.data.dataset.Dataset, predictor: TorchPredictor) -> List` (lines 77-98):
  - Preprocesses input dataset.
  - Maps `predictor.predict_proba()` over batches via Ray, collects all probability arrays.
  - For each sample, takes argmax over probabilities to get predicted class; formats full probability distribution.
  - Returns list of dicts: `[{"prediction": str (class name), "probabilities": {class_name: prob, ...}}, ...]`.
- `predict()` CLI command (lines 137-160): accepts run_id, title, description; creates single-sample Ray Dataset, calls `predict_proba()`, logs and returns results.

### Model Artifact Structure
- Checkpoint contains:
  - `args.json`: JSON file with keys `dropout_p`, `embedding_dim`, `num_classes` (model hyperparameters).
  - `model.pt`: PyTorch state_dict (model weights).
  - Metadata dict with key `class_to_index` (class name to integer mapping).

### Collation for Inference
- `collate_fn(batch: Dict[str, np.ndarray]) -> Dict[str, torch.Tensor]` (source: vault/made-with-ml/madewithml/utils.py, lines 76-91):
  - Pads `ids` and `masks` arrays to same length within batch via `pad_array()` (zero-pads to longest row).
  - Converts all arrays to torch tensors with appropriate dtypes: `ids` / `masks` int32, `targets` int64.
  - Places tensors on device (GPU if available).
  - Used internally by ray.train for batching during inference.

---

## Results / Model-Card-Like Reporting

The evaluation output (Dict structure, returned by `evaluate()` function) serves as a model card / performance report (lines 140-146 of evaluate.py).

**Result Dict Schema:**
- `timestamp`: ISO-like string, timestamp of evaluation run.
- `run_id`: experiment tracking ID (MLflow).
- `overall`: aggregate performance over full test set.
- `per_class`: per-label breakdown, sorted by F1 descending.
- `slices`: performance on domain-relevant subsets (e.g., NLP+LLM projects, short text projects).

**Semantics:**
- Precision / Recall / F1 are macro or weighted averages depending on computation (see `average` parameter in sklearn calls).
- Overall uses `average="weighted"` (per-class metrics weighted by class frequency).
- Slices use `average="micro"` (unweighted average of metric values per sample, equivalent to per-sample accuracy if binary).
- `num_samples` field indicates denominator (how many test samples contributed to each metric).

**Logging and Persistence:**
- Results printed as formatted JSON to stdout/log.
- Optionally saved to file via `utils.save_dict(d=metrics, path=results_fp)` (JSON serialization with optional custom encoder).
- Metadata from best MLflow run is embedded (run_id) for traceability.

---

## Out of Scope / Antilibrary

The following files are intentionally excluded from this distillation as they describe PyTorch training internals and are not part of the pipeline shape for a from-scratch tabular capstone:

- `train.py`: Ray train loop, TorchTrainer configuration, loss computation, checkpoint saving.
- `tune.py`: Hyperparameter optimization via Ray Tune and HyperOpt, trial scheduling, search algorithms.
- `models.py` (partial): model architecture (FinetunedLLM) is included for predict interface understanding, but forward/backward training details are excluded.

The capstone adopts the pipeline *shape* (load / preprocess / evaluate with slicing / predict interface) and results *structure* (overall + per-class + slice metrics as nested dict) but applies it to tabular data and a simpler model.
