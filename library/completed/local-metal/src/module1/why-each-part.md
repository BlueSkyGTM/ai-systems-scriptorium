# Why Each Part

Pick the wrong GPU and the model spills into RAM; pick the wrong RAM speed and the spill punishes you. Every line in the reference BOM is an inference constraint, not a shopping default.

## The 16 GB GPU Is Not a Gaming Splurge

The RTX 4060 Ti 16GB carries 288 GB/s of memory bandwidth across a 128-bit GDDR6 bus. That number matters less than the 16 GB itself.

A 14B coding model at Q4 quantization occupies roughly 8–9 GB of VRAM. On a 16 GB card the model sits entirely on-card, the KV cache grows into the remaining headroom, and every token is computed without leaving the GPU. On an 8 GB card, the same model cannot fit cleanly: the runtime spills layers into system RAM and fetches them over PCIe, which carries roughly 64 GB/s at Gen 4 x16, less than a quarter of GDDR6 bandwidth. Generation slows 2–10x, and a coding agent making multiple passes over a file hits that wall on every request. The 16 GB boundary is the difference between a local model server and a local model experiment.

CUDA is the second reason. Ollama, Docker-based model containers, and code-generation subagents all target CUDA without a translation layer. An NVIDIA card means the toolchain works; everything else requires workarounds.

## DDR5-6000: Bandwidth for the Overflow

When a 32B or 70B quantized model exceeds VRAM, the runner splits layers across GPU memory and system RAM, moving weights across PCIe on each forward pass. The speed of that transfer is bounded by system-RAM bandwidth: how fast the CPU can serve weights into the pipeline.

Dual-channel DDR5-6000 delivers a peak of 96 GB/s (6000 MT/s × 8 bytes × 2 channels). That is not VRAM speed, but it is roughly one-third of it, which keeps the overflow case usable rather than painful. A slower kit, say DDR4-3200 at 51 GB/s, widens the bottleneck; a faster kit costs more without changing the GPU-side ceiling. DDR5-6000 is the point where diminishing returns kick in on AM5 for inference-mixed workloads.

## AM5 and PCIe 5.0 Lanes

The Ryzen 7 7700X on the AM5 platform exposes 24 usable PCIe lanes from the CPU: 16 lanes to the GPU slot at PCIe 5.0 and four lanes to an M.2 slot at PCIe 5.0 or 4.0 (board-dependent), with four lanes connecting the CPU to the chipset. The GPU gets its full 16-lane allocation with no sharing; the NVMe drive does not compete with it for bandwidth. That matters when a model is loading from disk while the GPU is already serving an inference request.

## NVMe Gen 4: Model Weight Loading on Boot

Ollama loads model weights from disk into VRAM at startup. A cold pull of a 14B model file takes several seconds on any modern SSD, but the gap between a Gen 3 drive and a Gen 4 drive is measurable on larger models. The Crucial T500 reads at 7,400 MB/s sequential. A 9 GB weight file loads in about 1.2 seconds at that speed; on a Gen 3 drive at roughly 3,500 MB/s, the same load takes around 2.6 seconds. For a server that restarts after a power cycle or a kernel update, that gap is real. The 2 TB capacity splits cleanly into two partitions, Windows and Linux, without forcing a choice between them.

## The SFX PSU and the Fractal Ridge Are a Pair

The Fractal Ridge is a Mini-ITX case: it accepts only SFX power supplies, not the ATX format that fits standard towers. The Corsair SF750 is the pairing that closes that constraint. It is 80+ Platinum rated, which means less wasted heat inside a small enclosure, and it carries 750W continuous, enough headroom for the 7700X under load (105W TDP) plus the RTX 4060 Ti (165W TDP), with margin. The SFF form factor is the whole point: this machine sits on a desk, not in a rack.

## Assembly as a Checkable Component

The ProBuild service at Micro Center is not a convenience item; it is the stress-test step. The technician assembles the machine, posts it, runs a load test, and you leave with a result you can check. That covers the most common first-build failure modes: a RAM stick not seated, a cooler not making contact, a GPU not clicking into the slot. The assembly cost is buying a known-good baseline before any software touches the machine.

## Core Concepts

- 16 GB of VRAM is not headroom, it is the threshold: a 14B model at Q4 quantization fills roughly 8–9 GB, and the KV cache needs the rest; an 8 GB card spills to RAM and degrades 2–10x.
- DDR5-6000 dual-channel delivers 96 GB/s of system bandwidth, which sets the speed floor for any model that overflows VRAM; slower RAM widens the bottleneck without changing the GPU ceiling.
- AM5 allocates 16 PCIe 5.0 lanes to the GPU and 4 separate lanes to the M.2 slot so storage and the GPU never share bandwidth.
- The SFX PSU and Mini-ITX case are a constrained pair: the case dictates the PSU format, and the form factor is the build's design constraint, not an afterthought.

<div class="claude-handoff" data-exercise="exercises/module1/why-each-part/">

**Build It in Claude Code**: Create `HARDWARE.md` with the Bill of Materials table and `check_hardware.py` v1 that validates every row is filled and no placeholders remain.

</div>

<!-- SOURCES: https://technical.city/en/video/GeForce-RTX-4060-Ti-16-GB | https://videocardz.com/nvidia/geforce-40/geforce-rtx-4060-ti-16gb | https://localaimaster.com/blog/ollama-model-ram-vram-table | https://haimaker.ai/blog/ollama-coding-models-by-nvidia-rtx-vram/ | https://en.wikipedia.org/wiki/DDR5_SDRAM | https://www.tomshardware.com/pc-components/cpus/amd-says-dual-channel-ddr5-6000-is-the-sweet-spot-for-ryzen-8000g-apus | https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-7-7700x.html | https://www.crucial.com/ssd/t500/ct1000t500ssd8 -->
