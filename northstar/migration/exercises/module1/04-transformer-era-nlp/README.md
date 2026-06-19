# Exercise: Tokenizer Inspection

## Goal

Measure how token counts differ across content types using a real tokenizer — English prose, JSON, Python code, and a non-Latin script, all carrying equivalent information.

## Why

The tokenizer determines prompt cost and context budget. The same information encoded differently can consume 2–4× the tokens, which changes what fits in a context window and what it costs to call.

## Steps

1. Install `tiktoken` (for OpenAI-family models) and `transformers` (for a second tokenizer, e.g. Llama or T5's SentencePiece).
2. Write four representations of the same fact — for example, a description of a product order:
   - English prose (2–3 sentences)
   - JSON object with the same fields
   - Python dataclass instantiation
   - A translation of the prose into a non-Latin script (Japanese, Arabic, or Hindi — use a translation API or a pre-translated string)
3. Tokenize each representation with both tokenizers.
4. Print a table: representation × tokenizer × token count × ratio vs. the English prose baseline.
5. Inspect 5 tokens from each representation and print the decoded subwords — note any surprising splits.

## Done when

- The script prints a table with token counts and ratios for all four representations across both tokenizers.
- You can identify which representation is most token-efficient and which is least, and state why in a one-line comment in the script.

## Stretch

Add a fifth representation: the same data as a markdown table. Measure whether structured markdown is more or less efficient than JSON for the same schema.
