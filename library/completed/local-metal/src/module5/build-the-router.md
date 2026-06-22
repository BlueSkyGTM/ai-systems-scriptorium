# Build the Router

You wrote the routing policy in prose. Now make it executable. The key design choice is this: the
routing decision is pure logic, so it tests with no rig and no cloud key; only the live path
touches the network.

## Pure Policy, Testable Core

The entry point is `route(request)`. It takes a small `Request` dataclass carrying four signals,
the same four the policy in `ROUTING.md` names: `prompt_tokens`, `latency_budget_ms`, `sensitive`,
and `high_stakes`. It returns a `Decision`: a target (`"local"` or `"cloud"`) plus the reason the
policy chose it.

Because `route()` has no side effects and no network calls, `--selftest` can assert its decisions
on a fixed set of requests without anything running. The test does not start Ollama, does not reach
a cloud endpoint, and does not need your hardware. This is the same offline-core pattern as the
Module 3 client and the Module 4 benchmark: the pure function is the machine-checkable done-when,
and the live path is layered on top.

## The Compounding Payoff

The live path (`--run`) routes a prompt and, when the decision comes back `"local"`, calls
`call()` from the `ollama_client.py` you built in Module 3. That is not a coincidence in the
design. The client you built two modules ago is now the local arm of a hybrid system; the work
compounds exactly as the Module 3 ending said it would.

The cloud arm in `route.py` is a stub. It prints a placeholder and exits cleanly. You wire your
own cloud provider there when you need it; you do not need a cloud key to complete this module, and
the `--selftest` path does not care either way.

## Build It

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

Walk the pieces before you run them.

The four threshold constants at the top mirror `ROUTING.md`: if you tune your thresholds in the
policy document, change them here too. `LOCAL_CONTEXT_LIMIT` is the token count your local model
handles without degrading; 8,192 is a conservative floor for a 14B model, not the architectural
maximum.

`Request` and `Decision` are plain dataclasses with no magic. The four fields on `Request` are
exactly the four signals the module overview names; the two fields on `Decision` enforce that every
routing outcome carries a justification, not just a label.

The `route()` function reads the signals in a deliberate order. Sensitivity comes first because it
is the only signal that acts as an override: if the data must stay on the machine, it stays on the
machine, regardless of context size or stakes. After that, context fit is checked, because a
request that does not fit the local window has no local option. High-stakes comes last among the
escalation conditions; everything that clears all three checks goes local by default.

`selftest()` covers five fixed cases. Two confirm the default paths (small routine goes local,
huge context goes cloud). Two confirm the override properties (high-stakes escalates, sensitive
always stays local). The fifth case is the interesting one: a sensitive request that is also over
the context limit still goes local, because sensitivity beats context size in the ordering. Read
that case before you run it; it captures the design intent of the priority order.

`run()` estimates prompt tokens by dividing character count by four, a rough but consistent
heuristic. When the decision is local, it imports `call` from `ollama_client`. The import is
deferred inside the function deliberately: `--selftest` works even when `ollama_client.py` is
nowhere on the path, because the import is never reached.

## Run It

With no rig and no key, run the selftest:

```bash
python route.py --selftest
```

What you should see:

```
selftest passed: 5 routing decisions correct
```

With the rig running and `ollama_client.py` from Module 3 on the path:

```bash
python route.py --run "reformat this function"
```

What you should see (the reply text varies; the shape does not):

```
route: local (routine request fits the local window and is cost-sensitive)
Here's the reformatted function with consistent spacing and cleaner structure:
...
```

The route line prints before the network call completes. If the import fails, the error message
tells you exactly what is missing. If the route decision surprises you, check whether
`LOCAL_CONTEXT_LIMIT` in `route.py` matches the value in `ROUTING.md`.

The next lesson records and gates the policy: it takes the thresholds you just made executable and
writes them into a decision log that Module 6 reads when it decides whether to intervene.

## Core Concepts

- A routing policy is pure logic and should be testable as such: `route(request)` takes signals
  and returns a decision with no network calls, so the selftest runs anywhere with no rig.
- The offline selftest is the machine-checkable done-when: if `--selftest` exits 0, the policy
  is correct by construction, regardless of what the live path does.
- The live path reuses `ollama_client.py` directly, so the Module 3 work compounds: the client
  you built then is now the local arm of a hybrid routing system.
- Sensitivity-first ordering encodes the override: the policy checks `sensitive` before context
  size or stakes, because keeping data on the machine is a constraint, not a preference.

<div class="claude-handoff" data-exercise="exercises/module5/build-the-router/">

**Build It in Claude Code**: Create `exercises/module5/build-the-router/route.py`, a stdlib-only router whose pure `route(request)` function decides local vs cloud from the request signals, with a `--selftest` mode that asserts the decisions offline and a `--run` path that calls your Module 3 `ollama_client.py` for the local arm.

</div>

<!-- SOURCES: https://docs.litellm.ai/docs/routing | https://docs.ollama.com/api/openai-compatibility -->
