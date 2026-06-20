# The Day-One Stack

Every hour you spend fighting import errors, version conflicts, and missing CUDA drivers is an hour you are not building. Set the environment once, properly — and the rest of the course runs without friction.

**You build** a verified four-layer development stack: system foundation, package managers, language runtimes, and AI/ML libraries — plus a `verify.py` that confirms every layer is alive.

## The Four Layers

Think bottom-up. Each layer depends on the one below:

```
4. AI/ML Libraries   — PyTorch, transformers, JAX
3. Language Runtimes — Python 3.12, Node 22, Rust
2. Package Managers  — uv, pnpm, cargo
1. System Foundation — OS, shell, git, GPU drivers
```

Install them in that order. Jumping layers causes silent failures that waste hours.

## Layer 1 — System Foundation

**macOS:**

```sh
xcode-select --install
brew install git curl wget
```

**Ubuntu / Debian:**

```sh
sudo apt update && sudo apt install -y build-essential git curl wget
```

**Windows:** install WSL2 first (`wsl --install`), then use the Ubuntu path above inside it. Everything from here on runs inside WSL2.

## Layer 2 — Package Managers

Install `uv` for Python. It replaces pip, venv, and pyenv in one tool, and runs 10–100× faster.

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install `fnm` for Node (TypeScript arrives in Module 3 — you install the manager now, the language then):

```sh
curl -fsSL https://fnm.vercel.app/install | bash
fnm install 22
npm install -g pnpm
```

Install `rustup` for Rust (the serving layer arrives in Module 5 — same pattern: manager now, language then):

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## Layer 3 — Python Runtime and Virtual Environment

```sh
uv python install 3.12
uv venv .venv
source .venv/bin/activate          # Windows WSL2: same command
```

Create one `.venv` per module. PyTorch versions conflict across phases; global environments break things. The pattern is: `cd module1 && uv venv .venv && source .venv/bin/activate`.

## Layer 4 — AI/ML Libraries

```sh
uv pip install torch numpy matplotlib jupyter
```

**GPU (optional for now, required by Module 3):** check first:

```sh
nvidia-smi
```

If it returns a driver version, install the CUDA-enabled wheel:

```sh
uv pip install torch --index-url https://download.pytorch.org/whl/cu124
```

No GPU? Use Google Colab — it gives you a free T4 and nothing changes about the code. The course assumes you know which path you are on.

CUDA and driver versions move fast. If that wheel index 404s, look up the current build at pytorch.org rather than guessing the suffix.

## Reproducibility Posture

Three habits that save future you:

1. **Lockfile:** run `uv pip compile pyproject.toml -o requirements.lock` after adding packages. Commit the lock, not the venv.
2. **`.gitignore`:** add `.venv/`, `*.pt`, `*.pth`, `*.safetensors`, `*.gguf` — model weights belong in Git LFS or DVC, not in your repo history.
3. **Per-module venvs:** when you start a new module, create a fresh `.venv`. Never share a venv across modules with conflicting PyTorch/CUDA versions.

## Verify the Stack

```python
# verify.py
import sys, subprocess

checks = [
    ("python", sys.version),
    ("torch",  __import__("torch").__version__),
    ("cuda",   str(__import__("torch").cuda.is_available())),
    ("node",   subprocess.check_output(["node", "--version"]).decode().strip()),
    ("rust",   subprocess.check_output(["rustc", "--version"]).decode().strip()),
]

for name, result in checks:
    print(f"  {name:8s}  {result}")
```

Run it:

```sh
python verify.py
```

All five lines print without errors. That is done.

An AI Platform Engineer owns the environment that serves models — a reproducible, layer-by-layer setup is the substrate that everything else runs on.

## Core Concepts

- The four-layer stack (system → managers → runtimes → libraries) installs bottom-up because each layer depends on the one below.
- `uv` replaces pip, venv, and pyenv; one tool is faster and simpler than three.
- One virtual environment per module prevents PyTorch/CUDA version conflicts across phases.
- Toolchains for TypeScript (Module 3) and Rust (Module 5) install now so you never interrupt the work later to set up an environment.

<div class="claude-handoff" data-exercise="exercises/module1/01-dev-environment/">

**Build It in Claude Code** — Verify your four-layer stack and produce a passing `verify.py`.

</div>
