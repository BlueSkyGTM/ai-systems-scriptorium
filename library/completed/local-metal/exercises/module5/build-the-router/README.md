# Exercise: Build the Router

## Goal

Create `route.py`, a stdlib-only routing script whose core is a pure `route(request)` policy
function. It reads four signals off a request dataclass, returns a `Decision` (target plus reason),
and self-tests offline with no rig and no cloud key. The live path calls `ollama_client.py` from
Module 3 for the local arm.

## Why

This is the fifth compounding artifact in the portfolio. `ollama_client.py` (Module 3) gave you a
client. The Module 4 benchmark measured what that client costs. This file makes the routing
decision executable. Module 6 wires `route.py` into Claude Code so the delegation happens without
you thinking about it. Do not rename or move this file; Module 6 imports from this path.

## Files You Are Editing

`exercises/module5/build-the-router/route.py`

Do not rename it. Do not move it. Module 6 reuses it directly.

## Steps

Create `exercises/module5/build-the-router/route.py` with this exact code:

```python
#!/usr/bin/env python3
"""
route.py: decide whether a request runs on the local rig or escalates to the cloud.

The core is a pure policy function, route(request) -> Decision, that reads four
signals off a request and returns a target ("local" or "cloud") plus the reason.
The live path (--run) calls ollama_client.call() when the decision is local; the
cloud arm is a stub you wire to your own provider.

Usage:
  python route.py --selftest          # offline: assert the policy on a fixed request set
  python route.py --run "a prompt"    # live (local arm): route, and if local, call Ollama
"""

import argparse
import sys
from dataclasses import dataclass, field

# --- Policy thresholds (recorded in ROUTING.md; edit to match your rig) ---
LOCAL_CONTEXT_LIMIT = 8192          # tokens the local model can hold comfortably
LATENCY_BUDGET_MS = 2000            # below this, the request is "interactive" and wants speed
LOCAL_MODEL = "qwen2.5-coder:14b"
CLOUD_MODEL = "claude (frontier)"


@dataclass
class Request:
    prompt_tokens: int = 0          # estimated context size in tokens
    latency_budget_ms: int = 10_000  # how long the caller will wait
    sensitive: bool = False         # must the data stay on the machine?
    high_stakes: bool = False       # does the caller want the best answer regardless of cost?


@dataclass
class Decision:
    target: str                     # "local" or "cloud"
    reason: str


def route(request):
    """Pure routing policy: signals in, a decision out. No network, no side effects."""
    # Sensitivity wins: private data never leaves the machine.
    if request.sensitive:
        if request.prompt_tokens > LOCAL_CONTEXT_LIMIT:
            return Decision("local", "sensitive data stays local even though context is large; chunk it")
        return Decision("local", "sensitive data must stay on the machine")
    # Context that does not fit the local window must escalate.
    if request.prompt_tokens > LOCAL_CONTEXT_LIMIT:
        return Decision("cloud", f"context {request.prompt_tokens} tokens exceeds local limit {LOCAL_CONTEXT_LIMIT}")
    # High-stakes one-offs go to the frontier model.
    if request.high_stakes:
        return Decision("cloud", "high-stakes request wants the best answer regardless of cost")
    # Everything else fits the local window and is cheap and private: keep it local.
    return Decision("local", "routine request fits the local window and is cost-sensitive")


def selftest():
    """Assert the policy on a fixed set of requests. No rig, no cloud key."""
    cases = [
        (Request(prompt_tokens=500), "local"),
        (Request(prompt_tokens=200_000), "cloud"),
        (Request(prompt_tokens=500, high_stakes=True), "cloud"),
        (Request(prompt_tokens=500, sensitive=True), "local"),
        (Request(prompt_tokens=200_000, sensitive=True), "local"),
    ]
    for request, expected in cases:
        decision = route(request)
        assert decision.target == expected, (
            f"expected {expected} for {request}, got {decision.target} ({decision.reason})"
        )
        assert decision.reason, "every decision must carry a reason"
    print(f"selftest passed: {len(cases)} routing decisions correct")
    return 0


def run(prompt):
    """Live local arm: route a simple request and, if local, call Ollama."""
    request = Request(prompt_tokens=max(1, len(prompt) // 4))  # rough token estimate
    decision = route(request)
    print(f"route: {decision.target} ({decision.reason})")
    if decision.target == "local":
        try:
            from ollama_client import call  # the M3 client, the local arm of the router
        except ImportError:
            print("local arm needs ollama_client.py on the path (Module 3)", file=sys.stderr)
            return 1
        print(call(prompt, model=LOCAL_MODEL))
    else:
        print(f"(escalate to {CLOUD_MODEL}: wire your cloud provider here)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Route a request between local and cloud.")
    parser.add_argument("--selftest", action="store_true", help="assert the policy offline")
    parser.add_argument("--run", metavar="PROMPT", help="route a prompt and run the local arm")
    args = parser.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.run:
        sys.exit(run(args.run))
    parser.error("use --selftest or --run")


if __name__ == "__main__":
    main()
```

## Note

`--selftest` runs offline: no rig, no Ollama, no cloud key. `--run` requires the rig running and
`ollama_client.py` from `exercises/module3/the-openai-compatible-api/` on the Python path (or
copied into the same directory). Copy it or add its directory to `PYTHONPATH` before calling
`--run`.

## Done When

`python route.py --selftest` exits 0 and prints:

```
selftest passed: 5 routing decisions correct
```

With the rig running and `ollama_client.py` on the path, `python route.py --run "reformat this
function"` prints a route line followed by the local model's reply.

## Expected Output Shape

Selftest:

```
selftest passed: 5 routing decisions correct
```

Live (`--run`):

```
route: local (routine request fits the local window and is cost-sensitive)
Here's the reformatted function with consistent spacing and cleaner structure:
...
```

The reply text varies; the route line and its format do not.

## Stretch

Add a `cost_ceiling` field (a float, dollars) to `Request`. In `route()`, estimate the cloud cost
for the request (a rough `prompt_tokens * 0.000003` per-token rate is enough for a heuristic) and
route to local when that estimate exceeds `cost_ceiling`. Add two selftest cases: one where the
estimate is under the ceiling and another where it is over. Keep sensitivity-first ordering.
