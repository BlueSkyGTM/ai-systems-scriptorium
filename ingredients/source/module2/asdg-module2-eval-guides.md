# Module 2 · Evaluation Companion Guides — Structure  [THREAD: eval]

> Source: two root-level guides. Structure extraction only (each ~3,400 lines). `[THREAD: eval]` applies throughout.

---

## Guide 1 — AI Evals For Engineers, PMs & QAs: Complete Study Guide (LangWatch & Langfuse)

This guide is the most comprehensive evaluation treatment in the curriculum, covering the full lifecycle from observability setup through production monitoring, statistical correction, and human annotation. It is specifically oriented around the LangWatch and Langfuse platforms, providing platform-specific methods and integration patterns. The guide spans 16 chapters plus 7 appendices, including production-grade judge prompts and a 30-day learning path.

### Top-Level Structure

- **Table of Contents** — Navigation index for the full guide.
- **Chapter 1: What Are AI Evals and Why You Need Them** — Foundational motivation for evaluation: defines what AI evals are, distinguishes them from traditional software testing, and makes the case for why engineering, PM, and QA teams all need structured evaluation practices. Likely covers the cost of not evaluating, the spectrum of eval types, and a high-level workflow.
- **Chapter 2: Setting Up Observability** — Practical setup of tracing and observability tooling using LangWatch and Langfuse. Covers instrumentation, span capture, trace visualization, and establishing the data foundation upon which all subsequent evaluation work depends.
- **Chapter 3: Error Analysis: The Secret Sauce** — Methodology for systematically analyzing LLM errors to identify root causes and patterns. Includes taxonomy of common error types, workflows for triage, and how to turn error findings into actionable evaluation criteria.
- **Chapter 4: Building LLM-as-a-Judge Evaluators** — Deep dive into constructing automated evaluators powered by LLMs. Covers judge prompt design, scoring rubrics, evaluator calibration, handling edge cases, and production-ready judge prompt templates.
- **Chapter 5: Code-Based Evaluators** — Deterministic and programmatic evaluation approaches: regex checks, schema validation, length/count metrics, semantic similarity thresholds, and hybrid code-plus-LLM evaluators. Covers when code-based methods are preferable over LLM judges.
- **Chapter 6: RAG System Evaluation** — Specialized evaluation for retrieval-augmented generation: retrieval quality (precision/recall of chunks), generation quality (faithfulness, groundedness), and end-to-end RAG metrics. Covers component-level vs. pipeline-level evaluation strategies.
- **Chapter 7: Multi-Step Pipeline Evaluation** — Evaluation of complex, multi-stage LLM pipelines where intermediate steps must be assessed individually and as a chain. Includes pipeline state evaluators, intermediate output validation, and tracing evaluation across nodes.
- **Chapter 8: Multi-Turn Conversation Evaluation** — Methods for evaluating conversational agents across multiple turns: coherence over context windows, intent resolution, conversational degradation detection, and turn-by-turn scoring.
- **Chapter 9: Production Evals: Safety, Guardrails & Monitoring** — Runtime evaluation and safety infrastructure: input/output guardrails, toxicity detection, PII leakage checks, jailbreak resistance, and continuous monitoring strategies for production traffic.
- **Chapter 10: Statistical Correction with judgy** — Using the `judgy` library for statistical validation of evaluation results. Covers inter-rater reliability, confidence intervals, statistical significance testing for eval comparisons, and correcting for evaluator bias.
- **Chapter 11: Closing the Loop — From Evals to Improvements** — Translating evaluation results into system improvements: prompt iteration, retrieval tuning, model selection, and building feedback loops between eval findings and development cycles.
- **Chapter 12: Human Annotation Best Practices** — Guidelines for structured human evaluation: annotation guidelines, labeler training, inter-annotator agreement metrics, gold-set construction, and managing disagreement.
- **Chapter 13: Cost, Latency & Scaling Evals** — Operational concerns: cost of running large-scale evaluations, latency optimization for eval pipelines, batch processing strategies, caching judge results, and prioritizing which evals to run on every deploy vs. periodically.
- **Chapter 14: Practical Implementation Guide** — Step-by-step integration playbook: wiring evals into CI/CD, setting up eval datasets, configuring eval suites for different environments (dev, staging, production), and establishing team workflows.
- **Chapter 15: Common Mistakes to Avoid** — Anti-patterns and pitfalls in AI evaluation: over-reliance on a single judge, eval set contamination, metric gaming, ignoring distribution shift, and other documented failure modes.
- **Chapter 16: Tools and Resources** — Curated reference of evaluation tools, libraries, datasets, benchmarks, and community resources beyond LangWatch and Langfuse.
- **Appendix A: Glossary for PMs & QAs** — Definitions of evaluation terminology tailored for non-engineering stakeholders.
- **Appendix B: Quick Reference** — Condensed cheat-sheet of key formulas, decision trees, thresholds, and config snippets for rapid day-to-day reference.
- **Appendix C: Complete Judge Prompts from Production** — Full, production-tested LLM-as-a-judge prompt templates with annotations explaining design choices.
- **Appendix D: Pipeline State Evaluator Prompts** — Judge prompts specialized for evaluating intermediate state in multi-step pipelines.
- **Appendix E: Judge Prompt Engineering Tips** — Techniques for iteratively improving judge prompts: few-shot examples, chain-of-thought reasoning, rubric refinement, and avoiding common judge biases.
- **Appendix F: Platform Methods Reference (LangWatch & Langfuse)** — API and SDK reference for evaluation-related methods in LangWatch and Langfuse: tracing APIs, evaluation APIs, batch evaluation endpoints, and integration code samples.
- **Appendix G: 30-Day Learning Path** — Day-by-day curriculum for progressively mastering AI evaluation, structured from foundational concepts through advanced implementation.
- **Lessons Learned** — Distilled insights and takeaways from real-world evaluation deployments.
- **Conclusion** — Summary of key principles and forward-looking perspective on the evaluation discipline.
- **Learning Resources** — External reading, courses, papers, and community links for continued study.

---

## Guide 2 — AI Evals For Engineers, PMs & QAs: Complete Study Guide (Phoenix & Langfuse)

This guide mirrors the structure and coverage of Guide 1 but is oriented around the Arize Phoenix and Langfuse platforms rather than LangWatch. It provides the same chapter-by-chapter depth across the evaluation lifecycle, from observability through production safety, statistical correction, and human annotation. The platform-specific appendix references Phoenix and Langfuse APIs in place of LangWatch.

### Top-Level Structure

- **Table of Contents** — Navigation index for the full guide.
- **Chapter 1: What Are AI Evals and Why You Need Them** — Foundational definitions and motivation for structured AI evaluation across engineering, PM, and QA roles. Covers the gap between traditional testing and LLM evaluation, and introduces the core evaluation workflow.
- **Chapter 2: Setting Up Observability** — Instrumentation and tracing setup using Phoenix and Langfuse. Covers span/trace capture, project organization, trace visualization, and building the observability layer that evaluation depends on.
- **Chapter 3: Error Analysis: The Secret Sauce** — Systematic error discovery and classification methodology. Covers error taxonomies, triage workflows, and the conversion of recurring error patterns into automated evaluation checks.
- **Chapter 4: Building LLM-as-a-Judge Evaluators** — Comprehensive treatment of LLM-powered automated judges: prompt construction, scoring rubric design, multi-criteria evaluation, calibration against human labels, and judge reliability assessment.
- **Chapter 5: Code-Based Evaluators** — Programmatic evaluation techniques: structural validation, output format checks, lexical metrics, embedding-based similarity, and composing code-based checks with LLM judges in hybrid evaluators.
- **Chapter 6: RAG System Evaluation** — Evaluation decomposed across the RAG pipeline: chunk retrieval metrics, context relevance, answer groundedness and faithfulness, and end-to-end evaluation harness design for RAG systems.
- **Chapter 7: Multi-Step Pipeline Evaluation** — Evaluating each stage of multi-step LLM workflows independently and in aggregate. Covers intermediate-state evaluation, pipeline-level quality propagation, and failure attribution across nodes.
- **Chapter 8: Multi-Turn Conversation Evaluation** — Techniques for scoring multi-turn agent interactions: contextual coherence, task completion across turns, regression detection, and evaluation of memory/context management.
- **Chapter 9: Production Evals: Safety, Guardrails & Monitoring** — Production-grade safety evaluation and runtime guardrails: content classification, prompt injection detection, output filtering, and ongoing monitoring of live traffic for safety regressions.
- **Chapter 10: Statistical Correction with judgy** — Statistical methods for validating evaluation results using the `judgy` library: evaluator agreement metrics, significance testing, bias correction, and sample-size determination for eval confidence.
- **Chapter 11: Closing the Loop — From Evals to Improvements** — Operationalizing evaluation findings into systematic improvement: prompt engineering cycles, dataset curation, model comparison workflows, and tracking improvement metrics over time.
- **Chapter 12: Human Annotation Best Practices** — Structured human evaluation methodology: annotation schema design, rater training, quality control, agreement metrics, and integrating human labels with automated evaluators.
- **Chapter 13: Cost, Latency & Scaling Evals** — Scaling evaluation economically and operationally: cost modeling for judge-based evals, async and batch evaluation patterns, caching strategies, and tiered evaluation (run critical evals on every change, comprehensive evals on release).
- **Chapter 14: Practical Implementation Guide** — End-to-end implementation walkthrough: dataset assembly, eval suite configuration, CI/CD integration, team roles and workflows, and environment-specific eval strategies.
- **Chapter 15: Common Mistakes to Avoid** — Documented anti-patterns: single-judge over-reliance, metric Goodhart's law effects, dataset drift, over-fitting to eval sets, and ignoring evaluation of failure modes.
- **Chapter 16: Tools and Resources** — Reference catalog of complementary evaluation tools, benchmark datasets, and resources beyond Phoenix and Langfuse.
- **Appendix A: Glossary for PMs & QAs** — Terminology reference for non-engineering team members.
- **Appendix B: Quick Reference** — Condensed reference card for metrics, thresholds, decision heuristics, and common configuration patterns.
- **Appendix C: Complete Judge Prompts from Production** — Full production judge prompt library with explanatory annotations.
- **Appendix D: Pipeline State Evaluator Prompts** — Specialized judge prompts for intermediate pipeline state evaluation.
- **Appendix E: Judge Prompt Engineering Tips** — Practical guidance for refining judge prompts: example selection, reasoning strategies, rubric iteration, and bias mitigation.
- **Appendix F: Platform Methods Reference (Phoenix & Langfuse)** — SDK and API reference for Phoenix and Langfuse evaluation and tracing methods, with integration code examples.
- **Appendix G: 30-Day Learning Path** — Structured day-by-day progression plan for mastering AI evaluation from fundamentals to production deployment.
- **Lessons Learned** — Consolidated real-world insights and retrospective takeaways.
- **Conclusion** — Synthesis of core evaluation principles and outlook on evolving practices.
- **Learning Resources** — External references, papers, tools, and community resources for ongoing learning.
