# Why multi-agent — the single-agent ceiling

You built one agent that runs a loop, holds memory, and stays inside a budget. The temptation now is to make it bigger — more tools, a longer system prompt, a wider window. That instinct is wrong, and knowing why is the first thing this module teaches: past a certain point you don't scale an agent, you split it, and that split is where governance starts to cost real money.

## The complexity ladder, one rung higher

Module 2 gave you the complexity ladder, and Module 3 made you climb it. A direct model call when the answer comes from training or assembled context. A workflow when the steps are knowable up front. A single agent when the next step genuinely depends on the last. Each rung earns its place only when the rung below it can't do the job.

Multi-agent is the next rung, and it obeys the same rule. You don't reach for it because it sounds powerful. You reach for it when one agent has hit a wall you can name.

There are three walls, and they are concrete.

**Context overflow.** A task needs more material than fits in one window — a 200-file codebase, a quarter of support tickets, a research question that spans forty sources. You can summarize and lose detail, or you can split the work across agents that each hold a slice. The second is multi-agent.

**Mixed expertise in one prompt.** A single system prompt that has to be a careful researcher *and* a terse code reviewer *and* a diplomatic writer is none of them well. Instructions for one role dilute the others. Splitting roles into separate agents gives each a clean, undiluted prompt.

**The sequential bottleneck.** The work is parallelizable — ten independent sub-questions, fifty files to lint — but one agent does them one at a time. Fan the work out across agents and the wall-clock time collapses.

If your problem hits none of these, you do not have a multi-agent problem. You have a prompt you haven't tightened yet.

## More agents, not a bigger agent

This is the load-bearing reframe. When a single agent strains, the engineer's reflex is to give it more — more tools in the registry, more context stuffed in, more instructions piled on. Each addition makes the agent slower to reason and easier to confuse. A tool registry of sixty tools is a worse agent than one of six, because the model now spends its attention choosing badly among options it half-understands.

The move past the ceiling is *more agents, not a bigger agent*. Three focused agents — each with a narrow tool set, a clean prompt, and a fresh context — outperform one agent carrying all three jobs, and they do it for a reason you can measure. Anthropic's internal research system, an orchestrator delegating to subagents in fresh parallel contexts, beat a single-agent baseline by 90% on their research eval, and the gain traced to one mechanism: each subagent started with a clean window instead of inheriting the lead's clutter.

Fresh context per agent is the whole trick. It is also what makes the system harder to run.

## The bill comes due

Multi-agent is not free, and the costs are not footnotes. Three of them will shape every decision in this module.

**Latency.** A supervisor that delegates to three workers and waits for all three is bounded by the slowest worker, plus its own planning and synthesis turns. Even fanned out in parallel, you've added round-trips a single agent never paid.

**Token cost.** More agents means more model calls. Anthropic measured their multi-agent system burning roughly four times the tokens of a single agent on the same task — about fifteen times a plain chat. The accuracy can be worth it. The bill is real, and someone signs it.

**Debugging difficulty.** When one agent fails you read one trace. When five agents coordinate, a failure can hide in the handoff between two of them — a misread instruction, a lost message, a hallucinated "fact" that a downstream agent trusted. The trace is now a graph, and the bug lives on an edge. This is the failure surface lesson 04 catalogs and the rest of the module learns to govern.

So multi-agent buys you scale and pays for it in latency, money, and observability. That trade is the whole reason the back half of this module exists: budgets, kill switches, human checkpoints, and fleet governance are what make the trade survivable in production.

## The seam this module sits on

Single agent to many is the seam's defining move. The AI Engineer half asks *will the coordination produce a better answer* — topology, debate, role specialization. The MLOps half asks *what does it cost to run, and how do I stop it when it goes wrong* — budgets, identity, audit, kill switches. A bigger agent hides both questions inside one process. Splitting into many forces both into the open, which is exactly why an AI Platform Engineer has to own them. The next lesson starts at the open question: once you have many agents, how do they talk without lying to each other.

## Core concepts

- Multi-agent is the next rung of the complexity ladder: reach for it only when a single agent hits a nameable wall — context overflow, mixed expertise in one prompt, or a sequential bottleneck.
- The move past the single-agent ceiling is more agents, not a bigger agent; a focused agent with a fresh context outperforms one agent carrying every role, and fresh-context-per-agent is the mechanism that earns the gain.
- Multi-agent buys scale and pays in latency, token cost (several times a single agent's, an order of magnitude over a plain chat), and debugging difficulty — costs real enough that the rest of the module is about governing them.

<div class="claude-handoff" data-exercise="exercises/module4/01-why-multi-agent/">

**Build It in Claude Code** — start the `module4-fleet/` throughline by deciding, on paper and in code, when a single agent is enough and when it isn't. Run the `_harness/` orchestrator, force a task past one of the three walls, and document the ceiling you hit.

</div>
