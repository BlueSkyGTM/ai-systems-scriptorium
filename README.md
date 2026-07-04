# AI Systems Scriptorium

**Seven finished technical books on production AI systems engineering: dense, code-first, and written to be read by a human or ingested by an LLM.**

**[Read the library online](https://ai-systems-scriptorium.vercel.app)**: a landing page you arrive on and pick from, each book at its own path.

This is a working library, not a course platform. Seven books are finished and shipped, covering the ground from your first model call to a governed multi-agent fleet running in production. Each is self-contained, built with [mdBook](https://rust-lang.github.io/mdBook/), and each ends in portfolio artifacts you can run, not pages you can only cite.

---

## The Problems This Library Answers

Every book here exists because something specific is broken in how people learn AI engineering. The library is the answer to four of those failures.

### The Entry Barrier Is Manufactured

The standard path front-loads a wall: math, then ML theory, then deep learning, and only many months in, something you can ship. Most people stall on the wall, never the work. The wall is a sequencing choice, not a prerequisite; production teams onboard engineers through the work itself every day. So every book here inverts the order. You ship something real in the first module and earn depth at the moment the work demands it. The whole library shares one through-line: remove the roadblocks that prevent starting.

### Programming Changed and the Curriculum Did Not

Production code is now written with an AI pair in the loop. That moved the scarce skills: specifying work precisely, reading code critically, verifying output, deciding what ships. Most curricula still teach as if the reader will type every line by hand, which trains exactly the part of the job that changed. These books are built for the loop that exists now. Every lesson ends by handing its work to Claude Code with a structured payload; the reader's job is to direct, review, and prove, and the reading and the building form one loop.

### The Coding Bottleneck Moved from Writing to Verifying

When a model produces plausible code on demand, the differentiator is telling right from almost-right. Almost-right is the dangerous one: it runs, it demos, and it fails in production. So verification is not a chapter here; it is the spine. Every code artifact in the library is `pytest`-gated with a negative case, an oracle that proves the check catches the broken version, not just blesses the working one. Capstones are graded by code: rubrics implemented as runnable scripts that exit `READY` or refuse. The reader does not just build the thing; the reader builds the check that would catch its failure.

### Certificates Assert, Artifacts Prove

A completion badge says you watched. The hiring signal is a repo that runs. Each book therefore terminates in a portfolio artifact: a governed multi-agent fleet, an evaluation engine, a graded model pipeline, a fine-tune pipeline gated against a baseline, a local inference server wired into Claude Code. One book, [Answer Engineering](library/completed/answer-engineering), exists solely to convert those artifacts into interview narratives and hiring outcomes.

And underneath all four: most courses teach everything and prepare you for nothing. Each book here teaches a single job and deliberately omits what does not serve it.

---

## The Library

| Book | Read online | What it teaches | What you build |
|---|---|---|---|
| **Sans Python** | [Read](https://ai-systems-scriptorium.vercel.app/sans-python/) · [Source](library/completed/sans-python) | The whole production stack, in the right order: LLMs → agents → multi-agent systems → deploy and performance | A governed multi-agent fleet, turned loose to build a system as your final exam |
| **Just Python** | [Read](https://ai-systems-scriptorium.vercel.app/just-python/) · [Source](library/completed/just-python) | The applied Python you actually write: NumPy, Pandas, vectorization, idioms at interview speed | An evaluation engine (per-class P/R/F1 in pure NumPy) plus a code-graded integrated exam |
| **Machine Math** | [Read](https://ai-systems-scriptorium.vercel.app/machine-math/) · [Source](library/completed/machine-math) | Classic ML paired with the exact math each fundamental needs, built from scratch | Your own `ml` package; a real model built, evaluated, and graded with a model card |
| **Weights and Measures** | [Read](https://ai-systems-scriptorium.vercel.app/weights-and-measures/) · [Source](library/completed/weights-and-measures) | PyTorch and model training, with quality as the throughline | A full fine-tune pipeline gated against a baseline it has to beat |
| **Data Currents** | [Read](https://ai-systems-scriptorium.vercel.app/data-currents/) · [Source](library/completed/data-currents) | Data engineering for AI: SQL → ingestion → orchestration → streaming → lineage | One tested pipeline that every module extends, source doc to eval verdict |
| **Local Metal** | [Read](https://ai-systems-scriptorium.vercel.app/local-metal/) · [Source](library/completed/local-metal) | A home production rig and local models, wired into Claude Code | An MCP server spine: local client → router → Claude Code |
| **Answer Engineering** | [Read](https://ai-systems-scriptorium.vercel.app/answer-engineering/) · [Source](library/completed/answer-engineering) | Interview answers as an engineering discipline, not memorization | A calibration scorer and a dossier grader that only exit `READY` when you are |

> A custom subdomain can front the same deploy without changing anything here. Full status and provenance for each book live in [`CATALOG.md`](CATALOG.md).

---

## The Books, in More Depth

### Sans Python: the Flagship

The name carries the argument for the whole library, not just this book. The standard path front-loads a wall: math, then ML theory, then deep learning, then, many months in, something you can ship. Sans Python refuses that wall and starts on day one with the work itself: call a model, ground it in your data, wrap it in an agent, put that agent into production. Python arrives late, once you are past the gate, as read-literacy plus a narrow write-track (eval scripts, serving glue). That is the name: not *without* Python, but *get started without it.*

Every other book in this library inherits that same refusal under a different name: find the piece of the curriculum a reader is told to master before starting, prove it is optional at the start, and let the reader ship first. Sans Python said it loudest and first, so its name doubles as the mission statement for the whole Scriptorium: the entry barrier is manufactured, and the fix is to remove it, not to explain it better.

The production stack is **TypeScript** for the product layer and **Rust** for the serving layer, each taught the moment you first need it.

Eight modules; five teach (foundations, LLM engineering, single agents, multi-agent systems, deploy and performance) and three are proof. You build single agents, compose them into a governed team, and turn the team loose to build a production system as your final systems exam. Every artifact is a portfolio piece that solves a real problem.

### Just Python

The companion to *Sans Python*: the Python you actually write, not a language tour. NumPy in depth, Pandas for AI pipelines, vectorization discipline, idioms at interview speed. It ends in three runnable artifacts: a data-wrangling tool, an evaluation engine that computes per-class precision/recall/F1 in pure NumPy (no scikit-learn), and an integrated engineering exam that chains them under a six-criterion rubric graded by code.

### Machine Math

Classic machine learning paired with the exact math each fundamental needs: k-NN, gradient descent, linear and logistic regression, trees, ensembles, gradient boosting, evaluation, features, naive Bayes. All of it built from scratch in NumPy, with scikit-learn used only as an oracle. The capstone composes your own `ml` package off disk to build, evaluate, and grade a real model with a model card and a code rubric.

### Weights and Measures

PyTorch and model training with quality as the throughline: the weights you train and the measures that prove them. The training loop, reading loss curves, early stopping as a policy, dataset craft (the JSONL chat contract, dedup, leakage), adapters and LoRA fine-tuning, and an eval pipeline. It closes with three portfolio pieces: a tuned classifier gated against a majority-class baseline, an instruction-tuned LLM with a behavioral-regression suite, and a full fine-tune pipeline behind a code rubric.

### Data Currents

Data engineering for AI systems, end to end and compounding: SQL as an operator skill, batch ingestion (dbt and the medallion pattern), orchestration (Prefect/Airflow), streaming and change-data-capture (Kafka), warehouses and lakehouses (Delta/Iceberg), and lineage from source document to eval verdict. Each module is a real, tested pipeline, and the next module runs against the last one's output, so the throughline is provably continuous.

### Local Metal

The home production environment: build a rig, host local models, and offload Claude Code onto your own metal. The hardware build, Linux and CUDA, the model stack (Ollama/Docker), unified memory and the quantization tradeoffs that decide what fits, a local-vs-cloud routing layer, and an MCP server that wires it all into Claude Code: a runnable spine that reads end to end from local client to router to server.

### Answer Engineering

The getting-hired book: answer construction as an engineering discipline, not memorization. A transferable four-step framework carried across behavioral interviews, technical screens, and AI/ML systems design, then the move that ties it together: turning your real portfolio artifacts into interview narratives. It ends in two tools that grade you in code, a calibration scorer and a full dossier grader, and each exits `READY` only when the work clears the bar.

---

## What Makes the Books Different

- **One job, nothing else.** Each book teaches a single job and deliberately omits what does not serve it. No survey chapters, no "worth knowing it exists" detours.
- **Dense on purpose.** Written to William Zinsser's *On Writing Well* the way an engineer follows a spec: one idea per lesson, one voice, every qualifier that earns nothing cut. If a page reads fast, that is the work.
- **Code-first, not prose.** Reading happens on the page; the building happens in your editor. Every lesson hands its work to Claude Code and tells you what to build. The two are one loop.
- **Proven, not asserted.** Every code artifact is `pytest`-gated with a negative-case oracle, every external claim is verified live against Microsoft Learn, and every book builds clean with `mdbook build` before it ships.
- **Dual-use.** Every page is written to serve a human learner and to ingest cleanly into an LLM: dense, linked, plain markdown. The same page serves either reader.

---

## Under the Hood

The books are produced by an AI-engineering-specialized build system: an `AUTHOR → VERIFY → BUILD/TEST → SHIP` pipeline with a Zinsser-grade writing contract and human gates at the decisions that matter. The repo itself is a **routing system**, the Interpreted Context Methodology (ICM): every boundary carries a `CONTEXT.md` telling an arriving agent what to load, what *not* to load, and where to hand off next, enforced mechanically by `route-lint`. It is how one library stays coherent across seven books and a build engine. Details live in [`platform/CONTEXT.md`](platform/CONTEXT.md).

---

## Start Here

- **Read the flagship:** [Sans Python](https://ai-systems-scriptorium.vercel.app/sans-python/), the roadmap the other books branch from ([source](library/completed/sans-python)).
- **Browse everything:** [`CATALOG.md`](CATALOG.md), the full index and status of every book.
- **Build the whole site locally:**

  ```bash
  # Build every completed book into public/<slug>/ plus the landing page.
  # Needs mdbook on PATH, or point MDBOOK at a binary. This is what Vercel deploys (see vercel.json).
  bash platform/bin/build-site
  python platform/bin/route-lint               # verify the routing layer is sound
  ```

- **How the engine works:** [`platform/CONTEXT.md`](platform/CONTEXT.md) · **the AI contract:** [`CLAUDE.md`](CLAUDE.md) / [`AGENTS.md`](AGENTS.md).
