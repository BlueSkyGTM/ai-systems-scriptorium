# Module 4 · Made-With-ML Notebook — Outline

> Source: `notebooks/madewithml.ipynb` (243 cells). Outline only — section headings + a 1–2 sentence summary of what each section does. Tags mark the MLOps seam.

---

### 🛠️ Setup  [Training]
Introduces Ray as the framework for developing the application with distributed workloads, covering environment and library configuration.

### Data  [Training]
Top-level section covering the full data pipeline from ingestion through preprocessing.

#### 🔢 Data ingestion  [Training]
Loads the raw project dataset into a pandas DataFrame for subsequent processing.

#### ✂️ Data splitting  [Training]
Splits the dataset into training and validation/test sets using scikit-learn's `train_test_split` utility.

#### 🔍 Exploratory Data Analysis (EDA)  [Training]
Performs exploratory analysis to understand signals, distributions, and nuances in the dataset before model development.

#### ✨ Data Preprocessing  [Training]
Applies feature engineering, filtering, and cleaning; distinguishes between global preprocessing (language-agnostic) and local preprocessing (learned from the training split to avoid data leaks).

##### Feature engineering  [Training]
Combines existing input features (e.g., title and description) to create new, more predictive signals for the model.

##### Clean text  [Training]
Removes NLTK stop words and applies standard text normalization such as lowercasing.

##### Clean DataFrame  [Training]
Drops unused columns, removes null rows, and reorganizes the DataFrame into the final `text`/`tag` structure.

##### Label encoding  [Training]
Encodes categorical string labels into numerical class indices so models can process them.

##### Tokenizer  [Training]
Uses the SciBERT pretrained tokenizer to convert text input into subword token IDs, aligning with the LLM that will be fine-tuned later.

##### Distributed preprocessing  [Training]
Motivates and demonstrates scaling preprocessing beyond a single machine using Ray Data to handle larger datasets.

### Training  [Training]
Top-level section covering model definition, batching, utilities, and the distributed training loop using Ray Train.

#### 🤖 Model  [Training]
Defines a PyTorch neural network that wraps a pretrained BERT model with a custom classification head.

#### 📦 Batching  [Training]
Implements a custom `collate_fn` to re-pad items within each training batch so tensors have uniform sequence length.

#### 🧮 Utilities  [Training]
Imports and wires together Ray Train components — `TorchTrainer`, `ScalingConfig`, `Checkpoint`, and `DistributedDataParallel` — needed for distributed training.

#### 🗂️ Configurations  [Training]
Sets up configuration objects (including EFS directory paths) that parameterize the training and checkpointing runs.

#### 🚂 Training  [Training]
Loads and stratifies the dataset, then launches the distributed Ray TorchTrainer to execute the training loop.

##### Evaluation  [MLOps]
Computes precision, recall, and F1 scores on validation predictions using scikit-learn metrics.

##### Inference  [Training]
Wraps the trained model into a callable that accepts raw text (via pandas) and returns predicted labels and probabilities.

### 🧪 Experiment tracking  [MLOps]
Introduces MLflow as the system for tracking experiments — parameters, metrics, models, and artifacts — to organize and compare runs.

#### Dashboard  [MLOps]
Launches the MLflow tracking server on a localhost port so users can view and compare logged experiments via a web UI.

#### Loading  [MLOps]
Uses Ray Train's `Result` API to load a specific checkpoint from storage (including remote URIs) for evaluation or serving.

### ⚙ Hyperparameter tuning  [MLOps]
Configures Ray Tune with HyperOpt search and an AsyncHyperBand scheduler to run large-scale hyperparameter optimization over the training function.

### ⚖️ Evaluation  [MLOps]
Expands beyond overall precision/recall/F1 to include fine-grained, per-class, confusion-matrix, confidence-learning, slice, interpretability, and behavioral evaluations for deeper model assessment.

#### Coarse-grained metrics  [MLOps]
Computes weighted overall precision, recall, F1, and sample count across the entire test set.

#### Fine-grained metrics  [MLOps]
Calculates per-class precision, recall, and F1 to identify which specific labels the model handles well or poorly.

#### Confusion matrix  [MLOps]
Inspects true-positive, false-positive, and false-negative breakdowns to find areas for relabeling or targeted data collection.

#### Confidence learning  [MLOps]
Uses prediction confidence scores to surface potentially mislabeled training samples, feeding corrections back into annotation pipelines.

#### Slice metrics  [MLOps]
Defines and evaluates custom slicing functions to measure performance on critical data subsets (classes, features, metadata, priority groups).

#### Interpretability  [MLOps]
Applies techniques like SHAP or LIME to inspect which input tokens are most influential on the model's predictions.

#### Behavioral testing  [MLOps]
Runs invariance and directional tests (e.g., verb injection) to verify that predictions are robust to semantically irrelevant input changes.

### 🚀 Serving  [MLOps]
Top-level section covering deployment patterns: offline batch inference and real-time online inference with custom serving logic.

#### Batch inference (offline)  [MLOps]
Uses Ray Data with an actor pool strategy to run distributed, large-scale batch inference across the full dataset.

#### Online inference (real-time)  [MLOps]
Discusses serving models behind a real-time endpoint to deliver low-latency, high-throughput predictions for incoming requests.

#### Custom logic  [MLOps]
Adds a probability-threshold rule to the served model that routes low-confidence predictions to an `other` class for safer production behavior.
