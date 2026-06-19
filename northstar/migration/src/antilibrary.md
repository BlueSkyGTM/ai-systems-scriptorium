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
Made-with-ML model-centric MLOps (training pipelines, experiment tracking, model lifecycle) — the deploy/
serving/CI subset stays.

**M6–M8 — model-training builds.** GPT-from-scratch (capstone Part-2, 30–49: BPE → embeddings → attention →
transformer block → GPT assembly → training loop → SFT → DPO) + distributed training from scratch (76–81:
DDP/FSDP/ZeRO/pipeline). The sharpest cuts — building a model, not a platform.

## Course-wide foundations depth

`ai-engineering-from-scratch` 500+ from-scratch lessons — **linked, not reproduced** ([[antilibrary-principle]]).
Math foundations (linear algebra/calculus for backprop, matrix ops), ML fundamentals, deep-learning core,
computer vision, speech/audio, reinforcement learning, LLMs-from-scratch (Karpathy territory). `asdg`
antilibrary subset: Ch01 (LLM internals at implementation depth), Ch03 (training/adaptation), Ch04 (inference
optimization — handled in M5 via aipe).
