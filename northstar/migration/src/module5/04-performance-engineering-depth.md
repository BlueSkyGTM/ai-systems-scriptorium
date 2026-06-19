# Performance Engineering Depth

> **Migrated from** `aipe-module4-inference-serving-chapters` (ch15–20) + `aipe-module4-inference-reference-
> docs` (200+ item checklist) + `aipe-module4-full-sweep-checklist`. The thesis core:
> **"performance engineering > machine learning."**

Scoped to **inference serving** (the `aipe` training/CUDA chapters ch01–14 are in the
[Antilibrary](../antilibrary.md) — perf-eng is inference-only here).

- **Profiling** — Nsight Systems / Compute; roofline analysis (where you actually are vs hardware ceiling).
- **Topology & memory** — NVLink / NVSwitch topology, NUMA / OS tuning, the I/O pipeline.
- **Measured deltas throughout** — continuous batching 4.16×, NVLink KV pool 6.11×, tensor-core decode
  15.65× — you profile and attribute, you don't guess.
- **The 200-item production checklist** — applied to the student's own serving stack as a reference, not a
  read-through.

The discipline: **measure / profile / attribute** (this chapter) layered onto **operate / deploy** (chapter
1). Knowing when to go to Microcenter instead of hiring an MLE is a deployable, demonstrable skill.

**Relocated artifact:** the end-to-end fine-tuning pipeline (07) lives here as Optimize/Deploy reference —
executing the train, not deciding it (the fine-tune-vs-prompt *decision* stays in M2).
