# Exercise: The Day-One Stack

**Goal:** Install the four-layer development stack and produce a `verify.py` that confirms every layer is working.

**Why:** An Production AI Engineer owns the environment that serves models. A reproducible, verified setup is the substrate every later lesson runs on.

## Steps

1. Install the system foundation for your OS (Homebrew/apt/WSL2).
2. Install `uv` (Python manager), `fnm` + `pnpm` (Node manager), and `rustup` (Rust manager).
3. Use `uv` to create a `.venv` for this module and activate it.
4. Install `torch`, `numpy`, `matplotlib`, and `jupyter` into the venv.
5. Create `verify.py` in `exercises/module1/01-dev-environment/` using the template in the lesson.
6. Run `python verify.py`. Fix any layer that fails before moving on.
7. Add `.venv/`, `*.pt`, `*.pth`, `*.safetensors` to your `.gitignore`.

## Done when

`python verify.py` prints all five lines — python, torch, cuda, node, rust — without error. CUDA may print `False` if you have no GPU; that is acceptable. Any missing runtime is a failure.

## Stretch

Generate a `requirements.lock` with `uv pip compile pyproject.toml -o requirements.lock` and confirm it pins exact versions for torch and numpy.
