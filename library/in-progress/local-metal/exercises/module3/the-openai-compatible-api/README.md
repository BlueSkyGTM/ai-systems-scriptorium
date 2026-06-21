# Exercise: The OpenAI-Compatible API

**Goal:** Create `exercises/module3/the-openai-compatible-api/ollama_client.py`: a stdlib-only
client that POSTs a prompt to Ollama's OpenAI-compatible endpoint and prints the reply, with a
`--selftest` flag that validates the request payload offline without a running server.

**Why:** This is the throughline artifact for Module 3 and the seed the rest of the book builds
on. The routing layer in Module 5 wraps `call()` to choose between local and cloud; the Claude
Code wiring in Module 6 exposes it to the editor. Both reuse this exact file. Speaking the
OpenAI-compatible shape now means there is nothing to translate later.

## Files You Are Editing

- `exercises/module3/the-openai-compatible-api/ollama_client.py` (create it; this is the
  compounding artifact; do not move or rename it: Module 5 imports it from here)

## Steps

1. Create `exercises/module3/the-openai-compatible-api/ollama_client.py` with the following
   exact code:

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

2. Run the selftest to confirm the file is correctly structured:

   ```bash
   python ollama_client.py --selftest
   ```

**Note:** `--selftest` runs with no server and no model. Live mode requires the rig to be online
with Ollama running (`ollama serve` or the system service) and the model pulled
(`ollama pull qwen2.5-coder:14b`). If you do not yet have the rig set up, `--selftest` is the
complete done-when for now; return to live mode once the model is on-card.

## Done When

- `python ollama_client.py --selftest` exits 0 and prints the selftest line (no rig needed).
- With the rig online: `python ollama_client.py "explain a Python decorator in one sentence"`
  exits 0 and prints the model's reply.

## Expected Output Shape

Selftest (always):

```
selftest passed: request payload and endpoint are well formed
```

Live mode (representative; the exact phrasing varies):

```
A Python decorator is a function that takes another function as input, wraps it with
additional behavior, and returns the wrapped version.
```

## Stretch

Add a `--system` flag that prepends a system message to the `messages` array before the user
turn. A system message sets the model's behavior for the conversation:

```json
{"role": "system", "content": "Reply in exactly one sentence. No preamble."}
```

Update `build_request` to accept an optional `system` parameter (default `None`). When it is
set, insert the system message as the first element of `messages`. Re-run `--selftest` after
the change: add an assertion that confirms the system message appears first when the parameter
is provided and that `messages` still starts with the user turn when it is not.
