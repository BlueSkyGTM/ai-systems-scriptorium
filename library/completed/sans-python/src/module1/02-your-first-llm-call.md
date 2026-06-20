# Your first LLM call

Every lesson from Module 2 onward assumes you can reach a model. That assumption starts here.

**You build** a working API call that sends a prompt to Claude and prints a real response — no SDK, no Python, no framework. Plain HTTP.

## Get your API key

Go to [console.anthropic.com](https://console.anthropic.com), create an account, and generate an API key. Copy it once — you will not see it again.

## Store the key safely

The key is a secret. It never goes in code, never in a file you commit, and never in a log. Store it as an environment variable:

```sh
export ANTHROPIC_API_KEY="sk-ant-..."
```

Add that line to your `~/.zshrc` or `~/.bashrc` so it loads in every shell session. Verify it landed:

```sh
echo $ANTHROPIC_API_KEY
```

If you see the key, you are set. If you see nothing, the export did not persist — add it to the shell config file and open a new terminal.

**The rule:** env vars for secrets, `.gitignore` for `.env` files, never source-control a key. A key in git history is compromised even after deletion.

## Make the call

HTTP first. The SDK wraps this, but seeing the raw request once shows you what the SDK hides:

```sh
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-4-8",
    "max_tokens": 256,
    "messages": [
      {"role": "user", "content": "What is one sentence every AI Platform Engineer should know?"}
    ]
  }'
```

## Read the response

The API returns JSON. The shape you will see repeatedly:

```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "The model does not know what it cannot do — you do."
    }
  ],
  "model": "claude-opus-4-8",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 22,
    "output_tokens": 17
  }
}
```

Four fields matter now: `content[0].text` is the reply, `model` confirms which model answered, `stop_reason` tells you why generation stopped, and `usage` shows the token count. Token count is billing. Every call costs tokens. Keep `max_tokens` bounded.

## What just happened

You sent a structured HTTP request with your key in the header and a message array in the body. The model returned a structured JSON response. This is the whole API surface — every SDK, every framework, every agent library makes this same call underneath. Understanding the shape means you can debug anything built on top of it.

SDKs — `anthropic` in Python, `@anthropic-ai/sdk` in TypeScript — arrive at their language's point-of-use. Use them then. For now, knowing the wire format is enough.

Everything from Module 2 onward assumes you can call a model — this is the door the whole course walks through.

## Core concepts

- An LLM API is an HTTP POST with your key in a header and a message array in the body; every SDK wraps this and nothing more.
- Secrets live in environment variables, never in code or git history — a committed key is compromised even after deletion.
- The response shape (`content`, `model`, `stop_reason`, `usage`) stays constant across calls; `usage` is your billing meter.
- `max_tokens` bounds cost and latency; always set it.

<div class="claude-handoff" data-exercise="exercises/module1/02-your-first-llm-call/">

**Build it in Claude Code** — get a key, store it safely, fire the curl call, and parse the response. Open the repo and run the exercise for this lesson.

</div>
