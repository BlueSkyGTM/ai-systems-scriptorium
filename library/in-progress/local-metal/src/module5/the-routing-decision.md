# The Routing Decision

The rig only pays off when something decides when to use it. That decision is not made once and left alone; it is made per request, and it is made from a short list of signals you can read before any model sees the prompt.

## Step 1: Cost Is the Motivation

Local inference has an amortized cost structure. You spent money on the card; the per-token cost after that is electricity, which rounds to near zero at home inference volumes. Cloud inference is metered: every token you send costs a fraction of a cent, and routine high-volume work compounds that into a real line item.

That asymmetry is why a router exists at all. Work that is high-volume, repetitive, and well-defined belongs on the rig you already paid for. Work that is rare, large, or where the best possible answer justifies the price belongs on a frontier model you pay per call. The router is the mechanism that enforces this split automatically rather than leaving it to memory.

## Step 2: The Per-Request Signals

Every request carries four signals. You read them before routing, not after.

**Context size** is the closest thing to a hard rule. A 14B model on a 16 GB card holds roughly 4K to 8K tokens of context comfortably: the KV cache grows with context length and competes with the model weights for the same VRAM, so long contexts shrink the headroom fast. Frontier models operate in a different class entirely; Claude models support 200K tokens, with some configurations reaching 1M. A request that exceeds the local model's window is not a latency question or a quality question, it is a fit question, and the answer is always cloud.

**Latency budget** points in both directions. The local model is slower, a fact you measured in Module 4. A background job or batch run tolerates that; a tight interactive loop, a streaming response the user is watching form, may not. But the local model also has no network round-trip, which means small fast jobs can actually land faster locally when the cloud overhead dominates. Read the budget for the request in front of you, not for the average request.

**Task stakes** separate routine from consequential. Short edits, classification, reformatting, boilerplate generation: these are well-defined tasks with clear right answers, and a good local model handles them reliably. Open-ended reasoning, architecture decisions, one-shot deliverables you will ship on: these are cases where you want the best answer available regardless of what it costs. Escalate when the consequence of a weak answer is high.

**Sensitivity** is different from the other three. Cost, latency, and stakes are signals about the request itself; sensitivity is a rule you choose to encode. On your own rig, private data can stay on the machine as a hard constraint. If a prompt contains credentials, personal identifiers, or anything you would not paste into a browser, you can route it local even when another signal would otherwise send it to the cloud. This is a local-first benefit you enforce by policy, not an industry-standard routing lever. The sources on routing architecture emphasize cost, latency, context size, and task complexity as the standard signals; sensitivity is the one you add because you own the machine.

## Step 3: Which Way Each Signal Points

The defaults are simple. Route local when the request fits the local window, is cost-sensitive, latency-tolerant, or sensitivity-flagged. Escalate to cloud when the context exceeds the local window, or when the task is high-stakes enough that quality outweighs cost.

Sensitivity overrides toward local even when other signals point the other way. A prompt that is both private and large is a harder call, and the next lesson asks you to write that conflict down explicitly before you write any code.

The four signals in order of firmness: context size is a binary fit-or-no-fit gate; sensitivity is a hard local override when you choose to enforce it; latency and stakes are the sliding scale in between, where "routine" routes local and "consequential" escalates. Most requests settle quickly; the interesting ones sit at the edges, and naming the deciding signal in writing is how you debug a routing policy later.

When you can route any request by naming the signal that decided it, the next step is encoding those signals as thresholds rather than judgment calls.

## Core Concepts

- Local inference is amortized hardware cost, near zero per token after purchase; cloud is metered per token; that asymmetry is the reason a router exists.
- Context size is a binary gate: a request either fits the local model's window (roughly 4K to 8K tokens on a 16 GB card) or it does not, and a request that does not fit escalates regardless of other signals.
- Latency budget and task stakes are the sliding-scale signals: latency-tolerant or routine work routes local; tight interactive loops or high-consequence one-offs escalate.
- Sensitivity is a rule you choose to encode, not a standard routing signal: on your own rig, private data staying on the machine is a local-first policy you enforce, and it overrides other signals toward local.

<div class="claude-handoff" data-exercise="exercises/module5/the-routing-decision/">

**Build It in Claude Code**: Take five example requests and route each one to local or cloud, writing the deciding signal (context size, latency budget, stakes, or sensitivity) and a one-line reason for each.

</div>

<!-- SOURCES: https://docs.litellm.ai/docs/routing | https://www.mindstudio.ai/blog/hybrid-ai-architecture-local-models-cloud-frontier | https://pooya.blog/blog/local-ai-ollama-benchmarks-cost-2026/ | https://docs.ollama.com/faq | https://platform.claude.com/docs/en/docs/build-with-claude/context-windows | https://platform.claude.com/docs/en/docs/about-claude/pricing -->
