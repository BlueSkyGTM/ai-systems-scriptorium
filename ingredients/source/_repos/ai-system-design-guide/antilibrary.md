# Antilibrary — Out-of-Seam Chapters

> Chapters kept for reference but outside the systems-design seam (prompting → retrieval → agents → infra/eval).

## Chapter 01 — Foundations

- **Why antilibrary:** Covers LLM internals and model mechanics; foundational theory rather than systems-design practice.
- **Sub-sections:**
  - LLM Internals
  - Tokenization Deep Dive
  - Attention Mechanisms
  - Transformer Architecture
  - Embeddings and Vector Spaces
  - Inference Pipeline

## Chapter 02 — Model Landscape

- **Why antilibrary:** Reference material on evaluating, pricing, and selecting models; not part of the core build/deploy seam.
- **Sub-sections:**
  - Model Taxonomy
  - Capability Assessment
  - Pricing and Costs
  - Model Selection Guide

## Chapter 03 — Training and Adaptation

- **Why antilibrary:** Addresses pretraining, fine-tuning, and alignment techniques — model development rather than system design.
- **Sub-sections:**
  - Pretraining Basics
  - Fine-Tuning Strategies
  - LoRA, QLoRA, and PEFT
  - RLHF and DPO (Alignment)
  - Knowledge Distillation
  - Synthetic Data Generation
  - Quantization Deep Dive

## Chapter 04 — Inference Optimization

- **Why antilibrary:** Focuses on low-level inference performance and serving internals; supporting reference rather than core seam material.
- **Sub-sections:**
  - Inference Fundamentals
  - KV Cache and Context Caching
  - Speculative Decoding
  - Batching Strategies
  - PagedAttention
  - Serving Infrastructure
  - Cost Optimization Playbook

## Chapter 10 — Document Processing

- **Why antilibrary:** Covers OCR and layout analysis utilities; a peripheral data-processing topic outside the systems-design seam.
- **Sub-sections:**
  - OCR and Layout Analysis
