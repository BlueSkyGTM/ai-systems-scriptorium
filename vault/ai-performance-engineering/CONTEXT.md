# ai-performance-engineering — Extraction Context

<!-- Claude Code: read this file, then work through Extraction Targets in order. -->

## Role in Curriculum

O'Reilly book. Inference serving subset only — Module 4. The training/CUDA/distributed side stays in the antilibrary. The seam-relevant cut: cost per token, throughput per dollar, inference serving (vLLM/SGLang/TensorRT-LLM), hardware planning for serving, profiling inference bottlenecks, KV cache and paged attention. Students deploy and benchmark, not implement GPU kernels.

## Curriculum Mapping

| Module | Section | Source (path) |
|--------|---------|----------------|
| Module 4 | Performance Engineering: Inference Serving | `code/` (serving-relevant chapters), `docs/` |
| Module 4 | 200-item checklist | `code/FULL_SWEEP.md` (if exists) |
| Antilibrary | Training and CUDA subset | `code/ch01-ch07` (training/GPU kernel chapters) |

## Extraction Targets

Work through these in order.

### Target 1: Repo and chapter inventory
- **Source:** `code/` directory listing, `docs/` directory listing, `README.md`
- **What:** List all chapter directories (ch01–ch07) with their titles from each chapter's README.md. List all docs files. Note which chapters appear to cover training vs. inference serving. Note file counts per chapter.
- **Output:** `output/inventory.md`
- **Format:** Table: chapter | title | curriculum status (KEEP: inference / ANTILIBRARY: training/CUDA) | file count. Then a separate listing of docs files.
- **If missing:** Log and stop — required first step

### Target 2: Chapter READMEs — inference serving subset
- **Source:** `code/ch*/README.md` for chapters classified KEEP in Target 1
- **What:** For each keep chapter: extract the full README. Identify what inference serving concepts it covers (vLLM, SGLang, TensorRT-LLM, KV cache, paged attention, cost/token, goodput, profiling).
- **Output:** `output/content/module4-inference-serving-chapters.md`
- **Format:** One section per chapter: chapter number, title, full README content, key concepts list, hands-on tasks the student does.
- **If missing:** Log in inventory.md and continue

### Target 3: Docs directory
- **Source:** `docs/tooling-and-profiling.md`, `docs/appendix.md`, `docs/environment.md`, any other files in `docs/`
- **What:** Extract full content of all docs files. These are likely reference material and the 200-item checklist or similar production reference.
- **Output:** `output/content/module4-inference-reference-docs.md`
- **Format:** One section per file, full content preserved.
- **If missing:** Log in inventory.md and continue

### Target 4: FULL_SWEEP.md (200-item checklist)
- **Source:** `code/FULL_SWEEP.md`
- **What:** Extract full content. This is the production reference checklist students apply to their own serving stack.
- **Output:** `output/content/module4-full-sweep-checklist.md`
- **Format:** Full content as-is.
- **If missing:** Log in inventory.md and note it was not found

### Target 5: Antilibrary chapters
- **Source:** `code/ch*/README.md` for chapters classified ANTILIBRARY in Target 1
- **What:** For each antilibrary chapter: title and one-sentence description of what it covers (training, GPU kernel writing, distributed training, CUDA programming).
- **Output:** `output/antilibrary.md`
- **Format:** One entry per chapter: chapter number | title | why antilibrary
- **If missing:** Log in inventory.md and continue

### Target 6: Visuals
- **Source:** `img/` directory (260 images) + any Mermaid diagrams in markdown files
- **What:** Do NOT copy all 260 images. Extract only images referenced in keep-chapter READMEs and docs files. Copy those specific images to output/visuals/. Extract all Mermaid diagrams.
- **Output:** `output/visuals/` (referenced images only); `output/visuals/diagrams.md` (Mermaid diagrams with source context)
- **If missing:** Log "no visuals collected" in inventory.md and continue

## Repo Notes

- **Chapter classification:** The book covers GPU performance broadly (training, CUDA, inference). The seam-relevant chapters are the ones on inference serving. From the README and chapter titles, expect ch01–ch02 (performance fundamentals, GPU hardware) to be antilibrary, and the later chapters covering vLLM/SGLang/serving to be curriculum-relevant. Use the chapter READMEs to classify.
- **Code files:** Each chapter has Python and CUDA files. Do NOT extract code file contents — extract chapter READMEs and docs only. Students will use the actual code files when they work through the chapter.
- **260 images:** All in `img/` at the root. Do not bulk-copy. Pull only what's referenced in docs/READMEs being extracted.
- **TODO.md:** Check `code/TODO.md` and `code/BOOK-ERRATA.md` — may be useful for noting known gaps in the material.

## Done Checklist

_All targets complete and verified 2026-06-18. Repo has 20 chapters (not 7). Seam call: KEEP = ch15–20 (inference serving); ANTILIBRARY = ch01–14 (training/CUDA/kernels). Generation by glm-5.1 (thinking disabled) via repo-local `skills/glm-extractor/` (single | chapters | passthrough). Docs + checklist preserved verbatim. Zero failed/empty outputs._

- [x] `output/inventory.md` — 20 chapters classified KEEP/ANTILIBRARY + file counts + docs listing + TODO/ERRATA note
- [x] `output/curriculum-map.md` — inference-serving subset → Module 4 mapping
- [x] `output/content/module4-inference-serving-chapters.md` — ch15–20 (6 chapters): GLM key-concepts + hands-on-tasks + full README verbatim (collapsible)
- [x] `output/content/module4-inference-reference-docs.md` — 4 `docs/*.md` files verbatim (passthrough, ~1619 src lines)
- [x] `output/content/module4-full-sweep-checklist.md` — `code/FULL_SWEEP.md` verbatim
- [x] `output/antilibrary.md` — ch01–14 (14 chapters): title + one-line why-antilibrary
- [x] `output/visuals/diagrams.md` — "no visuals collected" logged (keep chapters + docs reference 0 images, contain 0 Mermaid; 260 `img/` files are out-of-seam antilibrary)
