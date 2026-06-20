# made-with-ml — Extraction Context

<!-- Claude Code: read this file, then work through Extraction Targets in order. -->

## Role in Curriculum

Hands-on MLOps depth for Module 4. Provides working implementations of data versioning, experiment tracking, and serving pipelines — each topic has production-grade code, not just notebooks. The goal is a portfolio-grade MLOps project alongside the Build track projects from Module 2.

## Curriculum Mapping

| Module | Section | Source (path) |
|--------|---------|----------------|
| Module 4 | MLOps in Practice | `notebooks/`, `madewithml/`, `deploy/` |
| Module 4 | Data versioning | `datasets/`, `madewithml/` |
| Module 4 | Serving pipelines | `deploy/` |
| Antilibrary | Pure ML training | Parts of `madewithml/` (training internals, not serving) |

## Extraction Targets

Work through these in order.

### Target 1: Repo inventory
- **Source:** Root directory, `madewithml/`, `notebooks/`, `deploy/`, `datasets/`
- **What:** List top-level structure and key files in each directory.
- **Output:** `output/inventory.md`
- **Format:** Directory tree with file counts and a 1-line purpose for each key file.
- **If missing:** Log and stop — required first step

### Target 2: Main notebook structure
- **Source:** `notebooks/madewithml.ipynb`
- **What:** Extract the notebook's section headers (cell titles/markdown headings) and first cell of each section. Do not extract full cell content — extract the outline.
- **Output:** `output/content/module4-madewithml-notebook-outline.md`
- **Format:** Ordered sections with heading and first-cell summary (1–2 sentences). Tag MLOps-relevant sections (serving, monitoring, deployment) vs. training sections.
- **If missing:** Log in inventory.md and continue

### Target 3: madewithml/ source code inventory
- **Source:** `madewithml/`
- **What:** List all Python modules. For each module, extract its docstring or first comment (purpose). Identify which modules handle serving vs. training vs. evaluation.
- **Output:** `output/content/module4-madewithml-code-inventory.md`
- **Format:** Table: module name | purpose | seam category (serving / training / eval / infra)
- **If missing:** Log in inventory.md and continue

### Target 4: Deploy scripts
- **Source:** `deploy/`
- **What:** List all deployment scripts and configs. For each: name, what it deploys, what infrastructure it targets.
- **Output:** `output/content/module4-deploy-scripts.md`
- **Format:** One entry per file: filename | purpose | infrastructure target | student build task.
- **If missing:** Log in inventory.md and continue

### Target 5: Makefile targets
- **Source:** `Makefile`
- **What:** Extract all make targets with their commands. This reveals the full workflow (how to run, test, deploy).
- **Output:** Append to `output/content/module4-madewithml-code-inventory.md` as a "Makefile" section.
- **Format:** Table: target name | command | purpose
- **If missing:** Log in inventory.md and continue

### Target 6: Visuals
- **Source:** Any `*.png`, `*.svg`, `*.jpg` in any directory + Mermaid diagrams in `*.md` files
- **What:** Collect architecture diagrams and system diagrams.
- **Output:** `output/visuals/` for images; `output/visuals/diagrams.md` for Mermaid diagrams
- **If missing:** Log "no visuals found" in inventory.md and continue

## Repo Notes

- **Python-heavy:** This is a Python MLOps repo. The curriculum uses TypeScript/Rust as the building language, but this repo's MLOps patterns (experiment tracking, serving, monitoring) are language-agnostic concepts with Python implementations. Extraction should focus on the concepts and workflow, not the Python syntax.
- **Notebooks:** The main notebook is large. Extract outline only — not full cell content.
- **datasets/:** Check what datasets are included. These are likely the pre-curated datasets students use in Module 4 exercises (consistent with tool-first, pre-curated data decision for Module 2).
- **tests/:** Note the test structure — this feeds the "MLOps concepts have working implementations" portfolio principle.

## Done Checklist

_All targets complete and verified 2026-06-18. Generation by glm-5.1 (thinking disabled) via the repo-local `skills/glm-extractor/` (single-mode + nb-outline). Zero failed/empty outputs._

- [x] `output/inventory.md` — full directory structure + key-file purposes; logs "no visuals found"
- [x] `output/curriculum-map.md` — section→Module 4 mapping (MLOps in practice / data versioning / serving)
- [x] `output/content/module4-madewithml-notebook-outline.md` — 36 sections, outline only, tagged [MLOps]/[Training]
- [x] `output/content/module4-madewithml-code-inventory.md` — 10/10 modules categorized (serving/training/eval/infra) + Makefile (style, clean)
- [x] `output/content/module4-deploy-scripts.md` — 6/6 deploy files (cluster, jobs, services)
- [x] `output/antilibrary.md` — training-internals modules (data/models/train/tune) noted out-of-seam
- [x] `output/visuals/` — `diagrams.md` logs no visuals (repo has no images and no Mermaid)
