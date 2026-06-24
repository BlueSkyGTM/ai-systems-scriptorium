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

Your checkpoint cannot be a dumb tensor dump. A production checkpoint carries its own metadata. The checkpoint bundles the `state_dict`, the `vocab`, the `class_names`, the model `config`, and the training-set majority class. When `eval.py` loads the model, it expects a self-contained dictionary.

```python
checkpoint = {
    "state_dict": model.state_dict(),
    "vocab": vocab.stoi,
    "class_names": CLASS_NAMES,
    "config": {
        "embed_dim": embed_dim,
        "hidden_dim": hidden_dim,
        "max_len": MAX_LEN,
        "num_classes": NUM_CLASSES,
    },
    "train_majority_class": majority_class(train_data),
}
torch.save(checkpoint, checkpoint_path)
```

If you separate the weights from the configuration that generated them, you invite silent shape mismatches and deployment failures. The `config` stores the architecture hyperparameters so `eval.py` rebuilds the model exactly, and `train_majority_class` lets it reconstruct the baseline without re-parsing the training file.

## Respect the Architecture

The training loop must respect structural boundaries. You apply early stopping (covered in Module 2) to prevent overfitting on the synthetic dataset. You use the adapter pattern (covered in Module 4) to ensure raw text inputs map cleanly into the model's expected tensor shapes. The loop trains the classifier, evaluates the validation accuracy, and writes the self-describing checkpoint.

## Core Concepts

* Fixed seeds (`SEED = 42`) must be applied to Python, PyTorch, and the environment hash before any RNG calls.
* A checkpoint must bundle the `state_dict` with its own metadata: `vocab`, `class_names`, model `config`, and `train_majority_class`.
* Training scripts must enforce determinism so downstream evaluation gates test the model, not the noise.

<div class="claude-handoff" data-exercise="exercises/module6/training-the-classifier/">
**Build It in Claude Code** · Exercise · exercises/module6/training-the-classifier/
</div>

A saved checkpoint is not the final output of your training pipeline; to a Production AI Engineer, it is the initialization state for the evaluation gate.