# Debate & Multi-Agent Failure Modes (MAST)

Multi-agent systems fail at rates that should stop you cold; the Berkeley study behind this lesson found correctness on some popular systems falling as low as 25%, and analyses of the field routinely report failure rates well above 40%. The reflex is to blame the model and wait for a better one. That reflex is wrong, and proving it is this lesson's job: most multi-agent failures are flaws in how you wired the system, not ceilings in the model running inside it. First, though, the pattern that shows what coordination can earn when it works.

## Debate: a Society of Minds

The oldest good idea in multi-agent is also one of the most reliable. Run N copies of a model on the same question. Let each propose an answer. Then show each one the others' answers and let them critique and revise; for R rounds, until they converge. Du and colleagues, in *Improving Factuality and Reasoning in Language Models through Multiagent Debate*, called it a "society of minds," and it beats a single model's zero-shot answer on factuality, rule-following, and reasoning.

Two findings make it more than a trick. Both *more agents* and *more rounds* contribute, and they contribute independently; adding agents alone plateaus, adding rounds alone barely moves, but together they produce the jumps. And debate across *different* base models beats debate among copies of one, because different models make different errors, and uncorrelated errors cancel where a monoculture's errors compound.

## Sparse Topology: the Same Accuracy, a Fraction of the Tokens

Here is the part that matters for the bill. The obvious way to run debate is full-mesh; every agent reads every other agent every round. With five agents over three rounds that's sixty critique operations, and tokens scale with the edges.

You don't need the edges. A sparse topology, a star (everyone reads one hub) or a ring (each reads one neighbor), matches full-mesh accuracy at a fraction of the cost. Star, five agents, three rounds: twelve critique operations instead of sixty. The accuracy holds because consensus doesn't require everyone to read everyone; it requires enough cross-pollination to break correlated errors, and a sparse graph delivers that.

The lesson generalizes past debate: topology is a cost knob, not just a correctness knob. The densest wiring is rarely the right one. Wire the minimum that breaks error correlation and stop.

## MAST: Fourteen Ways It Breaks

Now the wall. Berkeley's MAST study; the Multi-Agent System Failure Taxonomy, from Cemri and colleagues' *Why Do Multi-Agent LLM Systems Fail?*; read 1,600-plus traces from real multi-agent systems and catalogued fourteen distinct failure modes, with annotator agreement high enough (κ = 0.88) that these are real categories, not impressions. They sort into three families.

**Specification problems**; the largest share, around 42%. Role ambiguity, underspecified tasks, an agent that doesn't know what "done" means. The system fails before any coordination happens, because the work was never pinned down.

**Coordination failures**; around 37%. State desynchronization, lost messages, agents talking past each other. This is the handoff knob from lesson 03 breaking under load.

**Verification gaps**; around 21%. No independent check, so a wrong answer ships because nobody was assigned to catch it.

You don't need to memorize fourteen. Five recur often enough to name and watch for:

- **Hallucinated actions**; an agent invents a tool call or a step that doesn't exist.
- **Scope creep**; an agent quietly expands its task beyond what it was given, narrating each step in good faith.
- **Cascading errors**; one agent's mistake becomes the next agent's trusted input, and accuracy decays down the chain.
- **Context loss**; a handoff drops the detail the next agent needed, and it proceeds without it.
- **Tool misuse**; right tool, wrong arguments, or the wrong tool for the job.

## The Claim That Should Change How You Build

These are design flaws, not model limitations. That sentence is the lesson.

A better base model does not fix a role you never specified. It does not fix a handoff that drops context, or a chain with no verifier, or a blackboard that lets a hallucinated fact propagate. Swap the strongest model in the world into a system with a verification gap and you get a strong model confidently shipping unverified answers. The failure lives in the wiring, the specification, the coordination, the missing check, and wiring is something you own, not something you wait on a model release to repair.

This is why the back half of this module is built the way it is. Budgets, kill switches, propose-then-commit checkpoints, fleet registries with explicit identity and audit; every one of them is a design answer to a MAST family. Specification problems demand explicit scope contracts. Coordination failures demand typed handoffs and audited state. Verification gaps demand an independent verifier the builder can't overrule. You are not waiting for the model to get good enough. You are building the system that makes a good-enough model reliable.

## The Seam This Sits On

Debate is the AI Engineer's question; can coordination produce a better answer, and how sparsely can I wire it. MAST is the MLOps engineer's answer; most of what breaks is operational, and operational problems get operational fixes. An AI Platform Engineer holds both: reach for debate when accuracy justifies the tokens, wire it sparse, and treat every failure mode as a design input rather than a model complaint. The model is not the variable you control. The system around it is.

## Core Concepts

- Multi-agent debate ("society of minds") improves factuality and reasoning by having N agents propose then critique over R rounds; agent count and round count contribute independently, and cross-model debate beats a single-model monoculture by decorrelating errors.
- Sparse debate topologies (star, ring) match full-mesh accuracy at a fraction of the token cost; topology is a cost knob, so wire the minimum that breaks error correlation and stop.
- MAST documents fourteen multi-agent failure modes in three families (specification ~42%, coordination ~37%, verification ~21%); the five recurring ones, hallucinated actions, scope creep, cascading errors, context loss, tool misuse, are design flaws, not base-model limitations, so a better model doesn't fix them and the governance stack does.

<div class="claude-handoff" data-exercise="exercises/module4/04-debate-and-failure-modes/">

**Try It in Claude Code**: In `module4-fleet/`, run a debate between the harness agents with both full-mesh and star topology and confirm the star matches accuracy at far lower token cost. Then add a failure-mode tagger that labels traces with the five recurring MAST modes, and trigger one on purpose.

</div>
