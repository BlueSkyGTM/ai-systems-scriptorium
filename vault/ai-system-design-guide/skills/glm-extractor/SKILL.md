# GLM Extractor — ai-system-design-guide

Repo-specific extractor for the **AI System Design Guide** — a markdown systems-design guide (18 chapters of `.md` section files + huge root eval guides). Self-contained: this folder is the skill. Sibling skills exist in `ai-engineering-from-scratch/` (lesson folders) and `made-with-ml/` (Python project) — different shapes, do not reuse them here.

**Operating principle:** Claude orchestrates, GLM writes. Claude gathers source and runs the script; GLM does all summarization.

---

## 1. Repo shape → why this runner

Each chapter is a folder `NN-name/` of numbered section files `NN-section.md` (some also a `README.md`). A few targets are huge root files (two ~3,400-line eval guides) or want tables (design patterns, case studies). So `extract.py` has **three modes**:

| Mode | Use | How |
|---|---|---|
| `chapter` | Most chapters (05, 06, 07, 08, 09, 11–14, 16, 17) | Fan out **one concurrent GLM call per `*.md` file**, assemble in order under a header. `--include`/`--exclude` scope files (e.g. `--exclude README`). |
| `single` | Derived/table/structure docs (inventory, curriculum-map, design-patterns table, case-study table, interview list, eval-guide summaries, antilibrary) | Build a blob (instruction + gathered source), one call. |
| `headings` | The 3,400-line eval guides + antilibrary + interview bank | **Mechanical** heading-tree extractor (skips fenced code) → blob you feed to `single`. Never dumps full content. |

---

## 2. API config (universal — same key/plan across all sub-repos)

- **Model:** `glm-5.1` (preferred). Override via `GLM_MODEL`.
- **Endpoint:** `https://api.z.ai/api/coding/paas/v4/chat/completions`.
- **Key:** `3ee9e7dff7ca48199128ee2d70e7591d.dQf6EjZtSElYB1vc` — **coding-plan** key. **No second keys.**

### Two traps (key/plan reality, not repo-specific)
1. **`1113` on a general endpoint = model-not-in-plan, not no-balance.** This key only works on `/api/coding/`. (`glm-4-plus` & the high-concurrency roster need the general platform — unreachable here.)
2. **glm-5.x are reasoning models → thinking OFF** (`"thinking":{"type":"disabled"}`), or `content` comes back empty. Baked into `call_glm`.

### Bottleneck
Coding-plan **RPM limit = error `1302`**, bites before the concurrency tier. `chapter` mode runs `MAXWORKERS=6` behind a global `MIN_INTERVAL≈1.3s` gate (~46 req/min) + jittered 8-retry backoff (longer on `1302`). If `1302` appears, raise `MIN_INTERVAL` before `MAXWORKERS`. This repo fans out ~90 files, so the throttle matters.

---

## 3. Runner usage

```bash
# chapter: per-md-file fan-out
python3 skills/glm-extractor/extract.py chapter \
  --chapter-dir 06-retrieval-systems --out output/content/module2-retrieval-systems.md \
  --header-file H.txt --instr-file I.txt [--exclude README] [--max-tokens 1400]

# single: one blob -> one doc
python3 skills/glm-extractor/extract.py single --user-file BLOB.txt --out output/FILE.md [--max-tokens 3500]

# headings: mechanical heading tree (feeds single)
python3 skills/glm-extractor/extract.py headings --file BIG.md --out /tmp/tree.txt [--max-level 3]
```

---

## 4. Targets → mode & flags (this repo)

| # | Output | Mode | Notes |
|---|---|---|---|
| 1 | `output/inventory.md` | single | Chapter table: number \| title \| status (KEEP/ANTILIBRARY/AHAB) \| file count. Include COURSES.md + GLOSSARY.md one-liners. Log mermaid count, "no image files". |
| 2 | `module2-prompting-context.md` | chapter (05) | Tag `[THREAD: versioning]`. |
| 3 | `module2-retrieval-systems.md` | chapter (06) | Note production vs foundational RAG. |
| 4 | `module2-eval-guides.md` | headings→single ×2 | Structure + per-top-section summary. Tag `[THREAD: eval]` throughout. |
| 5 | `module3-agentic-systems.md` | chapter (07, `--exclude README`) | Flag `[THREAD: safety]` (kill-switch/HITL/agentic-security) + `[GAP 2: complexity ladder]`. |
| 6 | `module3-memory-state.md` | chapter (08) | |
| 7 | `module3-frameworks-tools.md` | chapter (09) | Note seam-relevant vs Optimize-territory. |
| 8 | `module3-design-patterns.md` | single | Feed ch15 (01+02) **+ root `PATTERNS.md`**. Catalog table (pattern \| problem \| when) + anti-patterns section. |
| 9 | `module3-tool-use-computer-agents.md` | chapter (17, `--exclude README`) | Flag `[THREAD: safety]`. |
| 10 | `module4-deploy-chapters.md` | chapter ×4 (11,12,13,14) | Run each, assemble 4 sections. Tags: `[THREAD: eval]`, `[THREAD: safety]`, `[THREAD: versioning]`. |
| 11 | `module4-case-studies.md` | chapter (16) → rows | Instruct each call to emit ONE table row: title \| architecture type \| what student replicates \| seam (Build/Deploy/Both). Prepend header row. |
| 12 | `ahab-interview-prep.md` | headings/single | List the 116 questions from `00-interview-prep/01-question-bank.md`; preserve section headers. **Label: routes to Ahab, NOT the curriculum.** |
| 13 | `output/antilibrary.md` | headings→single | ch 01,02,03,04,10: sub-section headings only + reason for antilibrary. |
| 14 | `output/visuals/diagrams.md` | mechanical | Extract ```mermaid blocks from curriculum chapters (05–09, 11–17) with file path + nearest heading. ~32 files. No GLM needed. |

Curriculum-map: single, derived from the mapping table in CONTEXT.md + inventory.

---

## 5. Verification — never trust "done"

Per target: section count vs source file count (`ls NN-*/*.md | wc -l`); grep for `FAILED`/`NO SOURCE`; no empty files; case-study table has 20 rows; eval-guide summaries cover every top-level heading. Mark the CONTEXT Done Checklist only with verified counts.

## 6. File manifest
```
skills/glm-extractor/
├── SKILL.md      ← this spec (ai-system-design-guide)
└── extract.py    ← runner: chapter | single | headings
```
