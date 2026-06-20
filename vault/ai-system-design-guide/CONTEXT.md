# ai-system-design-guide — Extraction Context

<!-- Claude Code: read this file, then work through Extraction Targets in order. -->

## Role in Curriculum

Systems thinking backbone across the teaching modules. Under the 8-module structure, chapter content maps to Modules 2, 3, 4, and 5 (case studies also seed the M8 exam). Two companion evaluation guides (Phoenix/Langfuse and LangWatch/Langfuse) are the deepest eval treatment in the stack. Chapter 00 (interview prep) routes to the Ahab project, not this course.

## Curriculum Mapping

| Module | Section | Source (path) |
|--------|---------|----------------|
| Module 2 | Prompting and Context | `05-prompting-and-context/` |
| Module 2 | Retrieval Systems (RAG) | `06-retrieval-systems/` |
| Module 2 | Eval companion guides | `ai_evals_complete_guide_langwatch_langfuse.md`, `ai_evals_comprehensive_study_guide.md` |
| Module 3 | Agentic Systems | `07-agentic-systems/` |
| Module 3 | Memory and State | `08-memory-and-state/` |
| Module 3 | Frameworks and Tools | `09-frameworks-and-tools/` |
| Module 3 | AI Design Patterns | `15-ai-design-patterns/` |
| Module 3 / 4 | Tool Use and Computer Agents | `17-tool-use-and-computer-agents/` (tool use → M3; computer agents → M4 thin) |
| Module 5 | Infrastructure and MLOps | `11-infrastructure-and-mlops/` |
| Module 5 | Security and Access | `12-security-and-access/` |
| Module 5 | Reliability and Safety | `13-reliability-and-safety/` |
| Module 5 | Evaluation and Observability | `14-evaluation-and-observability/` |
| Module 5 / 8 | Case Studies | `16-case-studies/` (Deploy reference + M8 exam architectures) |
| Ahab project | Interview Prep | `00-interview-prep/` |
| Antilibrary | LLM Foundations/Internals | `01-foundations/` |
| Antilibrary | Model Landscape | `02-model-landscape/` |
| Antilibrary | Training and Adaptation | `03-training-and-adaptation/` |
| Antilibrary | Inference Optimization | `04-inference-optimization/` |
| Antilibrary | Document Processing | `10-document-processing/` |

## Extraction Targets

Work through these in order. Each target produces one or more output files.

### Target 1: Chapter inventory
- **Source:** Root directory listing
- **What:** List every chapter folder with its number and title. Note file counts per chapter. Identify which chapters have sub-sections vs. single files.
- **Output:** `output/inventory.md`
- **Format:** Table: chapter number | title | curriculum status (KEEP / ANTILIBRARY / AHAB) | file count
- **If missing:** Log and stop — required first step

### Target 2: Module 2 — Prompting and Context (ch. 05)
- **Source:** `05-prompting-and-context/`
- **What:** Extract all section content. List every sub-section with title and summary (3–5 sentences). Note any Mermaid diagrams.
- **Output:** `output/content/module2-prompting-context.md`
- **Format:** Ordered sections. Each: section name, summary, key concepts introduced (as a short list). Tag versioning-relevant sections with `[THREAD: versioning]`.
- **If missing:** Log in inventory.md and continue

### Target 3: Module 2 — Retrieval Systems (ch. 06)
- **Source:** `06-retrieval-systems/`
- **What:** Extract all 14+ sub-sections. This is the deepest RAG treatment in the stack — full extraction is required.
- **Output:** `output/content/module2-retrieval-systems.md`
- **Format:** Ordered sections. Each: section name, summary (3–5 sentences), key tools/concepts. Note which sections cover production RAG vs. foundational RAG.
- **If missing:** Log in inventory.md and continue

### Target 4: Module 2 — Eval companion guides
- **Source:** `ai_evals_complete_guide_langwatch_langfuse.md`, `ai_evals_comprehensive_study_guide.md`
- **What:** Extract the structure of each guide (headings and sub-headings). For each top-level section, write a 2–3 sentence summary. These are ~3,000 lines each — extract structure, not full content.
- **Output:** `output/content/module2-eval-guides.md`
- **Format:** Two sections (one per guide). Each section: title, full heading structure, per-section summaries. Tag with `[THREAD: eval]` throughout.
- **If missing:** Log in inventory.md and continue

### Target 5: Module 3 — Agentic Systems (ch. 07)
- **Source:** `07-agentic-systems/`
- **What:** Extract all 10 sub-sections. This is the deepest agent treatment in the stack.
- **Output:** `output/content/module3-agentic-systems.md`
- **Format:** Ordered sections with summaries. Flag kill-switch, human-in-the-loop, and agentic security sections with `[THREAD: safety]`. Flag the complexity-ladder / "when to use agents" material with `[GAP 2: complexity ladder]`.
- **If missing:** Log in inventory.md and continue

### Target 6: Module 3 — Memory and State (ch. 08)
- **Source:** `08-memory-and-state/`
- **What:** Extract all sections covering L1–L3 memory tiers, Mem0, caching.
- **Output:** `output/content/module3-memory-state.md`
- **Format:** Ordered sections with summaries.
- **If missing:** Log in inventory.md and continue

### Target 7: Module 3 — Frameworks and Tools (ch. 09)
- **Source:** `09-frameworks-and-tools/`
- **What:** Extract all sections. LangGraph, DSPy, LlamaIndex, Claude Code.
- **Output:** `output/content/module3-frameworks-tools.md`
- **Format:** Ordered sections with summaries. Note which frameworks are seam-relevant vs. Optimize-territory.
- **If missing:** Log in inventory.md and continue

### Target 8: Module 3 — AI Design Patterns (ch. 15)
- **Source:** `15-ai-design-patterns/`
- **What:** Extract the pattern catalog and anti-patterns sections.
- **Output:** `output/content/module3-design-patterns.md`
- **Format:** Pattern catalog table (pattern name | problem it solves | when to use). Anti-patterns section separately.
- **If missing:** Log in inventory.md and continue

### Target 9: Module 3 — Tool Use and Computer Agents (ch. 17)
- **Source:** `17-tool-use-and-computer-agents/`
- **What:** Extract all sections on computer use, tool agents, safety/governance.
- **Output:** `output/content/module3-tool-use-computer-agents.md`
- **Format:** Ordered sections with summaries. Flag safety/governance with `[THREAD: safety]`.
- **If missing:** Log in inventory.md and continue

### Target 10: Module 4 — Infrastructure, Security, Reliability, Eval/Observability (ch. 11–14)
- **Source:** `11-infrastructure-and-mlops/`, `12-security-and-access/`, `13-reliability-and-safety/`, `14-evaluation-and-observability/`
- **What:** Extract all sections from all four chapters.
- **Output:** `output/content/module4-deploy-chapters.md`
- **Format:** Four sections (one per chapter). Each section: ordered sub-sections with summaries. Tag eval/observability sections with `[THREAD: eval]`. Tag guardrails/red-teaming with `[THREAD: safety]`. Tag versioning/staging with `[THREAD: versioning]`.
- **If missing:** Log missing chapters in inventory.md and continue

### Target 11: Module 4 — Case Studies (ch. 16)
- **Source:** `16-case-studies/`
- **What:** Extract all 20 case study summaries. These are portfolio templates for the capstone module.
- **Output:** `output/content/module4-case-studies.md`
- **Format:** Table: case study title | architecture type | what the student replicates | seam relevance (Build / Deploy / Both)
- **If missing:** Log in inventory.md and continue

### Target 12: Ahab — Interview Prep (ch. 00)
- **Source:** `00-interview-prep/`
- **What:** Extract the 116 interview questions (list them). Note any sections (behavioral, technical, system design).
- **Output:** `output/content/ahab-interview-prep.md`
- **Format:** Numbered question list. Section headers preserved.
- **Note:** This output routes to the Ahab project, NOT to the Sans Python curriculum. Label the file clearly.
- **If missing:** Log in inventory.md and continue

### Target 13: Antilibrary chapters
- **Source:** `01-foundations/`, `02-model-landscape/`, `03-training-and-adaptation/`, `04-inference-optimization/`, `10-document-processing/`
- **What:** For each chapter: list the sub-sections only (headings, no content extraction). Note why it's antilibrary.
- **Output:** `output/antilibrary.md`
- **Format:** One entry per chapter: chapter name | reason for antilibrary status | sub-sections (list)
- **If missing:** Log in inventory.md and continue

### Target 14: Visuals (Mermaid diagrams)
- **Source:** All `*.md` files across curriculum chapters (05–09, 11–17)
- **What:** Extract all Mermaid diagram blocks (`\`\`\`mermaid ... \`\`\``). ~38 files contain diagrams.
- **Output:** `output/visuals/diagrams.md`
- **Format:** Per diagram: source file path, surrounding heading context, the diagram block itself.
- **If missing:** Log "no mermaid diagrams found" in inventory.md and continue

## Repo Notes

- **No image files:** This repo has 0 PNG/SVG images. All visuals are Mermaid diagrams embedded in markdown.
- **Chapter depth varies:** Some chapters are single long markdown files, others have sub-folders. Inventory step will reveal the structure.
- **COURSES.md and GLOSSARY.md:** Read and include summaries in inventory.md — these may be useful structural references.
- **PATTERNS.md:** Contains a pattern reference. Extract and include in the design patterns output (Target 8).
- **Two companion eval guides:** These are standalone files at the root, not in a chapter folder. Very long — extract structure only, not full content.

## Done Checklist

_All 14 targets complete and verified 2026-06-18 (section counts checked against source files; zero failed/empty sections). Generation by glm-5.1 (thinking disabled) via the repo-local `skills/glm-extractor/` (chapter | single | headings modes). Mechanical for mermaid + interview list._

- [x] `output/inventory.md` — 18 chapters with KEEP/ANTILIBRARY/AHAB status + file counts; COURSES/GLOSSARY summaries
- [x] `output/curriculum-map.md` — section→module mapping (Modules 2/3/4 + Ahab + antilibrary routing)
- [x] `output/content/module2-prompting-context.md` — 8/8 sections (versioning tag on DSPy)
- [x] `output/content/module2-retrieval-systems.md` — 14/14 sections (foundational/production RAG tiers)
- [x] `output/content/module2-eval-guides.md` — both root guides, structure-only, `[THREAD: eval]`
- [x] `output/content/module3-agentic-systems.md` — 10/10 sections (safety + complexity-ladder tags)
- [x] `output/content/module3-memory-state.md` — 6/6 sections
- [x] `output/content/module3-frameworks-tools.md` — 11/11 sections (seam-relevant/optimize tags)
- [x] `output/content/module3-design-patterns.md` — pattern catalog (47 rows) + anti-patterns (ch15 + PATTERNS.md)
- [x] `output/content/module3-tool-use-computer-agents.md` — 7/7 sections (safety tags)
- [x] `output/content/module4-deploy-chapters.md` — 4 chapters (11–14), 9 subsections, eval/safety/versioning tags
- [x] `output/content/module4-case-studies.md` — 20/20 case studies (table: title/architecture/replicate/seam)
- [x] `output/content/ahab-interview-prep.md` — 116 questions by topic + companion files (routes to Ahab, not curriculum)
- [x] `output/antilibrary.md` — chapters 01–04, 10 documented (headings + reason)
- [x] `output/visuals/diagrams.md` — 64 Mermaid diagrams across 32 files (no image files in repo)
