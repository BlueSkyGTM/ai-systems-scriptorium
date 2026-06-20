# GLM Extractor — loop-engineering-orange-book

Repo-specific extractor for the **loop-engineering orange book** — a PDF companion guide (Module 3 reference). Self-contained; do not reuse sibling skills. **Different job from every other sub-repo: PDF structure extraction.**

**Operating principle:** extract **structure only** (TOC / parts / section headings + page numbers), NOT full text — the goal is to let Cowork decide whether the book becomes a Module 3 reading resource.

## 1. Repo shape
- `Loop-Engineering-The-Complete-Guide-v260615.pdf` — **English (primary)**, 36pp, a Chromium HTML→PDF export (no embedded outline → TOC recovered from text).
- `Loop-Engineering橙皮书-v260615.pdf` — Chinese translation (same content; extract only if English fails).
- `README.md` / `README_zh.md`, `cover.jpg`, `banner.jpg`, `screenshots/` (4 PNGs incl. `page-toc.png`).

## 2. Runner (`extract.py`)
- `pdf-toc` — **MECHANICAL**. Tries the embedded outline (pypdf); falls back to parsing the Contents page (Part + §section lines in order) and maps each section to its body **start page** (first §NN occurrence *after* the contents page; handles `§06Loops…` with no space). Emits a markdown TOC. Never dumps body prose.
- `single` — one GLM call (used for the 2-sentence README summary).

Deps: `pdftotext` (poppler) + `pypdf` (`pip install pypdf` if absent). Universal API config applies for `single` (coding-plan key, `/api/coding/` only, glm-5.x → thinking disabled).

```bash
python3 skills/glm-extractor/extract.py pdf-toc --pdf "Loop-Engineering-The-Complete-Guide-v260615.pdf" \
  --out output/content/orange-book-structure.md
```

## 3. Targets
| # | Output | How |
|---|---|---|
| 1 | `output/inventory.md` | mechanical — file list + sizes + English/Chinese note |
| 2 | `output/content/orange-book-structure.md` | `pdf-toc` — TOC: 4 parts, 9 sections (§01–§09) + start pages |
| 3 | (append to structure) | GLM 2-sentence README summary + `README.md` verbatim preamble |
| 4 | `output/visuals/` | mechanical — copy `cover.jpg` + 4 screenshots |
| — | `output/antilibrary.md` | mechanical — empty (single reference doc; inclusion is an open decision) |

## 4. Verify
9/9 sections have page numbers; 4 parts; README preamble present; cover + 4 screenshots copied. The TOC is the deliverable that enables the inclusion decision.

## 5. Manifest
```
skills/glm-extractor/
├── SKILL.md
└── extract.py   (pdf-toc | single)
```
