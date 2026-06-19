# Exercise: Embedding Context-Length Truncation

## Goal

Measure where an embedding model's retrieval quality degrades by placing the same target fact at different positions within a long document and running a similarity search.

## Why

Effective embedding context length is roughly 60–70% of the advertised number. Knowing where your embedding model actually degrades lets you set chunk sizes that keep retrieval reliable — not chunk sizes that hit the stated limit and silently lose facts.

## Steps

1. Pick an embedding model with a stated context window of at least 512 tokens (e.g. `BAAI/bge-small-en-v1.5` at 512, or `text-embedding-3-small` at 8191). Note the advertised limit.
2. Write a target fact: a made-up person's name, title, and a numerical detail (e.g. a budget figure).
3. Write a padding corpus: 10 sentences of filler text, each roughly 50 tokens.
4. Build 5 documents by inserting the target fact at token positions 10%, 25%, 50%, 75%, and 90% of the model's advertised context length. Fill the remaining tokens with padding.
5. Embed each document. Embed a short query that asks for the target fact (e.g. "What is [name]'s budget figure?").
6. Compute cosine similarity between the query embedding and each document embedding.
7. Print a table: position (%) × cosine similarity × rank if multiple documents are in the index.

## Done when

- The script runs and prints a table of similarity scores for each position.
- You can identify the position at which similarity begins to fall and state the effective context length (as a percentage of advertised) in a one-line comment.

## Stretch

Repeat the experiment with a second embedding model and compare the effective-length percentages. Plot similarity vs. position for both models on the same chart.
