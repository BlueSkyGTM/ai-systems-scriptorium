# Exercise: Evaluation `[THREAD: eval]`

**Goal** — Build an eval framework that traces a RAG pipeline, scores outputs on the RAG triad with an LLM-as-judge, runs statistical correction with confidence intervals, and outputs a pass/block report.

**Why** — Evals are the regression suite for non-deterministic systems; without this framework, every prompt change is a gamble.

**Steps**

1. Instrument a toy RAG pipeline (three documents, five test queries) with OpenTelemetry spans. Each span must capture: query, retrieved chunks, generated answer, latency.
2. Write three binary LLM-as-judge evaluators — one per RAG triad dimension (context relevance, groundedness, answer relevance) — using `claude-opus-4-8` as the judge model. Each judge returns `{"score": 0 | 1, "reason": "..."}`.
3. Run all five queries through the pipeline. Score every output on all three dimensions. Log each judge call as a child span.
4. Add a code-based evaluator that checks whether the answer is between 30 and 300 tokens (format compliance). Run it alongside the LLM judges.
5. Use `judgy` (or implement Wilson confidence intervals manually if `judgy` is unavailable) to compute a 95% confidence interval for each dimension's pass rate across the five queries.
6. Print a pass/block report: dimension name, pass count, pass rate, 95% CI. Flag `BLOCK` if the lower CI bound for any dimension falls below 0.6.

**Done when**

- The trace output shows at least five root spans with child judge spans attached.
- The report prints pass rates and confidence intervals for all four evaluators (three LLM-as-judge + one code-based).
- Changing one retrieved document to an off-topic chunk causes context relevance to drop and trigger a `BLOCK`.

**Stretch** — Add a second prompt variant for the generation step and run a significance test (Fisher's exact or bootstrap permutation) to determine whether the difference in groundedness scores between the two variants is statistically significant. Report the p-value alongside the CIs.
