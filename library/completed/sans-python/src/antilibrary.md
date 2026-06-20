# Antilibrary

Material held, not discarded — known and roughly located, reached for when a specific problem surfaces. This
page records what each module cut and why. (See `SYLLABUS.md` Antilibrary for the authoritative list.)

> *We don't need to read all of it. We just need to know it exists and roughly where to find it.*

## The throughline (Optimize ruling)

**The platform engineer builds and operates the platform; they don't train the models or set frontier-safety
policy.** Keep the decisions and the operations; antilibrary the training implementation and the research
survey. ([[optimize-archetype-ruling]])

## By module

**M1 — pre-transformer NLP.** Text processing, bag-of-words/TF-IDF, word2vec, GloVe/fastText, sentiment, NER,
POS/parsing, CNN/RNN for text, seq2seq, pre-transformer generation, rule-to-neural chatbots. The 09→10 seam
(seq2seq failure → attention) is the cut line.

**M2 — generative media + fine-tune implementation.** GANs, diffusion (DDPM/latent), video/audio/3D, VAR
(~90% off-seam by the source's own flags). The LoRA/QLoRA *implementation* (adapter injection, NF4
quantization) — keep the fine-tune-vs-prompt *decision*, antilibrary the build.

**M4 — frontier-safety research & policy.** STaR/V-STaR/Quiet-STaR, AlphaEvolve, Darwin Gödel Machine, AI
Scientist v2, Automated Alignment Research, recursive-self-improvement theory, bounded-self-improvement
designs, RSP v3.0, OpenAI PF / DeepMind FSF, METR time horizons, CAIS/CAISI. AI-safety-researcher /
policy-analyst material, not platform-build. (Operational agent safety — guardrails, kill switches, HITL —
stays in M4.)

**M5 — model-centric depth.** `ai-performance-engineering` training & CUDA subset (ch01–14: distributed
training FSDP/TP/PP, CUDA kernels, Triton, GPU-architecture deep dive) — perf-eng is inference-only.
Made-with-ML *deep* model-centric MLOps: training pipelines, model lifecycle, deep data-versioning (DVC) and
pipeline orchestration (Airflow/Prefect/Kubeflow), and fine-tuning *implementation* (training loops, dataset
engineering, optimizer internals). **Brought back at literacy depth in M5 ch5 (lessons 11–13):** data
ingestion (Docling), experiment tracking (MLflow), and fine-tuning *decisions* (LoRA/QLoRA literacy) — enough
to build the common case and speak to the rest; the deep build stays here → *Avec Python*.

**M6–M8 — model-training builds.** GPT-from-scratch (capstone Part-2, 30–49: BPE → embeddings → attention →
transformer block → GPT assembly → training loop → SFT → DPO) + distributed training from scratch (76–81:
DDP/FSDP/ZeRO/pipeline). The sharpest cuts — building a model, not a platform.

## Course-wide foundations depth

`ai-engineering-from-scratch` 500+ from-scratch lessons — **linked, not reproduced** ([[antilibrary-principle]]).
Math foundations (linear algebra/calculus for backprop, matrix ops), ML fundamentals, deep-learning core,
computer vision, speech/audio, reinforcement learning, LLMs-from-scratch (Karpathy territory). `asdg`
antilibrary subset: Ch01 (LLM internals at implementation depth), Ch03 (training/adaptation), Ch04 (inference
optimization — handled in M5 via aipe).

**Named *Avec Python* candidates** (the conceptual companion that may one day compile this antilibrary): the
**ML math** above (linear algebra / calculus / probability — the Machine-Learning-Engineer / Path-A
prerequisites the cusp splinter deliberately left behind) and **advanced Python** (NumPy / Pandas / vectorized
ops — the ~94%-of-postings screen the point-of-use "Sans Python" approach does not drill). Held, not
discarded; reached for when communicating with others, filling a gap, or remembering there is always more to
learn — zero risk in being discerning. See `build-stages/hireability-alignment.md` and
`build-stages/roadmap-coverage.md`.

---

None of this is a confession. A book that cut nothing would be a reading list, not a path, and a path is the
only thing that gets you to the job. Every entry above was left out so the sequence could hold — so you could
build on day one instead of grinding through a wall that was never load-bearing. The discernment that drew
these lines is the same discernment the job rewards: knowing what to learn next is worth as much as knowing
what you already know, and it costs nothing to hold a thing in reserve until a real problem asks for it.

So read this page as a map, not a deficit. When retrieval breaks in a way chunking can't fix, when a model
genuinely needs fine-tuning and the decision you learned to make now needs the build behind it, when the math
under an eval stops being a black box you can trust — you will know the name of what you need and roughly
where it lives. That is not a gap. That is the next move, already located. There is always more to learn; the
skill is knowing it exists, and knowing when it's your turn to go get it.
