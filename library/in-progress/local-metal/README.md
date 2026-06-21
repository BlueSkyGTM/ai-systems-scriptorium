# Local Metal — Blueprint

## Positioning

Local Metal is the Scriptorium's home production environment: the machine where a Production
AI Engineer actually runs and hosts the systems the rest of the library teaches them to build.
It is a companion to Sans Python, not a capstone above it, and it is deliberately home-scale,
not an enterprise feat. It is deliberately a simple system you can stand up
at home, then grow.

It is progress-agnostic. You do not have to finish the other books to start it; you can build
the rig early and host a first model on day one. What changes over time is the rig's ambition.
As you ingest the rest of the library, Local Metal earns its wings and gets more cutting-edge,
because each book upgrades the home environment:

| Book | What it adds to the home rig |
|---|---|
| Sans Python | the AI systems worth hosting in the first place |
| Just Python | the applied Python that wires the rig's tooling together |
| Machine Math | sharper judgment about what the models are doing on the metal |
| Weights and Measures | a model you fine-tuned and can now host yourself |
| Data Currents | a data pipeline that feeds the local models |
| Anatomy of an Answer | the story of the rig, told to a hiring manager |

Where Sans Python teaches AI engineering on hosted compute, Local Metal teaches the same
engineer to own a slice of compute at home: select and assemble the hardware, configure Linux
and CUDA, run a local model stack, route the right work to it, and offload it from a frontier
coding agent. It is the only title that touches physical assembly, Linux administration, CUDA
setup, VRAM budgeting, and home-network inference routing, so it overlaps almost nothing else;
it is the place all of it comes to run.

## Thesis

Every engineer learning AI eventually hits the frontier-API cost wall. Tokens accumulate,
context windows overflow, and the bill arrives. The answer is to own a machine that hosts
local models, runs on a home network, and routes the right tasks away from the frontier.

This course moves the reader from the Micro Center parts counter to a working, networked
local-model host that Claude Code can delegate to. It is organized around a real build
plan: the Cthulhu project, a SFF homebrew machine (Ryzen 7 7700X, RTX 4060 Ti 16GB, 64GB
DDR5-6000, Fractal Ridge case) with a routing layer that distinguishes local from frontier
by cost, latency, context size, and task type.

The reader assembles the machine, installs Linux and CUDA, fits a 14B coding model
entirely in 16GB VRAM, splits 32B-70B quantized models across GPU and system RAM, designs
a routing decision table, and wires Claude Code to delegate through it. The portfolio
artifact is a live, networked inference server with a routing layer; a real Claude Code
session delegates a task through it before the book closes.

## Scope

### In Scope

- Hardware selection: the SFF build (Cthulhu spec BOM), part-by-part rationale
- Physical assembly via Micro Center Express ProBuild
- Linux distribution selection and install (dual-partition: Windows gaming / Linux dev)
- CUDA driver installation and verification
- Ollama and Docker setup; 14B model on-card (zero VRAM overflow)
- Unified memory: 32B-70B quantized models split across GPU and system RAM
- Latency baselining: measure before routing decisions
- Routing layer design: cost, latency, context size, task type as routing signals
- Claude Code integration: API, MCP, or CLI delegation to the local stack
- Inference performance tuning from the aipe ore (GPU profiling, quantization tradeoffs,
  serving throughput)
- Network hosting: local model accessible to other machines on the same network

### Deliberately Out of Scope

- Datacenter or multi-GPU cluster operations (that is a different reader with a different
  budget and a different problem)
- From-scratch model training (that is the training book; see the Scriptorium backlog)
- Cloud GPU instances (the premise of this book is metal you own)
- Windows-only inference setups (the dual-partition is real, but the Linux partition is
  the working environment)

## Ore to Module Map

### Primary Source: Cthulhu SPEC

`C:\Users\raymo\OneDrive\Claude Cowork\Github\specs\cthulhu\SPEC.md`

The SPEC is the spine of this curriculum. Its six How-To steps map directly to the six
core modules:

| SPEC Step | Module | Content |
|---|---|---|
| Step 1: Build the machine | M1: The Build | BOM rationale, Micro Center ProBuild, stress test, first boot |
| Step 2: Choose and install Linux | M2: Linux and CUDA | Distro selection, partition setup, CUDA drivers, verification |
| Step 3: Install the model stack | M3: The Model Stack | Ollama + Docker install, 14B model pull, on-card confirmation |
| Step 4: Test unified memory | M4: Unified Memory | 32B-70B quantized pull, GPU+RAM split, latency baseline |
| Step 5: Design the routing layer | M5: The Routing Layer | Signal table, ROUTING.md design, decision logic |
| Step 6: Wire Claude Code | M6: Wire to Claude Code | API/MCP/CLI interface, delegation test, live run |

### Secondary Ore: aipe (ai-performance-engineering)

`vault/ai-performance-engineering/` (prefix: `aipe`, 725M)

This repo was deliberately antilibraried OUT of Sans Python because its depth belongs in
a hardware-live context. Once the machine is running, the aipe ore feeds:

- GPU profiling and CUDA kernel tuning (M3/M4 depth exercises)
- Quantization tradeoff analysis: GGUF formats, Q4 vs Q8 quality vs. speed curves
- Serving throughput optimization: batch size, KV-cache tuning, context length tradeoffs
- The NVIDIA GTC 2026 content in `resources/` for current best-practice citations

Survey aipe at process-ore time via `vault/MANIFEST.md` and
`ingredients/source/_repos/ai-performance-engineering/`.

## Curriculum Arc

Seven modules: six track the SPEC's steps, plus a perf-and-tuning capstone (M7).

**Module 1: The Build**
Parts list rationale and the Micro Center run: why each component (AM5 platform, RTX 4060 Ti
16GB VRAM, DDR5-6000 bandwidth, NVMe model weight loading, SFX PSU for SFF). Express
ProBuild + 10-minute stress test. First boot verification. Exercise: document your actual
BOM with prices paid vs. estimates.

**Module 2: Linux and CUDA**
Dual-partition plan, distro selection criteria (kernel LTS stability, CUDA support,
community), install walkthrough, NVIDIA driver install, CUDA toolkit, verification sequence
(`nvidia-smi`, a test Python call to the GPU). WSL2 as a counterpoint: why the bare Linux
partition wins for inference workloads. [MS-Learn: Set up a development environment with
WSL2 and CUDA on Windows 11] cited for contrast. Exercise: clean boot, `nvidia-smi` passes,
CUDA sample runs.

**Module 3: The Model Stack**
Ollama install, Docker install, first `ollama pull` for a 14B coding model (e.g.,
`codellama:13b` or `deepseek-coder`). Confirm zero VRAM overflow with `nvidia-smi dmon`.
Basic API call through Ollama's OpenAI-compatible endpoint. Exercise: pull a 14B model,
make an API call, confirm VRAM headroom.

**Module 4: Unified Memory**
Pull a 32B or 70B quantized model (GGUF Q4 or Q5). Watch the model split across GPU VRAM
and system DDR5. Log actual latency: tokens per second, time-to-first-token. Understand
why DDR5-6000 bandwidth matters here (the SPEC rationale for the RAM choice). aipe ore
for quantization depth. Exercise: latency log table filled in; baseline numbers recorded
for the routing decision in M5.

**Module 5: The Routing Layer**
Use the latency baseline from M4 to build a routing decision table. Routing signals:
cost (local is near-zero marginal), latency (local wins for short context, frontier wins
for complex multi-hop), context size (local context window is smaller), task type (code
generation and summarization route local; research and multi-document synthesis route
frontier). Write `ROUTING.md`. Exercise: implement a routing function that takes a task
descriptor and returns `local` or `frontier` with a logged rationale.

**Module 6: Wire to Claude Code**
Implement the Claude Code integration: expose the local Ollama stack via an MCP server or
a lightweight API wrapper. Configure Claude Code to call it. Run a real delegation: Claude
Code receives a task, routes it local via the routing function from M5, Cthulhu executes
it, output returns to Claude Code. Exercise and portfolio artifact: a session log showing
end-to-end delegation from Claude Code through the local routing layer to a 14B model.

**Module 7: Perf and Tuning (aipe depth)**
With the stack running, pull in the aipe ore: GPU profiling, KV-cache tuning, quantization
format tradeoffs (Q4 vs Q8 on the RTX 4060 Ti), throughput testing under concurrent load.
Understand the limits of the build and where the next hardware investment would go. Exercise:
before/after throughput benchmark showing one tuning decision's impact.

## Portfolio Artifact Strategy

The capstone artifact, delivered by M6 and extended in M7, is:

**A working networked local-model inference server with a routing layer, integrated into
Claude Code as a delegation target.**

Concretely: a repository containing the Ollama + Docker configuration, the routing
function (M5), the MCP or API wrapper (M6), and a documented session log proving Claude
Code delegated a real task through it. The hardware spec (BOM, actual prices, build notes)
is committed as `HARDWARE.md`. Latency baselines are committed as `ROUTING.md`.

This artifact is observable, reproducible, and demonstrable to a hiring manager: "I built
the inference server Claude Code delegates to." It is the most literal possible expression
of owning the AI engineering stack.

## Dual-Use Note

Written to be read by a human learner and ingested by an LLM: dense, linked, plain
markdown. Section anchors are stable. The BOM table, SPEC step map, and module table in
this file are machine-parseable. The same pages serve both parties.

---

## Name (GATE-NAME-BOOK — Cleared)

**Locked 2026-06-21: the title is _Local Metal_, the slug is `local-metal`.** The rig is built
and running, so the book graduates with all seven modules authorable and live-verifiable. The
candidates below are kept as the record of the decision.

| Name | Rationale |
|------|-----------|
| **Local Metal** (lead) | Precise, concrete, AI-engineering-idiomatic. "Local" signals the local-vs-frontier axis the routing layer lives on; "Metal" signals bare-metal hardware (not cloud). Names exactly what the reader builds and why it matters. Short enough to live in a path without ambiguity — and it is already the slug throughout the tree, so zero path churn. |
| **Home Inference** | Emphasizes the outcome (running inference at home) over the hardware. More accessible to a reader who does not yet know they want to build a machine; less precise for an engineer who already knows the domain. |
| **Bare Metal** | Classic sysadmin phrase for running directly on hardware without a hypervisor. Familiar and accurate, but slightly generic (used in cloud contexts too), which muddies the homebrew framing. Strongest for a sysadmin-leaning audience; weaker for the AI-Engineer audience this library targets. |

Decision: **Local Metal**. The book has graduated to `library/in-progress/local-metal`.
