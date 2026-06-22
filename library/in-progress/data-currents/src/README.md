# Data Currents

SQL and the data platform, taught as the AI engineer's operational instruments.

*Sans Python* ends at the data seam. Module 5 Lesson 14 names the boundary precisely: you own the
query, the freshness SLO, and the lineage contract into the data platform; you do not build the
platform. This book is what comes next. It is the deep build of everything that lesson named and
deferred.

The gap it closes is concrete. Data engineering and SQL show up in roughly half of AI Engineer
postings, yet most curricula hand you a single ingestion front door and call the data layer covered.
The interview screen is real and the coverage is thin. Here you learn to sit down at a trace store,
a corpus table, or a feature warehouse and answer the question yourself: where did the latency, the
cost, or the quality go, and what changed upstream to cause it.

## The Thesis

SQL is not a reporting language here. It is the interface to the corpus, the trace store, the
feature table, and the eval warehouse. Ingestion is not a data-ops abstraction; it is the mechanism
that decides whether your retrieval index is fresh enough to answer correctly. Lineage is not a
compliance checkbox; it is the chain that explains why an answer changed, running from the document
version that produced the chunk, through the embedding that placed it, to the eval verdict that
graded it.

You learn the data platform from the AI engineer's seat: querying telemetry, ingesting a corpus on a
freshness SLO, orchestrating the pipeline that moves it, choosing batch against streaming, landing it
in a warehouse or a lakehouse, and tracing every indexed document back to its source version. The
point is never the tool for its own sake. The point is the production question the tool answers.

## Who This Is For

You have shipped a governed multi-agent fleet in *Sans Python* M7, traced its cost and quality, and
run your first seam queries in M5 L14. You can write a `SELECT` and a `WHERE`. This book brings you
to the fluency a Production AI Engineer needs on the job: not DBA depth, but the ability to own the
platform side of the seam instead of only contracting with it.

It is not a data engineering degree. Standing up Kafka, sizing a Spark cluster, and designing star
schemas stay out of scope; you use those as services, not as the engineer who operates them. The
frame stays tight on the AI engineer's data seam at depth.

## What You Will Build

The book closes on a runnable, GitHub-postable proof, in the mold of the *Sans Python* capstones: a
multi-source ingestion pipeline that feeds an AI retrieval system. A batch source (a document corpus,
nightly transformed) and a streaming source (a live feed of updates) both flow through a medallion
lakehouse to a vector index. The pipeline carries a documented freshness SLO on each source leg and
writes a lineage row for every indexed document, so a single query resolves any answer back to the
exact source version that produced it.

Then you prove you can operate it. The final exam hands you a broken pipeline and a degraded
retrieval system; you diagnose the failure with SQL, identify the freshness breach, walk the lineage
to the document that changed the answer, and ship the fix. The artifact is the graded solution plus
the diagnostic query set, judged by a rubric expressed in code.

## How to Read This Book

Work the modules in order. Each one takes a layer of the platform and turns it into a running
artifact; the artifacts compound, so the telemetry store you build in Module 1 becomes the thing the
later modules query, transform, and trace. Every lesson ends with a "Build It in Claude Code"
exercise that hands the work to your editor and resumes the throughline where the last lesson left
it. Read the lesson, run the exercise, then move upstream.
