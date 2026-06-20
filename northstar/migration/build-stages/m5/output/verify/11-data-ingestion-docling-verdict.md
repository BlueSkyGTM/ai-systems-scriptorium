# VERIFY verdict — L11 Data Ingestion at Production Scale (Docling)

Verifier: Sonnet VERIFY subagent. Date: 2026-06-19. Sources: WebFetch (github.com/docling-project/docling README + docling-project.github.io docs) and MS Learn connector.

## Claim ledger (every claim grounded against primary docs)

| Claim | Source | Verdict |
|---|---|---|
| Docling is open-source, MIT-licensed | Docling README: "MIT license" | CONFIRMED |
| Hosted by LF AI & Data Foundation | README: "Docling is hosted as a project in the LF AI & Data Foundation" | CONFIRMED (reworded draft to "hosted as a project in") |
| Input formats: PDF, DOCX, PPTX, XLSX, HTML, images, audio | README: "PDF, DOCX, PPTX, XLSX, HTML, EPUB, WAV, MP3, WebVTT, email (EML, MSG), images (PNG, TIFF, JPEG...), LaTeX, ... and more" | CONFIRMED (draft's subset is accurate; audio = WAV/MP3) |
| DoclingDocument = typed tree: texts (paragraphs/headings/equations), tables (TableItem), pictures (PictureItem), body tree w/ reading order, bbox+provenance | DoclingDocument concept page: `texts` = "paragraph, section heading, equation, ..."; `tables` stores TableItem; `pictures` stores PictureItem; `body` = root of body tree; reading order via "the `body` tree and the order of _children_"; "Layout information (i.e. bounding boxes)" + "Provenance information" | CONFIRMED (tightened "reading order" wording to "child order holds reading order"; "bounding-box and provenance information") |
| Basic API: DocumentConverter().convert(source).document; export_to_markdown() | README example | CONFIRMED (README uses `result = converter.convert(source); result.document...`; chained `.convert(source).document` is equivalent and valid) |
| Exports: Markdown, HTML, lossless JSON | README: "Markdown, HTML, WebVTT, DocLang, DocTags and lossless JSON" | CONFIRMED |
| PDF understanding: layout, reading order, table structure, code, formulas, image classification | README: "Advanced PDF understanding incl. page layout, reading order, table structure, code, formulas, image classification, and more" | CONFIRMED (verbatim) |
| OCR for scanned PDFs/images | README: "Extensive OCR support for scanned PDFs and images" | CONFIRMED (added "extensive") |
| VLM support incl. GraniteDocling | README: "Support of several Visual Language Models (GraniteDocling)" | CONFIRMED. Removed unverified "callable from the command line" detail |
| Local/air-gapped execution | README: "Local execution capabilities for sensitive data and air-gapped environments" | CONFIRMED |
| HierarchicalChunker: one chunk per element + header/caption metadata | Chunking concept: "creates one chunk for each individual detected document element" + "attaching all relevant document metadata, including headers and captions" | CONFIRMED (reworded to "creates one chunk per detected document element... attaches the relevant headers and captions") |
| HybridChunker: starts from hierarchical, tokenizer-aware split-when-oversized, merge-undersized-same-headings | Chunking concept: "starts from the result of the hierarchical chunker... based on the user-provided tokenizer (typically aligned to the embedding model tokenizer)"; "splits chunks only when needed (oversized w.r.t. tokens)"; "merges chunks only when possible (undersized successive chunks with same headings & captions)" | CONFIRMED (added "only" + "and captions") |
| Integrations: LangChain, LlamaIndex, CrewAI, Haystack | README: "LangChain, LlamaIndex, Crew AI & Haystack" | CONFIRMED |
| MCP server | README: "Connect to any agent using the MCP server" | CONFIRMED |
| Azure AI Document Intelligence Layout: extracts text/tables/selection marks/structure from PDF/images/Office in one API call, emits Markdown for RAG semantic chunking | MS Learn (Document Intelligence RAG + Layout model docs): "parse different document types... with just a single API call"; "outputted to Markdown format, enabling you to define your semantic chunking strategy"; supports selection marks | CONFIRMED |
| DVC versions large data/model artifacts via Git-tracked pointer + bytes in remote object storage | DVC documented architecture (standard) | CONFIRMED (matches DVC's design; not independently re-fetched — settled tool knowledge) |
| M2 cross-ref: "RAG fails in retrieval roughly 73% of the time in enterprise deployments" | src/module2/03-rag-system.md lines 43, 58 (shipped) — identical phrasing | CONSISTENT with shipped M2; underlying figure FLAGGED (see below) |

## Markers resolved
All 11 `[verify:]` / `[MS-Learn:]` markers removed → clean prose. No markers remain (grep clean).

## FLAGGED
- **73% retrieval-failure stat (soft flag).** The figure is internally consistent with the shipped M2 lesson (03-rag-system.md), which states it identically with "roughly." L11 cites it as a back-reference ("The same lesson noted..."), not a fresh assertion, and is appropriately hedged. The figure's primary origin is industry/vendor commentary, not a peer-reviewed source. Did NOT soften L11's wording — softening here would desync it from the shipped M2 text. Recommend SHIP-level review re-weigh the underlying figure across both lessons together (out of this lesson's scope to change unilaterally).

## STYLE (full read)
- H1 present; single `## Core concepts` block; `claude-handoff` div present and last. ✓
- Lead: problem + seam stake, no throat-clearing. ✓
- Pronoun (you), tense (present), POV (practitioner), voice (blunt) consistent. ✓
- Ending shape: warning/cost ("the day you wish you had") + next-lesson bridge — not a template, not the banned "An AI Platform Engineer who…" opener. ✓
- Acronyms expanded on first use: OCR ✓, VLM ✓, DVC ✓. ✓
- Literacy depth: data-versioning kept "treated lightly," no DVC machinery imposed — correct for lite chapter. ✓

## Verdict: PASS
All capability claims grounded against primary Docling docs and MS Learn. Markers resolved, prose clean, STYLE holds. One soft FLAG on the 73% figure (consistency-preserving; deferred to SHIP).
