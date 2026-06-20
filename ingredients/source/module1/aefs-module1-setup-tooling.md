# Module 1 · Setup & Tooling — Phase 00 Extract

> Source: `phases/00-setup-and-tooling/` · Phase README is a stub (5 lines, points to ROADMAP.md); all content lives in per-lesson `docs/en.md` (12 lessons).
> Lesson type markers: **Build** = hands-on install/code; **Learn** = concept/workflow.

## Day-One Install Sequence

Phase 00 is structured as a **bottom-up four-layer stack**, installed in this order (each layer depends on the one below):

```
4. AI/ML Libraries   (PyTorch, JAX, transformers)
3. Language Runtimes (Python 3.11+, Node 20+, Rust, Julia)
2. Package Managers  (uv, pnpm, cargo, juliaup)
1. System Foundation (OS, shell, git, editor, GPU drivers)
```

**What the student installs on day one:**
1. **System** — `xcode-select`/`brew` (macOS), `apt build-essential git curl wget` (Ubuntu), WSL2 (Windows).
2. **Python via `uv`** — `curl … uv/install.sh`, `uv python install 3.12`, `uv venv`, `uv pip install numpy matplotlib jupyter`. (`uv` chosen as 10–100× faster than pip; `venv`/`conda` covered as fallbacks.)
3. **Node.js via `fnm`** — `fnm install 22`, `npm i -g pnpm` (for TS lessons in Phases 13–17).
4. **Rust via `rustup`** — for performance-critical lessons (Phases 12, 15–17).
5. **Julia (optional)** — for math-heavy Phase 1.
6. **GPU (optional)** — `nvidia-smi` + PyTorch CUDA wheel (`--index-url …/cu124`); Google Colab T4 as the free fallback.
7. **Docker** — Docker Desktop (mac) / `get.docker.com` (linux) + NVIDIA Container Toolkit; GPU image `nvidia/cuda:12.4.1-devel-ubuntu22.04`.
8. **Editor** — VS Code + extensions (Python, Pylance, Jupyter, GitLens, Remote-SSH, debugpy, Black, Ruff).

**Languages→phases map (from lesson 01):** Python (Ph 1–12, `uv`) · TypeScript (Ph 13–17, `pnpm`) · Rust (Ph 12, 15–17, `cargo`) · Julia (Ph 1, Pkg).

**Reproducibility posture:** per-phase `.venv/` (not one global env, because PyTorch/CUDA versions conflict across phases); `pyproject.toml` with optional-dependency groups + lockfile (`uv.lock`); `.gitignore`/Git LFS/DVC for large model/dataset files.

---

## Lessons

### 01 · Dev Environment — **Build** · Python/Node/Rust · ~45min
Establishes the four-layer stack and walks through installing all four language toolchains from scratch (Python via `uv`, Node via `fnm`+`pnpm`, Rust via `rustup`, Julia optional), then verifies GPU access with CUDA/MPS and a test tensor op. Frames the whole course's environment as a one-time setup: "do this once, properly" to avoid per-lesson import/version/CUDA fights. Produces a runnable `verify.py` (also `verify.ts`, `main.rs`) that checks the setup end-to-end.
**Tools/commands:** `uv`, `fnm`, `pnpm`, `rustup`, `cargo`, `juliaup`, `nvidia-smi`, `xcode-select`, `brew`, `apt`.

### 02 · Git & Collaboration — **Learn** · ~30min
Minimal-git lesson: `add`/`commit`/`push`, branching for experiments (`git checkout -b experiment/…`), reading `git log`, writing a `.gitignore` that excludes `.pt`/`.pth`/`.safetensors`. Explicitly scoped — "you don't need rebase, cherry-pick, or submodules for this course." Includes a working-directory→staging→local→remote sequence diagram and a "what people say vs what it means" glossary (commit/branch/merge/remote).
**Tools/commands:** `git`, GitHub (`git clone …ai-engineering-from-scratch`).

### 03 · GPU Setup & Cloud — **Build** · Python · ~45min
Three GPU options ranked by cost/setup: local NVIDIA (CUDA+cuDNN), Google Colab free T4, and cloud rental (Lambda/RunPod/Vast.ai at $0.20–2/hr). Includes a CPU-vs-GPU matmul benchmark and the fp16 VRAM rule of thumb (2 bytes/param) to estimate the largest fittable model. Positions GPU as optional for Phases 1–3 (CPU is fine) but required for Phases 4+.
**Tools/commands:** `nvidia-smi`, PyTorch CUDA API (`torch.cuda.*`), Colab runtime, `ssh`.

### 04 · APIs & Keys — **Build** · Python/TS · ~30min
First LLM API call, deliberately taught early so later phases (11+) can assume it. Covers secure key storage via env vars/`.env`, an Anthropic SDK call in both Python and TypeScript, **and the raw `urllib` HTTP equivalent** (so students see the `x-api-key` + `anthropic-version` headers the SDK hides). Touches error handling (auth, rate limits) and the token-as-billing-unit concept.
**Tools/commands:** `anthropic` SDK, `@anthropic-ai/sdk`, `export ANTHROPIC_API_KEY`, `urllib.request`.

### 05 · Jupyter Notebooks — **Build** · Python · ~30min
Notebooks as the "lab bench": cell types, kernel-as-background-process model, the magic commands that matter (`%timeit`, `%%time`, `%matplotlib inline`, `%env`, `!cmd`), and inline rich output (DataFrames, plots, images). The editorial spine is **"explore in notebooks, ship in scripts"** plus three named traps to avoid — out-of-order execution, hidden state, memory leaks — with restart-kernel/del+gc fixes. Covers Google Colab as a free cloud GPU notebook (90-min idle timeout caveat).
**Tools/commands:** `jupyterlab`/`notebook`, VS Code Jupyter ext, Colab, `%timeit`/`%%time`/`%matplotlib inline`.

### 06 · Python Environments — **Build** · Shell · ~30min
The dependency-hell cure: isolated envs per project. Three options — `uv venv` (recommended, fastest), `venv` (built-in), `conda` (when you need non-Python deps like CUDA toolkits) — with the cardinal rule "if you conda, conda everything; never mix pip into it." Introduces `pyproject.toml` with `[project.optional-dependencies]` groups (torch, llm), lockfiles (`uv.lock`/`requirements.lock`), and a **per-phase `.venv/` strategy** because different phases need conflicting PyTorch/CUDA versions. Five named common mistakes (global installs, pip+conda mixing, forgetting to activate, committing `.venv`, CUDA mismatch).
**Tools/commands:** `uv`, `python -m venv`, `conda`, `pyproject.toml`, `uv.lock`, `nvidia-smi`.

### 07 · Docker for AI — **Build** · Docker · ~60min
Containers as the reproducible-environment solution for the CUDA-driver-fragility + large-weights + multi-service problems specific to AI. Builds a full GPU Dockerfile (`nvidia/cuda:12.4.1-devel-ubuntu22.04` → Python 3.12 → PyTorch 2.3.1 cu124 → transformers/datasets/accelerate), covers volume mounts for `/workspace` `/models` `/datasets` (so a 14GB model isn't re-downloaded), NVIDIA Container Toolkit install, base-image sizing tradeoffs (devel ~4GB vs runtime ~1.5GB vs pytorch image ~6GB vs slim ~150MB), and Docker Compose for an inference-server + Qdrant-vector-DB RAG stack. Names three container archetypes: dev / training / inference.
**Tools/commands:** Docker, `Dockerfile`, `docker-compose.yml`, NVIDIA Container Toolkit, `--gpus all`, Qdrant.

### 08 · Editor Setup — **Build** · ~20min
VS Code as default, with a five-layer concept (base editor → extensions → AI settings → terminal → remote-dev). Installs eight extensions (Python, Pylance, Jupyter, GitLens, Remote-SSH, debugpy, Black, Ruff) and pins the settings that matter for AI work: `typeCheckingMode: basic`, `formatOnSave`, rulers at 88/120, `notebook.output.scrolling`. Remote-SSH is flagged as the most important extension (open a remote GPU box as if local, via `~/.ssh/config`). Covers alternatives Cursor/Windsurf (VS Code forks, same config) and Vim/Neovim (stay only if already productive).
**Tools/commands:** VS Code, Pylance/Black/Ruff, Remote-SSH, `ssh-keygen`/`ssh-copy-id`.

### 09 · Data Management — **Build** · Python · ~45min
Data workflow built on Hugging Face `datasets`/`huggingface_hub`: load, stream large datasets row-by-row (`streaming=True`), convert between CSV/JSON/Parquet/Arrow (Parquet best for storage, Arrow for in-memory), reproducible train/val/test splits with fixed seeds, and large-file versioning (`​.gitignore` < Git LFS < DVC by complexity). Lists the six datasets the course uses (IMDB, WikiText, SQuAD, Common Crawl, MNIST, COCO).
**Tools/commands:** `datasets`, `huggingface_hub`, `load_dataset`, `hf_hub_download`/`snapshot_download`, Git LFS, DVC.

### 10 · Terminal & Shell — **Learn** · ~35min
Terminal fluency for AI workflows: piping/redirects (`|`, `>`, `2>&1`) to filter training logs with `grep`/`awk`, background processes (`&`, `nohup`, `jobs`/`fg`), **tmux** as the single most useful tool (persistent multi-pane sessions for train+GPU-monitor+log-tail that survive SSH disconnect), and monitoring with `htop`/`nvtop`/`watch -n1 nvidia-smi`. Remote file transfer (`scp`, `rsync`, port-forward `ssh -L`). Ships a `shell_aliases.sh` (e.g. `gpu`, `killtraining`, `watchloss`).
**Tools/commands:** `grep`, `awk`, `tail -f`, `tmux`, `htop`, `nvtop`, `nvidia-smi`, `ssh`/`scp`/`rsync`.

### 11 · Linux for AI — **Learn** · ~30min
Survival guide for landing on a remote Ubuntu GPU box (no GUI). Filesystem layout (`/home`, `/tmp`, `/var/log`…), the ~15 commands covering 95% of work (nav, file ops, `grep`/`find`), `chmod`/`chown`/`sudo` permission fixes, `apt` package management with a "fresh GPU box" install bundle, `systemctl` for inference daemons, disk-space triage (`df`/`du`), and a macOS→Linux gotchas table (case sensitivity, `sed -i` differences, `bashrc` vs `zshrc`, no `pbcopy` over SSH). WSL2 path for Windows.
**Tools/commands:** `ls`/`cd`/`cp`/`mv`/`rm`, `chmod`/`chown`, `apt`, `systemctl`, `df`/`du`, `wget`/`curl`/`scp`/`rsync`.

### 12 · Debugging & Profiling — **Build** · Python · ~60min
The AI-specific debugging thesis: "the worst AI bugs don't crash — they train silently on garbage." Three-level model (standard Python → tensor ops → training dynamics) with the claim that 80% of bugs live in levels 1–2. Covers `debug_print` (shape/dtype/device/min/max/nan), conditional `breakpoint()`, Python `logging`, manual `Timer` context manager, `cProfile`/`line_profiler`, memory profiling (`tracemalloc`/`memory_profiler`/`torch.cuda.memory_summary`) with an OOM triage checklist (cut batch → `empty_cache` → `del` → mixed precision → grad checkpointing). Four named AI bug detectors: **shape mismatch** (forward-hook shape mapper), **NaN loss**, **data leakage** (id overlap + temporal leakage), **wrong device**. TensorBoard for loss/weight/gradient histograms.
**Tools/commands:** `breakpoint()`, `logging`, `cProfile`, `line_profiler` (`kernprof`), `tracemalloc`, `memory_profiler`, `torch.utils.tensorboard`, `torch.cuda.memory_summary`.
