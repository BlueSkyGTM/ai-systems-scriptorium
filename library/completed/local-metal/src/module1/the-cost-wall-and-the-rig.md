# The Cost Wall and the Rig

Every engineer who ships an AI feature eventually opens an invoice and does the arithmetic. A background
agent that runs all day, a coding assistant that holds a 100k-token context, a pipeline that retries on
every failure: each of these is metered inference, and the meter never stops.

## When the Bill Arrives

Frontier APIs price by the token. Claude Sonnet 4.6 runs $3.00 per million input tokens and $15.00 per
million output tokens; GPT-4o sits at $2.50 in, $10.00 out (as of June 2026; these rates change, verify
at the source before you model them). At low volumes that is cheap. At the volumes an agent accumulates
across a working day, it is a recurring line item.

The math compounds in three ways. First, tokens stack faster than most engineers expect: a 200k-token
context flushed and refilled ten times in a day is 2 million tokens before the agent does anything
useful. Second, retries multiply the count; a fragile tool call that fails three times before succeeding
triples its cost. Third, context windows overflow. When a conversation exceeds the window, you truncate
or summarize, and both paths cost output tokens you pay for to avoid paying for the tokens you cannot
keep.

None of this is a design flaw. Frontier APIs price the hardest work right: complex reasoning, broad
knowledge, and the latest model weights. The flaw is paying frontier rates for the routine work, the
code completions, the diff reviews, the prompt-to-struct transformations, that a smaller model handles
equally well.

## The Home-Scale Answer

The rig is a small-form-factor machine you build once, put on your desk, and run forever. Its marginal
cost per token is the electricity to compute it. A 14-billion-parameter coding model fits entirely in
the GPU's 16GB of VRAM; a 32B-to-70B quantized model splits across the card and system RAM. The machine
does not know or care how many tokens it processes in a day.

The reference build in this book totals roughly $1,450-$1,685 (the exact price turns on open-box
availability the day you buy). That is a one-time capital cost, not a subscription. You amortize it
against what you would have spent on metered inference, and at any realistic agent volume, the
break-even arrives within months.

What the rig is not: a datacenter, a cluster, or a replacement for the frontier. It is one machine that
handles the ninety percent of your inference that does not need the frontier's ceiling. The routing layer
you build in Module 5 is what decides, per request, which model answers it.

## The Arc from Here

This module gets the machine built and proved stable. The modules that follow fill the stack: Module 2
installs Linux and CUDA, Module 3 pulls the first models and confirms they fit, Module 4 measures
real throughput, Module 5 builds the routing layer that decides local or frontier per request, and
Module 6 wires the whole thing into Claude Code as a delegation target.

The rig is infrastructure. The value is everything that runs on it.

## Core Concepts

- Frontier-API costs compound: context size, retry count, and daily agent volume multiply against a
  per-token rate that never stops.
- A 14B coding model fits entirely in 16GB of VRAM; the rig's marginal cost per token is electricity,
  not a metered rate.
- The break-even on a one-time hardware investment arrives within months at realistic agent volumes,
  not years.
- The rig handles the routine ninety percent; the routing layer decides what the frontier handles.

<div class="claude-handoff" data-exercise="exercises/module1/the-cost-wall-and-the-rig/">

**Build It in Claude Code**: Build `breakeven.py`, a stdlib-only cost model that prints the month when cumulative local cost drops below cumulative frontier spend.

</div>

<!-- SOURCES: https://platform.claude.com/docs/en/about-claude/pricing | https://openai.com/api/pricing/ -->
