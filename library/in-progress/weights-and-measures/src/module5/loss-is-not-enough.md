# Loss Is Not Enough

A training script that prints only the loss is lying in three ways. It cannot tell
you whether the loss is decreasing for the right reason. It cannot tell you if a
divergence is starting. And it cannot tell you what the model has learned, only that
the optimizer found a direction that reduced the training objective.

Loss is not a bad signal. It is an incomplete one. The gap between "loss went down"
and "the model is better" is where most fine-tuning projects fail.

## What Loss Measures

Cross-entropy loss measures how surprised the model is by the training data. At each
position in a sequence, the model assigns a probability distribution over the vocabulary;
loss penalizes the mass it puts on the wrong token. If the model improves at predicting
the training distribution, loss decreases.

This is exactly the right thing to optimize during training. The problem is that the
task is usually something different. A question-answering model is not graded on how
well it predicts training tokens; it is graded on whether it produces the correct answer
string. A classifier is not graded on next-token prediction; it is graded on whether it
assigns the correct label. Loss measures the proxy. Evaluation measures the task.

## Four Dimensions Loss Misses

**String correctness.** If the model outputs "the answer is Paris" and the reference
is "Paris", a token-level loss computed on the full string might be lower than if the
model outputs "Paris" directly, but exact match will correctly score the verbose answer
as 0 (after normalization) while the terse answer scores 1. Loss does not know about
output format; exact match does.

**Lexical overlap.** A model that outputs "PyTorch uses dynamic computation" when the
reference is "PyTorch uses dynamic computation graphs" has missed one token. Exact match
scores that as 0. Token F1 scores it at 0.89, reflecting that most of the answer is
correct. Loss might be low on both depending on where in the sequence the model made the
error. Neither loss nor exact match captures partial credit; token F1 does.

**Language model fit on the held-out distribution.** Perplexity measures how well the
model's distribution fits the held-out text, independent of any specific label or reference
string. A model that overfit the training set may have low training loss and high
held-out perplexity simultaneously. Loss tracked on training data does not catch this;
perplexity on a held-out corpus does.

**Qualitative correctness.** A model that produces a factually accurate but poorly
reasoned answer and a model that produces a confident but wrong answer can have similar
token overlap with a reference. An LLM judge, evaluating along dimensions like relevance,
correctness, and helpfulness, distinguishes them. Loss cannot; overlap metrics may not.

## The Eval Contract

The eval contract replaces "loss went down" with something checkable:

1. Run four metrics on a fixed held-out set for both the tuned model and the baseline.
2. Normalize each metric to [0, 1].
3. Compute a weighted aggregate.
4. If the tuned model's aggregate meets or beats the baseline's aggregate minus a margin,
   promote the checkpoint. Otherwise, block it.

The gate exits 0 on PASS and 1 on BLOCK. Any upstream script, CI job, or notebook that
calls the gate can branch on the exit code. The checkpoint is not promoted by a human
reading a loss curve; it is promoted by a script that ran the four metrics and found the
tuned model better.

This is the same pattern applied to data in M3 (the curation gate exits 0 or 1) and to
the loop in M1 (the validator exits 0 or 1). The rubric is always code. The evaluation
gate is that pattern applied to model quality.

## What This Module Builds

`eval_gate.py` in `exercises/spine/` is the M5 spine tool. It contains `exact_match`,
`token_f1`, `mock_judge`, and `perplexity_from_nll` as standalone functions; an
`EvalResult` dataclass that computes all four on construction; and `eval_gate` that
returns `True` (PASS) or `False` (BLOCK) by comparing two lists of results. It is
pure stdlib and math, no framework required, and `--selftest` exits 0.

The lessons that follow build each piece of this script from first principles before
the capstone wires them into the gate.

## Core Concepts

- Loss measures the training objective, not the task. A model can achieve low loss and
  still fail at string correctness, partial-answer credit, held-out distribution fit,
  and qualitative correctness simultaneously.
- Four dimensions loss misses: string correctness (exact match), lexical overlap (token
  F1), held-out distribution fit (perplexity), qualitative correctness (LLM-as-judge).
- The eval contract: run metrics on a fixed held-out set for tuned and baseline; compute
  a weighted aggregate; gate on the comparison with a margin; exit 0 (PASS) or 1 (BLOCK).
- The gate is a script. Checkpoint promotion is not a human judgment call on a loss curve;
  it is the exit code of a deterministic program.

<div class="claude-handoff" data-exercise="exercises/module5/loss-is-not-enough/">

**Build It in Claude Code**: Write a script that takes a list of (train_loss, val_loss)
pairs representing epoch history and detects three failure modes: (1) val_loss never
improves below its epoch-1 value (stalled), (2) val_loss increases for three consecutive
epochs after a minimum (overfitting confirmed), (3) train_loss and val_loss both increase
for two consecutive epochs (divergence). Return a named diagnosis for each case. Write
a `--selftest` that plants each failure mode and confirms the detector catches it. This
is the loss-curve reading discipline in code, not prose.

</div>
