# Transformer-Era NLP

You won't implement these models. You will call them, configure them, and debug them — and the decisions that cost you production headaches live at the tokenizer and the output format, not inside the architecture.

## Pretrained encoder-decoders

Machine translation and summarization are the clearest examples of what a pretrained encoder-decoder does: encode the source sequence into a rich representation, decode it into the target sequence. You don't train these from scratch. You pick a pretrained checkpoint (NLLB-200 for translation, BART or T5 for summarization), configure the decoding (beam width, length penalty), and evaluate the output (BLEU/chrF for translation, ROUGE for summarization).

Abstractive summarization is fluent but hallucination-prone; extractive summarization is always grammatical but misses distributed content. The failure modes are different — knowing which model family you're using tells you which failures to expect.

## Subword tokenization

Every frontier LLM ships on subword tokenization — BPE, WordPiece, or Unigram — for one reason: it eliminates the out-of-vocabulary problem. Word-level vocabularies fail on rare words, new terms, and code; character-level vocabularies produce extremely long sequences. Subwords split rare words into reusable pieces. Byte-level BPE goes further: it operates on raw bytes, so the vocabulary covers every possible input and the `[UNK]` token disappears entirely.

The practical split: BPE is used by GPT, Llama, Gemma, Mistral, and Qwen. Unigram is used by T5 and mBART. SentencePiece trains vocabularies on raw Unicode; tiktoken and HuggingFace Tokenizers encode text with a pre-built vocabulary. They are not interchangeable — the tokenizer is part of the model contract.

Why this matters for platform engineering: the tokenizer determines prompt cost, context budget, and the way code, numbers, and non-English text consume tokens. A 1,000-word English prompt is not the same token count as a 1,000-word Japanese prompt.

[MS-Learn: Verify Azure OpenAI tokenization behavior for non-Latin scripts and code in production deployments]

## Structured outputs and constrained decoding

Getting structured JSON from an LLM has three reliability tiers. Prompting works roughly 80% of the time — it fails on complex schemas and adversarial inputs. Native structured-output APIs (OpenAI's `response_format`, Anthropic tool use, Gemini JSON mode) move you past that, but still rely on the model following instructions. Constrained decoding is the ceiling: a logit processor sets invalid-token logits to −∞ before sampling, so it's structurally impossible to produce invalid output. Implementations include Outlines, XGrammar, vLLM's `guided_json`, and Instructor.

One counterintuitive result: constrained decoding is often faster than unconstrained, because the model wastes no probability mass on invalid tokens.

The field-order pitfall is worth naming directly: if your schema puts `answer` before `reasoning`, the model commits to an answer before it has reasoned. Reverse the field order — `reasoning` first, `answer` last — to let the model think before it commits.

This feeds Module 3's reliable tool calls directly. A tool call is a structured output with a function signature as the schema; the same three-tier reliability stack applies.

Tokenization and structured outputs are where prompt cost, context budget, and tool-call reliability are decided — before a single agent runs.

## Core concepts

- Subword tokenization (BPE/WordPiece/Unigram) eliminates `[UNK]` by splitting rare words into reusable pieces; byte-level BPE guarantees zero unknown tokens by operating on raw bytes.
- The tokenizer is part of the model contract — BPE and Unigram models are not interchangeable, and token counts vary significantly across languages and content types.
- Structured-output reliability follows three tiers: prompting (~80%) → native APIs → constrained decoding (100% valid); the tier you choose determines how much downstream code must handle parse failures.
- Placing `answer` before `reasoning` in a schema commits the model before it thinks — field order is a reliability decision, not a style choice.

<div class="claude-handoff" data-exercise="exercises/module1/04-transformer-era-nlp/">

**Try it in Claude Code** — inspect a tokenizer to measure how token counts differ across content types: tokenize identical information expressed as English prose, JSON, Python code, and a non-Latin script, then compute the ratio.

Open the repo and pick up from this lesson.

</div>
