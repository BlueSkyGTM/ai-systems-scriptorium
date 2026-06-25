# Streaming vs Batch: The Freshness SLO Decides

The nightly pipeline is fine until a compliance edit lands at 9 a.m. and your index serves the old paragraph until 2 a.m. tomorrow. Some sources cannot wait, and once you understand that, the decision is not "streaming or batch" for the whole system: it is "streaming or batch" per source, driven by a single number.

That number is the freshness SLO.

## What the SLO Exposes

You already have one: `freshness_slos` seeds `corpus_raw` at 25 hours. That target tells the system the source is allowed to be almost a day old before anything fires. Nightly loads satisfy it easily. Now consider a live compliance feed where an edit must appear in the index within five seconds of being written. A 25-hour SLO is irrelevant; a 5-second one is not. The SLO does not describe what the system can do; it describes what the source requires. Change the requirement, and you change the pipeline.

The two SLOs side by side make this concrete:

```python
# batch leg (M2/M3): freshness SLO measured in HOURS
batch_slo_hours = 25            # nightly reload; stale after ~a day

# streaming leg (M4): freshness SLO measured in SECONDS
streaming_slo_seconds = 5       # a change must be in the index within 5s
```

Same corpus, two legs, two SLOs. The batch leg is a nightly job that the M3 orchestrator fires and monitors. The streaming leg is a continuously running consumer that applies each change as it arrives. You choose the leg by reading the SLO, not by picking a technology.

## The Cost Is Real

Streaming satisfies a seconds-scale SLO; it does not do it for free. A nightly job wakes up, runs, and sleeps. A streaming consumer runs continuously, holding a connection, processing every event, and writing to the index in near-real time. On Microsoft Fabric, that means an Eventstream resource stays live around the clock: it captures events from the source, routes them to a Lakehouse or Eventhouse, and your consumer reads from that stream. [MS-Learn Eventstream overview: https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/overview]

The batch pipeline costs compute for the duration of the load. The streaming pipeline costs compute for the life of the source. Whether that trade is worth it depends entirely on the SLO. A reference corpus that changes once a month does not need a live consumer; a compliance feed that changes hourly and must be current in five seconds cannot live without one.

Mixing both in one system is normal. Most real data platforms batch the stable sources and stream the fast-moving ones. The routing decision is made per source at SLO definition time, not once at architecture review.

## Deciding Per Source

Three questions settle it:

**What is the required freshness?** If the answer is hours, the batch leg is already built (M2/M3). If the answer is seconds or low minutes, streaming is the only path.

**How often does the source change?** A slowly-changing reference corpus churns a batch leg efficiently; an event-dense feed would cost far more to reload nightly than to stream incrementally.

**What is the cost of being stale?** A retriever serving an outdated compliance paragraph is a liability. A retriever serving a corpus that is 18 hours old instead of 22 is probably fine. Name the cost before you name the architecture.

These three questions together produce a defensible routing decision. The routing decision is an engineering judgment call about latency versus cost; there is no product feature that makes it for you.

## Core Concepts

- The freshness SLO is the decision variable: a source with a seconds-scale SLO streams; a source with an hours-scale SLO batches. The architecture follows the requirement.
- The routing decision is per source, not per system: a stable reference corpus and a live compliance feed can coexist in one platform on different legs.
- Streaming satisfies low-latency SLOs at the cost of a continuously running consumer; batch satisfies high-latency SLOs at the cost of a scheduled job. Neither is free; the SLO determines which cost is worth paying.
- Microsoft Fabric Eventstream is the no-code service that captures and routes real-time event streams to a Lakehouse or Eventhouse; it is the streaming counterpart to the batch Data Factory pipeline built in M2/M3.

The SLO you write today is the number that determines whether a compliance edit lands in five seconds or 17 hours. Write it first; build the pipeline second.

<div class="claude-handoff" data-exercise="exercises/module4/streaming-vs-batch/">

**Build It in Claude Code**: Write a `decide_mode(required_freshness_seconds)` function that returns `"stream"` when the SLO is seconds-scale (60 seconds or under) and `"batch"` otherwise; classify a handful of example sources (a nightly reference corpus, a live compliance feed, a price-update feed, a monthly audit log); add a `pytest` test that asserts each classification is correct. This decision helper frames the streaming pipeline you build across the rest of the module: every source that routes to `"stream"` is a candidate for the Eventstream leg.

</div>
