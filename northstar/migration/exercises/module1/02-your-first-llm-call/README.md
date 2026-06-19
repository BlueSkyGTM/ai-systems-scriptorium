# Exercise: Your First LLM Call

**Goal:** Store an API key safely and fire a working `curl` call that returns a real Claude response.

**Why:** Every lesson from Module 2 onward calls a model. Proving you can reach one — and that your secret is stored correctly — is the door the course walks through.

## Steps

1. Create an account at [console.anthropic.com](https://console.anthropic.com) and generate an API key.
2. Add `export ANTHROPIC_API_KEY="sk-ant-..."` to your `~/.zshrc` or `~/.bashrc`. Open a new terminal and run `echo $ANTHROPIC_API_KEY` to confirm it loads.
3. Run the `curl` command from the lesson verbatim.
4. Copy the JSON response and identify these four fields: `content[0].text`, `model`, `stop_reason`, `usage.input_tokens`.
5. Write a short `notes.md` (in this folder, not committed) with: your model name, the stop reason you got, and the input/output token counts.

## Done when

The curl command returns HTTP 200 with a non-empty `content[0].text`. `echo $ANTHROPIC_API_KEY` prints the key in a fresh terminal. The key does not appear in any committed file.

## Stretch

Write the same call as a one-liner Python script using only `urllib.request` from the standard library — no SDK, no `requests`. Print `content[0].text` to stdout.
