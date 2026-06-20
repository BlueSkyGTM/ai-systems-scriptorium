# loop-engineering-orange-book — Extraction Context

<!-- Claude Code: read this file, then work through Extraction Targets in order. -->

## Role in Curriculum

PDF companion guide to loop-engineering. The complete reference for loop engineering concepts. Open question: whether this gets included as a reading resource in Module 3 or stays as background reference. The English-language PDF is the primary; the Chinese PDF is a translation.

## Curriculum Mapping

| Module | Section | Source (path) |
|--------|---------|----------------|
| Module 3 | Agent Engineering (reference) | `Loop-Engineering-The-Complete-Guide-v260615.pdf` |

## Extraction Targets

### Target 1: PDF inventory
- **Source:** Root directory
- **What:** List all files. Confirm the PDF filenames and sizes.
- **Output:** `output/inventory.md`
- **Format:** File list with sizes. Note English vs. Chinese.
- **If missing:** Log and stop

### Target 2: PDF structure extraction
- **Source:** `Loop-Engineering-The-Complete-Guide-v260615.pdf`
- **What:** Extract the table of contents, chapter headings, and section headings. Do NOT extract full text content. The goal is to understand what topics are covered so Cowork can decide inclusion in Module 3.
- **Output:** `output/content/orange-book-structure.md`
- **Format:** Full table of contents (headings only). Organized by chapter. Include page numbers if available.
- **If missing:** Log in inventory.md and note PDF extraction failed

### Target 3: README and cover context
- **Source:** `README.md`, `README_zh.md`, `cover.jpg`, `banner.jpg`, `screenshots/`
- **What:** Extract README content (English). Note what the book claims to cover.
- **Output:** Append to `output/content/orange-book-structure.md` as a preamble section.
- **Format:** README content as-is, with a 2-sentence summary at the top.
- **If missing:** Log in inventory.md and continue

### Target 4: Visuals
- **Source:** `screenshots/`, `cover.jpg`, `banner.jpg`
- **What:** Copy cover.jpg and any screenshots from the screenshots/ folder — these show the PDF's visual style.
- **Output:** `output/visuals/`
- **If missing:** Log in inventory.md and continue

## Repo Notes

- **PDF extraction:** Use the pdf skill or equivalent. Extract structure (TOC/headings) only — not full text content.
- **Decision pending:** The open question in CONTEXT.md (root northstar) is whether this PDF gets included as a reading resource in Module 3. Extraction of the TOC enables that decision.
- **Chinese PDF:** Extract the Chinese PDF structure only if the English extraction fails. Both are the same content.

## Done Checklist

_All targets complete and verified 2026-06-18. PDF structure extracted via repo-local `skills/glm-extractor/` (pdf-toc, mechanical) + glm-5.1 for the README summary. English PDF used (had no embedded outline — TOC recovered from text). Zero empty outputs._

- [x] `output/inventory.md` — files + sizes (English PDF primary, Chinese translation noted)
- [x] `output/content/orange-book-structure.md` — full TOC: 4 parts, 9 sections (§01–§09) with start pages + README preamble (2-sentence summary + verbatim)
- [x] `output/visuals/` — cover.jpg + 4 screenshots copied
- [x] `output/antilibrary.md` — noted empty (single reference doc; Module 3 inclusion is an open editorial decision the TOC now enables)
