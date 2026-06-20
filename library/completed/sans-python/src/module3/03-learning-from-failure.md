# Learning from failure

An agent that fails the same way twice has a memory problem, not a model problem. The patterns in this lesson fix failures in language — the same language the agent already speaks — without touching a single weight.

## Reflexion: verbal reinforcement

Reflexion (Shinn et al., 2023) adds one step after a failed trial: the agent writes a reflection on what went wrong, stores it in an episodic memory buffer, and conditions the next trial on that reflection. The structure is three roles: an **Actor** that attempts the task, an **Evaluator** that scores the outcome, and a **Self-Reflector** that generates the verbal lesson.

On ALFWorld and HotpotQA, Reflexion outperforms ReAct by wide margins — not because the model improves, but because the agent stops repeating the failure it already diagnosed. The lesson is stored in working memory for the current task and in episodic memory for future sessions.

This is the same pattern behind `CLAUDE.md` learnings and the `/learn` command in Claude Code: when a trial fails, write a natural-language rule describing why, and prepend it to the next attempt. The agent improves without a fine-tune. (That's genuinely underrated — most practitioners reach for fine-tuning before they've tried writing the lesson down.)

**Evaluator types matter.** A scalar evaluator (correct/incorrect) is cheapest but coarsest. A heuristic evaluator (partial credit for each step) is richer for multi-step tasks. A self-evaluated critic (the model grades its own output) is flexible but unreliable on hard facts — which leads directly to the next pattern. These three types are a practical framing, not an established taxonomy; the key distinction is whether the quality signal is internal to the model or grounded externally.

Foundry's built-in agent evaluators follow the same logic: `IntentResolution` and `TaskAdherence` score agent runs against defined criteria, enabling the same evaluate-then-improve cycle in a managed runtime.

## Self-Refine and CRITIC: generate → feedback → refine

Self-Refine (Madaan et al., 2023) runs one model in three roles: generate a draft, critique it, refine based on the critique. It earns +20 absolute points across 7 tasks. The loop continues until the critique says the output is good enough or a round budget is exhausted.

The vulnerability is self-verification: LLMs are unreliable at catching their own factual errors, because the same model that generated the error is also grading it. CRITIC (Gou et al., 2023) hardens the feedback step by routing verification through external tools — a search engine, a code interpreter, a test runner, a calculator. The model cannot fake a test result.

Anthropic's evaluator-optimizer workflow is this pattern: a generator produces output, an evaluator with tool access scores it against ground truth, the generator refines based on the score. The evaluator is a separate call, sometimes a separate model, and it uses tools the generator cannot hallucinate around. Microsoft documents the same pattern explicitly — one LLM generates, another evaluates and feeds back, the loop runs until a termination condition is met.

The two-line rule: use Self-Refine when the quality signal is stylistic (fluency, coherence, tone). Use CRITIC when the quality signal is factual or execution-based (does this code run, is this claim true, does this SQL return the right rows).

## Reasoning as search: ToT and LATS (cost-gated)

Tree-of-Thoughts (Yao et al., 2023) turns reasoning into a search problem: instead of committing to one chain of thought, the model grows a tree of candidate thoughts, evaluates each node, and expands the most promising branches. On the Game of 24, standard chain-of-thought solves 4% of problems; ToT with BFS solves 74% — with GPT-4, which was the test model in the original paper.

LATS (Zhou et al., 2024) unifies ToT with ReAct and Reflexion under Monte Carlo Tree Search — select, expand, simulate, backpropagate. It achieves 92.7% on HumanEval by treating each reasoning step as a node, using the model to evaluate branches, and propagating failure signals back up the tree.

Apply the complexity-ladder cost test before reaching for either:

- ToT multiplies token cost by the branching factor times the depth. For a 5-branch, 3-level tree, that is 15× the cost of a straight chain.
- LATS multiplies further: each simulated path is a full rollout.

The multiplier is worth it for high-stakes, offline work where the correct answer is hard to find and easy to verify — mathematical proofs, code synthesis against a test suite, complex planning. It is not worth it for latency-sensitive production paths. Apply the cost test: if you can afford 10–15× the tokens and the task is offline, try ToT. If you cannot, stay with Reflexion.

## What you build

You extend `module3-agent/` with a Reflexion layer: an episodic memory that stores post-failure reflections, a Self-Reflector that writes the lesson, and a feedback loop that conditions the next trial. The CRITIC pattern — routing verification to an external tool — wires into the stop condition: the loop continues until the external check passes or the round budget is exhausted.

Get the evaluator wrong and every other improvement is noise.

## Core concepts

- Reflexion fixes repeated failures in natural language: the agent writes a verbal lesson after each failure, stores it in episodic memory, and conditions the next trial on it — no weight update required.
- LLMs self-verify poorly on hard facts; CRITIC hardens the feedback loop by routing verification through external tools (search, code execution, test runners) the model cannot hallucinate around.
- Tree-of-Thoughts and LATS multiply token cost by 10–15× or more; apply the complexity-ladder cost test and use them only for high-stakes, offline work where a fast external verifier exists.
- The evaluator-optimizer pattern — a generator and a separate evaluator with tool access — is the 2026 production form of iterative improvement.

<div class="claude-handoff" data-exercise="exercises/module3/03-learning-from-failure/">

**Build it in Claude Code** — extend `module3-agent/` with a Reflexion layer: an episodic memory buffer, a Self-Reflector that writes a verbal lesson after each failure, and a feedback loop that prepends the reflection to the next trial. Wire a CRITIC-style stop condition: the loop passes only when an external check (a stub verifier) confirms the output. Open the repo and run the exercise for this lesson.

</div>
