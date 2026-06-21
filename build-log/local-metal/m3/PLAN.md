# Module 3 — The Model Stack — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared).** Third authoring stage for Local Metal
(M1 + M2 shipped 2026-06-21). All five open decisions accepted as recommended (see Locked decisions
below). M3 puts the first model on the GPU and proves you can call it. It is the first module whose
done-when is real command output from a running stack (the M1 live-vs-expected rule applies: live when
the reader has the machine, recorded expected output otherwise). Authoring underway conductor-direct.

## The stage in one line

M2 left a Linux host with a working CUDA runtime. M3 installs the serving layer (Ollama + Docker),
pulls a 14B coding model that fits entirely in the RTX 4060 Ti's 16GB of VRAM, proves zero overflow
with `nvidia-smi`, and calls the model through Ollama's OpenAI-compatible API. Seam: the whole point
of the rig is to serve a model the rest of your tooling can call; M3 is where the metal first answers
an API request, and the client it builds is what the routing layer (M5) and the Claude Code wiring
(M6) extend.

## Settled decisions (from the blueprint + the SPEC Step 3)

1. **Stage = module.** Same shape as M1/M2; writes `build-log/local-metal/m3/output/{...}`.
2. **Held to the three contracts**; every worker brief carries them + the shipped M1/M2 lessons as the
   locked voice exemplar.
3. **The portfolio repo grows to runnable code.** M1 `HARDWARE.md`, M2 `SETUP.md`, and now M3 seeds
   `ollama_client.py` (a tiny OpenAI-compatible client) plus `MODELS.md` (the record of what is pulled
   and its VRAM footprint). `ollama_client.py` is the compounding artifact: M5 wraps it in the routing
   function, M6 exposes it to Claude Code. The reuse is real (later modules import it), not restated.
4. **aipe ore enters here, lightly.** M3 introduces quantization at the level needed to read a model
   tag (Q4 vs Q8, why a 14B fits in 16GB at Q4); the deep tradeoff curves are M4 and M7.

## Proposed M3 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | The runtime is live; now serve a model. Install the stack, fit a 14B on-card, call it over an API. | concept | SPEC Step 3 + M2 close |
| 1 | `install-ollama-and-docker` | Install Ollama (native, for direct GPU serving) and Docker (for containerized tooling later); the systemd service and the `:11434` endpoint. | build | Ollama + Docker install docs |
| 2 | `a-14b-model-on-card` | `ollama pull` a 14B coding model and prove it fits entirely in 16GB VRAM with `nvidia-smi` (zero overflow); read the model tag and its quantization. | build | Ollama model library; aipe (VRAM/quant) |
| 3 | `the-openai-compatible-api` | Call the model through Ollama's OpenAI-compatible `/v1/chat/completions`; build `ollama_client.py`, the client the routing layer will reuse. | build | Ollama OpenAI-compat docs |
| 4 | `record-the-stack` | Record `MODELS.md` (model, quant, VRAM used/total, a sample response) and validate it; the module's done-when. | build | STANDARDS artifact contract |

## The compounding throughline (STANDARDS Part 3)

M3 seeds two artifacts. `ollama_client.py` (L3) is a stdlib-only client that posts a chat request to
the local OpenAI-compatible endpoint and prints the reply; it ships an offline self-test
(`--selftest`) that validates request construction without a running server, so the exercise is
machine-checkable even pre-hardware, plus a live mode that hits `localhost:11434` when the rig exists.
`MODELS.md` (L4) records the pulled model and its VRAM footprint, gated by `check_models.py` (the same
completeness-validator family as `check_hardware.py`/`check_setup.py`). M5 imports `ollama_client.py`
into the routing function; M6 exposes it to Claude Code.

## Sources (three-source rule)

1. **Ingredient:** SPEC Step 3 + the aipe ore (`vault/ai-performance-engineering/`) for VRAM/quant.
2. **External grounding:** Ollama's official docs (install, model library, OpenAI compatibility),
   Docker install docs, NVIDIA `nvidia-smi dmon`; cite real URLs, capture to
   `vault/local-metal/m3-sources/PROVENANCE.md`. MS-Learn where it has coverage. USE THE TOOLS.
3. **Editorial seam framing** in every lead.

## The fleet plan

Conductor-direct (the M1/M2 pattern): 4 Sonnet workers (lessons 1-4) + conductor overview,
integration, review, artifact reconciliation, and validator/self-test testing before ship. Briefs
carry the exact canonical `MODELS.md` schema + `ollama_client.py` interface to prevent the L4-style
drift seen in M2.

## Locked decisions (all five accepted as recommended, 2026-06-21)

1. **Reference model: `qwen2.5-coder:14b`** (modern, strong on code, Q4 fits in 16GB) as the book's
   default; `deepseek-coder` and `codellama:13b` named as swap-ins. Grounded against Ollama's library
   + VRAM guidance (Haiku source-fetch tier).
2. **Throughline artifacts: yes, all of them.** `ollama_client.py` (runnable client, the M5/M6 seed) +
   `MODELS.md` (record) + `check_models.py` (validator).
3. **Machine-checkable done-when without hardware: offline self-test + live mode + MODELS.md gate.**
   `ollama_client.py --selftest` validates the request payload offline (always runnable); live mode +
   `MODELS.md` completeness (incl. a VRAM-Used ≤ VRAM-Total zero-overflow assertion) cover the
   has-hardware path.
4. **Docker depth: Ollama native; Docker installed for later modules.** Run Ollama natively (direct
   GPU, simplest); name the "Ollama in Docker" option (`--gpus=all`) without making it the path.
5. **Quantization depth: light here, depth later.** Enough in M3 to read a tag (Q4 vs Q8) and know why
   a 14B fits at Q4; the tradeoff curves stay in M4 (unified memory) and M7 (tuning).

On lock: the fleet authors M3, VERIFY gates voice + grounding, BUILD/TEST runs `mdbook build` +
`ollama_client.py --selftest` + `check_models.py`, and the stage stops at `GATE-APPROVE-SHIP`.
