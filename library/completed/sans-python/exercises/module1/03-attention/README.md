# Exercise: Attention and Prompt Position

## Goal

Measure how prompt position affects LLM recall — place the same fact at the start, middle, and end of a long prompt and record where the model loses it.

## Why

Attention is a weighted sum over input positions. Context-window limits and prompt-position sensitivity are both downstream of that design. This exercise makes the effect concrete and measurable, not just conceptual.

## Steps

1. Choose a target fact (a made-up name, date, and role — something the model cannot know from training).
2. Write a padding template: lorem-ipsum paragraphs that bring the total prompt to roughly 4,000 tokens.
3. Build three prompts: fact at the start (first 200 tokens), fact at the middle (tokens 1,800–2,000), fact at the end (last 200 tokens).
4. For each prompt, ask the model to retrieve the target fact in a single sentence.
5. Run each prompt 5 times. Record whether the model retrieved the fact correctly, partially, or not at all.
6. Print a position × accuracy table.

## Done when

- The script runs without errors and prints a table showing retrieval accuracy (correct / partial / miss) for each of the three positions across 5 trials.
- At least one position shows a measurably different accuracy from the others.

## Stretch

Extend to five positions (0%, 25%, 50%, 75%, 100% into the prompt) and plot retrieval accuracy vs. position. Try a second model and compare the curves.
