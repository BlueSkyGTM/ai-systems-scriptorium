# Module 5: The Eval Pipeline

M1 built the training loop. M2 decided when to stop. M3 cleaned the data. M4 fine-tuned
the model without touching the base weights. This module asks the question none of the
previous four can answer: is the tuned model actually better?

Loss going down is not the answer. A model can reach low training loss by predicting
the next token well on training data while producing wrong labels, mismatched strings,
or outputs a human would reject. Loss measures the training objective. Evaluation measures
the task. This module builds the eval pipeline that bridges the gap: four metrics, a
weighted aggregate, and a gate script that exits 0 (promote) or 1 (block) based on whether
the tuned model beats the baseline on a held-out set.

The thesis: evaluation is something you build, not something you run once at the end.

## Four Lessons

1. **Loss Is Not Enough** (`loss-is-not-enough`): why loss curves mislead; the four
   dimensions a loss curve cannot see; the eval contract that replaces "loss went down"
   with "the gate passed."

2. **Task Metrics** (`task-metrics`): exact match, token F1, and perplexity: their
   formulas, their edge cases, how each normalises to [0, 1], and what each catches
   that the others miss.

3. **LLM-as-Judge** (`llm-as-judge`): the mock judge (deterministic, no API key required);
   the real judge pattern (reference only); rubric design that reduces variance; the cost
   math for budgeting live eval.

4. **Building the Eval Gate** (`building-the-eval-gate`): stitch the four metrics into a
   weighted aggregate, compare the tuned model against the baseline with a margin, and emit
   an exit code. MLflow as the production logging reference.

## What This Module Feeds Forward

The adapter checkpoint M4 produced is what M5's gate runs on. M6 closes the loop on the
classifier side: it ships a fine-tuned text classifier together with the eval gate that
proves it beats the base, with an MLflow run logged and a checkpoint versioned. M7 extends
the gate to behavioral regression: not just "does the aggregate improve" but "does it pass
the specific behavioral tests that define correct behavior." The gate built here is the
common foundation both artifacts depend on.
