# Module 2: LLM Engineering

The LLM engineering core: prompting → embeddings/RAG → evaluation → the agent on-ramp. Everything is
**tool-first**; you use foundation models as APIs, not train them. This is the densest module; the work is
curation (one RAG spine, one eval thread), not new sequencing.

Four chapters:

1. **Prompting & Context**; engineering the call: instruction hierarchy, few-shot/CoT/ToT, context
   engineering, structured outputs, prompt-injection defense.
2. **Embeddings & RAG**; the canonical RAG spine, fundamentals → production at scale.
3. **Evaluation**; eval-driven development: LLM-as-judge, the RAG triad, observability, statistical
   correction.
4. **The Agent On-Ramp**; structured output → function calling → MCP (intro) → LangGraph → the complexity
   ladder. The bridge into Module 3.

**Data is given here.** RAG runs on pre-curated corpora so you build pipeline intuition on clean data first;
building the data layer comes in Module 5. **Fine-tune vs prompt** is taught as a *decision* you own; the
LoRA/QLoRA *implementation* is out of scope. **Generative media** (GANs, diffusion) is cut entirely.
