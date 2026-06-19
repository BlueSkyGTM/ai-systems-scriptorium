```markdown
# AI Performance Engineering — Inventory

> O'Reilly book repo. Curriculum seam = INFERENCE SERVING only (ch15–20). Training/CUDA/kernel chapters (ch01–14) are antilibrary. 260 images in `img/` (none referenced by keep content). Code files are not extracted.

## Chapters

| Chapter | Title | Status | Files |
|---------|-------|--------|-------|
| ch01 | Performance Fundamentals | ANTILIBRARY: training/CUDA | 25 files |
| ch02 | GPU Hardware Architecture | ANTILIBRARY: training/CUDA | 30 files |
| ch03 | System Tuning | ANTILIBRARY: training/CUDA | 31 files |
| ch04 | Distributed Communication & Multi-GPU Distribution | ANTILIBRARY: training/CUDA | 151 files |
| ch05 | Storage and IO Optimization | ANTILIBRARY: training/CUDA | 25 files |
| ch06 | CUDA Programming Fundamentals | ANTILIBRARY: training/CUDA | 53 files |
| ch07 | Memory Access Patterns | ANTILIBRARY: training/CUDA | 64 files |
| ch08 | Occupancy, Warp Efficiency & ILP | ANTILIBRARY: training/CUDA | 73 files |
| ch09 | Arithmetic Intensity & Kernel Fusion | ANTILIBRARY: training/CUDA | 80 files |
| ch10 | Tensor Core Pipelines & Cluster Features | ANTILIBRARY: training/CUDA | 122 files |
| ch11 | Streams & Concurrency | ANTILIBRARY: training/CUDA | 55 files |
| ch12 | CUDA Graphs & Dynamic Workloads | ANTILIBRARY: training/CUDA | 75 files |
| ch13 | PyTorch Profiling & Memory Tuning | ANTILIBRARY: training/CUDA | 90 files |
| ch14 | Compiler & Triton Optimization | ANTILIBRARY: training/CUDA | 48 files |
| ch15 | Disaggregated Inference & KV Management | KEEP: inference | 80 files |
| ch16 | Production Inference Optimization | KEEP: inference | 56 files |
| ch17 | Disaggregated Prefill/Decode & Routing | KEEP: inference | 44 files |
| ch18 | Advanced Attention & Decoding | KEEP: inference | 75 files |
| ch19 | Dynamic & Adaptive Inference Precision/Memory Systems | KEEP: inference | 52 files |
| ch20 | AI-Assisted Performance Optimization & Case Studies | KEEP: inference | 33 files |

## Docs

- `docs/appendix.md` — Appendix
- `docs/environment.md` — Environment and Configuration
- `docs/gb300-nvfp4-dual2sm.md` — GB300 NVFP4 dual_2sm port (Front N4b, 2026-06-12)
- `docs/tooling-and-profiling.md` — Tooling and Profiling Guide

## Notes

- `code/FULL_SWEEP.md` = 200-item-style production checklist (extracted)
- `code/TODO.md` and `code/BOOK-ERRATA.md` note known gaps/errata
- No visuals collected (keep chapters + docs reference 0 images and contain 0 Mermaid)
```
