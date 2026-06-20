# Exercise: Data Ingestion at Production Scale (Docling)

## Goal

Add an ingestion front door to `module5-serving/`: run Docling locally on a sample PDF to produce a `DoclingDocument`, chunk it with the `HybridChunker`, and feed the chunks into a tiny in-memory index the serving app can query — all offline, no cloud, no GPU.

## Why

Ingestion is the RAG front door, and garbage in is garbage retrieved — the AI Platform Engineer owns the parse-to-chunk seam that decides retrieval quality before retrieval ever runs.

## Steps

1. In `module5-serving/`, create an `ingest/` package. Add `docling` to the project's dependencies (`pip install docling`). First run downloads models; everything after runs locally.
2. Drop a sample document at `ingest/samples/sample.pdf` — use any multi-section PDF with at least one table (a paper, a datasheet, a report). Commit it so the exercise is reproducible.
3. Implement `ingest/parse.py` with `to_document(path) -> DoclingDocument`:
   - Use `DocumentConverter().convert(source).document`.
   - Print `doc.export_to_markdown()` to a file `ingest/out/sample.md` so you can eyeball that reading order, headings, and the table survived. This visual check is the point — confirm the front door works before trusting it.
4. Implement `ingest/chunk.py` with `chunk(doc) -> list[Chunk]`:
   - Use Docling's `HybridChunker`, passing a tokenizer aligned to the embedding model you intend to use (a small local sentence-transformer tokenizer is fine — no API key needed).
   - Each `Chunk` carries: the text, the source headings/captions metadata Docling attaches, and a stable chunk id.
5. Implement `ingest/index.py` with a `TinyIndex`:
   - Embed each chunk with a small local embedding model (e.g. a sentence-transformer) — keep it CPU-only.
   - Store vectors in memory; expose `search(query, k) -> list[Chunk]` by cosine similarity. No vector DB.
6. Record reproducibility: write `ingest/manifest.json` capturing the source filename + hash, the chunker settings, and the embedding-model identifier — the triple that makes the index reproducible.
7. Wire one route into the serving app: `GET /retrieve?q=...` returns the top-k chunk texts and ids from `TinyIndex`. The existing `/generate` endpoint stays untouched.

## Done when

- `python -m ingest.parse ingest/samples/sample.pdf` writes `ingest/out/sample.md`, and the table from the PDF appears as a Markdown table (not flattened text).
- `python -m ingest.chunk` prints the chunk count and shows each chunk carrying its source heading metadata.
- `GET /retrieve?q=<a question answerable from the PDF>` returns relevant chunks, top result first.
- `ingest/manifest.json` exists and records source hash + chunker config + embedding-model id.
- The whole flow runs offline on a laptop with no GPU and no cloud calls after the first model download.

## Stretch

Add a second source format — a `.docx` or `.pptx` of the same content — and confirm it flows through the identical `to_document → chunk → index` path with no change downstream. That is the `DoclingDocument` seam doing its job: prove the parser swapped but the chunker and index did not.
