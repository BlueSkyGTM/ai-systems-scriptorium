# Module 3: The Model Stack

Module 2 left you with a Linux host whose GPU answers to code: `nvidia-smi` lists the card, `nvcc`
compiles, and `deviceQuery` returns `Result = PASS`. That is a working runtime and nothing more. No
model is loaded, nothing is listening on a port, and the rig cannot yet do the one job you built it
for. This module puts the first model on the card and proves you can call it.

The temptation is to grab the largest model that will download and point a chat window at it. That is
how you end up with a model spilling out of VRAM into system RAM, generating at a crawl, with no
record of what you actually ran. Local Metal treats the serving layer the way it treated the base
layer: chosen on real constraints, installed once, and documented so every later module can trust it.

The constraint that drives every choice here is the 16GB of VRAM on the RTX 4060 Ti. A model that
fits entirely on the card serves fast; a model that overflows serves slowly or not at all. You will
install Ollama as the serving layer and Docker for the containerized tooling later modules need, pull
a 14B coding model quantized to fit on-card with headroom, prove there is zero overflow with
`nvidia-smi`, and then call the model the way the rest of your tooling will: through an
OpenAI-compatible API.

The reference build serves `qwen2.5-coder:14b`, a current coding model whose four-bit quantization
fits comfortably in 16GB. Your choice can differ; `deepseek-coder` and `codellama:13b` swap in
cleanly. The reasoning that keeps a model on the card and off the system bus does not change.

This is the module where the metal first answers an API request. The small client you build here,
`ollama_client.py`, is not a throwaway: the routing layer in Module 5 wraps it, and the Claude Code
wiring in Module 6 exposes it. You leave this module with a third file in the portfolio repository,
`MODELS.md`, recording the model you serve, its quantization, the VRAM it occupies against the VRAM
you have, and a sample of it answering. The metal was documented in Module 1, the runtime in Module 2;
now the stack that runs on top of them is too.
