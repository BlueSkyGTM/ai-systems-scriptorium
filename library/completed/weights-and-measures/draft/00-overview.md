# Module 1: The PyTorch Operator

The hiring screen asks for PyTorch. What it actually tests is whether you can read, run, and
modify a training script without flailing — and whether you understand what each part is for.
This module builds that foundation: tensors, autograd, `nn.Module`, the training loop, and the
first signal that something is or is not working.

The through-line starts here. Every lesson frames its mechanics around a question you will need
to answer in production: "How do I know this is doing what I think?" That discipline is not a
detour from the PyTorch content; it is the point of the PyTorch content.

Two lessons:

1. **Tensors, Autograd, and the Training Loop** — the minimal PyTorch surface that a fine-tuning
   engineer reads and modifies every day: tensor creation, device transfer, gradient accumulation,
   `optimizer.step()`, and a bare training loop that actually runs. Framed throughout around what
   to inspect and verify, not just what to call.

2. **Loss Curves and the Overfitting Signal** — the vocabulary of "is it working": train and
   validation loss, token accuracy, the divergence pattern that flags overfitting, and early
   stopping as a policy decision, not a hyperparameter tweak. References `results.csv` metrics
   from Azure AI Foundry fine-tuning runs [MS-Learn: Azure AI Foundry fine-tuning metrics] as a
   real artifact the production engineer reads.

**What this module feeds forward:** the training loop built in Lesson 1 is the scaffold every
later module modifies — adapter insertion in M4, eval gate attachment in M5. The loss-curve
literacy from Lesson 2 is the precondition for overfitting-aware training in M4 and for reading
the MLflow charts in M5. You will not touch LoRA before you can read a loss curve.
