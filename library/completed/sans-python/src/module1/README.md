# Module 1 — Foundations

The environment, your first call against a live model, and the transformer-forward NLP that everything
LLM-related assumes. Two chapters:

1. **Setup & First Call** — the day-one, four-layer install stack, then your first LLM call against it. The
   universal root: every hands-on lesson in the course depends on the stack, and the first call proves it
   runs.
2. **NLP: Transformer-Forward** — from **attention** forward, through transformer-era NLP and into the
   retrieval and evaluation foundations the rest of the book builds on. How transformers work is seam
   knowledge for every engineer who designs prompts and evals. The pre-transformer half (classical NLP,
   RNN/LSTM, seq2seq) is in the [Antilibrary](../antilibrary.md).

**Languages install here, but you learn them later.** You set up the TypeScript and Rust toolchains in
Setup & Tooling, but the *teaching* is threaded to point-of-use: TypeScript arrives in Module 3 (your first
typed tools and MCP contracts), Rust in Module 5 (the serving layer). This is the Sans Python sequencing
thesis — no front-loaded language wall.

**What this module feeds forward:** the NLP chapter's retrieval components (QA, information retrieval,
embeddings, chunking) are the foundations half of Module 2's RAG system; its evaluation lessons (NLI,
LLM-evaluation, long-context) seed the course-wide eval-driven-development thread.
