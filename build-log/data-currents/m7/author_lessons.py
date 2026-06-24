"""
author_lessons.py
Orchestrates GLM 5.2 (complex) / GLM 5.1 (simple) to write the 5 DC M7 lessons.
Run from the repo root:
    python build-log/data-currents/m7/author_lessons.py
"""

import json
import os
import textwrap
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_KEY  = os.environ.get("ZHIPU_API_KEY", "")
BASE_URL = "https://api.z.ai/api/coding/paas/v4/chat/completions"
MODEL_COMPLEX = "glm-5.2"
MODEL_SIMPLE  = "glm-5.1"

REPO = Path(__file__).parent.parent.parent.parent   # ai-systems-scriptorium/
REF  = REPO / "build-log/data-currents/m7/reference/module7-pipeline"
OUT  = REPO / "library/in-progress/data-currents/src/module7"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# API helper
# ---------------------------------------------------------------------------

def call_glm(prompt: str, model: str = MODEL_COMPLEX, max_tokens: int = 8192) -> str:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        BASE_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
    return body["choices"][0]["message"]["content"]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# STYLE CONTRACT (embedded — must be in every lesson prompt)
# ---------------------------------------------------------------------------

STYLE = """
STYLE CONTRACT (mandatory — treat as an engineering spec; violations are defects):

1. UNITY: Second person ("you"), present tense ("reads"), confident/blunt voice. Never "we."
2. SIMPLICITY: Cut every word that earns nothing. Kill qualifiers (very, quite, basically, actually,
   just, rather). Kill "in order to" → "to"; "utilize" → "use". Active voice always.
3. ONE IDEA PER LESSON. One thought per paragraph.
4. LEAD: 1-2 sentences. First sentence only job: make reader read the second. No "In this lesson we will…"
5. ENDING (seam line): One sentence on what this means for a Production AI Engineer. Vary the shape
   (consequence / warning / cost / reframe / question answered). Never reuse a template.
   Then a blank line, then the handoff block.
6. CORE CONCEPTS: Before the handoff, a `## Core Concepts` section with 1-4 testable propositions
   (one sentence each, stated as claims, not topics).
7. HANDOFF BLOCK (exact format):
   <div class="claude-handoff" data-exercise="exercises/module7/SLUG/">
   **Inspect It in Claude Code** · Exercise · exercises/module7/SLUG/
   </div>
   Replace SLUG with the lesson filename (without .md).
8. HEADINGS: Title Case for every H1/H2/H3. Lowercase articles, conjunctions, short prepositions
   except first/last word.
9. NO EM-DASHES. Use commas, colons, or semicolons instead.
10. MACHINE TOKENS: No runnable command mid-sentence. Put commands/paths in their own fenced block.
11. CODE EXCERPTS: Must be verbatim from the reference files — never invented.
"""

# ---------------------------------------------------------------------------
# Reference file content (read once, reused across lessons)
# ---------------------------------------------------------------------------

PIPELINE = read(REF / "pipeline_flow.py")
SMOKE    = read(REF / "smoke.py")
LINEAGE  = read(REF / "lib/m6_lineage.py")
CORPUS_STORE = read(REF / "lib/corpus_store.py")
CDC_PIPELINE = read(REF / "lib/cdc_pipeline.py")
LAKEHOUSE    = read(REF / "lib/m5_lakehouse.py")
README       = read(REF / "README.md")

# ---------------------------------------------------------------------------
# Lesson 1: 00-overview.md
# ---------------------------------------------------------------------------

def author_overview():
    print("Authoring 00-overview.md...")
    prompt = f"""
You are authoring a lesson for a technical book called Data Currents, aimed at AI Engineers.
The lesson is Module 7, Lesson 1: the overview.

{STYLE}

LESSON SPEC:
- Filename: 00-overview.md
- H1: # Module 7: The Pipeline Artifact
- ONE IDEA: M7 is proven composition, not new code. The reader leaves knowing the capstone
  imports five prior artifacts off disk and orchestrates them.
- LEAD (1-2 sentences): The retrieval system needs both batch and stream fresh, every answer
  traceable; this module proves the five prior modules compose into one run.
- Body paragraph: The composition thesis tied to the STANDARDS Part 3 contract
  (portfolio artifacts reuse, not rebuild; the capstone imports prior artifacts off disk).
- ## What This Module Covers — one paragraph per remaining lesson (the-architecture,
  wiring-the-legs, the-freshness-lineage-proof, the-orchestrated-run), each naming its
  load-bearing detail.
- ## The Diagram — the dependency DAG as a fenced ASCII block. Use VERBATIM from
  pipeline_flow.py lines 13-16:
      batch_ingest   -> stream_apply -> land_lakehouse
                                     -> capture_lineage
      all of the above               -> freshness_gate
- ## The Artifact — module7-pipeline/: a Prefect flow composing five vendored modules,
  28-assertion smoke oracle, dual freshness gate. Reuse is real (imports, not restated).
- ## Who This Is For — finished M2-M6; now compose them.
- ## Prerequisites — Module 1 through Module 6; Python 3.11+; Prefect 3.x; deltalake; pandas
- ## Time Estimate — each lesson 60-90 minutes including exercise
- Key excerpt: the five import blocks from pipeline_flow.py (lines 44-66), condensed, to make
  "composition" concrete. Show them in a fenced Python block.
- Ending: a reframe seam line. Composition as the production standard.
- SLUG for handoff: 00-overview

Cross-links to use (relative paths from module7/):
- M2: ../module2/the-incremental-merge.md
- M4: ../module4/change-data-capture.md
- M5: ../module5/open-table-formats-delta-and-iceberg.md
- M6: ../module6/capturing-lineage-automatically.md

REFERENCE — pipeline_flow.py (read verbatim imports and DAG comment from this):
```python
{PIPELINE[:3000]}
```

Write the complete lesson now. Output only the markdown, no commentary.
"""
    content = call_glm(prompt)
    (OUT / "00-overview.md").write_text(content, encoding="utf-8")
    print("  -> written.")


# ---------------------------------------------------------------------------
# Lesson 2: the-architecture.md
# ---------------------------------------------------------------------------

def author_architecture():
    print("Authoring the-architecture.md...")
    prompt = f"""
You are authoring a lesson for a technical book called Data Currents, aimed at AI Engineers.
The lesson is Module 7, Lesson 2: The Architecture.

{STYLE}

LESSON SPEC:
- Filename: the-architecture.md
- H1: # The Architecture
- ONE IDEA: Two source legs (batch + streaming) converge on one Delta landing and one lineage
  store, gated by a dual freshness check with an alert hook.
- LEAD: Batch is comprehensive but stale by morning; CDC is fast but thin; neither alone is
  sufficient.
- ## The Dependency DAG
  Explain batch->stream->lakehouse, ->lineage, all->gate.
  Show the DAG call section from pipeline_flow.py (the five task calls with their comments,
  lines ~540-573). Note the deliberate stream_results= param (lines ~251-260 docstring)
  that records Prefect edges without a data dependency.
- ## The Dual Freshness Gate
  Hours SLO (batch) + seconds SLO (stream). Show the freshness_gate task body verbatim
  (lines ~442-467 from pipeline_flow.py): the check_freshness call, the is_breached call,
  and the raise RuntimeError if failures.
- ## The Alert Hook
  on_failure=[on_flow_failure] (line ~488). Show the on_flow_failure hook body verbatim
  (lines ~94-110 from pipeline_flow.py).
- Ending: consequence seam line. A healthy stream cannot mask a stalled batch.
- SLUG for handoff: the-architecture

Cross-links:
- M2 freshness SLO: ../module2/the-batch-freshness-slo.md
- M4 streaming monitor: ../module4/the-streaming-freshness-monitor.md
- M3 alerting on breach: ../module3/alerting-on-breach.md

REFERENCE — pipeline_flow.py (read the flow decorator, on_failure hook, DAG section, and freshness_gate task):
```python
{PIPELINE[3000:]}
```

Write the complete lesson now. Output only the markdown, no commentary.
"""
    content = call_glm(prompt)
    (OUT / "the-architecture.md").write_text(content, encoding="utf-8")
    print("  -> written.")


# ---------------------------------------------------------------------------
# Lesson 3: wiring-the-legs.md
# ---------------------------------------------------------------------------

def author_wiring():
    print("Authoring wiring-the-legs.md...")
    prompt = f"""
You are authoring a lesson for a technical book called Data Currents, aimed at AI Engineers.
The lesson is Module 7, Lesson 3: Wiring the Legs.

{STYLE}

LESSON SPEC:
- Filename: wiring-the-legs.md
- H1: # Wiring the Legs
- ONE IDEA: M2 and M4 share one MERGE keyed on (doc_id, content_hash); thin adapters bridge
  schema gaps; vendored modules needed no edits.
- LEAD: Composition fails if each module has its own write path; it works here because batch
  and stream share one contract.
- ## One MERGE, Two Legs
  The content-hash MERGE. Show merge_one_document from corpus_store.py: the hash computation,
  the "same hash skip" branch, the "new hash insert new version" branch. Verbatim.
  Cross-link M2 incremental-merge and M4 change-data-capture.
- ## The Idempotency Contract
  Show the cdc_pipeline.py module docstring (lines ~19-24): insert/update keyed on
  (doc_id, content_hash); replay cannot duplicate.
  Cross-link M3 retries-and-idempotency.
- ## Thin Adapters Bridge Schemas
  Show _corpus_to_dataframe from pipeline_flow.py (lines ~117-140): why a synthetic title
  column is added (M2 collapses title+body into text at silver). This is the only glue;
  modules themselves are untouched.
- ## Delta as the Shared Output
  land_lakehouse writes v0 (batch baseline, version_id == 'v1' filter) then v1 (post-stream).
  Show the key lines from land_lakehouse in pipeline_flow.py (~lines 269-284).
  Cross-link M5 open-table-formats-delta-and-iceberg.
- ## Why No Edits Were Needed
  Payoff paragraph: shared hash contract + thin adapters = vendored modules import clean.
- Ending: reframe seam line. The edits you didn't make are the proof the contract held.
- SLUG for handoff: wiring-the-legs

Cross-links:
- M2 incremental merge: ../module2/the-incremental-merge.md
- M4 change-data-capture: ../module4/change-data-capture.md
- M3 retries: ../module3/retries-and-idempotency.md
- M5 open table formats: ../module5/open-table-formats-delta-and-iceberg.md

REFERENCE — corpus_store.py:
```python
{CORPUS_STORE}
```

REFERENCE — cdc_pipeline.py (first 60 lines for docstring and idempotency contract):
```python
{CDC_PIPELINE[:3000]}
```

REFERENCE — pipeline_flow.py _corpus_to_dataframe adapter and land_lakehouse task:
```python
{PIPELINE[3500:6000]}
```

Write the complete lesson now. Output only the markdown, no commentary.
"""
    content = call_glm(prompt)
    (OUT / "wiring-the-legs.md").write_text(content, encoding="utf-8")
    print("  -> written.")


# ---------------------------------------------------------------------------
# Lesson 4: the-freshness-lineage-proof.md
# ---------------------------------------------------------------------------

def author_proof():
    print("Authoring the-freshness-lineage-proof.md...")
    prompt = f"""
You are authoring a lesson for a technical book called Data Currents, aimed at AI Engineers.
The lesson is Module 7, Lesson 4: The Freshness-Lineage Proof.

{STYLE}

LESSON SPEC:
- Filename: the-freshness-lineage-proof.md
- H1: # The Freshness-Lineage Proof
- ONE IDEA: Two guarantees make this artifact production-grade: freshness gating that fails
  loud, and lineage that answers both directions.
- LEAD: A pipeline that runs is not enough; it must refuse a stale corpus and trace every
  answer to a content hash.
- ## The Gate Fires on a Stale Source
  The negative run: inject "now" 30 hours after ingest (past the 25-hour SLO), gate raises,
  alert fires. Show the _run_negative function from smoke.py: the stale timestamp injection
  and the two negative assertions (ALERTS >= 1, result is None).
  Cross-links: M2 freshness SLO, M3 alerting-on-breach.
- ## Tracing an Answer to Its Sources
  trace_answer_to_sources walks answer -> retrievals -> chunks -> source_documents ->
  content_hash + eval_verdict. Show the function from lib/m6_lineage.py verbatim
  (the SQL JOIN chain).
  Cross-links: M6 querying-the-lineage-store.md, the-lineage-graph.md
- ## Impact Analysis: Which Answers Break?
  impact_of_version reverses the query: given a doc + version, which answers cited it?
  Show the function from lib/m6_lineage.py verbatim.
  Tie to the smoke proof: CDC update to doc_alpha v2 means impact_of_version(doc_alpha, v1)
  returns the affected answer.
  Cross-link: M6 capturing-lineage-automatically.md
- Ending: question-answered seam line. "Why did the model say that?" is now a query.
- SLUG for handoff: the-freshness-lineage-proof

Cross-links:
- M2 freshness SLO: ../module2/the-batch-freshness-slo.md
- M3 alerting: ../module3/alerting-on-breach.md
- M6 querying: ../module6/querying-the-lineage-store.md
- M6 lineage graph: ../module6/the-lineage-graph.md
- M6 capturing: ../module6/capturing-lineage-automatically.md

REFERENCE — lib/m6_lineage.py (trace_answer_to_sources and impact_of_version functions):
```python
{LINEAGE}
```

REFERENCE — smoke.py (full file — find _run_negative and negative assertions):
```python
{SMOKE}
```

Write the complete lesson now. Output only the markdown, no commentary.
"""
    content = call_glm(prompt)
    (OUT / "the-freshness-lineage-proof.md").write_text(content, encoding="utf-8")
    print("  -> written.")


# ---------------------------------------------------------------------------
# Lesson 5: the-orchestrated-run.md
# ---------------------------------------------------------------------------

def author_run():
    print("Authoring the-orchestrated-run.md...")

    # Count check( calls in smoke.py
    check_count = SMOKE.count("check(")

    prompt = f"""
You are authoring a lesson for a technical book called Data Currents, aimed at AI Engineers.
The lesson is Module 7, Lesson 5: The Orchestrated Run.

{STYLE}

LESSON SPEC:
- Filename: the-orchestrated-run.md
- H1: # The Orchestrated Run
- ONE IDEA: Orchestration turns five functions into one scheduled, retryable, verifiable run;
  the smoke oracle is what makes "it works" a machine fact.
- LEAD: Composition is a claim until something runs it on a schedule and proves it.
- ## What Each Task Does
  One line per @task: batch_ingest (retries=2), stream_apply (retries=2), land_lakehouse
  (retries=1), capture_lineage (retries=1), freshness_gate (retries=0).
  Show the five @task decorator lines verbatim from pipeline_flow.py to show the retry
  policy differences. Explain why the gate has zero retries (a stale corpus is not transient).
  Cross-links: M3 dag-tasks-and-dependencies, retries-and-idempotency.
- ## What the Smoke Test Proves
  The 7 assertion groups (batch leg, streaming leg, lakehouse time-travel, lineage trace,
  freshness pass, impact analysis, negative run).
  The exact assertion count is {check_count} (counted from check( calls in smoke.py).
  Emphasize: a deficient run MUST fail the gate. Show the check() helper verbatim and
  the PASS/FAIL summary block from smoke.py.
- ## How to Run It
  Prose sentence introducing the three commands, then a fenced bash block:
  python pipeline_flow.py
  python smoke.py
  python -m pytest tests/ -v
- ## Running in Deployment
  cron="0 2 * * *" (from pipeline_flow.py lines 17-18). Cross-link M3 scheduling-and-backfill.
- ## Success Metrics
  Smoke exits 0, all {check_count} assertions pass, negative run fails gate and fires alert.
- Ending: warning seam line. The run you cannot prove is a run you cannot ship.
- SLUG for handoff: the-orchestrated-run

Cross-links:
- M3 dag tasks: ../module3/the-dag-tasks-and-dependencies.md
- M3 retries: ../module3/retries-and-idempotency.md
- M3 scheduling: ../module3/scheduling-and-backfill.md

REFERENCE — smoke.py (full file):
```python
{SMOKE}
```

REFERENCE — pipeline_flow.py (task decorators and __main__ section):
```python
{PIPELINE[7000:]}
```

Write the complete lesson now. Output only the markdown, no commentary.
"""
    content = call_glm(prompt)
    (OUT / "the-orchestrated-run.md").write_text(content, encoding="utf-8")
    print("  -> written.")


# ---------------------------------------------------------------------------
# SUMMARY.md update (GLM 5.1 — simpler task)
# ---------------------------------------------------------------------------

def update_summary():
    print("Updating SUMMARY.md...")
    summary_path = REPO / "library/in-progress/data-currents/src/SUMMARY.md"
    current = summary_path.read_text(encoding="utf-8")

    prompt = f"""
The following is the current SUMMARY.md for an mdBook. Append a Module 7 section at the end.

CURRENT SUMMARY.md:
{current}

Add exactly this block at the end (after the last line), preserving the existing format:

---

# Module 7: The Pipeline Artifact

- [Overview](module7/00-overview.md)
- [The Architecture](module7/the-architecture.md)
- [Wiring the Legs](module7/wiring-the-legs.md)
- [The Freshness-Lineage Proof](module7/the-freshness-lineage-proof.md)
- [The Orchestrated Run](module7/the-orchestrated-run.md)

Output the COMPLETE updated SUMMARY.md content. Output only the markdown, no commentary.
"""
    content = call_glm(prompt, model=MODEL_SIMPLE)
    summary_path.write_text(content, encoding="utf-8")
    print("  -> SUMMARY.md updated.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    author_overview()
    author_architecture()
    author_wiring()
    author_proof()
    author_run()
    update_summary()
    print("\nAll lessons written. Run verification next:")
    print("  grep -rn -- '—' library/in-progress/data-currents/src/module7/")
    print("  ~/.tools/mdbook/mdbook.exe build library/in-progress/data-currents")
    print("  python platform/bin/route-lint")
