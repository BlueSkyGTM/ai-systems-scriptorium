# Prompt engineering

Every output a model gives you is a function of what you put in. The question isn't whether the prompt matters — it always does — it's whether you're engineering it or just hoping.

## Anatomy of a prompt

An LLM API call carries a tiered instruction hierarchy. The **system** message sets the model's role and constraints — it runs before the user sees anything and carries the highest trust. Below it sits the **user** message, the runtime input. The model's prior replies return in the **assistant** role — conversation history, the lowest-trust tier. Some providers add a **developer** tier between system and user for technical overrides that shouldn't be user-editable.

The order matters: instructions closer to the top outweigh instructions lower down. A system-level guardrail survives a user-level override attempt. A user-level instruction outranks anything the assistant turn carries. Build with the hierarchy, not against it.

**Role prompting** is the most direct use of the system tier. You aren't decorating the model — you're anchoring its capabilities. `You are a triage nurse classifying patient symptoms by urgency` shifts the vocabulary, the reasoning pattern, and the output structure. Use delimiters — XML tags, triple backticks, or clear labeled sections — to separate the parts of your prompt so the model doesn't hallucinate context boundaries.

## Few-shot and in-context learning

A few-shot example shows the model what *done* looks like. Each example has three parts: a realistic input, optional reasoning, and a gold-standard output. The model reads the pattern and continues it.

Optimal example counts scale inversely with model size. A frontier model needs one or two examples to lock onto a format; a smaller model may need five to ten. More examples beyond the knee of that curve add latency and dilute attention — the model starts tracking every example equally instead of reasoning from them.

In production, you replace static example lists with **dynamic example selection**: a vector DB of gold examples, queried at runtime by semantic similarity to the current input. This keeps your few-shot payload compact and locally relevant. Two things to watch: label distribution bias (if your gold set skews toward one category, the examples you retrieve will too) and attention dilution (too many examples spread the model's attention across all of them, weakening each).

## Chain-of-Thought

Chain-of-Thought (CoT) puts the model's working memory on the page before it answers. The simplest form is zero-shot: append "think step by step" and the model produces intermediate reasoning before its final answer. Few-shot CoT shows worked examples of that reasoning. Programmatic CoT breaks reasoning into explicit, numbered steps for agent pipelines where you need to inspect intermediate state.

Modern reasoning models — those with extended thinking or hidden reasoning windows — bake CoT into the architecture via reinforcement learning. You don't prompt for it; you configure a thinking budget. The tradeoff is real: longer thinking reliably improves hard tasks and reliably over-thinks easy ones. Use a hybrid routing layer — classify query complexity first, then route to the right reasoning tier.

Layer **self-verification** on top: generate, then critique, then correct. For code, go further with execution-verified CoT — write, run, fix. The model's reasoning is no longer guesswork; it has a ground truth to check against.

## Tree-of-Thought

Where CoT is linear, Tree-of-Thought (ToT) is branching. The architecture runs a loop: a **thought proposer** generates three to five candidate next steps, a **state evaluator** grades each as viable or dead, and a search algorithm (BFS or DFS) traverses the branches. Errors get caught at the evaluator before they cascade.

The cost is steep: exploring a branch to depth can require fifteen to twenty model calls for a single query. That makes ToT the wrong choice for real-time requests and the right choice for high-stakes offline tasks — generating a gold evaluation dataset, refactoring a legacy codebase, solving a logic puzzle where one wrong step ruins the whole answer.

## The versioning thread

Prompts drift. A prompt you shipped in March behaves differently in September because the model updated, the data shifted, or a well-meaning colleague added a clause. Treat prompts as versioned artifacts — the same way you version code. MLflow's prompt registry stores prompt text with version aliases (`champion`, `challenger`, `staging`) so you can run experiments and roll back without touching application code.

This is a development-time practice, not a production afterthought. Every prompt that matters ships with a registry entry and a version tag. When the model swaps, you recompile; you don't guess.

The prompt is the program — and an AI Platform Engineer treats it as versioned, testable infrastructure, not a string in a config file.

## Core concepts

- The instruction hierarchy (system → developer → user → assistant) determines which instructions survive conflict — higher tiers outweigh lower ones.
- Few-shot example count scales inversely with model size; dynamic example selection via semantic search replaces static lists in production.
- Chain-of-Thought externalizes reasoning before the answer; the inference-scaling tradeoff means longer thinking helps hard tasks and hurts easy ones.
- Tree-of-Thought catches hallucination cascades early via a branching evaluator loop, at a cost (fifteen to twenty calls per query) that limits it to offline, high-stakes use.

<div class="claude-handoff" data-exercise="exercises/module2/01-prompt-engineering/">

**Build It in Claude Code** — build a prompt-testing harness that versions three prompt variants in an MLflow registry and scores them against a rubric.

</div>
