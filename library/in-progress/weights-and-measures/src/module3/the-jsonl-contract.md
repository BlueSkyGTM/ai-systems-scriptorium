# The JSONL Contract

The upload button does not tell you your data is wrong. The fine-tuning job starts, runs for
hours, and exits cleanly; the resulting model is just quietly worse than it should be, because
a handful of malformed lines were skipped or mis-parsed without ceremony. The contract is simple
and strict: one JSON object per line, a `messages` array in every object, a valid role and
non-empty content in every message. A line that violates any part of it is a training example
the model never saw.

## One Line, One Example

A JSONL file for chat fine-tuning is a sequence of independent JSON objects, one per line. No
surrounding array, no commas between lines: each line is self-contained. The file as a whole is
not valid JSON; each line on its own is. A blank line is silently skipped. A non-blank line that
is not valid JSON is a failure.

The `messages` key holds an array of turn objects, in conversation order. The Azure AI Foundry
fine-tuning documentation
([learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning))
specifies the schema and provides this canonical example:

```json
{"messages": [{"role": "system", "content": "Clippy is a factual chatbot that is also sarcastic."}, {"role": "user", "content": "Who discovered Antarctica?"}, {"role": "assistant", "content": "Some chaps named Fabian Gottlieb von Bellingshausen and Mikhail Lazarev, as if they don't teach that in every school!"}]}
```

That is one line in the file. Three turns: a system prompt that sets the persona, a user
question, an assistant answer. The model learns to produce the assistant turn given the prior
context. Get any piece of that structure wrong, and the example is either rejected or silently
misread.

## The Role Constraint

Every turn object has exactly two required fields: `role` and `content`. The role must be one
of three strings:

- `system`: sets the model persona or task framing; optional, but common
- `user`: the human side of the turn
- `assistant`: the model's response; the turn the fine-tune is teaching

Any other string is an unknown role and the example fails. The validator `check_dataset.py`
captures this as `role-unknown`, with the offending string quoted:

```
line 2 message[0]: role-unknown ('oracle')
```

The content field must be a non-empty string after stripping whitespace. A turn with `"content":
"  "` fails as `content-empty`. A turn with `"content"` absent fails as `content-missing`.

## What the Validator Catches

`check_dataset.py` reads a JSONL file line by line and returns a list of named failure reasons.
The selftest output from `FREEZE-VERIFIED.md` shows every failure class in action:

```
[FAIL] BAD invalid JSON line
    - line 2: invalid-json
[FAIL] BAD unknown role
    - line 2 message[0]: role-unknown ('oracle')
[FAIL] BAD empty content
    - line 2 message[0]: content-empty
[FAIL] BAD exact duplicate
    - line 3: duplicate (matches line 1)
```

The full set of named reasons the validator returns:

| Reason | What triggered it |
|---|---|
| `invalid-json` | The line is not parseable as JSON |
| `messages-missing` | The top-level object has no `messages` key |
| `messages-not-list` | `messages` is present but not an array |
| `messages-empty` | `messages` is an empty array |
| `message-not-object` | A turn entry is not a dictionary |
| `role-missing` | A turn has no `role` key |
| `role-unknown` | The role string is not `system`, `user`, or `assistant` |
| `content-missing` | A turn has no `content` key |
| `content-empty` | The content string is empty or whitespace-only |
| `duplicate` | This example's content hash matched an earlier line in the same file |

The validator exits non-zero on any failure. A clean file exits 0 and prints `[PASS]`.

## The Optional `weight` Field

An assistant turn can carry an optional `weight` field set to `0` or `1`. Setting `weight` to
`0` tells the fine-tuning infrastructure to skip that turn's loss contribution: the model reads
the turn as context but is not trained to reproduce it. This is useful for long reasoning chains
where only the final answer matters. The validator does not require `weight`; most datasets omit
it entirely.

## Validate Before You Upload

The Azure AI Foundry platform rejects datasets that fail schema checks, but it rejects them at
job-submission time, not at upload time. You find out after waiting for the validation pass to
run. Running `check_dataset.py` locally takes seconds:

```
python check_dataset.py your_data.jsonl
```

A clean file prints `[PASS]` for each check and exits 0. A broken file prints the named failure
reason and the line number. Fix every failure before uploading. The validation-at-upload habit is
the difference between catching a `role-unknown` in ten seconds on your machine and catching it
after a ten-minute job submission cycle.

The same validator catches the duplicate case that silent preprocessing misses: two examples with
identical normalized content report `duplicate (matches line N)`. A dataset where the model sees
the same example multiple times biases training toward those examples and wastes the budget. The
validator's content hash catches this before the job starts.

A format the machine rejects is a fine-tune that never starts. Validate every line before you
upload.

## Core Concepts

- A JSONL fine-tune file is one JSON object per line, not a JSON array. Each line is
  independent; the file as a whole is not valid JSON. A non-blank line that fails JSON parsing
  is a training example the model never sees.
- Every line must contain a `messages` key whose value is a non-empty array of turn objects.
  Each turn requires `role` (one of `system`, `user`, or `assistant`) and a non-empty `content`
  string. Any deviation produces a named failure reason from the validator.
- The nine named failure reasons `check_dataset.py` returns (`invalid-json`,
  `messages-missing`, `messages-not-list`, `messages-empty`, `message-not-object`,
  `role-missing`, `role-unknown`, `content-missing`, `content-empty`) map one-to-one to the
  structural rules in the schema. A clean file exits 0; any failure exits non-zero.
- The optional per-assistant `weight` field (0 or 1) lets you exclude a turn from the loss
  without removing it from context. Most datasets omit it.
- Validating locally before uploading collapses a multi-minute job-submission cycle into
  a ten-second command. A format the machine rejects is a fine-tune that never starts.

<div class="claude-handoff" data-exercise="exercises/module3/the-jsonl-contract/">

**Build It in Claude Code**: Write a small JSONL file with at least five chat examples in the
`messages` schema shown in this lesson, then deliberately introduce one invalid-json line, one
`role-unknown` turn, and one `content-empty` turn. Run `python check_dataset.py your_data.jsonl`
and read the named failure reasons it prints. Fix each failure in turn until the file exits 0
with `[PASS]`. The goal is not to produce a clean file by guessing; it is to read the validator's
output, trace each named reason back to the line it flagged, and correct that exact structural
flaw.

</div>
