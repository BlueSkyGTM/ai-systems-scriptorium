# Exercise: Prompt Engineering

**Goal** — Build a prompt-testing harness that registers three prompt variants in MLflow's prompt registry, scores each variant against a rubric, and reports which version wins.

**Why** — Prompts are versioned artifacts; a harness that can compare and roll back versions is the foundation of every subsequent eval cycle in this course.

**Steps**

1. Create an MLflow experiment and register three prompt variants (zero-shot, few-shot, chain-of-thought) under the same registered prompt name with aliases `v1`, `v2`, `v3`.
2. Write a rubric function that scores a model response on three binary criteria: correct format, correct answer, no hallucinated content.
3. Run each prompt variant against five test inputs using the Anthropic API (model: `claude-opus-4-8`). Score every response with the rubric.
4. Log each run's scores, prompt alias, and input/output to MLflow as run metrics.
5. Print a comparison table: prompt variant, pass rate, and the winning alias.

**Done when**

- `mlflow ui` shows three logged runs with at least three metrics each.
- The comparison table prints to stdout with a clear winner identified.
- Rolling back to `v1` (by alias) and re-running produces the same scores as the first run.

**Stretch** — Add a fourth variant using DSPy's `BootstrapFewShot` teleprompter to auto-optimize the prompt, register it as `v4-dspy`, and include it in the comparison table.
