# Training the Classifier

A training run you cannot reproduce is not a training run; it is a guess. You must kill every source of uncontrolled randomness and document your model's birth certificate.

## Lock the Randomness

Randomness hides bugs. You demand reproducibility by hardcoding a seed before any other operation executes. The Python environment, the random module, and PyTorch must all align to a deterministic state.

```python
SEED = 42
os.environ.setdefault("PYTHONHASHSEED", str(SEED))
random.seed(SEED)
torch.manual_seed(SEED)
```

You place these calls at the top of `train.py`. A single unseeded initialization destroys your ability to debug a failing model or prove your results.

## Bundle the Metadata

Your checkpoint cannot be a dumb tensor dump. A production checkpoint carries its own metadata. The checkpoint format combines the `state_dict`, the hyperparameters, the current epoch, and the final `val_accuracy`. When `eval.py` loads the model, it expects a self-contained dictionary.

```python
{
    "vocab":   Dict[str, int],         # word -> id; must contain <pad>, <unk>
    "label_map": Dict[str, int],       # label string -> id (5 classes)
    "config":  {embed_dim, hidden_dim, max_len, ...},
    "state_dict": OrderedDict,         # TextClassifier weights
}
```

If you separate the weights from the configuration that generated them, you invite silent shape mismatches and deployment failures. The `config` stores the hyperparameters, ensuring the evaluation script can rebuild the architecture exactly.

## Respect the Architecture

The training loop must respect structural boundaries. You apply early stopping (covered in Module 2) to prevent overfitting on the synthetic dataset. You use the adapter pattern (covered in Module 4) to ensure raw text inputs map cleanly into the model's expected tensor shapes. The loop trains the classifier, evaluates the validation accuracy, and writes the self-describing checkpoint.

## Core Concepts

* Fixed seeds (`SEED = 42`) must be applied to Python, PyTorch, and the environment hash before any RNG calls.
* A checkpoint must bundle the `state_dict` with its own metadata (hyperparameters, epoch, `val_accuracy`).
* Training scripts must enforce determinism so downstream evaluation gates test the model, not the noise.

<div class="claude-handoff" data-exercise="exercises/module6/training-the-classifier/">
**Build It in Claude Code** · Exercise · exercises/module6/training-the-classifier/
</div>

A saved checkpoint is not the final output of your training pipeline; to a Production AI Engineer, it is the initialization state for the evaluation gate.