# Measure Latency

A model that splits onto system RAM is slower. "Slower" is not a decision until it is a number.
Two numbers make it one: tokens per second (how fast the model generates once it starts) and time
to first token (how long you wait before anything arrives). You will build `bench.py`, a stdlib
tool that reads those numbers from Ollama's own response fields, so "smarter but slower" becomes
something you can actually weigh.

## Where the Numbers Come From

Ollama's native `/api/generate` endpoint embeds timing data directly in its response body. You do
not wire up a stopwatch: the server already did the accounting. The relevant fields, all in
nanoseconds:

| Field | What It Measures |
|---|---|
| `total_duration` | wall clock for the whole request |
| `load_duration` | time to load the model into memory |
| `prompt_eval_count` | tokens in the prompt |
| `prompt_eval_duration` | time to process the prompt |
| `eval_count` | tokens generated |
| `eval_duration` | time spent generating |

The Ollama API documentation includes a sample response body that shows every field
([github.com/ollama/ollama/blob/main/docs/api.md](https://github.com/ollama/ollama/blob/main/docs/api.md)).
Using the numbers from that sample: `eval_count: 290`, `eval_duration: 4709213000` nanoseconds.
Tokens per second:

```
290 / (4709213000 / 1e9) = 290 / 4.709 ≈ 61.6 tok/s
```

The formula is always `eval_count / (eval_duration / 1e9)`. That is it.

Time to first token (TTFT) is harder to read from the final body alone. The body gives you
`load_duration + prompt_eval_duration`, which approximates the pre-generation wait, but it misses
any network or queueing time between your client and the server. The real TTFT is the wall-clock
interval from the moment you send the request to the moment the first generated token arrives.
You measure that with a streaming request.

## TTFT by Streaming

Setting `"stream": true` in the request body changes the response from a single blocking JSON
object to a sequence of newline-delimited JSON chunks
([docs.ollama.com/api/usage](https://docs.ollama.com/api/usage)). Each chunk carries a partial
`response` string as the model generates. The final chunk sets `"done": true` and includes all
the timing fields listed above.

The TTFT measurement is simple: start a timer when you send the request, read chunks line by line,
and stop the timer when the first chunk arrives that contains a non-empty `response`. The `done`
chunk at the end gives you `eval_count` and `eval_duration` for the tokens-per-second calculation.

Two measurements, one streaming pass.

## Build the Tool

Create `exercises/module4/measure-latency/bench.py` with this exact code. It uses only the
standard library: `urllib`, `json`, `argparse`, `sys`, and `time`.

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

Three functions do the real work. `tokens_per_second` contains the formula: nanoseconds to seconds,
then divide into token count. `metrics_from_response` pulls `eval_count` and `eval_duration` from
the final `done` chunk and combines them with the wall-clock TTFT your caller measured.
`selftest` runs the math against a fixed sample response and asserts exact values, so you have a
machine-checkable done-when before the rig is online: 240 tokens over 6.0 seconds is 40.0 tok/s,
and a 250 ms measured wall-clock is 250.0 ms TTFT.

## Run It

No rig needed for the first check. Validate the math offline:

```bash
python bench.py --selftest
```

What you should see:

```
selftest passed: tok/s and TTFT math are correct
```

With the rig running and a model pulled, benchmark a live generation:

```bash
python bench.py "write a haiku about latency"
```

What you should see (representative output; exact numbers vary by hardware and prompt):

```
model:  qwen2.5-coder:14b
tok/s:  31.4
TTFT:   214.7 ms
tokens: 38
```

A 14B model running entirely on the RTX 4060 Ti's 16GB typically lands in the 25-34 tok/s range
with TTFT under 250 ms. Benchmark the same prompt against `qwen2.5-coder:32b` and the tok/s will
drop: part of that model lives in system RAM, and every layer that crosses the PCIe bus costs time.
That drop is the number this tool exists to show you.

The next lesson records these measurements for each model in `LATENCY.md`, the baseline that every
tuning decision in Module 7 is measured against. Run `bench.py` for each model before you build
that file; the output lines paste in directly.

## Core Concepts

- Tokens per second is throughput; time to first token is responsiveness. They are different problems:
  a model can be fast once it starts yet still feel slow if it makes you wait 2 seconds for the
  first word.
- The numbers come from the server's own timing fields in the `/api/generate` response, not a
  stopwatch you bolt on. `eval_count / (eval_duration / 1e9)` is the complete formula for tok/s.
- The offline selftest is the machine-checkable done-when: it asserts exact values against a fixed
  sample, so the math is proven before the rig is online.
- A measured baseline is what converts "smarter but slower" into a decision: without a number,
  the tradeoff is a guess; with one, it is a policy.

<div class="claude-handoff" data-exercise="exercises/module4/measure-latency/">

**Build It in Claude Code**: Create `exercises/module4/measure-latency/bench.py`, a stdlib-only tool that streams a generation from `http://localhost:11434/api/generate`, times the first token, and reports tokens per second and TTFT from the response's timing fields, with a `--selftest` mode that validates the math offline.

</div>

<!-- SOURCES: https://github.com/ollama/ollama/blob/main/docs/api.md | https://docs.ollama.com/api/usage | https://github.com/ollama/ollama/blob/main/docs/faq.mdx -->
