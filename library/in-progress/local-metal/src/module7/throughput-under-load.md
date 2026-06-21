# Throughput Under Load

Module 4 measured one request at a time. A server answers several at once, and that is a
different number entirely.

## Why Aggregate Is Different

`bench.py` reports single-stream tok/s: how fast the model generates when exactly one request
is in flight. That number is real, but it is not the number that tells you whether the rig
holds up under real use.

When `OLLAMA_NUM_PARALLEL` is greater than 1, Ollama runs multiple sequence positions through
the model in the same forward pass. The GPU reads the weights once and produces tokens for
several concurrent requests from that single read. This is the win concurrency unlocks:
aggregate throughput, the total tokens all requests together produce per wall-clock second,
can exceed single-stream tok/s because the memory bus is serving multiple clients from one
fetch.

The cost is visible on any individual request. Each one waits its turn in the batch, so
per-request latency rises a little as concurrency climbs. That tradeoff is the shape of the
number you need to read: aggregate throughput goes up; the slowest single request gets slower.
Both facts belong in the measurement.

You need two numbers, then: aggregate throughput (total tokens across all requests divided by
the wall-clock time the whole batch took) and tail latency (the slowest single request).
`bench.py` gives you neither, because it only fires one.

## The Measurement

Fire N requests simultaneously, start one clock before they all launch, stop it after the last
one returns. Then:

```
aggregate tok/s = total tokens across all N requests / wall-clock time for the batch
```

The denominator is not the sum of per-request times. The requests ran concurrently, so you
divide by the time the batch itself occupied the clock, not by the accumulated serial time. A
batch of four requests that each take 10 seconds but overlap gives a wall time of roughly 10
seconds, not 40.

Tail latency is the slowest individual request time. That number tells you the worst-case wait
any one caller experiences, which is the number a user feels.

## Build It

Create `exercises/module7/throughput-under-load/loadbench.py` with this exact code. It uses
only the standard library: `urllib`, `json`, `argparse`, `sys`, `time`, and
`concurrent.futures`.

```python
#!/usr/bin/env python3
"""
loadbench.py: measure aggregate throughput under concurrent load.

Single-stream tok/s (Module 4's bench.py) is the wrong metric for a server that
answers more than one request at a time. loadbench.py fires N concurrent
generations at Ollama's /api/generate and reports aggregate tokens/second and the
slowest request (tail latency), the numbers that show whether the rig holds up.

Usage:
  python loadbench.py "a prompt" --concurrency 4   # live: N concurrent generations
  python loadbench.py --selftest                   # offline: validate the aggregation math
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

DEFAULT_MODEL = "qwen2.5-coder:14b"
GENERATE_URL = "http://localhost:11434/api/generate"


def aggregate(results, wall_seconds):
    """Aggregate per-request (eval_count, seconds) into throughput + tail latency.

    Aggregate tokens/sec is total generated tokens over the wall-clock time the
    whole batch took, not the sum of per-request times, because the requests ran
    concurrently. Tail latency is the slowest single request.
    """
    if wall_seconds <= 0:
        raise ValueError("wall_seconds must be positive")
    total_tokens = sum(count for count, _ in results)
    slowest = max(seconds for _, seconds in results)
    return {
        "requests": len(results),
        "aggregate_tokens_per_second": round(total_tokens / wall_seconds, 1),
        "slowest_request_s": round(slowest, 2),
    }


def one_request(prompt, model, url=GENERATE_URL):
    """Run one non-streaming generation; return (eval_count, seconds)."""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    start = time.perf_counter()
    with urllib.request.urlopen(request) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body.get("eval_count", 0), time.perf_counter() - start


def loadbench(prompt, concurrency, model=DEFAULT_MODEL):
    """Fire `concurrency` requests at once and aggregate the result."""
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(pool.map(lambda _: one_request(prompt, model), range(concurrency)))
    return aggregate(results, time.perf_counter() - start)


def selftest():
    """Validate the aggregation math offline. No server, no threads needed."""
    # 4 requests, 200 tokens each (800 total); batch wall time 10.0 s -> 80 tok/s aggregate.
    results = [(200, 8.0), (200, 9.0), (200, 10.0), (200, 7.5)]
    agg = aggregate(results, wall_seconds=10.0)
    assert agg["aggregate_tokens_per_second"] == 80.0, f"aggregate math wrong: {agg}"
    assert agg["slowest_request_s"] == 10.0, f"tail latency wrong: {agg}"
    assert agg["requests"] == 4, "request count wrong"
    print("selftest passed: aggregate throughput and tail latency math are correct")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Benchmark aggregate throughput under load.")
    parser.add_argument("prompt", nargs="?", help="the prompt to send concurrently")
    parser.add_argument("--concurrency", type=int, default=4, help="number of concurrent requests")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="model tag to benchmark")
    parser.add_argument("--selftest", action="store_true", help="validate the aggregation math offline")
    args = parser.parse_args()

    if args.selftest:
        sys.exit(selftest())

    if not args.prompt:
        parser.error("provide a prompt, or use --selftest")

    try:
        agg = loadbench(args.prompt, args.concurrency, model=args.model)
    except urllib.error.URLError as exc:
        print(f"could not reach Ollama at {GENERATE_URL}: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"requests:            {agg['requests']}")
    print(f"aggregate tok/s:     {agg['aggregate_tokens_per_second']}")
    print(f"slowest request (s): {agg['slowest_request_s']}")


if __name__ == "__main__":
    main()
```

Four functions do the work. `aggregate` contains the formula: total tokens divided by
wall-clock batch time, plus the max of per-request durations for tail latency. It is pure
and takes no network calls, which is why `selftest` can verify it without a running server.
`one_request` posts a single non-streaming generation to `/api/generate` and reads
`eval_count` from the response body, the same field `bench.py` uses, documented in Ollama's
API reference
([github.com/ollama/ollama/blob/main/docs/api.md](https://github.com/ollama/ollama/blob/main/docs/api.md)).
`loadbench` wraps N calls in a `ThreadPoolExecutor`, starts the wall clock before the pool
opens, and stops it after all futures resolve. `selftest` fixes four results at 200 tokens
each over a 10-second wall time and asserts the aggregate comes out to exactly 80.0 tok/s,
with the slowest request at 10.0 seconds.

## Run It

Start with the offline check. No rig required:

```bash
python loadbench.py --selftest
```

What you should see:

```
selftest passed: aggregate throughput and tail latency math are correct
```

With the rig running, set `OLLAMA_NUM_PARALLEL` to allow concurrent serving
([github.com/ollama/ollama/blob/main/envconfig/config.go](https://github.com/ollama/ollama/blob/main/envconfig/config.go)):

```bash
OLLAMA_NUM_PARALLEL=4 ollama serve
```

Then fire four concurrent requests:

```bash
python loadbench.py "explain what a transformer is" --concurrency 4
```

What you should see (representative; exact numbers depend on your hardware, model, and
prompt length):

```
requests:            4
aggregate tok/s:     61.4
slowest request (s): 6.83
```

Single-stream, the same prompt might produce around 30 tok/s from `bench.py`. Four concurrent
requests pushing through `num_parallel` can roughly double aggregate throughput because the
GPU amortizes one weight read across multiple sequence positions. The gain is real but not
linear: it saturates as VRAM fills and the memory bus becomes the ceiling again. The slowest
request also takes longer than it would alone, which is the tradeoff the tail latency number
makes visible. Both figures together tell you where the rig actually stands under load; the
next lesson records the before-and-after of every lever you pulled to get there.

## Core Concepts

- Aggregate throughput is total tokens across all concurrent requests divided by the
  wall-clock time for the whole batch, not by the sum of per-request times; the requests
  overlapped, so the denominator is the elapsed clock, not the serial total.
- Single-stream tok/s (from `bench.py`) measures how fast one reply streams; aggregate tok/s
  measures how much total work the server delivers per second when several requests run
  together: these are different quantities and both belong in a complete benchmark.
- Tail latency is the slowest single request in the batch; it is the number a user actually
  feels, and it rises as concurrency increases because each request waits its turn in the batch.
- Concurrency trades a little per-request latency for more total throughput: the GPU serves
  multiple sequence positions from one weight read, amortizing the memory-bandwidth cost, but
  the gain saturates once the bus is fully loaded.

<div class="claude-handoff" data-exercise="exercises/module7/throughput-under-load/">

**Build It in Claude Code**: Create `exercises/module7/throughput-under-load/loadbench.py`, a stdlib tool that fires N concurrent generations at `http://localhost:11434/api/generate` and reports aggregate tokens/second and the slowest request, with a `--selftest` mode that validates the aggregation math offline.

</div>

<!-- SOURCES: https://github.com/ollama/ollama/blob/main/docs/api.md | https://github.com/ollama/ollama/blob/main/envconfig/config.go -->
