# M5 SHIP manifest — Module 5, Deploy & Performance Engineering

Shipped 2026-06-19. AUTHOR → VERIFY → SHIP complete. 15 lessons, 6 chapters; `mdbook build` PASS (M1–M5 live).

## What shipped
- 15 lessons relocated `build-stages/m5/output/author/*.md` → `src/module5/`.
- 15 exercise briefs + the `module5-serving/` starter (`_serving/`) → `exercises/module5/`.
- `src/module5/README.md` rewritten: 5-chapter overview → 15-lesson, 6-chapter arc.
- `src/SUMMARY.md` M5 section rewritten: 5 chapters → 15 lessons.
- 5 old ingredient stubs deleted.
- **Antilibrary updated (maintenance rule):** M5 model-centric line revised (experiment tracking now *in* at literacy depth; deep training/lifecycle/DVC/orchestration/fine-tune-impl stays cut); **advanced Python + ML math named as explicit *Avec Python* candidates.**

## Stub → lesson map (5 ingredient chapters → 15 lessons, 6 chapters)
| Old stub (deleted) | Finished lessons |
|---|---|
| 01-serving-and-inference-optimization | 01 Serving Engines · 02 Inside the Engine · 03 Optimization Levers |
| 02-metrics-observability-rollout | 04 Inference Metrics & Load Testing · 05 Safe Rollout · 06 Observability & SRE-for-AI |
| 03-operations-security-compliance-finops | 07 Security & Compliance · 08 Token FinOps |
| 04-performance-engineering-depth | 09 Measure Before You Optimize · 10 The Performance Checklist |
| *(new — MLOps-inventory pass)* | 11 Data Ingestion (Docling) · 12 Experiment Tracking · 13 Fine-Tuning in Proportion |
| 05-rust-entry | 14 Rust Break-In · 15 Async Rust for Serving |

## Carried forward
- `module5-serving/` throughline (serving + metrics + rollout + finops + ingest + Rust proxy) is the platform the **M6 artifacts deploy onto**.
- VERIFY ledger: `build-stages/m5/output/verify/SUMMARY.md`. Carried flag: the ~73% RAG stat (M2 + L11) for M1/M2 reconciliation.
- **Next: M6 (Agent Artifacts)** — the runnable **BUILD→TEST gate begins here** (`tsc --noEmit` / `cargo check` / smoke-with-mocks). Define artifact→platform bindings (capability + one stack + portable seam), the dry-run-first cloud prereqs (`exercises/module6/_prereqs/`), the M8 student-role (before M6 design locks), and the "strong project" bar (deployed + README + eval + tests + versioned) from `hireability-alignment.md`. Write `build-stages/m6/PLAN.md` first.
