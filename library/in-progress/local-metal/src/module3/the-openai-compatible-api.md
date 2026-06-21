# The OpenAI-Compatible API

The model is loaded and proven on-card. Now make it answer. The reason the next step matters: your
other tooling already speaks the OpenAI chat-completions shape, so if the local server speaks it
too, anything that talks to a cloud model can talk to your rig with a hostname change.

## The Two API Surfaces

Ollama exposes two API surfaces. The native surface (`/api/chat`, `/api/generate`) is Ollama's own
protocol: terse, capable, and not portable. The OpenAI-compatible surface (`/v1/chat/completions`)
is the lingua franca: the same request body works against OpenAI, against vLLM, and against your
rig.

You use the OpenAI-compatible surface for one reason: portability. Every tool in the later modules
already knows that shape. Teaching them a second protocol would mean maintaining two paths; using
the compatible API means there is one.

The base URL is `http://localhost:11434` and the endpoint is `/v1/chat/completions`
([docs.ollama.com/api/openai-compatibility](https://docs.ollama.com/api/openai-compatibility)).

## The Request by Hand

Before writing code, verify the endpoint responds. Send a bare request with `curl`:

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder:14b",
    "messages": [{"role": "user", "content": "explain a Python decorator in one sentence"}]
  }'
```

The response is a JSON object. The model's reply text sits at `choices[0].message.content`. The
outer envelope also carries `id`, `created`, `model`, and `usage` (prompt and completion token
counts), matching the OpenAI shape exactly.

Common parameters work as expected: `temperature`, `top_p`, `max_tokens`, `stop`, `seed`, and
`stream`. The `stream` key defaults to false here; set it to true to receive server-sent events
instead of a single blocking response
([docs.ollama.com/api/openai-compatibility](https://docs.ollama.com/api/openai-compatibility)).

## Build the Client

Now encode that request as a reusable function. Create
`exercises/module3/the-openai-compatible-api/ollama_client.py` with this exact code (stdlib only:
`urllib`, `json`, `argparse`):

```python
#!/usr/bin/env python3
"""
ollama_client.py: a tiny OpenAI-compatible client for the local Ollama endpoint.

This is the seed the routing layer (Module 5) and the Claude Code wiring (Module 6)
extend. It speaks Ollama's OpenAI-compatible API at /v1/chat/completions, so the same
request shape works against any OpenAI-compatible server.

Usage:
  python ollama_client.py "explain a Python decorator in one sentence"
      Live mode: POST the prompt to the local Ollama server and print the reply.

  python ollama_client.py --selftest
      Offline mode: validate request construction without a running server.
      Exits 0 on success, 1 on failure. Runnable with no hardware and no model.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "qwen2.5-coder:14b"
BASE_URL = "http://localhost:11434/v1"
ENDPOINT = f"{BASE_URL}/chat/completions"


def build_request(prompt, model=DEFAULT_MODEL):
    """Build the OpenAI-compatible chat-completions payload for a single user turn."""
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }


def call(prompt, model=DEFAULT_MODEL, endpoint=ENDPOINT):
    """POST the prompt to the local endpoint and return the model's reply text."""
    payload = json.dumps(build_request(prompt, model)).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"]


def selftest():
    """Validate request construction offline. No network, no server, no model required."""
    payload = build_request("ping", model="test-model")
    assert payload["model"] == "test-model", "model not set on payload"
    assert payload["messages"], "messages must not be empty"
    assert payload["messages"][0]["role"] == "user", "first message must be the user turn"
    assert payload["messages"][0]["content"] == "ping", "prompt not carried into content"
    assert payload["stream"] is False, "stream must be False for a single blocking reply"
    # The endpoint must be the OpenAI-compatible path, not the native /api path.
    assert ENDPOINT.endswith("/v1/chat/completions"), "endpoint is not the OpenAI-compatible path"
    print("selftest passed: request payload and endpoint are well formed")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Call the local Ollama OpenAI-compatible API.")
    parser.add_argument("prompt", nargs="?", help="the prompt to send to the model")
    parser.add_argument("--selftest", action="store_true", help="validate request construction offline")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="model tag to call")
    args = parser.parse_args()

    if args.selftest:
        sys.exit(selftest())

    if not args.prompt:
        parser.error("provide a prompt, or use --selftest")

    try:
        reply = call(args.prompt, model=args.model)
    except urllib.error.URLError as exc:
        print(f"could not reach Ollama at {ENDPOINT}: {exc}", file=sys.stderr)
        print("is the server running? check: curl http://localhost:11434/api/version", file=sys.stderr)
        sys.exit(1)
    print(reply)


if __name__ == "__main__":
    main()
```

Three functions do all the work. `build_request` assembles the payload; the shape is the same
regardless of which OpenAI-compatible server you point it at. `call` posts the payload and pulls
the reply text out of `choices[0].message.content`. `selftest` checks the payload structure and
the endpoint path without touching the network: it is the machine-checkable done-when for readers
who do not yet have the rig online.

## Run It

`--selftest` runs anywhere, no server required:

```bash
python ollama_client.py --selftest
```

What you should see:

```
selftest passed: request payload and endpoint are well formed
```

With the rig running and `qwen2.5-coder:14b` pulled, run live mode:

```bash
python ollama_client.py "explain a Python decorator in one sentence"
```

What you should see (the exact phrasing varies; the shape does not):

```
A Python decorator is a function that takes another function as input, wraps it with
additional behavior, and returns the wrapped version.
```

One sentence, no preamble, no trailing explanation: the model respects the constraint in the
prompt. If the reply is truncated or garbled, check `nvidia-smi` for VRAM pressure; if
`choices[0]` is missing from the response, the model tag is wrong or the model is not pulled yet.

## Why This Is the Seed

This client is not a throwaway. Module 5 wraps `call()` in a routing function that chooses
between this local model and a cloud fallback based on latency and cost. Module 6 exposes
`call()` to Claude Code so the editor itself can reach the local model without leaving the
development loop. Building on the OpenAI-compatible shape now is exactly what makes both of
those extensions trivial: there is nothing to translate, nothing to adapt, and no second
protocol to learn. The compounding starts here.

The rig now answers an API request the same way a cloud endpoint does. That changes what you
can reuse: every wrapper, every test, every routing policy written for one works for the other.

## Core Concepts

- The OpenAI-compatible API (`/v1/chat/completions`) is the lingua franca: one request shape
  works against OpenAI, vLLM, or your local Ollama server, with only the hostname changing.
- The `/v1/chat/completions` request body carries `model`, `messages`, and optional parameters
  (`temperature`, `max_tokens`, `seed`, `stream`); the reply text sits at
  `choices[0].message.content`.
- The `--selftest` flag validates the request payload and the endpoint path without a running
  server, giving you a machine-checkable done-when that works before the rig is online.
- `ollama_client.py` is the compounding artifact: Module 5 wraps `call()` in a router and
  Module 6 exposes it to Claude Code, so the shape you lock in here carries forward without
  rewriting.

<div class="claude-handoff" data-exercise="exercises/module3/the-openai-compatible-api/">

**Build It in Claude Code**: Create `exercises/module3/the-openai-compatible-api/ollama_client.py`, a stdlib-only OpenAI-compatible client that POSTs to `http://localhost:11434/v1/chat/completions` and prints the reply, with a `--selftest` mode that validates the request payload offline. This is the client Modules 5 and 6 reuse.

</div>

<!-- SOURCES: https://docs.ollama.com/api/openai-compatibility | https://docs.ollama.com/api/introduction -->
