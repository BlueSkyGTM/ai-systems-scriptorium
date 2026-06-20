# Inference metrics & load testing

A REST endpoint has one latency number, and it tells you everything. An LLM endpoint has at least four, and the average of any of them lies to you. Before you put a serving stack in front of users, you have to know which numbers decide whether it works — and you have to learn them by pushing the endpoint until it breaks, not by reading the model card.

## A token stream is not a request

The serving engine you built in chapter 1 does not return a response; it returns a stream. The first token arrives, then the rest dribble out one at a time. That shape forces a vocabulary a normal service never needs.

**Time to first token (TTFT)** is the wait before anything appears — prefill plus queue time plus network. It is what a user feels as "did it hear me?" In a chat UI it is the single most visible number, because a 200-millisecond TTFT feels instant and a two-second one feels broken, no matter how fast the rest streams.

**Time per output token (TPOT)**, also written as inter-token latency, is the gap between each subsequent token once the stream is running. This is the decode phase, and it is memory-bandwidth-bound: the model reads its whole weight set from high-bandwidth memory for every single token, so TPOT barely moves whether the prompt was short or long. End-to-end latency is then TTFT plus TPOT times the output length — a long answer is slow even on a fast engine, because every token pays the TPOT tax.

**Throughput** is the fleet-level number: total tokens per second across all concurrent requests. It is what your bill divides into, and it trades directly against the latencies above. Continuous batching (chapter 2) buys throughput by packing more sequences into each decode step — which lengthens the queue and pushes TTFT up. You cannot maximize both. You pick the point on that curve your product can live with.

To make the shape concrete: in one TensorRT-LLM benchmark, a Llama-3.1-8B landed around a 162-millisecond mean TTFT and a 7.3-millisecond TPOT, for a roughly one-second end-to-end on a medium answer. Treat that as one data point on one engine and one GPU, not a target — change the model, the hardware, or the prompt mix and every number moves. Your numbers will differ. The discipline is to measure your own.

## The average is the enemy

Report the mean latency and you have hidden the failure. LLM latency is right-skewed — a long tail of slow requests sits above a fast bulk — so the mean tells you about a request almost nobody made. Always report percentiles: p50 (the median, the typical request), p90, and p99 (the slow one your heaviest users hit several times a session). A deployment with a great p50 and an ugly p99 is a deployment that feels broken to your most active users, and the mean will never show it.

There is a metric above latency that the others feed into: **goodput** — the fraction of requests that meet *every* service-level objective at once. Throughput counts tokens served; goodput counts only the requests that came back fast enough *and* completely enough to be usable. A box reporting high throughput at 60% goodput is failing, because four in ten responses missed an SLO and shipped anyway. Goodput is the honest top-line; the rest are the diagnostics under it.

On Azure, the same numbers surface as platform metrics rather than something you scrape by hand: Azure Monitor and Application Insights collect latency and token-usage telemetry from Azure OpenAI deployments and the gateway in front of them, so the percentile views and token-per-minute counters exist before you write any instrumentation.

## Load-test before you ship, and don't trust the load tester

You do not know your TTFT, TPOT, or goodput until you have driven the endpoint under realistic concurrency. A model that streams beautifully for one request can fall over at fifty, because the batch fills, the queue grows, and TTFT walks off the chart. Load testing is how you find the concurrency at which goodput collapses — the number that sizes your fleet and sets your autoscaling trigger.

Two traps make generic load tools lie for LLM endpoints, and both are worth naming because they will burn you.

The first is the **client-side tokenization trap**. A general-purpose tester that tokenizes prompts in the same Python process that generates load runs the tokenizer under the interpreter's global lock; under concurrency the tokenizer queues behind the request generator, and the tool reports inflated inter-token latency that is *your client's* bottleneck, not the server's. Purpose-built LLM load tools push tokenization onto a separate process to keep it off the hot path.

The second is the **uniform-prompt trap**. Fire the same prompt in a loop and you hit the prefix cache on nearly every request — you have measured one lucky point on the token distribution, not your traffic. Vary input length around a mean and standard deviation so the test exercises real prefill cost.

Run four shapes, each catching a different failure: **steady** load to find the sustainable goodput ceiling, a **ramp** to locate the concurrency where percentiles break, a **spike** to test whether autoscaling reacts before users do, and a **soak** — hours at moderate load — to surface the memory leak that only shows after the thousandth request. Azure's GenAI gateway toolkit ships a load-testing setup aimed precisely at exercising token-limit and spillover policies before production traffic does.

This is the same eval discipline as Module 2, pointed at a different question. There you scored *output quality* with an LLM-as-judge before shipping a prompt; here you measure *serving performance* before shipping an endpoint. Module 2 was the inner loop — quality at development time. This chapter is the outer loop — the production control plane that watches both quality and performance live, and the next two lessons build out the rollout and observability halves of it.

## Core concepts

- An LLM endpoint has four core metrics, not one: TTFT (the wait for the first token), TPOT (the per-token decode gap, memory-bandwidth-bound), throughput (fleet tokens per second), and end-to-end latency = TTFT + TPOT × output length.
- Report percentiles (p50/p90/p99), never the mean — LLM latency is right-skewed, so the mean describes a request almost nobody made; goodput, the fraction of requests meeting every SLO at once, is the honest top-line the rest diagnose.
- Throughput and latency trade against each other: continuous batching raises throughput by lengthening the queue, which raises TTFT — you choose a point on that curve, you do not win both.
- Load-test before shipping with steady, ramp, spike, and soak shapes; distrust generic load tools, which inflate inter-token latency by tokenizing client-side and hit the prefix cache when prompts are uniform.

<div class="claude-handoff" data-exercise="exercises/module5/04-inference-metrics-and-load-testing/">

**Build it in Claude Code** — add a metrics middleware to `module5-serving/` that records TTFT, TPOT, and throughput per request and exposes p50/p90/p99 plus goodput against a declared SLO, then write a local load-test script that drives the endpoint with varied-length prompts in steady, ramp, and spike shapes and prints the concurrency at which goodput collapses. Open the repo and run the exercise for this lesson.

</div>
