# Local Metal — Module 1 Source Provenance

Cited-resource record for Module 1 ("The Build"). Per the authoring directive, every external
resource a lesson cites is captured here as tracked ore: the URL, what specific fact it grounds,
the source type, and the retrieval date. The shipped book cites the URLs; this manifest preserves
the underlying fact against link rot, so a dead link never orphans a claim.

Retrieved 2026-06-21 by the M1 authoring fleet (Sonnet workers + conductor), grounded via web
search/fetch and the Microsoft Learn connector. Full-page snapshots are deliberately not committed:
these are third-party vendor, forum, and pricing pages (not redistributable); the load-bearing
fact is recorded here instead.

## Frontier pricing (Lesson 1: the-cost-wall-and-the-rig)

Volatile — these rates change; the lesson and `breakeven.py` both flag this and date the figure.

| Fact grounded | Value (as of 2026-06-21) | Source |
|---|---|---|
| Claude Sonnet 4.6 API price | $3.00 / MTok input, $15.00 / MTok output | https://platform.claude.com/docs/en/about-claude/pricing |
| GPT-4o API price | $2.50 / MTok input, $10.00 / MTok output | https://openai.com/api/pricing/ |

## GPU: RTX 4060 Ti 16GB (Lessons 2, 4)

| Fact grounded | Value | Source |
|---|---|---|
| Memory bandwidth | 288 GB/s, 128-bit GDDR6 | https://technical.city/en/video/GeForce-RTX-4060-Ti-16-GB |
| VRAM / TDP | 16,384 MiB / 165W | https://technical.city/en/video/GeForce-RTX-4060-Ti-16-GB |
| Spec corroboration | RTX 4060 Ti 16GB specs | https://videocardz.com/nvidia/geforce-40/geforce-rtx-4060-ti-16gb |
| Throttle temperature | ~83°C | https://www.nvidia.com/en-us/geforce/forums/geforce-graphics-cards/5/527616/rtx-4060-ti-temp/ |
| nvidia-smi VRAM reads 16380MiB (driver reservation) | Ubuntu 24.04, driver 550.90.12, CUDA 12.4 | https://gist.github.com/fordnox/538b48ac956341728573786a80e08859 |
| nvidia-smi reference | tool documentation | https://docs.nvidia.com/deploy/nvidia-smi/index.html |

## Model VRAM fit (Lesson 2)

| Fact grounded | Value | Source |
|---|---|---|
| 14B model at Q4 VRAM footprint | ~8.7–9 GB; 8GB cards spill 2–10x | https://localaimaster.com/blog/ollama-model-ram-vram-table |
| Ollama coding-model VRAM by GPU tier | 16GB fits 14B on-card | https://haimaker.ai/blog/ollama-coding-models-by-nvidia-rtx-vram/ |

## RAM / platform (Lesson 2)

| Fact grounded | Value | Source |
|---|---|---|
| DDR5-6000 dual-channel bandwidth | ~96 GB/s (6000 MT/s × 8 bytes × 2 channels) | https://en.wikipedia.org/wiki/DDR5_SDRAM |
| DDR5-6000 is the AM5 sweet spot | inference-mixed workloads | https://www.tomshardware.com/pc-components/cpus/amd-says-dual-channel-ddr5-6000-is-the-sweet-spot-for-ryzen-8000g-apus |
| Ryzen 7 7700X: cores/clocks/TDP, 24 PCIe 5.0 lanes, TJmax 95°C | 8C, 4.5/5.4 GHz, 105W | https://www.amd.com/en/products/processors/desktops/ryzen/7000-series/amd-ryzen-7-7700x.html |
| 7700X TJmax 95°C (community corroboration) | normal max temp | https://pcforum.amd.com/s/question/0D5Pd00000m1n8cKAA/my-7700x-max-temperature-is-955it-is-a-normal |

## Storage (Lesson 2)

| Fact grounded | Value | Source |
|---|---|---|
| Crucial T500 Gen4 NVMe sequential read | 7,400 MB/s | https://www.crucial.com/ssd/t500/ct1000t500ssd8 |

## Assembly + stress test (Lesson 3)

| Fact grounded | Value | Source |
|---|---|---|
| Express ProBuild service | $249.99, same-day, OCCT testing, 90-day labor warranty | https://www.microcenter.com/product/688266/express-probuild-custom-pc-build-service |
| OCCT: what it tests, pass/fail criteria | CPU/GPU/VRAM/memory/power, zero-error pass | https://www.ocbase.com/occt |
