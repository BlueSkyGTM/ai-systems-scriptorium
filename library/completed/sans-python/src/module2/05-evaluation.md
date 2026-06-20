# Evaluation

You can't ship what you can't measure. LLM applications fail silently — a prompt change that helps one case breaks three others, and you find out from a user complaint six weeks later. Eval-driven development breaks that cycle by making quality visible before it escapes.

## Why traditional testing fails here

Unit tests pass or fail. LLM outputs are correct or incorrect on a spectrum, and the spectrum shifts with every model update, every prompt edit, every change to the retrieval corpus. Exact-match metrics miss semantic equivalence. Human review doesn't scale. The production answer is **LLM-as-judge**: an automated evaluator powered by a model, scoring outputs against a rubric.

The inner loop runs during development — model selection, prompt iteration, RAG tuning — before any code hits staging. The outer loop runs in production — monitoring live traffic, detecting drift, catching regressions. Both loops use the same discipline. The inner loop is where this lesson lives.

## The lifecycle: from traces to improvements

### 1. Set up observability

You can't evaluate what you can't see. Before you write a single judge prompt, instrument your application with tracing. LangWatch, Arize Phoenix, and Langfuse capture span-level data: what the model received, what it returned, how long each step took, what it cost. Every evaluation check runs against this trace data.

Tracing is the data foundation. Skip it and you're debugging with print statements.

### 2. Error analysis

Systematic error analysis is the underrated step. Build a taxonomy of your failure modes: wrong answer, hallucinated citation, wrong format, off-topic response, contradicts the retrieved context. Triage a sample of traces against it. The categories you find most often become your eval criteria.

This is what the guides call "the secret sauce." Most teams jump straight to building judges without knowing what they're judging for. Error analysis tells you.

### 3. Build LLM-as-judge evaluators

A judge is a model call with a rubric. The prompt receives the input, the output under evaluation, and (when relevant) the expected output — then scores against a criterion.

Design rules:

- **Binary over scaled.** "Did the answer correctly cite the source document? Yes or No" is more reliable than "Rate answer quality 1–5." Scales introduce rater drift and make aggregation meaningless.
- **One criterion per judge.** A judge that scores faithfulness, relevance, and format in one call conflates signals. Run three separate judges.
- **Freeze the judge model.** Version-pin the model and prompt used to generate scores. A silent model update changes your scores retroactively.
- **Calibrate against human labels.** Score a set of human-labeled examples — a hundred is a reasonable target. Treat the judge as trustworthy only at a strong rank correlation with those labels; Spearman ρ around 0.7 or higher is a common bar. Below that, the judge is measuring something, but not what you think.
- **Avoid self-preference.** A model asked to evaluate its own output is biased toward that output. Use a different model as judge, or a dedicated evaluator.

### 4. Code-based evaluators

Not everything needs a model. Deterministic checks are cheaper, faster, and perfectly reproducible: schema validation (is the JSON valid?), length bounds (is the answer between fifty and two hundred tokens?), format checks (does the output include the required section headers?), regex patterns (does the citation match `[Author, Year]` format?).

Hybrid evaluators combine code and LLM: code filters out the obvious failures first, then the judge handles the ambiguous cases. You pay LLM costs only where a model judgment is necessary.

### 5. RAG evaluation — the triad

RAG failures split into three independent components:

- **Context relevance** — did retrieval return chunks related to the query? (Retrieval quality)
- **Groundedness** — does the generated answer stay within what the retrieved context says? (Faithfulness, no hallucination)
- **Answer relevance** — does the answer address what the user asked? (End-to-end quality)

Score all three. An answer can score high on groundedness (no hallucination) and low on context relevance (the retrieved chunks were off-topic) — those are different bugs with different fixes. The RAG triad decomposes the pipeline so you know which component failed.

### 6. Multi-step and multi-turn evaluation

Multi-step pipelines — where one model call feeds the next — require evaluating intermediate state, not just the final output. A failure at step two propagates forward and shows up as a failure at step five. Trace the pipeline and evaluate each node. Failure attribution tells you where the error originated.

Multi-turn conversation evaluation adds a temporal dimension: does the agent maintain coherent context across turns? Does it correctly incorporate what the user said three turns ago? Score turn-by-turn coherence and task completion across the full conversation, not just the last response.

### 7. Statistical correction

A judge score is a noisy measurement. Before you act on an evaluation result, know how noisy it is.

The `judgy` library computes inter-rater reliability, confidence intervals, and significance testing for judge-based evaluations. The workflow: run your judge over a test set, compute a confidence interval on the aggregate score, and run a significance test before declaring one prompt variant better than another. A difference in pass rate from 78% to 80% is likely noise. A difference from 78% to 91% is likely real — but you need the statistics to know which.

Confidence intervals on Wilson or bootstrap methods are more honest than point estimates. Report them.

### 8. Close the loop

Evaluation findings are not reports — they're action items. Map each failure category to a hypothesis: wrong answer → prompt needs more context; hallucinated citation → groundedness judge fires, retrieval needs reranking; wrong format → add a format constraint to the system prompt. Build the iteration cycle and track whether each change moved the eval metric. That's the inner loop.

## Why the AI Platform Engineer owns this

Build owns the prompt. Deploy owns the serving layer. Neither owns the eval pipeline — it spans both. You define what quality means, instrument it, run it in CI, and close the gap between development-time expectations and production-time behavior. Evals are the regression suite for non-deterministic systems, and the AI Platform Engineer is the one who builds and runs them.

## Core concepts

- LLM-as-judge is the production answer to quality measurement: exact-match and human review both fail to scale.
- The RAG triad (context relevance, groundedness, answer relevance) scores the three independent failure modes in a retrieval-augmented system — an answer can fail on one dimension while passing on the others.
- Judge reliability requires calibration against ~100 human labels and a Spearman ρ ≥ 0.7 threshold; freeze the judge model and version-pin its prompt.
- Eval-driven development closes the loop: error analysis → judge design → statistical correction → prompt or retrieval fix → re-eval, iterated.

<div class="claude-handoff" data-exercise="exercises/module2/05-evaluation/">

**Build It in Claude Code** — build an eval framework that traces a RAG pipeline, scores outputs on the RAG triad with an LLM-as-judge, runs statistical correction with confidence intervals, and produces a pass/block report.

</div>
