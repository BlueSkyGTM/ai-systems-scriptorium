# AI Systems Scriptorium

**Seven finished technical books on production AI systems engineering — dense, code-first, and written to be read by a human *or* ingested by an LLM.**

> Most courses teach you everything and prepare you for nothing. These books are built the other way around: each one teaches a single job, cuts everything that doesn't serve it, and ends every lesson in runnable, tested code.

This is a working library, not a course platform. Seven books are finished and shipped — from your first model call to a governed multi-agent fleet running in production. Each is self-contained (built with [mdBook](https://rust-lang.github.io/mdBook/)), each pairs its lessons with portfolio artifacts you can actually run, and each was written to one spec: clarity is the feature, clutter is a defect.

---

## The library

| Book | What it teaches | What you build |
|---|---|---|
| **[Sans Python](library/completed/sans-python)** — Production AI Engineering | The whole production stack, in the right order: LLMs → agents → multi-agent systems → deploy & performance | A governed multi-agent fleet, turned loose to build a system as your final exam |
| **[Just Python](library/completed/just-python)** | The applied Python you actually write: NumPy, Pandas, vectorization, idioms at interview speed | An evaluation engine (per-class P/R/F1 in pure NumPy) + a code-graded integrated exam |
| **[Machine Math](library/completed/machine-math)** | Classic ML paired with the exact math each fundamental needs — built from scratch | Your own `ml` package; a real model built, evaluated, and graded with a model card |
| **[Weights and Measures](library/completed/weights-and-measures)** | PyTorch and model training, with quality as the throughline | A full fine-tune pipeline gated against a baseline it has to beat |
| **[Data Currents](library/completed/data-currents)** | Data engineering for AI: SQL → ingestion → orchestration → streaming → lineage | One tested pipeline that every module extends, source doc to eval verdict |
| **[Local Metal](library/completed/local-metal)** | A home production rig and local models, wired into Claude Code | An MCP server spine: local client → router → Claude Code |
| **[Answer Engineering](library/completed/answer-engineering)** | Interview answers as an engineering discipline, not memorization | A calibration scorer and a dossier grader that only exit `READY` when you are |

---

## The books, in a little more depth

### Sans Python — Production AI Engineering · *the flagship*

The thesis: **the bottleneck is sequencing, not content.** The standard path front-loads a wall — math, then ML theory, then deep learning, then, many months in, something you can ship. This book inverts it. You start on day one with the work itself: call a model, ground it in your data, wrap it in an agent, put that agent into production.

The production stack is **TypeScript** for the product layer and **Rust** for the serving layer, each taught the moment you first need it. Python is *read-literacy* plus a narrow write-track (eval scripts, serving glue) that arrives late, once you're past the gate. That's the name: not *without* Python, but *get started without it.*

Eight modules — five teach (foundations, LLM engineering, single agents, multi-agent systems, deploy & performance), three are proof: you build single agents, compose them into a governed team, and turn the team loose to build a production system as your final systems exam. Every artifact is a portfolio piece that solves a real problem.

### Just Python

The companion to *Sans Python*: the Python you actually write, not a language tour. NumPy in depth, Pandas for AI pipelines, vectorization discipline, idioms at interview speed. It ends in three runnable artifacts — a data-wrangling tool, an evaluation engine that computes per-class precision/recall/F1 in pure NumPy (no scikit-learn), and an integrated engineering exam that chains them under a six-criterion rubric graded by code.

### Machine Math

Classic machine learning paired with the exact math each fundamental needs — k-NN, gradient descent, linear and logistic regression, trees, ensembles, gradient boosting, evaluation, features, naive Bayes — all built from scratch in NumPy, with scikit-learn used only as an oracle. The capstone composes your own `ml` package off disk to build, evaluate, and grade a real model with a model card and a code rubric.

### Weights and Measures

PyTorch and model training with quality as the throughline — the weights you train and the measures that prove them. The training loop, reading loss curves, early stopping as a policy, dataset craft (the JSONL chat contract, dedup, leakage), adapters and LoRA fine-tuning, and an eval pipeline. It closes with three portfolio pieces: a tuned classifier gated against a majority-class baseline, an instruction-tuned LLM with a behavioral-regression suite, and a full fine-tune pipeline behind a code rubric.

### Data Currents

Data engineering for AI systems, end to end and compounding: SQL as an operator skill, batch ingestion (dbt + the medallion pattern), orchestration (Prefect/Airflow), streaming and change-data-capture (Kafka), warehouses and lakehouses (Delta/Iceberg), and lineage from source document to eval verdict. Each module is a real, tested pipeline — and the next module runs against the last one's output, so the throughline is provably continuous.

### Local Metal

The home production environment: build a rig, host local models, and offload Claude Code onto your own metal. The hardware build, Linux + CUDA, the model stack (Ollama/Docker), unified memory and the quantization tradeoffs that decide what fits, a local-vs-cloud routing layer, and an MCP server that wires it all into Claude Code — a runnable spine that reads end to end from local client to router to server.

### Answer Engineering

The getting-hired book: answer construction as an engineering discipline, not memorization. A transferable four-step framework carried across behavioral interviews, technical screens, and AI/ML systems-design, then the move that ties it together — turning your real portfolio artifacts into interview narratives. It ends in two tools that grade you in code: a calibration scorer and a full dossier grader that each exit `READY` only when the work clears the bar.

---

## What makes the books different

- **One job, nothing else.** Each book teaches a single job and deliberately omits what doesn't serve it. No survey chapters, no "worth knowing it exists" detours.
- **Dense on purpose.** Written to William Zinsser's *On Writing Well* the way an engineer follows a spec — one idea per lesson, one voice, every qualifier that earns nothing cut. If a page reads fast, that's the work.
- **Code-first, not prose.** Reading happens on the page; the building happens in your editor. Every lesson hands its work to Claude Code and tells you what to build. The two are one loop.
- **Proven, not asserted.** Every code artifact is `pytest`-gated with a negative-case oracle, every external claim is verified live against Microsoft Learn, and every book builds clean with `mdbook build` before it ships.
- **Dual-use.** Every page is written to serve a human learner *and* ingest cleanly into an LLM — dense, linked, plain markdown. The same page serves either reader.

---

## Under the hood

The books are produced by an AI-engineering-specialized build system: an `AUTHOR → VERIFY → BUILD/TEST → SHIP` pipeline with a Zinsser-grade writing contract and human gates at the decisions that matter. The repo itself is a **routing system** — the Interpreted Context Methodology (ICM): every boundary carries a `CONTEXT.md` telling an arriving agent what to load, what *not* to load, and where to hand off next, enforced mechanically by `route-lint`. It's how one library stays coherent across seven books and a build engine. Details live in [`platform/CONTEXT.md`](platform/CONTEXT.md).

---

## Start here

- **Read the flagship:** [`library/completed/sans-python`](library/completed/sans-python) — the roadmap the other books branch from.
- **Browse everything:** [`CATALOG.md`](CATALOG.md) — the full index and status of every book.
- **Build a book locally:**

  ```bash
  mdbook build library/completed/sans-python   # static site -> library/completed/sans-python/book
  python platform/bin/route-lint               # verify the routing layer is sound
  ```

- **How the engine works:** [`platform/CONTEXT.md`](platform/CONTEXT.md) · **the AI contract:** [`CLAUDE.md`](CLAUDE.md) / [`AGENTS.md`](AGENTS.md).
