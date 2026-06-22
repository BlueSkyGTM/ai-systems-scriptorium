# Module 4: Unified Memory

Module 3 ended on a rule: keep the model on the card. A model that fits entirely in the RTX 4060 Ti's
16GB serves fast, and `ollama ps` reading `100% GPU` was the proof you had done it right. That rule is
correct, and this module is about the times you will choose to break it on purpose.

A 32B model is meaningfully smarter than a 14B one. A 70B model is smarter still. Neither fits in 16GB
of VRAM at a usable quantization. The instinct is to treat that as a wall: the model does not fit, so
you cannot run it. The truth is that you can, because the rig has a second memory pool. The 64GB of
DDR5 alongside the GPU is slower than VRAM, but it is real, and Ollama will split a too-large model
across both, running as many layers on the GPU as fit and the rest on the CPU.

That split is the subject of this module. Treating VRAM and system RAM as one budget is what "unified
memory" means here: not the shared silicon of an Apple chip, but a discrete GPU and its host RAM that
Ollama spans when a model is too big for the fast half alone. Spanning them has a price, paid in
tokens per second, and the only way to spend it wisely is to measure it.

You will see exactly what Ollama does when a model exceeds VRAM, learn the quantization tradeoffs that
decide how much of a model fits on the card in the first place, and build `bench.py`, a tool that
reads the server's own timing fields to report tokens per second and time to first token. Then you
will run a 14B model that fits on-card against a 32B model that does not, and watch the numbers move.

You leave this module with a fourth file in the portfolio repository: `LATENCY.md`, the measured
baseline for every model you run, recording its tokens per second, its time to first token, and how it
split across the GPU and CPU. The metal, the runtime, and the model stack were documented in the
first three modules; now their performance is too. That baseline is the number every tuning decision in
Module 7 is measured against.
