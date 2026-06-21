# Local Metal — Module 3 Source Provenance

Cited-resource record for Module 3 ("The Model Stack"). Per the authoring directive, every external
resource a lesson cites is captured here as tracked ore: the URL, what it grounds, the source type,
and the retrieval date. The shipped book cites the URLs; this manifest preserves the underlying fact
against link rot. Retrieved 2026-06-21 by the M3 source-fetch tier (three Haiku fetchers) and the
authoring fleet (Sonnet workers + conductor), grounded via official Ollama, Docker, NVIDIA, and
Hugging Face docs plus the Microsoft Learn connector where it has coverage.

## Serving layer install (Lesson 1: install-ollama-and-docker)

| Fact grounded | Source | Type |
|---|---|---|
| Ollama Linux install (`curl -fsSL https://ollama.com/install.sh \| sh`); systemd service at `/etc/systemd/system/ollama.service` (`ExecStart=/usr/bin/ollama serve`, user `ollama`) | https://docs.ollama.com/linux | Ollama (authoritative) |
| Default endpoint `http://localhost:11434`; API base `/api`; OpenAI-compat base `/v1` | https://docs.ollama.com/api/introduction | Ollama (authoritative) |
| Bind address 127.0.0.1:11434, `OLLAMA_HOST` override; default models dir `/usr/share/ollama/.ollama/models`, `OLLAMA_MODELS` override | https://docs.ollama.com/faq | Ollama (authoritative) |
| Docker Engine on Ubuntu via the official apt repository (GPG key + repo + `apt install docker-ce ...`) | https://docs.docker.com/engine/install/ubuntu/ | Docker (authoritative) |
| NVIDIA Container Toolkit (configures the NVIDIA container runtime so `docker run --gpus=all` reaches the host GPU) | https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html | NVIDIA (authoritative) |
| Official `ollama/ollama` Docker image; GPU run `docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama` (named as the option; book runs native) | https://docs.ollama.com/docker | Ollama (authoritative) |

## A 14B model on-card (Lesson 2: a-14b-model-on-card)

| Fact grounded | Source | Type |
|---|---|---|
| `qwen2.5-coder:14b` exists; default quantization Q4_K_M; 9.0 GB on disk | https://ollama.com/library/qwen2.5-coder:14b | Ollama library (authoritative) |
| Tag/size matrix: Q2_K 5.8 GB, Q3_K_M 7.3 GB, Q4_K_M 9.0 GB, Q8_0 16 GB, FP16 30 GB | https://ollama.com/library/qwen2.5-coder/tags | Ollama library |
| Quantization meaning (Q4_K_M = 4-bit hierarchical K-quant; Q8_0 = 8-bit); GGUF size breakdown | https://huggingface.co/bartowski/Qwen2.5-Coder-14B-Instruct-GGUF | Hugging Face (model card) |
| 14B Q4 loaded VRAM footprint ~10-12 GB (9 GB weights + KV cache 0.7-1.5 GB + buffers 0.3-0.7 GB) | https://github.com/ollama/ollama/issues/10445 | GitHub (real-world VRAM logs) |
| `ollama ps` PROCESSOR column: `100% GPU` means fully on-card, no overflow; a CPU/GPU split means spill | https://github.com/ollama/ollama/issues/9704 | GitHub (ollama repo) |
| Swap-ins: `codellama:13b` (7.4 GB); `deepseek-coder` family (1.3b/6.7b/33b; v2 16b ~8.9 GB) | https://ollama.com/library/codellama , https://ollama.com/library/deepseek-coder | Ollama library |

## The OpenAI-compatible API (Lesson 3: the-openai-compatible-api)

| Fact grounded | Source | Type |
|---|---|---|
| OpenAI-compatible endpoint `POST /v1/chat/completions`; request `{model, messages:[{role,content}]}`; reply at `choices[0].message.content`; params temperature/top_p/max_tokens/stop/seed/stream supported | https://docs.ollama.com/api/openai-compatibility | Ollama (authoritative) |
| Endpoint/base-URL confirmation for the client (`http://localhost:11434`) | https://docs.ollama.com/api/introduction | Ollama (authoritative) |

## Record the stack (Lesson 4: record-the-stack)

| Fact grounded | Source | Type |
|---|---|---|
| `ollama ps` 100% GPU as the zero-overflow proof recorded in MODELS.md | https://github.com/ollama/ollama/issues/9704 | GitHub (ollama repo) |
| Reference model identity/quant/size recorded in MODELS.md | https://ollama.com/library/qwen2.5-coder:14b | Ollama library (authoritative) |

## Reference figures (the numbers the lessons quote)

The reference build serves `qwen2.5-coder:14b` at Q4_K_M (9.0 GB on disk), with a loaded VRAM
footprint of roughly 11 GB against the RTX 4060 Ti's 16380 MiB usable (the M2 source set records the
card's 16380 MiB readout). The `~11 GB used / 16 GB total` figure is labeled representative in the
lessons; the exact value depends on context length. The Ollama version `0.30.10` used in the
reference `MODELS.md` is a real current release confirmed against a live `GET /api/version` on the
authoring host (no model was pulled there; the sample model reply is the labeled representative
output the reader reproduces on their own build).
