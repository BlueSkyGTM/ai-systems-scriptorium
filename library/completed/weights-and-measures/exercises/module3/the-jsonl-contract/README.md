# Exercise: The JSONL Contract

## Goal

Write a set of JSONL fine-tuning examples from scratch, run `check_dataset.py` against them,
fix every named failure, and exit 0 with a clean file.

## Why

The Azure OpenAI fine-tuning API accepts exactly one format: a JSONL file where every line is a
valid JSON object with a `messages` array, and every message in that array has a `role` (one of
`system`, `user`, `assistant`) and a non-empty string `content`. There is no partial credit. A
single malformed line causes the upload to fail or the training job to reject the dataset. The
failure mode is silent: the API will not always tell you which line failed or why. The only
reliable defense is a local validator that catches every named failure before the file leaves
your machine. This exercise puts that defense in place.

## What You Are Building

A file `my_data.jsonl` with at least 10 chat examples, and the discipline to run the gate
before calling anything else a deliverable.

## Steps

1. Create `exercises/module3/the-jsonl-contract/my_data.jsonl` with at least 10 examples in the
   fine-tuning format. Each line must be a complete JSON object on a single line, not wrapped
   across multiple lines. A valid example looks like this:

   ```json
   {"messages": [{"role": "system", "content": "You are a concise assistant."}, {"role": "user", "content": "What is a loss function?"}, {"role": "assistant", "content": "A measure of how far the model's predictions are from the true labels."}]}
   ```

   Cover at least three distinct behaviors or topics so the set has real coverage breadth.

2. Run the validator against your file:

   ```
   python exercises/spine/check_dataset.py my_data.jsonl
   ```

   Read every failure it prints. The failure names it produces are:

   - `invalid-json`: the line is not parseable JSON.
   - `messages-missing`: the object has no `messages` key.
   - `messages-not-list`: `messages` is present but is not a list.
   - `messages-empty`: `messages` is an empty list.
   - `message-not-object`: a message entry is not a dict.
   - `role-missing`: a message has no `role` key.
   - `role-unknown`: a message role is not in `{system, user, assistant}`.
   - `content-missing`: a message has no `content` key.
   - `content-empty`: a message content is an empty or whitespace-only string.
   - `duplicate`: this example's content hash matches an earlier line.

3. Fix every failure. Re-run the validator after each fix. Do not move on until you see:

   ```
   [PASS] my_data.jsonl
   ```

4. Deliberately introduce one of each of the following failures in a separate file,
   `bad_examples.jsonl`, so you can confirm the validator catches them:

   - A line that is not valid JSON.
   - A message with `"role": "oracle"`.
   - A message with `"content": "   "` (whitespace only).

   Run:

   ```
   python exercises/spine/check_dataset.py bad_examples.jsonl
   ```

   Confirm the output names each failure. Then delete `bad_examples.jsonl`.

## Done When

`python exercises/spine/check_dataset.py my_data.jsonl` exits 0 and prints:

```
[PASS] my_data.jsonl
```

## Estimated Time

30 to 40 minutes.

## Stretch

Add an optional `"weight": 0` field to one assistant turn in `my_data.jsonl`. This tells the
fine-tuning API to skip that turn from the loss calculation, which is useful when an assistant
response is necessary for conversational flow but is not a behavior you are training. Confirm
the validator still exits 0: the `weight` field is optional and does not affect validity.
