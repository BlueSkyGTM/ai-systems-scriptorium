# Module 5 — Migration Dossier (Deploy & Performance Engineering)

Source: `ingredients/source/module4/` (old Deploy module) + `module1/rust-*` (threaded in). The
seam's home turf — the infrastructure MLOps engineers and app devs *use*. **Built, not described.**

## Source files in

| Source file | Verdict | Destination / note |
|-------------|---------|--------------------|
| `aefs-module4-infrastructure-production.md` (Ph17, 28 lessons) | **KEEP** | The deploy/ops spine → `src/module5/01,02,03`. |
| `aipe-module4-inference-serving-chapters.md` (ch15–20) | **KEEP — perf depth** | → `src/module5/04`. Measure/profile/attribute layer. |
| `aipe-module4-inference-reference-docs.md` (200+ item checklist) | **KEEP — reference** | Production checklist → `src/module5/04` reference. |
| `aipe-module4-full-sweep-checklist.md` | **KEEP — reference** | Full-sweep checklist. |
| `asdg-module4-deploy-chapters.md` (Ch11–14) | **KEEP** | Infra/MLOps, security/access, reliability/safety, eval/observability → folded into 01/02/03. |
| `asdg-module4-case-studies.md` (Ch16, 20 architectures) | **KEEP — reference** | → `src/module5` reference + **M8 exam architectures**. |
| `mwml-module4-deploy-scripts.md` | **KEEP — deploy subset** | Serving/CI/deploy material → `src/module5/03`. |
| `mwml-module4-madewithml-code-inventory.md` / `-notebook-outline.md` | **CUT (training-pipeline) / KEEP (deploy)** | Model-centric training/lifecycle → antilibrary; deploy/serving stays. |
| `module1/rust-module1-*` | **THREAD IN (from M1)** | Rust ownership on-ramp + async serving → `src/module5/05`. |

## Cuts → antilibrary

- **`aipe` training/CUDA chapters (ch01–14)** — already scoped out at source; perf-eng is inference-only.
- **`mwml` model-centric MLOps** — training pipelines, experiment tracking, model lifecycle. AI Platform
  Engineering is infrastructure-centric, distinct from model-centric MLOps (deviation D2,
  [[delivery-platform-pivot]] not relevant here; see `step2-flow-audit.md`).

## Relocated artifacts land here (Deploy/Optimize, not agent artifacts)

From the old capstone set: **11** observability & eval dashboard, **13** MCP server with registry &
governance (its governance also feeds the M7 fleet finale), **14** speculative-decoding inference server,
**07** end-to-end fine-tuning pipeline (Optimize — executing the train, not deciding it).

## Layering note

`aefs` Ph17 (operate) and `aipe` ch15–20 (measure/profile/attribute) overlap on *topics* (quantization, spec
decode, disaggregation, KV) at different *depths* — **layer them, don't dedup to one.**

## Accounted-for check

Ph17 + aipe inference + asdg deploy + mwml deploy kept; aipe training + mwml training-pipeline → antilibrary;
Rust threaded in; case studies double as M8 reference. Nothing uncatalogued.
