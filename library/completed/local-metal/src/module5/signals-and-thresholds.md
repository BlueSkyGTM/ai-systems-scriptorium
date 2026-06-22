# Signals and Thresholds

A routing decision you keep in your head is not a policy. A policy is written down, with
numbers you can point to and a rule that applies them. This lesson writes it.

## Step 1: Pick the Thresholds

You have four signals from the module overview. Each one needs a concrete cut: not "large
context" but a token count, not "slow" but a millisecond budget. Here is the cut for each,
and the reason behind each number.

**Context size.** The local 14B model holds roughly 4K to 8K tokens comfortably on a 16 GB
card. Ollama defaults `num_ctx` to 2048 or 4096 depending on the version; as context grows,
the KV cache grows with it and competes with the model weights for VRAM. Set the local
context limit at 8192 tokens. Over that, the request escalates to cloud. A frontier model
like Claude reaches 200K to 1M tokens, so the escalation covers everything the local model
cannot hold.

**Latency budget.** Tie this to your Module 4 baseline. The on-card 14B runs around 30
tokens per second with a time-to-first-token under 250 ms. A model that has spilled into
system RAM crawls, and a split model across two machines adds a network round-trip on top.
Set a latency budget of 2000 ms: any request tagged as interactive that still fits the local
context window goes local, because local avoids the network round-trip entirely.

**Sensitivity.** Private data stays on the machine. This is not a soft preference; it is a
hard local rule you enforce as an override. If a request carries data you would not send to
a third party, the target is local regardless of context size or stakes.

**Stakes.** Some requests are one-offs where you want the best answer regardless of cost: a
tricky architectural decision, a document going to a client, a prompt you will run once.
Route these to cloud and pay the metered cost. Local inference is amortized, near zero per
token; cloud inference is metered per token. The economics favor local for high-volume
routine work and favor cloud for high-stakes one-offs.

## Step 2: Write ROUTING.md

Create the policy file at `exercises/module5/signals-and-thresholds/ROUTING.md` using
exactly this template:

```markdown
# Routing Policy

How requests are routed between the local rig and the cloud. Read by check_routing.py.

## Signals

| Signal | Threshold | Routes To |
|--------|-----------|-----------|
| Context size | over 8192 tokens | cloud |
| Latency budget | under 2000 ms, fits local | local |
| Sensitivity | private / on-machine | local |
| Stakes | high-stakes one-off | cloud |

## Targets

Local model: qwen2.5-coder:14b (8K practical context)
Cloud model: claude (frontier, 1M-token context)

## Policy

Route to local when the request fits the local context window and is cost-sensitive,
latency-tolerant, or privacy-sensitive. Escalate to cloud when the context exceeds the local
window or the task is high-stakes and wants the best answer regardless of cost. Sensitive data
never leaves the machine.
```

The file has three sections. `## Signals` is the table: one row per signal, one threshold,
one target. `## Targets` names the two endpoints by their actual identifiers, not abstract
labels. `## Policy` is the prose rule that ties the table together: it is the readable
version of the decision logic, the thing you would explain to a colleague.

## Step 3: Justify Against the Data

None of these thresholds are guesses. The 8192 token limit comes from the VRAM-vs-context
tradeoff you saw in Module 4: on a 16 GB card at Q4_K_M, the KV cache starts to crowd the
model above that window size. The 2000 ms latency budget comes from the 30 tok/s baseline
you measured; at that speed the first token arrives in under 250 ms and a short response
completes well within the budget. The cloud escalation comes from the frontier context window,
published at 200K to 1M tokens, which is why the escalation is not "somewhat larger context"
but "context the local model cannot hold at all."

A policy is defensible when each number traces to a measurement. This one does.

The next lesson turns this written policy into a function: the same four signals, the same
thresholds, but expressed in Python so the routing happens without you.

## Core Concepts

- A routing policy is thresholds written down; a threshold kept only in your head cannot be
  tested, shared, or enforced.
- Each threshold in ROUTING.md traces to a measurement, not a guess: context limit to VRAM
  headroom, latency budget to tok/s baseline, cloud escalation to frontier context window.
- ROUTING.md has three sections: Signals (the decision table), Targets (the named endpoints),
  and Policy (the prose rule that ties them together).
- Sensitivity is an override, not a row to weigh against others: private data never leaves
  the machine regardless of context size or stakes.

<div class="claude-handoff" data-exercise="exercises/module5/signals-and-thresholds/">

**Build It in Claude Code**: Create `exercises/module5/signals-and-thresholds/ROUTING.md` with a `## Signals` table, a `## Targets` section naming your local and cloud models, and a `## Policy` paragraph; set each threshold from your own card's limits and your Module 4 latency baseline.

</div>

<!-- SOURCES: https://docs.ollama.com/faq | https://platform.claude.com/docs/en/docs/build-with-claude/context-windows | https://docs.litellm.ai/docs/routing | https://pooya.blog/blog/local-ai-ollama-benchmarks-cost-2026/ -->
