# Module 1 · NLP: Transformer-Forward — Phase 05 Extract

> Source: `phases/05-nlp-foundations-to-advanced/` (29 lessons). Phase README is a stub (5 lines); content in per-lesson `docs/en.md`.
> **Editorial cut (per CONTEXT.md):** the transformer-forward subset starts at lesson 10. Pre-attention lessons are skipped and flagged `[ANTILIBRARY — pre-transformer]`. Where a lesson spans both classical and transformer methods, it's extracted and flagged `[CHECK: classical core, transformer-era default]` — the lesson-level audit decides.

## Skipped — Antilibrary (pre-attention)

These are listed for completeness; not extracted. They are either pre-transformer methods or the immediate precursors attention replaced.

- `01-text-processing` `[ANTILIBRARY — pre-transformer]`
- `02-bag-of-words-tfidf` `[ANTILIBRARY — pre-transformer]`
- `03-word-embeddings-word2vec` `[ANTILIBRARY — pre-transformer]`
- `04-glove-fasttext-subword` `[ANTILIBRARY — pre-transformer]`
- `05-sentiment-analysis` `[ANTILIBRARY — pre-transformer]`
- `06-named-entity-recognition` `[ANTILIBRARY — pre-transformer]`
- `07-pos-tagging-parsing` `[ANTILIBRARY — pre-transformer]`
- `08-cnns-rnns-for-text` `[ANTILIBRARY — pre-transformer]`
- `09-sequence-to-sequence` `[ANTILIBRARY — pre-transformer]` (the encoder-decoder-with-one-fixed-state failure that lesson 10 fixes)
- `16-text-generation-pre-transformer` `[ANTILIBRARY — pre-transformer]`
- `17-chatbots-rule-to-neural` `[ANTILIBRARY — pre-transformer]`

---

## Extracted — Transformer-Forward

### 10 · Attention Mechanism — The Breakthrough — **Build** · ~45min
The conceptual pivot of the whole module. Starts from the measured failure of fixed-state seq2seq (89% accuracy at length 5 → near-chance at 80) and builds Bahdanau (additive) and Luong (multiplicative) attention as the fix: keep every encoder state, recompute a weighted-average context vector at each decoder step. Includes the shape table that bites everyone (queries, scores, weights, context), the additive vs multiplicative scoring math, and the Bahdanau-uses-`s_{t-1}`/Luong-uses-`s_t` gotcha. Explicitly frames transformers as "attention plus engineering" once this exists.
**Tools/libraries:** NumPy (from-scratch `additive_attention`/`Luong`), softmax; references Bahdanau 2014, Luong 2015.

### 11 · Machine Translation — **Build** · ~75min
The working 2026 MT pipeline, skipping history: pretrained multilingual transformer encoder-decoder (NLLB-200 distilled 600M / 3.3B), SentencePiece BPE subword tokenization with shared cross-language vocab, beam search (width 4–5 + length penalty), BLEU/chrF scoring. Three operational levers named: tokenizer, model size, decoding. Notes NLLB-specific `src_lang` + `forced_bos_token_id` tricks are not interchangeable with mBART/M2M-100.
**Tools:** `transformers` (`AutoModelForSeq2SeqLM`, `.generate(num_beams=…)`), `sentencepiece`, BLEU/chrF scoring.

### 12 · Text Summarization — **Build** · ~75min
Two contrasting formulations built side by side: **extractive** TextRank (sentences-as-graph-nodes, similarity-edges, PageRank-style scoring, output always grammatical) vs **abstractive** transformer encoder-decoder (BART/T5/Pegasus, gap-sentence pretraining in Pegasus, fluent but hallucination-prone). Evaluation via ROUGE-1/2/L. The failure modes each owns: extractive misses distributed content; abstractive fabricates.
**Tools:** from-scratch TextRank (Python stdlib), `transformers` (BART/T5/Pegasus), `rouge-score`.

### 13 · Question Answering Systems — **Build** · ~75min
Three QA architectures that shaped the field: extractive (BERT-family span start/end heads, SQuAD), retrieval-augmented/open-domain (retriever→reader split, the bedrock of RAG), and generative/closed-book (decoder LLM from parametric memory, hallucination ∝ fact rarity). 2026 trend is hybrid retrieve-then-generate. Builds extractive QA with a pretrained SQuAD model and flags the `handle_impossible_answer` + `score`-check nuance.
**Tools:** `transformers` (`pipeline("question-answering")`, `deepset/roberta-base-squad2`), `sentence_transformers` for the RAG sketch.

### 14 · Information Retrieval and Search — **Build** · ~75min
The IR pipeline under every RAG/search system, built as four complementary layers: BM25 sparse retrieval (exact-match precise, sub-10ms, inverted index), dense retrieval (semantic, 50–200ms via FAISS/vector DB), Reciprocal Rank Fusion (merges ranked lists by rank not score), and cross-encoder rerank (top-30→top-5, accurate but slow per-pair). Names which failures each layer catches; positions two-way + cross-encoder rerank as the 2026 sweet spot.
**Tools:** from-scratch `BM25`, `sentence_transformers`, FAISS / vector DB, cross-encoder, RRF fusion.

### 15 · Topic Modeling — LDA and BERTopic — **Learn** · ~45min `[CHECK: classical core, transformer-era default]`
Unsupervised corpus-to-topics via two families: LDA (documents-as-topic-mixtures, topics-as-word-distributions, Bayesian inference, mixed-membership, explainable) vs BERTopic (BERT-encode → UMAP → HDBSCAN → class-based TF-IDF, one-topic-per-doc, wins on short/semantic text). Pick-by-corpus guidance. Flagged because LDA is classical, but the modern default (BERTopic) is transformer-based.
**Tools:** `sklearn` (`LatentDirichletAllocation`, `CountVectorizer`), `sentence_transformers`, UMAP, HDBSCAN.

### 18 · Multilingual NLP — **Learn** · ~45min
Cross-lingual transfer via shared SentencePiece/WordPiece vocab + shared multilingual transformer representation (mBERT/XLM-R/NLLB), enabling zero-shot transfer (fine-tune English, infer Urdu) and few-shot (100–500 target examples → 95–98% of English baseline). Includes the model table (mBERT→Aya-23) and the 2026 source-language finding: typological similarity (qWALS/LANGRANK) predicts transfer better than corpus size — for Slavic targets, German/Russian often beat English.
**Tools:** `transformers` (`xlm-roberta-large-xnli` zero-shot classification), NLLB-200, XLM-R.

### 19 · Subword Tokenization — BPE, WordPiece, Unigram, SentencePiece — **Learn** · ~60min
Why every 2026 frontier LLM ships on one of BPE/Unigram/WordPiece: solves the `[UNK]` information-loss problem by decomposing rare words into reusable subwords. Byte-level BPE guarantees zero `[UNK]`. Library roles: SentencePiece *trains* vocabs on raw Unicode, tiktoken is a fast pre-built *encoder*, HF Tokenizers does both. BPE (GPT/Llama/Gemma/Qwen/Mistral) vs Unigram (T5/mBART/Gemma) vs WordPiece (BERT).
**Tools:** from-scratch BPE trainer, `sentencepiece`, `tiktoken` (cl100k_base/o200k_base), HF `tokenizers`.

### 20 · Structured Outputs & Constrained Decoding — **Build** · ~60min
Turning "returns JSON most of the time" into "always": three layers — prompting (~80%), native structured-output APIs (OpenAI `response_format`, Anthropic tool use, Gemini JSON mode), and constrained decoding (logit processor sets invalid-token logits to −∞, 100% valid on any local model). Names the implementations (Outlines FSM, XGrammar/llguidance CFG, vLLM `guided_json`, Instructor retries) and the counterintuitive "often faster than unconstrained" result. **The field-order pitfall:** `answer` before `reasoning` commits before thinking → wrong-but-valid.
**Tools:** `transformers` logit processors, Outlines, XGrammar, vLLM `guided_json`, Instructor + Pydantic.

### 21 · NLI — Textual Entailment — **Learn** · ~60min
Natural Language Inference (entail/contradict/neutral) framed as one task with three production uses: **hallucination check** (source→summary claim), **grounded QA** (passage→answer), **zero-shot classification** (document→verbalized label). BERT/RoBERTa/DeBERTa `[CLS] premise [SEP] hypothesis`, 3-way softmax, MNLI training. This is the mechanism under HF's `zero-shot-classification` and under every RAG faithfulness metric (cf. lesson 27).
**Tools:** `transformers` (`pipeline("text-classification")`, `facebook/bart-large-mnli`, `microsoft/deberta-v3-large-mnli`).

### 22 · Embedding Models — The 2026 Deep Dive — **Learn** · ~60min
Choosing an embedding across five axes: dense/sparse/multi-vector, language coverage, context length (effective ≈ 60–70% of advertised), dimension budget (Matryoshka truncation → 6× storage for ~1% accuracy), open-vs-hosted. Dense (text-embedding-3/BGE-M3/Voyage) vs sparse (SPLADE) vs multi-vector late-interaction (ColBERTv2 MaxSim) vs BGE-M3-all-three. MTEB leaderboard is "necessary but not sufficient — benchmark on your domain." Three-tier pattern: dense first-pass → sparse+RRF recall boost → multi-vector/cross-encoder precision.
**Tools:** `sentence_transformers`, BGE-M3, SPLADE, ColBERTv2, FAISS/vector DB, MTEB.

### 23 · Chunking Strategies for RAG — **Build** · ~60min
"Chunking influences retrieval quality as much as the embedding model." Six strategies: fixed, recursive (LangChain default), semantic, sentence, parent-document, late chunking (2024), and contextual retrieval (Anthropic 2024, 35–50% improvement). Feb-2026 evidence: recursive 512-token beat semantic chunking 69%→54%; overlap gave zero benefit under SPLADE+Mistral; quality drops sharply past ~2,500 tokens. **The rule that beats defaults:** match chunk size to query type (factoid 256–512, multi-hop 512–1024, whole-section 1024–2048).
**Tools:** LangChain `RecursiveCharacterTextSplitter`, `sentence_transformers`, from-scratch fixed/recursive/semantic/parent-chunk implementations, BGE-M3/Jina v3 for late chunking.

### 24 · Coreference Resolution — **Learn** · ~60min `[CHECK: classical core, transformer-era default]`
Clustering every mention of the same entity (named/nominal/pronominal/appositive). Architectures from Hobbs 1978 rules → mention-pair → mention-ranking → **span-based end-to-end (Lee 2017, transformer-encoder, the modern default)** → generative-LLM. Five eval metrics (MUC/B³/CEAF/BLANC/LEA), CoNLL F1 ≈ 83. Flagged because it bridges classical IE and modern transformer methods; included because span-based e2e is transformer-era and it's the glue under QA/summarization/KG.
**Tools:** spaCy `en_coreference_web_trf`, AllenNLP; from-scratch Hobbs rules.

### 25 · Entity Linking & Disambiguation — **Build** · ~60min `[CHECK: classical core, transformer-era default]`
Resolving a mention to a unique KB entry (Wikidata/Wikipedia) via candidate-generation (alias index, 10–30 candidates) + disambiguation (prior+context Milne-Witten / embedding-based BLINK-REL / generative GENRE constrained to a trie of valid names). Always report both mention-recall (candidate-gen floor) and disambiguation-F1. Flagged for the same classical/transformer bridge reason as 24.
**Tools:** Wikipedia alias data / Wikidata dumps, `sentence_transformers` for BLINK-style, GENRE trie-constrained decoding.

### 26 · Relation Extraction & Knowledge Graph Construction — **Build** · ~60min `[CHECK: classical core, transformer-era default]`
Free text → `(subject, relation, object)` triples → knowledge graph. Three approaches: Hearst patterns/regex (brittle, debuggable), supervised classifier (TACRED/ACE), generative LLM. **2026 problem: LLMs hallucinate triples.** Solution is AEVS (Anchor-Extract-Verify-Supplement): anchor spans by exact position, extract, verify each triple element against source, supplement coverage. Closed-ontology vs OpenIE tradeoff. Flagged for the classical/transformer bridge; included because the AEVS provenance pattern is the seam to trustworthy LLM extraction.
**Tools:** from-scratch Hearst patterns, `transformers` relation classifier, LLM extraction + AEVS verification, Wikidata properties.

### 27 · LLM Evaluation — RAGAS, DeepEval, G-Eval — **Build** · ~75min `[THREAD: eval]`
Exact-match/F1 miss semantic equivalence; human review doesn't scale → LLM-as-judge is the production answer. Three frameworks: RAGAS (four RAG metrics: faithfulness via NLI, answer-relevance, context-precision/recall), DeepEval (pytest-for-LLMs, CI/CD-native), G-Eval (CoT judge with custom criteria, 0–1). Names the silent failures — judge bias (length/own-family/style), JSON-parse → NaN exclusion, judge-version drift — and the trust layer: **freeze judge model+version, calibrate against 100 human labels, require Spearman ρ ≥ 0.7.**
**Tools:** `transformers` NLI (`DeBERTa-v3-large-mnli-fever-anli-ling-wanli`), RAGAS, DeepEval, G-Eval, LLM judge (~GPT-4o-mini $0.003/case).

### 28 · Long-Context Evaluation — NIAH, RULER, LongBench, MRCR — **Learn** · ~60min `[THREAD: eval]`
Advertised ≠ usable context (Gemini 3 Pro: 10M advertised; at 1M tokens 8-needle MRCR drops to 26.3%; effective is ~60–70%, less for multi-hop). Benchmark tour: NIAH (needle-in-haystack, frontier-saturated baseline), RULER (13 task types, reveals multi-hop failures — only half of 17 "32k+" models held quality at 32k), LongBench v2 (production benchmark), MRCR (multi-round coreference scale), NoLiMa (non-lexical needle), HELMET, BABILong. **Report two numbers:** retrieval-effective length and reasoning-effective length (usually 25–50% of advertised).
**Tools:** custom NIAH builder, RULER, LongBench v2, MRCR, a tokenizer for depth/length control.

### 29 · Dialogue State Tracking — **Build** · ~75min `[CHECK: classical core, transformer-era default]`
Keeping the slot-value dict in sync across turns (`{cuisine, area, price}`), the hinge between what the user said and what the backend executes — still needed in 2026 for compliance domains (deterministic slots), tool-use agents, and multi-turn corrections. Architectures: rule/slot-regex → TripPy/BERT-DST → LDST (LLaMA+LoRA) → ontology-free → **LLM + Pydantic + constrained decoding (5 lines, production-ready)**. Joint Goal Accuracy (all-slots-correct), MultiWOZ 2.4 ≈ 83%. Classic failure modes: co-reference across turns, overwrite-vs-append, implicit confirmations, corrections. Flagged for classical/transformer bridge; included because the modern default is LLM + structured output.
**Tools:** from-scratch slot regex, TripPy/BERT-DST, LLaMA+LoRA (LDST), LLM + Pydantic schema + constrained decoding, MultiWOZ 2.4.

---

## Notes for the lesson-level audit

- **The 09→10 seam is the single most important cut in this phase.** Lessons 10 onward all assume attention/transformers; 01–09 and 16–17 don't. If any pre-attention lesson survives the audit, it's 09 (seq2seq) as the immediate motivator for 10 — but the spec is explicit that it's antilibrary.
- **Five lessons (15, 24, 25, 26, 29) are classical-and-modern hybrids.** I extracted and flagged them because their *modern defaults* (BERTopic, span-based e2e coref, BLINK-style EL, transformer RE, LLM+structured-output DST) are transformer-era and connect directly to RAG/eval/agent seams. The audit may demote any to antilibrary.
- **Eval thread (lessons 21, 27, 28)** is concentrated here and feeds Gap 1 (the eval thread). 21 (NLI) is the backend of 27 (RAGAS faithfulness); 28 (long-context) is the capacity-truth bench. Worth surfacing as a cluster.
- **RAG seam** lives across 13 (QA) + 14 (IR) + 22 (embeddings) + 23 (chunking) + 27 (RAGAS). These five are the Phase-05 half of Module 2's RAG material (Phase 11 has the build-track RAG).
