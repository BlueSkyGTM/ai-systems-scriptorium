# Weights and Measures — Blueprint

## Positioning

Sans Python teaches when to fine-tune (M5 L13: fine-tune-vs-RAG-vs-prompt), what the seam looks
like from the outside, and how experiment tracking wraps it (M5 L12). It teaches none of the
inside: no training loop, no PyTorch, no validation discipline, no answer to "how do I know the
tune is actually good." That gap is row 2 of
`build-log/sans-python/antilibrary-gap-report.md` — the 78% PyTorch + model-training hiring
screen.

This book fills that inside. It is post-Sans-Python: the reader has already made the
fine-tune-vs-RAG decision and now has to execute it. The entry point is the fine-tuning literacy
Sans Python built; the exit point is a tuned model on disk with a gated eval that proves it
behaves better than the base, logged to a tracking server, and defensible in a code review.

**Not a book about running training commands.** The thesis is taste and judgment: how to know
when a tune is good, how to build the eval signal that gates that judgment, and how to keep
both signal and model honest as the data changes. Training mechanics are the scaffolding; the
deliverable is the operator who can say "this tune passes" or "this tune doesn't" and be right.

Scope note: PyTorch/training depth here. Classic ML (regression, trees, AUC-ROC, feature
engineering) belongs in the planned `ml-in-proportion` book. The CUDA kernel and distributed
training internals from `ai-performance-engineering` chapters 01-14 were antilibrary'd OUT of
Sans Python as MLE/research track; the subset that is AI-Engineer-relevant (profiling, memory
tuning, `torch.compile`) is squarely IN scope here.

## Thesis

The hiring screen asks for PyTorch. The job asks for something narrower: can you fine-tune a
model, evaluate whether the tune is good, and ship the result with confidence? Most practitioners
either skip evaluation entirely or treat loss curves as the verdict. Both are wrong.

This book teaches the full build: dataset curation, training loop mechanics in PyTorch, the eval
pipeline that produces a defensible verdict, and the judgment layer on top of metrics. The
through-line is quality. Every chapter answers a version of the same question: how do you know
this is working?

## Scope

### In scope

- PyTorch fundamentals at AI-Engineer depth: tensors, autograd, `nn.Module`, the training loop,
  `DataLoader`, optimizers, learning-rate schedules, checkpointing
- Fine-tuning adapters: LoRA, QLoRA, PEFT library; adapter merging and versioning
- Dataset curation for fine-tuning: quality over quantity, deduplication, formatting, the
  JSONL contract [MS-Learn: Azure ML fine-tuning data preparation]
- Eval pipeline construction: held-out sets, task-specific metrics (perplexity, BLEU, ROUGE,
  exact-match, LLM-as-judge), the eval loop that runs before any checkpoint is promoted
- Calibration and overfitting detection: train/val loss curves, token accuracy, early stopping
  [MS-Learn: Azure OpenAI fine-tuning results.csv analysis]
- Hyperparameter hygiene: learning rate, batch size, gradient accumulation, epochs; sweep
  strategy without burning compute [MS-Learn: Azure ML PyTorch hyperparameter sweep, BanditPolicy]
- Experiment tracking at the training loop: MLflow logging of loss, metrics, and hyperparameters;
  model registry; the artifact handoff that Sans Python's M5 L12 names but does not build
- `torch.compile` and mixed precision (AMP) for single-GPU efficiency; profiling with
  `torch.profiler`; GPU memory accounting
- The eval gate as a CI artifact: a script that fails loudly when the tuned model underperforms
  the baseline on the held-out set
- Inference validation: comparing tuned vs. base on representative prompts; behavioral regression
  testing before deployment

### Deliberately out of scope

- From-scratch pre-training and distributed training (FSDP/DDP, pipeline parallel): MLE/research
  track, not the 78% AI-Engineer screen
- Custom CUDA kernels, NCCL collectives, NVLink tuning: `ai-performance-engineering` chapters
  01-12 are deep infrastructure that sits outside this seam
- Classic ML (regression, trees, boosting, AUC-ROC, feature engineering): belongs in
  `ml-in-proportion`
- Diffusion, GANs, vision-specific fine-tuning: correctly cut in Sans Python, still out
- RLHF/DPO from scratch: literacy-level treatment only (the decision layer); implementation
  lives in from-scratch ML books
- Azure ML managed fine-tuning UI: shown as a reference [MS-Learn: Azure ML fine-tune a
  foundation model from model catalog], not the teaching target; the book builds locally
  and the cloud is an optional deploy surface

## Ore to Module Map

Three ore sources, each pre-inventoried in `ingredients/source/_repos/`:

| Source | Prefix | What it contributes |
|---|---|---|
| `ai-engineering-from-scratch` | `aefs` | Phase 03 (Deep Learning Core, PyTorch intro, backprop, optimizers), Phase 07 (Transformers deep dive, attention, scaling laws), Phase 10 capstone items (training loop, classifier fine-tuning, instruction tuning, DPO, eval pipeline — lessons 36-41, 49, 73-75) |
| `ai-performance-engineering` | `aipe` | Chapter 13 (PyTorch profiling, memory tuning, AMP, compiled autograd — the subset that applies to single-GPU fine-tuning without the kernel-authoring parts) |
| `made-with-ml` | `mwml` | `train.py`, `tune.py`, `models.py`, `evaluate.py` (the antilibrary'd training internals that are squarely in-seam here); the Ray Tune hyperparameter sweep pattern |

Survey all three at process-ore time via `vault/MANIFEST.md` and
`ingredients/source/_repos/<repo>/antilibrary.md`.

## Curriculum Arc

Eight modules mirroring Sans Python's structure. The first five build the stack; the last three
are runnable portfolio artifacts.

| Module | Title | What it covers |
|---|---|---|
| M1 | The PyTorch Operator | Tensors, autograd, `nn.Module`, the training loop from scratch, `DataLoader`, GPU transfer; enough PyTorch to read and modify a fine-tuning script |
| M2 | Fitting and Not Fitting | Loss curves, train/val split discipline, overfitting signals, early stopping, learning-rate schedules; the vocabulary of "is it working" |
| M3 | Dataset Craft | Curating fine-tuning data: quality signals, deduplication, formatting, the JSONL contract, held-out set design; why small + clean beats large + noisy |
| M4 | Adapters and the Fine-Tune Build | LoRA / QLoRA / PEFT; building the fine-tuning loop end-to-end; checkpointing; adapter merging; `torch.compile` and AMP for single-GPU efficiency |
| M5 | The Eval Pipeline | Task-specific metrics (perplexity, BLEU, ROUGE, exact-match, LLM-as-judge); building the eval loop; MLflow logging; the gated eval script that promotes or blocks a checkpoint [MS-Learn: Azure ML evaluation flows and metrics] |
| M6 | Artifact: Tuned Classifier with Eval Gate | Ship a fine-tuned text classifier with a held-out eval script that proves it beats the base; MLflow run logged; checkpoint versioned |
| M7 | Artifact: Instruction-Tuned LLM with Behavioral Regression Suite | Ship an instruction-tuned small LLM (LoRA on a 1-3B base); behavioral regression tests that catch regressions before a checkpoint is promoted |
| M8 | Artifact: The Full Fine-Tune Pipeline | End-to-end: data curation script, training loop, eval gate, MLflow logging, artifact handoff to a serving endpoint; the thing you put in a portfolio and walk through in an interview |

## Portfolio Artifact Strategy

Sans Python's M6/M7/M8 pattern: each artifact is a runnable repo with a smoke test and a
`pytest` gate that confirms it actually works. This book follows the same pattern at the training
boundary.

The three artifacts together form a portfolio that answers the interview question "show me a
fine-tune you shipped":

- **M6 artifact** — proof you can fine-tune and evaluate a classifier; the simplest possible
  complete loop
- **M7 artifact** — proof you can instruction-tune an LLM and build behavioral regression tests;
  the thing that separates "I ran a notebook" from "I built a quality gate"
- **M8 artifact** — the full pipeline as a single callable workload: curation + training +
  eval + handoff; the capstone that mirrors what a production AI Engineer actually ships

Each artifact has:
- `train.py`: the training loop
- `eval.py`: the gated eval script (exits non-zero if the tuned model does not beat the base
  on the held-out set by a defined margin)
- `smoke.py`: a fast sanity check runnable in < 30 seconds on CPU
- `pytest` suite covering the eval gate and the data pipeline
- `README.md` documenting the run command and the expected output

The eval gate is the differentiator. Most fine-tuning tutorials end at "loss went down." This
book ends at "the eval script passed" — a concrete, reproducible claim.

## Dual-Use Note

Written to be read by a human learner and ingested by an LLM. Dense, linked, plain markdown.
The same page serves either party; that is part of why the focused books pay off.

## Candidate Names (GATE-NAME-BOOK)

Stop here. The real title and slug require Ray's sign-off before the in-progress directory is
created. The following are proposals only.

**Lead candidate: Weights and Measures**
Rationale: thesis-forward — a model's weights are earned through honest evaluation, not blindly
produced. The phrase encodes the judgment thesis directly and reads cleanly as a portfolio artifact
description ("I built Weights and Measures, a fine-tuning book about quality gates and earned results").

**Candidate 2: Tasteful Tuning**
Rationale: captures the taste and judgment angle; memorable and distinctive. Slightly abstract
compared to the lead; "tuning" underindexes the evaluation thesis.

**Candidate 3: The Fine-Tune Build**
Rationale: operator-framed, action-oriented, immediately clear to a hiring manager scanning a
GitHub portfolio. Less distinctive; could describe any fine-tuning tutorial.

**Candidate 4: Quality at Training Time**
Rationale: thesis-forward and accurate; emphasizes the eval/quality angle. Slightly verbose and
less sticky than the lead. Works better as a subtitle than a title.
