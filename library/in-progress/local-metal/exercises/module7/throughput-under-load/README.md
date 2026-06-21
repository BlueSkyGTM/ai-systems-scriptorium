# Exercise: Throughput Under Load

**Goal:** Create `exercises/module7/throughput-under-load/loadbench.py`: a stdlib-only tool
that fires N concurrent generations at Ollama's `/api/generate` endpoint, measures the
wall-clock time for the whole batch, and reports aggregate tokens per second and the slowest
single request, with a `--selftest` flag that validates the aggregation math offline.

**Why:** Single-stream tok/s tells you how fast one reply streams. It does not tell you how
much total work the rig delivers when several callers hit it at once, which is the metric
that matters once the server is wired up and in real use. `loadbench.py` fires N requests
through a thread pool, times the whole batch as one wall-clock interval, and computes
aggregate throughput correctly: total tokens divided by elapsed batch time, not the sum of
per-request times. The tail latency figure shows the worst-case wait any individual request
experiences. Together, these numbers are what you record in `TUNING.md` to prove the rig
holds up under load.

## Files You Are Editing

`exercises/module7/throughput-under-load/loadbench.py` (do not move or rename this file).

## Steps

1. Create `exercises/module7/throughput-under-load/loadbench.py` with this exact code:

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

2. Run the selftest to confirm the aggregation math is correct:

   ```bash
   python loadbench.py --selftest
   ```

3. With the rig running and `OLLAMA_NUM_PARALLEL` set, fire four concurrent requests:

   ```bash
   OLLAMA_NUM_PARALLEL=4 ollama serve   # in one terminal
   python loadbench.py "explain what a transformer is" --concurrency 4
   ```

**Note:** `--selftest` runs with no server and no model; it only validates the `aggregate`
function's math offline. Live mode requires Ollama running with `OLLAMA_NUM_PARALLEL` set
to at least the concurrency level you are testing, and a model pulled
(`ollama pull qwen2.5-coder:14b`). If the rig is not yet available, `--selftest` is the
complete done-when for now. `loadbench.py` does not import from any earlier artifact; it is
standalone.

## Done When

- `python loadbench.py --selftest` exits 0 and prints the selftest line (no rig needed).
- With the rig online: `python loadbench.py "explain what a transformer is" --concurrency 4`
  exits 0 and prints three lines (requests, aggregate tok/s, slowest request).

## Expected Output Shape

Selftest (always):

```
selftest passed: aggregate throughput and tail latency math are correct
```

Live mode (representative; exact numbers vary by hardware, model, and prompt length):

```
requests:            4
aggregate tok/s:     61.4
slowest request (s): 6.83
```

## Stretch

Sweep concurrency levels 1, 2, 4, and 8 against the same prompt and record the aggregate
tok/s at each level. Plot (or table) where aggregate throughput stops growing: that plateau
is the point where the memory bus is fully loaded and adding more concurrent requests no
longer helps. The level just before the plateau is the practical value for `OLLAMA_NUM_PARALLEL`
on your card.
