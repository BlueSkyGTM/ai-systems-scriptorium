# Data Ingestion at Production Scale (Docling)

The retriever you built in Module 2 is only as good as what you feed it, and most of what enterprises want to feed it arrives as PDFs, slide decks, and Word files — formats designed for human eyes, not for a vector index. The chunk is the unit your RAG system retrieves; if the chunk is born from a mangled PDF whose two columns got interleaved and whose tables collapsed into word salad, no reranker downstream can save it. Ingestion is the front door, and garbage in is garbage retrieved.

## The Front Door Nobody Wants to Own

Module 2 taught the RAG spine — ingestion, chunking, embedding, storage, retrieval, generation — and then moved fast past the first step to spend its attention on hybrid search and reranking. That order was honest about where the lessons were, but it inverts where the failures are. The same lesson noted that, by widely-cited industry estimates, the large majority of enterprise RAG failures trace to retrieval rather than generation — and a large share of those failures are upstream of retrieval entirely: the document was parsed wrong before it was ever chunked.

A native-text PDF reads cleanly. A two-column research paper, a scanned contract, a slide with a table and a chart, an invoice — these are where naive extraction dies. Pull the raw text stream out of a two-column PDF and you get the left column's first line, then the right column's first line, then back to the left: reading order destroyed. Tables flatten into a run of numbers with no rows. The chart that carried the actual finding becomes nothing, because it was never text. You can chunk that output perfectly and embed it flawlessly, and you have still indexed nonsense.

This is the step the AI Platform Engineer owns and the step that decides retrieval quality. It deserves a real tool, not a regex over `pdftotext`.

## Docling, and the DoclingDocument Seam

[Docling](https://github.com/docling-project/docling) is that tool: an open-source document-processing library, MIT-licensed and hosted as a project in the LF AI & Data Foundation, that parses the messy formats into one structured representation. It converts PDF, DOCX, PPTX, XLSX, HTML, images, and audio into a single in-memory model called the `DoclingDocument`. The basic call is three lines:

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
doc = converter.convert(source).document   # source = path or URL
print(doc.export_to_markdown())
```

The `DoclingDocument` is the thing to fix your eyes on, because it is the **portable seam** of this whole lesson. It is not a string. It is a typed tree: `texts` for paragraphs, headings, and equations; `tables` as structured `TableItem`s; `pictures` as `PictureItem`s; a `body` tree whose child order holds reading order; and bounding-box and provenance information tying every element back to its page coordinates. From that one model you can serialize out to Markdown, HTML, or lossless JSON.

Why does the seam matter more than the parser? Because everything downstream — your chunker, your embedder, your index — binds to `DoclingDocument`, not to "a PDF" or "a DOCX." Swap a scanned-image source for a native PDF and the structure your chunker sees is the same shape. Add a new input format and nothing downstream changes. The contract is the structured document; the parsers are interchangeable behind it. That is the same swappable-engine stance the serving stack takes — one stable interface, many backends.

## Structure-Aware Parsing: Layout, Tables, OCR, VLMs

What earns Docling its place is the parsing underneath that seam. Its PDF understanding recovers page layout, reading order, table structure, code, and formulas, and classifies images — so the two-column paper comes out in the order a human reads it, and the table comes out as rows and columns rather than a flat token run. For scanned documents and images, it provides extensive OCR (optical character recognition, turning pixels of text into characters) so a scanned contract becomes searchable text instead of an opaque image.

For the documents that defeat layout heuristics, Docling runs vision-language models — a VLM is a model that reads an image and emits structured text, the "use a vision model to extract positional structure" step Module 2 named in the abstract. Docling ships a compact one, GraniteDocling. The escalation ladder is the point: cheap layout parsing for the clean native PDF, OCR for the scan, a VLM for the genuinely hard page. You pay for vision only where the document forces you to, the same proportionality the rest of this module insists on.

This is the same job a managed cloud service does, and naming the parallel keeps the choice honest: Azure's AI Document Intelligence Layout model extracts text, tables, selection marks, and structure from PDFs, images, and Office files in one API call and can emit Markdown specifically for RAG semantic chunking — the cloud counterpart to what Docling does locally. The trade is the one this module keeps making: a managed API buys you scale and language coverage; the local library buys you air-gapped execution and no per-page bill.

That local execution is the operational note worth its weight: Docling runs on your own machine, for sensitive data and air-gapped environments. The contract you ingest never has to leave the building. For the regulated corpora that make up much of the enterprise RAG market — the contracts, the clinical notes, the compliance filings — that is not a nice-to-have, it is the whole reason you can take the job.

## Structure-Aware Chunking — Where This Rejoins Module 2

Parsing into a `DoclingDocument` is half the front door; chunking it is the other half, and Docling chunks the structured document directly rather than re-splitting exported text. It offers a `HierarchicalChunker` that creates one chunk per detected document element and attaches the relevant headers and captions along as metadata, and a `HybridChunker` that starts from that hierarchical result and then makes token-aware adjustments against your embedding model's tokenizer — splitting a chunk only when it overflows the token budget, merging adjacent undersized chunks that share the same headings and captions.

Look at what that gives you for free. Module 2 argued for structure-aware splitting at logical boundaries, hierarchical parent-child chunking for precision-with-context, and aligning chunk size to the embedding model — and then left those as principles. The `HybridChunker` *is* those principles, executed: it splits at structural boundaries because it starts from the document tree, and it sizes to your embedding model because you hand it that model's tokenizer. The Module 2 chunk you embed and the Docling chunk you produce here are the same artifact, and that closes the loop the RAG lesson opened. This is also the concrete tool behind the M2 contextual-retrieval move — the header and caption metadata each chunk carries is exactly the source-anchoring context that lifted retrieval recall.

Docling integrates with LangChain, LlamaIndex, CrewAI, and Haystack, so the chunks flow into whichever framework your RAG stack already speaks, and it exposes an MCP server, which means an agent can call ingestion as a tool — the M3 pattern reaching forward into M6.

## Version the Data, Not Just the Code

A pipeline that turns documents into chunks has inputs that drift. The corpus changes. The chunking parameters change. The embedding model is upgraded, and every vector in the index is now incomparable with the queries embedded by the new one. If you cannot say which corpus version and which chunking config produced the index a given answer came from, you cannot reproduce a result or diagnose a regression — and "the retrieval got worse last Tuesday" becomes unanswerable.

The discipline is data versioning, and the canonical tool is DVC (Data Version Control), which sits beside Git: Git tracks your code and your small config files, while DVC tracks the large data and model artifacts by storing a lightweight pointer in Git and the bytes themselves in object storage. Treated lightly — which is all this module asks — the rule is simply this: pin the corpus snapshot, the chunking parameters, and the embedding-model identifier together, so an index is reproducible from a recorded triple. Prompts get the same treatment; a prompt is an input that changes behavior, so it is versioned like one. You do not need the full DVC machinery on day one. You need the habit of treating data and prompts as versioned inputs, because the day a result you cannot reproduce reaches a customer is the day you wish you had.

That habit is the bridge into the next lesson. Once inputs are versioned, the runs that consume them can be tracked and compared — and eval-driven development gets its durable record.

## Core Concepts

- Ingestion is the RAG front door, and garbage in is garbage retrieved: a mangled parse of a two-column PDF or a flattened table poisons the index before chunking or reranking can run, so parsing quality is upstream of retrieval quality.
- The `DoclingDocument` is the portable seam — a typed tree of texts, tables, pictures, reading order, and bounding-box provenance — that lets parsers (native PDF, OCR, VLM) be swapped behind one stable contract while the chunker, embedder, and index downstream never change shape.
- Docling's `HybridChunker` executes the Module 2 chunking principles concretely: it splits at the document's structural boundaries and sizes chunks to your embedding model's tokenizer, closing the loop the RAG lesson left as theory.
- Data and prompts are versioned inputs, not afterthoughts: pin the corpus snapshot, chunking config, and embedding-model identifier together (DVC-style) so any index — and any answer it produced — is reproducible.

<div class="claude-handoff" data-exercise="exercises/module5/11-data-ingestion-docling/">

**Build It in Claude Code** — add an ingestion front door to `module5-serving/`: install Docling, run it locally on a sample PDF to produce a `DoclingDocument`, chunk it with the `HybridChunker` against a tokenizer, and feed the chunks into a tiny in-memory index the serving app can query. Record the corpus + chunking config so the index is reproducible. No cloud, no GPU.

</div>
