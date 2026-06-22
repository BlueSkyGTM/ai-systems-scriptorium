# Exercise: Measure Latency

**Goal:** Create `exercises/module4/measure-latency/bench.py`: a stdlib-only tool that streams a
generation from Ollama's `/api/generate` endpoint, measures the wall-clock time to the first token,
and reports tokens per second and TTFT from the server's own timing fields, with a `--selftest`
flag that validates the metric math offline.

**Why:** You cannot decide whether a 32B model that splits onto system RAM is worth running until
you know what it costs in time. `bench.py` reads Ollama's own `eval_count` and `eval_duration`
fields rather than timing the whole request with an external stopwatch, so the numbers reflect the
server's accounting, not network jitter. The output feeds `LATENCY.md` in the next lesson: that
file is the baseline every Module 7 tuning decision is measured against.

## Steps

1. Create `exercises/module4/measure-latency/bench.py` with the following exact code:

```python
#!/usr/bin/env python3
"""
bench.py: measure local model latency from Ollama's own timing fields.

Reports tokens/second (generation rate) and time to first token (TTFT) for a
model served by Ollama, reading the timing fields in the /api/generate response.

Usage:
  python bench.py "write a haiku about latency"          # live: benchmark the default model
  python bench.py --model qwen2.5-coder:32b "a prompt"   # live: benchmark a specific model
  python bench.py --selftest                              # offline: validate the metric math
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

DEFAULT_MODEL = "qwen2.5-coder:14b"
GENERATE_URL = "http://localhost:11434/api/generate"


def tokens_per_second(eval_count, eval_duration_ns):
    """tok/s = generated tokens / generation time. eval_duration is nanoseconds."""
    if eval_duration_ns <= 0:
        raise ValueError("eval_duration must be positive")
    return eval_count / (eval_duration_ns / 1e9)


def metrics_from_response(body, ttft_s):
    """Extract tok/s and TTFT (ms) from an /api/generate body plus a measured TTFT."""
    eval_count = body["eval_count"]
    eval_duration = body["eval_duration"]
    return {
        "model": body.get("model", "unknown"),
        "tokens_per_second": round(tokens_per_second(eval_count, eval_duration), 1),
        "ttft_ms": round(ttft_s * 1000, 1),
        "eval_count": eval_count,
    }


def bench(prompt, model=DEFAULT_MODEL, url=GENERATE_URL):
    """Stream a generation, time the first token, and return latency metrics."""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": True}).encode("utf-8")
    request = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    start = time.perf_counter()
    ttft_s = None
    final = {}
    with urllib.request.urlopen(request) as response:
        for line in response:
            chunk = json.loads(line.decode("utf-8"))
            if ttft_s is None and chunk.get("response"):
                ttft_s = time.perf_counter() - start
            if chunk.get("done"):
                final = chunk
    if ttft_s is None:
        ttft_s = time.perf_counter() - start
    return metrics_from_response(final, ttft_s)


def selftest():
    """Validate the metric math offline against a sample /api/generate response."""
    sample = {
        "model": "qwen2.5-coder:14b",
        "eval_count": 240,
        "eval_duration": 6_000_000_000,  # 6.0 s expressed in nanoseconds
        "done": True,
    }
    m = metrics_from_response(sample, ttft_s=0.250)
    assert m["tokens_per_second"] == 40.0, f"tok/s math wrong: {m['tokens_per_second']}"
    assert m["ttft_ms"] == 250.0, f"ttft math wrong: {m['ttft_ms']}"
    assert tokens_per_second(100, 1_000_000_000) == 100.0, "tok/s helper wrong"
    print("selftest passed: tok/s and TTFT math are correct")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Benchmark a local Ollama model's latency.")
    parser.add_argument("prompt", nargs="?", help="the prompt to benchmark with")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="model tag to benchmark")
    parser.add_argument("--selftest", action="store_true", help="validate the metric math offline")
    args = parser.parse_args()

    if args.selftest:
        sys.exit(selftest())

    if not args.prompt:
        parser.error("provide a prompt, or use --selftest")

    try:
        m = bench(args.prompt, model=args.model)
    except urllib.error.URLError as exc:
        print(f"could not reach Ollama at {GENERATE_URL}: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"model:  {m['model']}")
    print(f"tok/s:  {m['tokens_per_second']}")
    print(f"TTFT:   {m['ttft_ms']} ms")
    print(f"tokens: {m['eval_count']}")


if __name__ == "__main__":
    main()
```

2. Run the selftest to confirm the math is correct:

   ```bash
   python bench.py --selftest
   ```

3. With the rig running and a model pulled, benchmark a live generation:

   ```bash
   python bench.py "write a haiku about latency"
   ```

**Note:** `--selftest` runs with no server and no model. Live mode requires Ollama running
(`ollama serve` or the system service) and a model pulled (`ollama pull qwen2.5-coder:14b`). If
the rig is not yet set up, `--selftest` is the complete done-when for now; return to live mode
once the model is on-card. `bench.py` is a standalone tool: it does not import from `ollama_client.py`
and does not need the Module 3 artifact to run.

## Done When

- `python bench.py --selftest` exits 0 and prints the selftest line (no rig needed).
- With the rig online: `python bench.py "write a haiku about latency"` exits 0 and prints four
  lines (model, tok/s, TTFT, tokens).

## Expected Output Shape

Selftest (always):

```
selftest passed: tok/s and TTFT math are correct
```

Live mode (representative; exact numbers vary by hardware and prompt):

```
model:  qwen2.5-coder:14b
tok/s:  41.3
TTFT:   214.7 ms
tokens: 38
```

## Stretch

Add a `--runs N` flag that benchmarks the same prompt `N` times and reports the median tok/s
across all runs, since a single run is noisy: the first run may trigger a model reload, and
subsequent runs reflect the steady-state throughput. Update `main` to call `bench` in a loop when
`--runs` is set and compute the median from the resulting list of `tokens_per_second` values.
Report the median as a fifth output line:

```
median tok/s (N runs): 40.8
```
